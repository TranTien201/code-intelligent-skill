"""Dựng code graph bằng Doxygen (XML) -> cùng schema với build_graph_ts.py.

Cách dùng:  python tools/build_graph_doxygen.py <thư_mục_source> <output.json> [--define MODEL_A]

Doxygen đã tự nối tên -> định nghĩa (references / referencedby), script này chỉ
chạy Doxygen rồi đọc XML, đổi sang schema chung.
"""
import argparse
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import code_hash, is_include_guard, list_files, read_lines, save_graph, symbol_key  # noqa: E402

DOXYFILE = """\
INPUT = {src}
RECURSIVE = YES
FILE_PATTERNS = *.c *.h
OUTPUT_DIRECTORY = {out}
GENERATE_HTML = NO
GENERATE_LATEX = NO
GENERATE_XML = YES
EXTRACT_ALL = YES
EXTRACT_STATIC = YES
EXTRACT_LOCAL_CLASSES = YES
REFERENCES_RELATION = YES
REFERENCED_BY_RELATION = YES
ENABLE_PREPROCESSING = YES
SEARCH_INCLUDES = YES
INCLUDE_PATH = {src}/config
PREDEFINED = {defines}
OPTIMIZE_OUTPUT_FOR_C = YES
FULL_PATH_NAMES = YES
STRIP_FROM_PATH = {src}
QUIET = YES
WARNINGS = NO
"""

KIND_EDGE = {"function": "CALLS", "var": "USES_VAR", "macro": "USES_MACRO",
             "enumconst": "USES_CONST", "type": "USES_TYPE"}


def run_doxygen(src: Path, work: Path, defines: str) -> Path:
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    (work / "Doxyfile").write_text(DOXYFILE.format(src=src, out=work, defines=defines))
    subprocess.run(["doxygen", str(work / "Doxyfile")], check=True, capture_output=True)
    return work / "xml"


def body_range(loc):
    file = loc.get("bodyfile") or loc.get("file")
    start = int(loc.get("bodystart") or loc.get("line") or 0)
    end = int(loc.get("bodyend") or -1)
    if end < start:
        end = start
    return file, start, end


def build(src: Path, work: Path, defines: str) -> dict:
    xml_dir = run_doxygen(src, work, defines)
    nodes, id2key, field_owner, raw_edges = {}, {}, {}, []

    def add(key, name, kind, file, start, end, is_static, code):
        if key in nodes and nodes[key]["file"].endswith(".c"):
            return  # đã có bản định nghĩa ở .c (ưu tiên hơn prototype ở .h)
        nodes[key] = dict(name=name, kind=kind, file=file, start=start, end=end,
                          static=is_static, hash=code_hash(code), guards=[])

    compounds = [ET.parse(p).getroot().find("compounddef") for p in sorted(xml_dir.glob("*.xml"))
                 if p.name not in ("index.xml", "Doxyfile.xml")]
    compounds = [c for c in compounds if c is not None]

    # pass 1: định nghĩa
    for cd in compounds:
        ckind = cd.get("kind")
        if ckind == "struct":
            name = cd.findtext("compoundname")
            loc = cd.find("location")
            file, start, end = body_range(loc)
            add(name, name, "type", file, start, end, False, read_lines(src, file, start, end))
            id2key[cd.get("id")] = name
            for m in cd.iter("memberdef"):
                field_owner[m.get("id")] = name
            continue
        if ckind != "file":
            continue
        for m in cd.iter("memberdef"):
            kind, name = m.get("kind"), m.findtext("name")
            loc = m.find("location")
            file, start, end = body_range(loc)
            is_static = m.get("static") == "yes"
            if kind == "function":
                if loc.get("bodyfile") is None:
                    continue  # chỉ là prototype, không có thân
                key = symbol_key(name, file, is_static)
                add(key, name, "function", file, start, end, is_static, read_lines(src, file, start, end))
            elif kind == "variable":
                key = symbol_key(name, file, is_static)
                add(key, name, "var", file, start, end, is_static, read_lines(src, file, start, end))
            elif kind == "define":
                init = "".join(m.find("initializer").itertext()) if m.find("initializer") is not None else ""
                if is_include_guard(name, init):
                    continue
                key = name
                add(key, name, "macro", file, start, start, False, f"#define {name} {init}")
            elif kind == "typedef":
                key = name
                add(key, name, "type", file, start, end, False, read_lines(src, file, start, end))
            elif kind == "enum":
                key = name if not name.startswith("@") else None
                if key:
                    add(key, name, "type", file, start, end, False, read_lines(src, file, start, end))
                for ev in m.findall("enumvalue"):
                    evn = ev.findtext("name")
                    init = "".join(ev.find("initializer").itertext()) if ev.find("initializer") is not None else ""
                    add(evn, evn, "enumconst", file, start, end, False, f"{evn} {init}")
                    id2key[ev.get("id")] = evn
                    if key:
                        raw_edges.append((key, ev.get("id"), None))
            else:
                continue
            if kind in ("function", "variable", "define", "typedef", "enum") and (kind != "enum" or key):
                id2key[m.get("id")] = key
                # references (gọi hàm, dùng biến/hằng...)
                for r in m.findall("references"):
                    raw_edges.append((key, r.get("refid"), None))
                # ref trong initializer (bảng đăng ký) và trong kiểu trả về/tham số
                for tag in ("initializer", "type"):
                    el = m.find(tag)
                    if el is not None:
                        for r in el.iter("ref"):
                            raw_edges.append((key, r.get("refid"), "REFERENCES" if tag == "initializer" else None))
                for p in m.findall("param"):
                    for r in p.iter("ref"):
                        raw_edges.append((key, r.get("refid"), None))

    # pass 2: đổi refid -> key
    edges = set()
    for src_key, refid, forced in raw_edges:
        if refid in field_owner:
            dst, etype = field_owner[refid], "USES_FIELD"
        else:
            dst = id2key.get(refid)
            if dst is None or dst not in nodes:
                continue
            etype = forced if forced and nodes[dst]["kind"] == "function" else KIND_EDGE[nodes[dst]["kind"]]
        if dst != src_key and src_key in nodes:
            edges.add((src_key, dst, etype))

    return dict(builder="doxygen", root=str(src), files=list_files(src), nodes=nodes,
                edges=[dict(src=s, dst=d, type=t) for s, d, t in sorted(edges)])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--define", default="", help="macro cấu hình model, vd MODEL_A")
    a = ap.parse_args()
    src, out = Path(a.src).resolve(), Path(a.out).resolve()
    g = build(src, out.parent / f"_doxy_{out.stem}", a.define)
    save_graph(g, out)
    print(f"[doxygen]    {src.name}: {len(g['nodes'])} nodes, {len(g['edges'])} edges -> {out}")
