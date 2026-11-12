"""Dựng code graph bằng tree-sitter.

Cách dùng:  python tools/build_graph_ts.py <thư_mục_source> <output.json>

Tree-sitter chỉ là parser (cắt cú pháp từng file). Phần nối tên -> định nghĩa (dựng edge)
là do script này tự làm, theo luật C:
  - symbol static chỉ nhìn thấy trong cùng file
  - còn lại: tên là duy nhất toàn dự án (C không có overload/namespace)
"""
import re
import sys
from pathlib import Path

import tree_sitter_c
from tree_sitter import Language, Parser

sys.path.insert(0, str(Path(__file__).parent))
from common import CODE_EXT, code_hash, is_include_guard, list_files, save_graph, symbol_key  # noqa: E402

PARSER = Parser(Language(tree_sitter_c.language()))
IDENT = re.compile(r"\b[A-Za-z_]\w*\b")


def text(n):
    return n.text.decode()


def first_desc(node, types):
    """Tìm node con đầu tiên (theo chiều sâu) có type thuộc types."""
    stack = [node]
    while stack:
        n = stack.pop(0)
        if n.type in types:
            return n
        stack = list(n.children) + stack
    return None


def has_static(node):
    return any(c.type == "storage_class_specifier" and text(c) == "static" for c in node.children)


def guard_from_error(n):
    """Xử lý '#ifdef X' / '#endif' bị tree-sitter báo ERROR (vd. #ifdef trong initializer list)."""
    t = text(n).strip()
    if t.startswith("#ifdef") or t.startswith("#if"):
        ids = [x for x in IDENT.findall(t) if x not in ("ifdef", "if", "defined")]
        return ("push", ids)
    if t.startswith("#endif"):
        return ("pop", None)
    return None


