"""Chấm điểm manifest so với đáp án (data/expected.json).

Cách dùng: python tools/evaluate.py data/expected.json out/ts/manifest.json [out/doxygen/manifest.json ...]
"""
import json
import sys
from pathlib import Path


def extract(m):
    return {
        "add_symbols": {a["key"] for a in m["add"]},
        "merge_symbols": set(m["merge"]),
        "conflicts": {c["key"] for c in m["conflicts"]},
        "guards": {g["macro"] for g in m["guards"]},
        "drift": set(m["drift"]),
        "report_only": {r["key"] for r in m["report_only"]},
        "glue_review": {r["key"] for r in m["glue_review"]},
        "new_files": set(m["files"]["new"]),
        "merge_files": set(m["files"]["merge"]),
        "high_impact": {b["key"] for b in m["b_impact"] if b["kind"] == "type"},
    }


def score(exp, got):
    tp = len(exp & got)
    recall = tp / len(exp) if exp else 1.0
    precision = tp / len(got) if got else (1.0 if not exp else 0.0)
    return recall, precision


def main():
    expected = json.loads(Path(sys.argv[1]).read_text())
    manifests = {Path(p).parent.name: extract(json.loads(Path(p).read_text())) for p in sys.argv[2:]}
    cats = [c for c in expected if c != "must_not_copy"]
    names = list(manifests)

    rows = ["| Hạng mục | " + " | ".join(f"{n} recall | {n} precision" for n in names) + " |",
            "|---|" + "---|---|" * len(names)]
    detail = []
    for c in cats:
        exp = set(expected[c])
        cells = []
        for n in names:
            got = manifests[n][c]
            r, p = score(exp, got)
            cells.append(f"{r:.0%} | {p:.0%}")
            miss, extra = sorted(exp - got), sorted(got - exp)
            if miss or extra:
                detail.append(f"- **{n} / {c}**: thiếu {miss or '-'}; thừa {extra or '-'}")
        rows.append(f"| {c} | " + " | ".join(cells) + " |")

    for n in names:
        copied = manifests[n]["add_symbols"] | manifests[n]["merge_symbols"]
        bad = sorted(set(expected["must_not_copy"]) & copied)
        detail.append(f"- **{n} / must_not_copy**: " + (f"SAI - đã kéo theo {bad}" if bad else "OK, không kéo thừa"))

    out = "\n".join(rows) + "\n\n" + "\n".join(detail) + "\n"
    print(out)
    Path(sys.argv[2]).parent.parent.joinpath("evaluation.md").write_text("# Kết quả chấm điểm\n\n" + out)


if __name__ == "__main__":
    main()
