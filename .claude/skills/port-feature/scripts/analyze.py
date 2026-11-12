"""Bước 2-5 - Phân tích: drift, closure đi ra, closure đi vào, guard, đánh giá ảnh hưởng.

Cách dùng:
  python tools/analyze.py --graph-a A_latest.json --graph-b B_latest.json --seed seed.json \
                          --out-dir out/ts [--config-dir config]

Nguyên tắc tiết kiệm: chỉ đi theo edge từ các symbol của feature; dừng nhánh ngay khi
B đã có symbol y hệt (hash giống). LLM/người chỉ cần đọc snippet trong llm_review.md.
"""
import argparse
import json
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import load_graph, read_lines  # noqa: E402

OUT_EDGES = {"CALLS", "REFERENCES", "USES_TYPE", "USES_MACRO", "USES_CONST", "USES_VAR", "USES_FIELD"}


class Analyzer:
    def __init__(self, ga, gb, seed, config_dir):
        self.ga, self.gb, self.seed = ga, gb, seed
        self.A, self.B = ga["nodes"], gb["nodes"]
        self.config_dir = config_dir.rstrip("/") + "/"
        self.out_adj, self.in_adj = {}, {}
        for e in ga["edges"]:
            self.out_adj.setdefault(e["src"], []).append((e["dst"], e["type"]))
            self.in_adj.setdefault(e["dst"], []).append((e["src"], e["type"]))
        self.b_files = set(gb["files"])
        self.b_macros = {n["name"] for n in self.B.values() if n["kind"] == "macro"}

    def status_in_b(self, key):
        if key not in self.B:
            return "MISSING"
        return "IDENTICAL" if self.B[key]["hash"] == self.A[key]["hash"] else "DIFFERENT"

    def deps(self, k):
        """Edge đi ra của k. Với symbol dùng chung bị feature sửa: chỉ giữ edge tới tên
        mà feature thêm vào (new_tokens), vì ta chỉ merge HUNK của feature sang B."""
        edges = self.out_adj.get(k, [])
        new_tokens = self.seed.get("new_tokens", {})
        if k in new_tokens:
            allowed = set(new_tokens[k])
            edges = [(d, t) for d, t in edges
                     if (self.A[d]["name"] if d in self.A else d) in allowed]
        return edges

    def is_config(self, key):
        n = self.A.get(key)
        return n is not None and n["file"].startswith(self.config_dir)

    def run(self):
        seed = self.seed
        seed_keys = [k for k in seed["added"] + seed["modified"]]
        res = dict(add=[], merge=[], conflicts=[], guards=[], drift=[], drift_shared=[], report_only=[],
                   glue_review=[], stop_identical=[], already_in_b=[], b_impact=[],
                   missing_in_latest=[], visited=0)
        parent = {}
        in_scope = set()  # symbol sẽ được đưa sang B (add + merge)
        guard_users = {}

        # --- seed: phân loại + drift ---
        for k in seed_keys:
            if k not in self.A:
                res["missing_in_latest"].append(k)  # feature đã bị xoá/đổi tên ở A_latest
                continue
            if seed["after_hash"][k] != self.A[k]["hash"]:
                # symbol của riêng feature đổi sau commit -> lấy bản A_latest (bug-fix...)
                # symbol dùng chung đổi -> thường do feature khác, chỉ ghi nhận
                res["drift" if k in seed["added"] else "drift_shared"].append(k)
            if self.is_config(k):
                guard_users.setdefault(self.A[k]["name"], set())
                continue
            st = self.status_in_b(k)
            if st == "MISSING":
                res["add"].append(dict(key=k, reason="feature"))
                in_scope.add(k)
            elif st == "DIFFERENT":
                res["merge"].append(k)
                in_scope.add(k)
            else:
                res["already_in_b"].append(k)

        # --- closure đi ra (BFS), dừng khi B đã có y hệt ---
        q = deque(k for k in in_scope)
        seen = set(in_scope)
        while q:
            k = q.popleft()
            res["visited"] += 1
            for dst, etype in self.deps(k):
                if etype == "GUARDED_BY":
                    guard_users.setdefault(dst, set()).add(k)
                    continue
                if dst in seen or dst not in self.A:
                    continue
                seen.add(dst)
                parent[dst] = k
                if self.is_config(dst):
                    guard_users.setdefault(self.A[dst]["name"], set()).add(k)
                    continue
                st = self.status_in_b(dst)
                if st == "IDENTICAL":
                    res["stop_identical"].append(dst)
                elif st == "MISSING":
                    res["add"].append(dict(key=dst, reason="dependency", path=self.path(dst, parent)))
                    in_scope.add(dst)
                    q.append(dst)
                else:
                    users_in_b = sorted({s for s, _ in self._b_in_edges(dst)})
                    # B không có chỗ nào dùng -> thay bằng bản A là an toàn
                    suggestion = "SAFE_REPLACE" if not users_in_b else "NEEDS_REVIEW"
                    res["conflicts"].append(dict(key=dst, path=self.path(dst, parent),
                                                 used_in_b_by=users_in_b, suggestion=suggestion))
        # edge GUARDED_BY của các symbol trong scope (kể cả symbol do seed thêm)
        for k in in_scope:
            for dst, etype in self.deps(k):
                if etype == "GUARDED_BY":
                    guard_users.setdefault(dst, set()).add(k)

        # --- guard: macro cấu hình mà code của feature phụ thuộc ---
        for macro, users in sorted(guard_users.items()):
            if macro in self.b_macros:
                continue
            a_node = self.A.get(macro)
            # macro chỉ là guard của code KHÔNG thuộc feature (vd SUPPORT_ECO_REPORT) thì bỏ qua
            feature_macro = a_node is not None and macro in {self.A[k]["name"] for k in seed_keys if k in self.A}
            if users or feature_macro:
                res["guards"].append(dict(macro=macro, defined_in_a=a_node["file"] if a_node else None,
                                          used_by=sorted(users)))

        # --- closure đi vào: ai trong A_latest đang dùng symbol MỚI của feature mà nằm ngoài diff ---
        # chỉ xét symbol DO FEATURE TẠO RA (không xét phụ thuộc như density - module đó
        # được nhiều chỗ khác của A dùng, không liên quan feature)
        feature_owned = {a["key"] for a in res["add"] if a["reason"] == "feature"}
        for k in feature_owned:
            for src, etype in self.in_adj.get(k, []):
                if src in in_scope or src not in self.A or etype == "GUARDED_BY":
                    continue
                st = self.status_in_b(src)
                item = dict(key=src, uses=k, edge=etype)
                if st == "MISSING":
                    res["report_only"].append(item)   # feature khác (chỉ có ở A) dùng lại feature này
                else:
                    res["glue_review"].append(item)   # B có symbol này -> có thể là điểm nối bị sót
        # --- ảnh hưởng phía B: symbol dùng chung bị sửa -> ai ở B đang dùng ---
        for k in res["merge"]:
            users = sorted({s for s, _ in self._b_in_edges(k)})
            res["b_impact"].append(dict(key=k, kind=self.A[k]["kind"], used_in_b_by=users))

        res["files"] = self.files(res)
        res["risk"] = self.risk(res)
        for key in ("stop_identical", "report_only", "glue_review"):
            res[key] = dedupe(res[key])
        return res

    def _b_in_edges(self, key):
        return [(e["src"], e["type"]) for e in self.gb["edges"] if e["dst"] == key]

    def path(self, k, parent):
        p = [k]
        while p[-1] in parent:
            p.append(parent[p[-1]])
        return " <- ".join(p)

    def files(self, res):
        new_files, insert_into_existing = set(), set()
        for a in res["add"]:
            f = self.A[a["key"]]["file"]
            if f not in self.b_files:
                new_files.add(f)
                # header đi kèm .c (vd density.c -> density.h)
                h = f[:-2] + ".h"
                if f.endswith(".c") and (Path(self.ga["root"]) / h).exists() and h not in self.b_files:
                    new_files.add(h)
            elif f not in self.seed["changed_files"]:
                insert_into_existing.add(f)
        new_files |= {f for f in self.seed["new_files"] if f not in self.b_files}
        merge_files = [f for f in self.seed["changed_files"] if f in self.b_files]
        config_files = [f for f in self.seed["changed_files"]
                        if f.startswith(self.config_dir) and f not in self.b_files]
        return dict(new=sorted(new_files), merge=sorted(merge_files),
                    insert_symbol_into_existing=sorted(insert_into_existing),
                    config_not_in_b=sorted(config_files))

    def risk(self, res):
        reasons = []
        for item in res["b_impact"]:
            if item["kind"] == "type":
                reasons.append(f"HIGH: kiểu dữ liệu dùng chung '{item['key']}' bị sửa "
                               f"(B đang dùng ở {len(item['used_in_b_by'])} chỗ; kiểm tra NVRAM/layout)")
        for c in res["conflicts"]:
            reasons.append(f"HIGH: '{c['key']}' có ở B nhưng KHÁC A -> xung đột, cần người/LLM quyết")
        for g in res["guards"]:
            reasons.append(f"MEDIUM: B chưa define '{g['macro']}' -> copy xong code KHÔNG được build")
        if res["drift"]:
            reasons.append(f"MEDIUM: {len(res['drift'])} symbol đã thay đổi sau commit feature (drift)")
        if res["glue_review"]:
            reasons.append(f"MEDIUM: {len(res['glue_review'])} điểm nối nghi vấn ngoài diff")
        level = "HIGH" if any(r.startswith("HIGH") for r in reasons) else \
            "MEDIUM" if reasons else "LOW"
        return dict(level=level, reasons=reasons)


