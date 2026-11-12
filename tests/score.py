#!/usr/bin/env python3
"""Score one port-request run against the golden (manual) port.

Usage: score.py <case_dir> <output_root> <score_json>
  case_dir    : tests/cases/<case>  (input/B_latest, golden/After, golden/expected.json)
  output_root : OUTPUT_ROOT of the run (contains After/, _work/, PORT_REPORT.md)

Levels (docs/PORT_REQUEST_CONTEXT.md section 7):
  1 file set, 2 per-file +/- line counts vs B_latest, 3 exact lines, 4 bytes (encoding + EOL).
"""
import filecmp, json, os, re, subprocess, sys

IGNORE = {".DS_Store"}
BUILD_ARTIFACT = re.compile(r"(^|/)(printer_[A-Za-z0-9]+|.*\.o|.*\.dSYM(/.*)?)$")


def files(root):
    out = set()
    for d, _, fs in os.walk(root):
        if "/.git" in d:
            continue
        for f in fs:
            rel = os.path.relpath(os.path.join(d, f), root)
            if f not in IGNORE and not BUILD_ARTIFACT.search(rel):
                out.add(rel)
    return out


def changed(base, tree):
    """{path: (added, deleted)} of tree vs base, like git diff --numstat."""
    fb, ft = files(base), files(tree)
    res = {}
    for p in sorted(fb | ft):
        a, b = os.path.join(base, p), os.path.join(tree, p)
        if p in fb and p in ft and filecmp.cmp(a, b, shallow=False):
            continue
        r = subprocess.run(["git", "diff", "--no-index", "--numstat",
                            a if p in fb else "/dev/null", b if p in ft else "/dev/null"],
                           capture_output=True, text=True)
        line = r.stdout.strip().splitlines()
        add, dele = (line[0].split("\t")[:2] if line else ("0", "0"))
        res[p] = (add, dele)
    return res