class Extractor:
    def __init__(self, root: Path):
        self.root = root
        self.nodes = {}        # key -> node info
        self.bodies = []       # (key, ts_node, file) để duyệt edge ở pass 2
        self.defs_by_name = {}  # name -> [key]
        self.field_owner = {}  # field name -> [type key]

    # ---------- pass 1: định nghĩa ----------
    def add(self, name, kind, file, ts_node, is_static, guards, body=True):
        key = symbol_key(name, file, is_static)
        self.nodes[key] = dict(
            name=name, kind=kind, file=file,
            start=ts_node.start_point[0] + 1, end=ts_node.end_point[0] + 1,
            static=is_static, hash=code_hash(text(ts_node)), guards=list(guards),
        )
        self.defs_by_name.setdefault(name, []).append(key)
        if body:
            self.bodies.append((key, ts_node, file))
        return key

    def collect_enum(self, enum_node, file, guards):
        lst = enum_node.child_by_field_name("body")
        if not lst:
            return
        for e in lst.children:
            if e.type == "enumerator":
                self.add(text(e.child_by_field_name("name")), "enumconst", file, e, False, guards)

    def collect_struct_fields(self, spec, type_key):
        body = spec.child_by_field_name("body")
        if not body:
            return
        stack = [body]
        while stack:
            n = stack.pop()
            if n.type == "field_identifier":
                self.field_owner.setdefault(text(n), []).append(type_key)
            stack.extend(n.children)

    def visit_top(self, node, file, guards):
        t = node.type
        if t in ("preproc_ifdef", "preproc_if", "preproc_else", "preproc_elif"):
            g = list(guards)
            name = node.child_by_field_name("name")
            is_ifndef = node.children and text(node.children[0]) == "#ifndef"
            if name is not None and not is_ifndef:
                g.append(text(name))
            cond = node.child_by_field_name("condition")
            if cond is not None:
                g += [x for x in IDENT.findall(text(cond)) if x != "defined"]
            for c in node.children:
                if c != name and c != cond:
                    self.visit_top(c, file, g)
            return
        if t == "function_definition":
            name = first_desc(node.child_by_field_name("declarator"), {"identifier"})
            self.add(text(name), "function", file, node, has_static(node), guards)
        elif t in ("preproc_def", "preproc_function_def"):
            name = text(node.child_by_field_name("name"))
            value = node.child_by_field_name("value")
            if not is_include_guard(name, text(value) if value else ""):
                self.add(name, "macro", file, node, False, guards)
        elif t == "type_definition":
            decl = node.child_by_field_name("declarator")
            name = first_desc(decl, {"type_identifier"}) if decl else None
            if name is not None:
                key = self.add(text(name), "type", file, node, False, guards)
                spec = node.child_by_field_name("type")
                if spec is not None and spec.type == "enum_specifier":
                    self.collect_enum(spec, file, guards)
                if spec is not None and spec.type == "struct_specifier":
                    self.collect_struct_fields(spec, key)
        elif t == "declaration":
            spec = node.child_by_field_name("type")
            if spec is not None and spec.type == "enum_specifier":
                self.collect_enum(spec, file, guards)
            for d in node.children_by_field_name("declarator"):
                if first_desc(d, {"function_declarator"}) is not None:
                    continue  # prototype -> không phải định nghĩa
                name = first_desc(d, {"identifier"})
                if name is not None:
                    self.add(text(name), "var", file, node, has_static(node), guards)
        elif t in ("struct_specifier", "enum_specifier") or (t == "expression_statement"):
            spec = node if t != "expression_statement" else first_desc(node, {"enum_specifier", "struct_specifier"})
            if spec is not None and spec.type == "enum_specifier":
                self.collect_enum(spec, file, guards)
        else:
            for c in node.children:
                if c.type in ("preproc_ifdef", "preproc_if", "declaration", "function_definition",
                              "type_definition", "preproc_def", "preproc_function_def", "enum_specifier"):
                    self.visit_top(c, file, guards)

    # ---------- pass 2: edge ----------
    def resolve(self, name, file):
        cands = self.defs_by_name.get(name, [])
        same_file = [k for k in cands if self.nodes[k]["file"] == file]
        if same_file:
            return same_file[0]
        visible = [k for k in cands if not self.nodes[k]["static"]]
        if visible:
            # ưu tiên định nghĩa thật (.c) hơn
            return sorted(visible, key=lambda k: self.nodes[k]["file"].endswith(".h"))[0]
        return None

    def edges_for(self, key, ts_node, file):
        edges = set()
        own = self.nodes[key]["name"]
        kind = self.nodes[key]["kind"]

        if ts_node.type in ("preproc_def", "preproc_function_def"):
            value = ts_node.child_by_field_name("value")
            for name in IDENT.findall(text(value)) if value else []:
                dst = self.resolve(name, file)
                if dst and dst != key:
                    edges.add((key, dst, "USES_MACRO" if self.nodes[dst]["kind"] == "macro" else "REFERENCES"))
            return edges

        for g in self.nodes[key]["guards"]:
            edges.add((key, g, "GUARDED_BY"))

        def walk(n, guard_stack):
            # n: node; duyệt children theo thứ tự để theo dõi #ifdef nằm trong ERROR
            stack = list(guard_stack)
            for c in n.children:
                if c.type == "ERROR":
                    g = guard_from_error(c)
                    if g and g[0] == "push":
                        stack.append(g[1])
                        for name in g[1]:
                            edges.add((key, name, "GUARDED_BY"))
                        continue
                    if g and g[0] == "pop":
                        if stack:
                            stack.pop()
                        continue
                if c.type in ("preproc_ifdef", "preproc_if"):
                    name = c.child_by_field_name("name")
                    is_ifndef = c.children and text(c.children[0]) == "#ifndef"
                    if name is not None and not is_ifndef:
                        edges.add((key, text(name), "GUARDED_BY"))
                    cond = c.child_by_field_name("condition")
                    if cond is not None:
                        for x in IDENT.findall(text(cond)):
                            if x != "defined":
                                edges.add((key, x, "GUARDED_BY"))
                    for cc in c.children:
                        if cc != name and cc != cond:
                            walk_one(cc, stack)
                    continue
                walk_one(c, stack)

        def walk_one(c, stack):
            if c.type == "identifier":
                name = text(c)
                if name != own:
                    dst = self.resolve(name, file)
                    if dst:
                        dk = self.nodes[dst]["kind"]
                        parent = c.parent
                        is_call = parent is not None and parent.type == "call_expression" \
                            and parent.child_by_field_name("function") == c
                        etype = {"function": "CALLS" if is_call else "REFERENCES",
                                 "var": "USES_VAR", "macro": "USES_MACRO",
                                 "enumconst": "USES_CONST", "type": "USES_TYPE"}[dk]
                        edges.add((key, dst, etype))
            elif c.type == "type_identifier":
                dst = self.resolve(text(c), file)
                if dst and dst != key:
                    edges.add((key, dst, "USES_TYPE"))
            elif c.type == "field_identifier" and kind != "type":
                owners = self.field_owner.get(text(c), [])
                if len(owners) == 1:  # chỉ nối khi field name là duy nhất -> tránh nối sai
                    edges.add((key, owners[0], "USES_FIELD"))
            walk(c, stack)

        walk(ts_node, [])
        return edges


def build(root: Path) -> dict:
    ex = Extractor(root)
    files = list_files(root)
    trees = {}
    for f in files:
        if Path(f).suffix in CODE_EXT:
            trees[f] = PARSER.parse((root / f).read_bytes())
            ex.visit_top(trees[f].root_node, f, [])

    edges = set()
    for key, ts_node, file in ex.bodies:
        edges |= ex.edges_for(key, ts_node, file)

    return dict(
        builder="treesitter", root=str(root), files=files, nodes=ex.nodes,
        edges=[dict(src=s, dst=d, type=t) for s, d, t in sorted(edges)],
    )


if __name__ == "__main__":
    src, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
    g = build(src)
    save_graph(g, out)
    print(f"[treesitter] {src.name}: {len(g['nodes'])} nodes, {len(g['edges'])} edges -> {out}")