def dedupe(items):
    out, seen = [], set()
    for x in items:
        s = json.dumps(x, sort_keys=True)
        if s not in seen:
            seen.add(s)
            out.append(x)
    return out


def snippet(graph, key):
    n = graph["nodes"][key]
    return read_lines(Path(graph["root"]), n["file"], n["start"], n["end"])


def write_review(res, ga, gb, out_dir: Path):
    """Chỉ những đoạn cần người/LLM phán đoán -> đây là toàn bộ 'context' cần đọc."""
    parts = ["# Cần review (chỉ snippet liên quan)\n"]
    for c in res["conflicts"]:
        parts += [f"## Xung đột: `{c['key']}`  ({c['path']})", "**A_latest:**", "```c",
                  snippet(ga, c["key"]), "```", "**B_latest:**", "```c", snippet(gb, c["key"]), "```",
                  f"B đang dùng ở: {c['used_in_b_by']}\n"]
    for k in res["drift"]:
        parts += [f"## Drift: `{k}` đã đổi sau commit feature -> dùng bản A_latest", "```c",
                  snippet(ga, k), "```\n"]
    for r in res["report_only"] + res["glue_review"]:
        parts += [f"## Phụ thuộc chiều vào: `{r['key']}` dùng `{r['uses']}`", "```c",
                  snippet(ga, r["key"]), "```\n"]
    text = "\n".join(parts)
    (out_dir / "llm_review.md").write_text(text)
    return len(text)