def line_diff(g, o):
    r = subprocess.run(["diff", "-U0", g, o], capture_output=True, text=True, errors="replace")
    issues = []
    for h in re.finditer(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@\n((?:[-+].*\n?)*)", r.stdout, re.M):
        body = h.group(5).splitlines()
        issues.append({"golden_line": int(h.group(1)), "output_line": int(h.group(3)),
                       "missing": [l[1:] for l in body if l.startswith("-")],
                       "extra": [l[1:] for l in body if l.startswith("+")]})
    return issues


def eol_enc(p):
    data = open(p, "rb").read()
    enc = subprocess.run(["file", "-b", "--mime-encoding", p], capture_output=True, text=True).stdout.strip()
    return {"crlf": b"\r\n" in data, "encoding": enc}


def main(case, out_root, score_path):
    base = os.path.join(case, "input", "B_latest")
    gold = os.path.join(case, "golden", "After")
    outp = os.path.join(out_root, "After")
    s = {"case": os.path.basename(case.rstrip("/")), "output_root": out_root, "levels": {}}
    if not os.path.isdir(outp):
        s["levels"] = {k: "FAIL" for k in ("1_files", "2_line_counts", "3_lines", "4_bytes")}
        s["error"] = "OUTPUT/After not found"
        s["pass"] = False
        json.dump(s, open(score_path, "w"), indent=2, ensure_ascii=False)
        print(json.dumps(s, indent=2, ensure_ascii=False)); return

    cg, co = changed(base, gold), changed(base, outp)
    missing, extra = sorted(set(cg) - set(co)), sorted(set(co) - set(cg))
    s["levels"]["1_files"] = "PASS" if not missing and not extra else "FAIL"
    s["files"] = {"golden_changed": len(cg), "output_changed": len(co),
                  "missing_files": missing, "extra_files": extra}

    count_diff = {p: {"golden": "+%s/-%s" % cg[p], "output": "+%s/-%s" % co[p]}
                  for p in sorted(set(cg) & set(co)) if cg[p] != co[p]}
    s["levels"]["2_line_counts"] = "PASS" if not count_diff and s["levels"]["1_files"] == "PASS" else "FAIL"
    s["line_count_mismatch"] = count_diff

    lines = {}
    for p in sorted(set(cg) | set(co)):
        g, o = os.path.join(gold, p), os.path.join(outp, p)
        if os.path.exists(g) and os.path.exists(o):
            d = line_diff(g, o)
            if d:
                lines[p] = d
    s["levels"]["3_lines"] = "PASS" if not lines and s["levels"]["1_files"] == "PASS" else "FAIL"
    s["line_mismatch"] = lines

    byte_issues = {}
    for p in sorted(set(cg) & set(co)):
        g, o = os.path.join(gold, p), os.path.join(outp, p)
        if not filecmp.cmp(g, o, shallow=False):
            eg, eo = eol_enc(g), eol_enc(o)
            byte_issues[p] = {"golden": eg, "output": eo, "content_differs": True}
    s["levels"]["4_bytes"] = "PASS" if not byte_issues and s["levels"]["3_lines"] == "PASS" else "FAIL"
    s["byte_mismatch"] = byte_issues

    # Checkpoint signals: look for expected symbols in the report / _work files.
    exp_path = os.path.join(case, "golden", "expected.json")
    if os.path.exists(exp_path):
        exp = json.load(open(exp_path))
        corpus = ""
        for d, _, fs in os.walk(out_root):
            if d.startswith(os.path.join(out_root, "After")) or d.startswith(os.path.join(out_root, "Before")):
                continue
            for f in fs:
                if f.endswith((".md", ".txt", ".diff")):
                    corpus += open(os.path.join(d, f), errors="replace").read()
        chk = {}
        for k, names in exp.items():
            names = [n.split("@")[0] for n in names]
            chk[k] = {"found": [n for n in names if n in corpus], "not_mentioned": [n for n in names if n not in corpus]}
        s["expected_mentions"] = chk

    # Checkpoint B anchoring (diagnostic, not part of PASS): request name -> latest name on one line of the work files.
    anc_path = os.path.join(case, "golden", "expected_anchor.json")
    if os.path.exists(anc_path):
        anc = json.load(open(anc_path))
        work = os.path.join(out_root, "_work")
        wl = []
        for f in ("alias_map.md", "B_anchor.md"):
            p = os.path.join(work, f)
            if os.path.exists(p):
                wl += open(p, errors="replace").read().splitlines()
        rank = {"Low": 0, "Medium": 1, "High": 2}

        def find(old, new):
            hits = [l for l in wl if old in l and new in l]
            if not hits:
                return {"found": False}
            conf = [c for c in rank if re.search(r"\b%s\b" % c, " ".join(hits))]
            return {"found": True, "confidence": max(conf, key=rank.get) if conf else None, "line": hits[0][:200]}

        ac = {"files": {}, "renames": {}, "blocked_wrongly": []}
        for f in anc.get("files", []):
            ac["files"][f["request"]] = find(f["request"], f["latest"])
        for r in anc.get("renames", []):
            res = find(r["request"], r["latest"])
            if res["found"] and res["confidence"]:
                res["confidence_ok"] = rank[res["confidence"]] >= rank[r["min_confidence"]]
            if r.get("split_parts"):
                res["split_parts_found"] = [p for p in r["split_parts"] if any(p in l for l in wl)]
            ac["renames"][r["request"]] = res
        for r in anc.get("renames", []):
            for bad in anc.get("must_not_be_blocked_as", []):
                if any(r["request"] in l and re.search(r"\b%s\b" % bad, l) for l in wl):
                    ac["blocked_wrongly"].append("%s as %s" % (r["request"], bad))
        n_ok = sum(v.get("found", False) for v in list(ac["files"].values()) + list(ac["renames"].values()))
        ac["summary"] = "%d/%d anchors found, %d wrongly blocked" % (
            n_ok, len(ac["files"]) + len(ac["renames"]), len(ac["blocked_wrongly"]))
        s["anchor_checks"] = ac

    rep = os.path.join(out_root, "PORT_REPORT.md")
    if os.path.exists(rep):
        txt = open(rep).read()
        s["workflow_status"] = re.findall(r"^\|\s*([A-F])\s*\|[^|]*\|\s*([^|]+?)\s*\|", txt, re.M)
    s["pass"] = all(v == "PASS" for v in s["levels"].values())
    json.dump(s, open(score_path, "w"), indent=2, ensure_ascii=False)
    print(json.dumps(s, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main(*sys.argv[1:4])
