#!/usr/bin/env python3
"""Test cho merge_ui.py + merge_ui_template.html.

Chạy: python3 -m unittest test_merge_ui.py   (trong thư mục tools/)
Test so sánh JS cần `node`; không có node thì bỏ qua test đó.
"""
import copy
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import merge_ui as mu

HERE = Path(__file__).parent
FIX = HERE / "fixtures" / "phase4_mock"
VIEW = FIX / "WORK" / "phase3" / "merge_view.json"


def load():
    return mu.load_view(VIEW, None)


def decide(view, mode):
    """mode: default | accept | reject → {path: {id: decision}}"""
    out = {}
    for f in view["files"]:
        d = mu.default_decisions(f)
        if mode == "accept":
            d = {k: "accept" for k in d}
        elif mode == "reject":
            d = {k: "reject" for k in d}
        else:
            d = {k: ("reject" if v == "pending" else v) for k, v in d.items()}
        out[f["path"]] = d
    return out


class TestFixture(unittest.TestCase):
    def test_fixture_is_valid(self):
        errors, warns = mu.validate(load())
        self.assertEqual(errors, [])
        self.assertEqual(warns, [])

    def test_covers_all_cases(self):
        hunks = [h for f in load()["files"] for h in f["hunks"]]
        results = {h["result"] for h in hunks}
        self.assertTrue({"MERGED", "MERGED_NEW", "MERGED_DEP", "DELETED", "NEED_CONFIRM", "SKIP_EXISTS"} <= results)
        self.assertEqual({mu.hunk_kind(h) for h in hunks}, {"insert", "replace", "delete", "unplaced"})
        self.assertEqual({h.get("match") for h in hunks} - {None}, {"EXACT", "NEAR"})

    def test_check_against_target_out(self):
        r = subprocess.run(["python3", str(HERE / "merge_ui.py"), "check", str(VIEW),
                            "--target-out-root", str(FIX / "WORK" / "target_out")], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_phase4_mock_run(self):
        """Chạy run_mock.sh: check → render → apply decisions.mock.json → so với expected/."""
        with tempfile.TemporaryDirectory() as d:
            r = subprocess.run(["bash", str(FIX / "run_mock.sh"), d], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("OK: WORK/target_out giống expected/target_out_final", r.stdout)
            self.assertTrue((Path(d) / "WORK" / "phase4" / "merge_view.html").exists())

    def test_mock_decisions_cover_every_pending(self):
        """decisions.mock.json phải quyết định mọi hunk NEED_CONFIRM có vị trí."""
        dec = json.loads((FIX / "decisions.mock.json").read_text(encoding="utf-8"))
        for f in load()["files"]:
            fd = dec["files"][f["path"]]["decisions"]
            for hid, d in mu.default_decisions(f).items():
                if d == "pending":
                    self.assertIn(fd.get(hid), ("accept", "reject"), f"{f['path']} {hid}")

    def test_accept_all(self):
        view = load()
        dec = decide(view, "accept")
        files = {f["path"]: mu.apply_file(f, dec[f["path"]]) for f in view["files"]}
        art = "\n".join(files["src/artlib/artrcp.c"])
        self.assertIn("attr.Linked == ON", art)
        self.assertNotIn("(variable != NULL)) {", art)  # guard FOMULAR bị thay
        rif = files["src/rcp/rifback2.c"]
        i = rif.index("    if (rec->linkFlag == ON) {")
        self.assertTrue(rif[i + 4].startswith("    retCode = RcpIfSetAllVari("))
        self.assertIn("    retCode = RcpIfGetAllVari(ON, rec->className, rec->recipeName,", rif)  # B8 không có vị trí → không đổi
        h = files["inc/rcpif.h"]
        self.assertIn("#define RCP_NAME_LEN            32", h)
        self.assertIn("extern unsl RcpIfGetAllVariForce(unsl force, text *className, text *recipeName,", h)

    def test_reject_all_is_identity(self):
        view = load()
        dec = decide(view, "reject")
        for f in view["files"]:
            self.assertEqual(mu.apply_file(f, dec[f["path"]]), f["target_lines"])


class TestValidate(unittest.TestCase):
    def test_overlap_and_exact_mismatch(self):
        view = load()
        f = view["files"][1]
        bad = copy.deepcopy(f["hunks"][2])  # B3 delete 19-23
        bad["id"] = "X1"
        bad["target"] = {"start": 22, "end": 24}
        f["hunks"].append(bad)
        ins = {"id": "X2", "unit": "u", "minus": [], "plus": ["x"], "target": {"after": 20}, "result": "MERGED"}
        f["hunks"].append(ins)
        errors, warns = mu.validate(view)
        self.assertTrue(any("chồng lên" in e for e in errors), errors)
        self.assertTrue(any("X2" in e and "nằm giữa" in e for e in errors), errors)
        self.assertTrue(any("X1" in w and "EXACT" in w for w in warns), warns)

    def test_need_confirm_never_in_default_output(self):
        """NEED_CONFIRM: mặc định không áp → vị trí giữ nguyên Target gốc."""
        view = load()
        for f in view["files"]:
            out = mu.apply_file(f, {k: ("reject" if v == "pending" else v) for k, v in mu.default_decisions(f).items()})
            out_lines = set(out)
            merged_plus = {p for h in f["hunks"] if h["result"] != "NEED_CONFIRM" for p in h["plus"]}
            for h in f["hunks"]:
                if h["result"] != "NEED_CONFIRM":
                    continue
                own = [p for p in h["plus"] if p.strip() and p not in f["target_lines"] and p not in merged_plus]
                for p in own:
                    self.assertNotIn(p, out_lines, f"{f['path']} {h['id']}")

    def test_out_of_range(self):
        view = load()
        view["files"][2]["hunks"][0]["target"] = {"after": 999}
        errors, _ = mu.validate(view)
        self.assertTrue(any("ngoài file" in e for e in errors))


class TestEncoding(unittest.TestCase):
    def test_cp932_crlf_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "t").mkdir()
            src = "/* 日本語コメント */\r\nint a;\r\nint b;\r\n"
            (d / "t" / "x.c").write_bytes(src.encode("cp932"))
            view = {"rt": "RTX", "target_root": "t", "files": [{"path": "x.c", "hunks": [
                {"id": "1", "unit": "a", "minus": ["int a;"], "plus": ["int a2; /* 変更 */"],
                 "target": {"start": 2, "end": 2}, "result": "MERGED", "match": "EXACT"}]}]}
            (d / "v.json").write_text(json.dumps(view, ensure_ascii=False), encoding="utf-8")
            (d / "dec.json").write_text("{}", encoding="utf-8")
            r = subprocess.run(["python3", str(HERE / "merge_ui.py"), "apply", str(d / "v.json"),
                                "--decisions", str(d / "dec.json"), "-o", str(d / "out")],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            got = (d / "out" / "x.c").read_bytes()
            self.assertEqual(got, "/* 日本語コメント */\r\nint a2; /* 変更 */\r\nint b;\r\n".encode("cp932"))

    def test_apply_refuses_pending(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "dec.json").write_text("{}", encoding="utf-8")
            r = subprocess.run(["python3", str(HERE / "merge_ui.py"), "apply", str(VIEW),
                                "--decisions", str(Path(d) / "dec.json"), "-o", str(Path(d) / "out")],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 1)
            self.assertIn("chưa quyết định", r.stdout)


class TestRender(unittest.TestCase):
    def test_render_embeds_data(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "v.html"
            r = subprocess.run(["python3", str(HERE / "merge_ui.py"), "render", str(VIEW), "-o", str(out)],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            html = out.read_text(encoding="utf-8")
            m = re.search(r'<script type="application/json" id="view-data">(.*?)</script>', html, re.S)
            data = json.loads(m.group(1))
            self.assertEqual(data["rt"], "RT9001")
            self.assertEqual(len(data["files"]), 3)
            self.assertIn("target_lines", data["files"][0])


@unittest.skipUnless(shutil.which("node"), "cần node")
class TestJsParity(unittest.TestCase):
    """applyFile / layout trong HTML phải cho kết quả giống merge_ui.py."""

    def test_parity(self):
        html = mu.TEMPLATE.read_text(encoding="utf-8")
        core = html.split("// CORE-BEGIN", 1)[1].split("\n", 1)[1].split("// CORE-END", 1)[0]
        view = load()
        cases = {m: decide(view, m) for m in ("default", "accept", "reject")}
        script = core + """
const input = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const out = {};
for (const mode in input.cases) {
  out[mode] = {};
  for (const f of input.files) out[mode][f.path] = applyFile(f, input.cases[mode][f.path]).map(l => l.text);
}
out.layout = {};
for (const f of input.files) {
  const items = layout(f);
  out.layout[f.path] = { lines: items.filter(x => x.type === 'line').map(x => x.tline),
                         hunks: items.filter(x => x.type === 'hunk').map(x => x.h.id) };
}
process.stdout.write(JSON.stringify(out));
"""
        payload = json.dumps({"files": view["files"], "cases": cases})
        r = subprocess.run(["node", "-e", script], input=payload, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        js = json.loads(r.stdout)
        for mode, dec in cases.items():
            for f in view["files"]:
                self.assertEqual(js[mode][f["path"]], mu.apply_file(f, dec[f["path"]]), f"{mode} {f['path']}")
        for f in view["files"]:
            lay = js["layout"][f["path"]]
            covered = set(lay["lines"])
            for h in f["hunks"]:
                t = h["target"]
                if t and "start" in t:
                    covered |= set(range(t["start"], t["end"] + 1))
            self.assertEqual(covered, set(range(1, len(f["target_lines"]) + 1)), f["path"])
            placed = [h["id"] for h in f["hunks"] if h["target"]]
            self.assertEqual(sorted(lay["hunks"]), sorted(placed))


if __name__ == "__main__":
    unittest.main()