def write_report(res, out_dir: Path, ga, review_chars):
    repo_chars = sum((Path(ga["root"]) / f).stat().st_size for f in ga["files"])
    L = [f"# Báo cáo port feature  (builder: {ga['builder']})\n",
         f"**Mức rủi ro: {res['risk']['level']}**\n"]
    L += [f"- {r}" for r in res["risk"]["reasons"]]
    L += ["\n## File", f"- Copy mới: {res['files']['new']}", f"- Merge (3-way): {res['files']['merge']}",
          f"- Chèn symbol vào file có sẵn ở B: {res['files']['insert_symbol_into_existing']}",
          f"- File cấu hình A (map sang B): {res['files']['config_not_in_b']}",
          "\n## Symbol cần thêm vào B"]
    L += [f"- `{a['key']}` ({a['reason']}{', ' + a['path'] if a.get('path') else ''})" for a in res["add"]]
    L += ["\n## Symbol có sẵn ở B cần merge hunk của feature"] + [f"- `{k}`" for k in res["merge"]]
    L += ["\n## Xung đột"] + [f"- `{c['key']}`: {c['path']}" for c in res["conflicts"]]
    L += ["\n## Guard (#ifdef) B chưa define"] + [f"- `{g['macro']}` dùng bởi {g['used_by']}" for g in res["guards"]]
    L += ["\n## Drift (lấy bản A_latest)"] + [f"- `{k}`" for k in res["drift"]]
    L += ["\n## Symbol dùng chung đã đổi sau feature (do commit khác, chỉ merge hunk feature)"]
    L += [f"- `{k}`" for k in res["drift_shared"]]
    L += ["\n## Chỉ báo cáo - feature khác của A đang dùng feature này (KHÔNG copy)"]
    L += [f"- `{r['key']}` -> `{r['uses']}`" for r in res["report_only"]]
    L += ["\n## Điểm nối nghi vấn cần review"] + [f"- `{r['key']}` -> `{r['uses']}`" for r in res["glue_review"]]
    L += ["\n## Dừng vì B đã có y hệt (không cần đọc)"] + [f"- `{k}`" for k in res["stop_identical"]]
    L += ["\n## Chi phí context",
          f"- Toàn bộ source A_latest: {repo_chars:,} ký tự (~{repo_chars // 4:,} token)",
          f"- Snippet cần người/LLM đọc (llm_review.md): {review_chars:,} ký tự (~{review_chars // 4:,} token)",
          f"- Số symbol đã duyệt trên graph: {res['visited']}"]
    (out_dir / "report.md").write_text("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph-a", required=True)
    ap.add_argument("--graph-b", required=True)
    ap.add_argument("--seed", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--config-dir", default="config")
    a = ap.parse_args()
    ga, gb = load_graph(a.graph_a), load_graph(a.graph_b)
    seed = json.loads(Path(a.seed).read_text())
    res = Analyzer(ga, gb, seed, a.config_dir).run()
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "manifest.json").write_text(json.dumps(res, indent=2, ensure_ascii=False))
    n = write_review(res, ga, gb, out)
    write_report(res, out, ga, n)
    print(f"[analyze] add={len(res['add'])} merge={len(res['merge'])} conflicts={len(res['conflicts'])} "
          f"guards={len(res['guards'])} drift={len(res['drift'])} report_only={len(res['report_only'])} "
          f"risk={res['risk']['level']} -> {out}/report.md")


if __name__ == "__main__":
    main()
