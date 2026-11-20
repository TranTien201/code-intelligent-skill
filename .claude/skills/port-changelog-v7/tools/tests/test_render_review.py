#!/usr/bin/env python3
"""Test cho tools/render_review.py (fixture tests/fixtures/synthetic).

Chạy (từ thư mục tools/):  python3 -m unittest discover -s tests -p 'test_render_review.py' -v
Test so sánh Python ↔ JS (review_core.js) cần `node`; không có node thì bỏ qua.
"""
import copy
import json
import random
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))
import render_review as rr  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures" / "synthetic"
PLAN = FIX / "merge-plan.json"
TARGET = FIX / "target"
NODE = shutil.which("node")


def load_plan():
    return json.loads(PLAN.read_text(encoding="utf-8"))


def load_files():
    plan, files, _ = rr.load_inputs(PLAN, TARGET)
    return files


def run_cli(*args):
    r = subprocess.run([sys.executable, str(TOOLS / "render_review.py"), *map(str, args)],
                       capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


class TestReadWrite(unittest.TestCase):
    def test_read_meta(self):
        _, files, meta = rr.load_inputs(PLAN, TARGET)
        self.assertEqual(meta["src/eco.c"], {"encoding": "utf-8", "eol": "lf", "bom": False, "mixed_eol": False})
        self.assertEqual(meta["src/eco.h"]["eol"], "crlf")
        self.assertNotIn("\r", files["src/eco.h"])
        self.assertIn("エコ設定", files["src/eco.h"])
        self.assertFalse(files["src/eco.c"].endswith("\n"))

    def test_bom_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "a.c"
            p.write_bytes(b"\xef\xbb\xbfint a;\r\nint b;\r\n")
            text, meta = rr.read_target(p, "utf-8")
            self.assertEqual(text, "int a;\nint b;\n")
            self.assertTrue(meta["bom"])
            self.assertEqual(rr.encode_output(text, meta, "a.c"), p.read_bytes())


class TestCore(unittest.TestCase):
    def test_validate_ok(self):
        self.assertEqual(rr.validate(load_plan(), load_files()), [])

    def test_status_default(self):
        st = rr.compute_status(load_plan(), {})
        self.assertEqual({k: v["status"] for k, v in st.items()},
                         {"K1": "APPLIED", "K2": "NEED_CONFIRM", "K3": "BLOCKED", "K4": "BLOCKED", "K5": "FOLLOW", "K6": "FOLLOW"})
        self.assertEqual(st["K2"]["by"], ["Q1"])
        self.assertEqual(st["K6"]["by"], ["K5"])

    def test_build_expected(self):
        files = load_files()
        for scn, dec in (("default", {}), ("q1a", {"answers": {"Q1": "A"}})):
            out = rr.build(load_plan(), files, dec)
            self.assertEqual(out["src/eco.c"], (FIX / "expected" / scn / "src/eco.c").read_text(encoding="utf-8"))

    def test_closure_dependents(self):
        p = load_plan()
        self.assertEqual(rr.closure(p, "K4"), ["K3", "K5", "K2", "K6"])
        self.assertEqual(rr.dependents(p, "K6"), ["K5", "K4"])


class TestCli(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_render_ok(self):
        out = self.tmp / "review.html"
        code, log = run_cli("--plan", PLAN, "--target-root", TARGET, "-o", out)
        self.assertEqual(code, 0, log)
        self.assertIn("2 file, 6 chunk, 1 câu hỏi", log)
        html = out.read_text(encoding="utf-8")
        self.assertNotIn("/*__PAYLOAD__*/", html)
        self.assertNotIn("/*__REVIEW_CORE__*/", html)
        self.assertIn("function computeStatus", html)
        # không có thẻ </script> lọt vào dữ liệu
        self.assertEqual(html.count("</script>"), 3)

    def test_apply_matches_expected_bytes(self):
        for scn, dec in (("default", None), ("q1a", FIX / "decisions-q1a.json")):
            out = self.tmp / scn
            if dec is None:
                dec = self.tmp / "d.json"
                dec.write_text('{"rt": "RT9001", "answers": {}, "choices": {}}', encoding="utf-8")
                code, log = run_cli("--plan", PLAN, "--target-root", TARGET, "--decisions", dec, "--apply", "-o", out)
                self.assertEqual(code, 3, log)  # Q1 chưa trả lời
                self.assertFalse(out.exists())
                code, log = run_cli("--plan", PLAN, "--target-root", TARGET, "--decisions", dec, "--apply",
                                    "--allow-pending", "-o", out)
            else:
                code, log = run_cli("--plan", PLAN, "--target-root", TARGET, "--decisions", dec, "--apply", "-o", out)
            self.assertEqual(code, 0, log)
            for rel in ("src/eco.c", "src/eco.h"):
                self.assertEqual((out / rel).read_bytes(), (FIX / "expected" / scn / rel).read_bytes(), f"{scn} {rel}")

    def test_input_errors_exit_2(self):
        bad = self.tmp / "bad.json"
        bad.write_text("{not json", encoding="utf-8")
        code, log = run_cli("--plan", bad, "--target-root", TARGET, "-o", self.tmp / "x.html")
        self.assertEqual(code, 2)
        self.assertIn("JSON", log)

        code, log = run_cli("--plan", PLAN, "--target-root", self.tmp, "-o", self.tmp / "x.html")
        self.assertEqual(code, 2)
        self.assertIn("Thiếu file Target", log)

        p = load_plan()
        p["files"]["src/eco.h"]["encoding"] = "utf-8"  # file thật là cp932
        pp = self.tmp / "p.json"
        pp.write_text(json.dumps(p, ensure_ascii=False), encoding="utf-8")
        code, log = run_cli("--plan", pp, "--target-root", TARGET, "-o", self.tmp / "x.html")
        self.assertEqual(code, 2)
        self.assertIn("không decode được", log)

        p["files"]["src/eco.h"]["encoding"] = "no-such-enc"
        pp.write_text(json.dumps(p, ensure_ascii=False), encoding="utf-8")
        code, log = run_cli("--plan", pp, "--target-root", TARGET, "-o", self.tmp / "x.html")
        self.assertEqual(code, 2)

        code, log = run_cli("--plan", PLAN, "--target-root", TARGET, "--apply", "-o", self.tmp / "o")
        self.assertEqual(code, 2)
        self.assertIn("--decisions", log)

    def test_validation_errors_exit_1(self):
        p = load_plan()
        p["chunks"][2]["target"]["text"] = "    total = page * 3;\n"
        pp = self.tmp / "p.json"
        pp.write_text(json.dumps(p, ensure_ascii=False), encoding="utf-8")
        out = self.tmp / "x.html"
        code, log = run_cli("--plan", pp, "--target-root", TARGET, "-o", out)
        self.assertEqual(code, 1)
        self.assertTrue(out.exists())
        self.assertIn("K3: target.text không khớp", log)
        code, log = run_cli("--plan", pp, "--target-root", TARGET, "--decisions", FIX / "decisions-q1a.json",
                            "--apply", "-o", self.tmp / "o")
        self.assertEqual(code, 1)
        self.assertFalse((self.tmp / "o").exists())


# ---------------------------------------------------------------------- Python ↔ JS

JS_RUNNER = r"""
const core = require(process.argv[1]);
let buf = '';
process.stdin.on('data', (d) => (buf += d));
process.stdin.on('end', () => {
  const cases = JSON.parse(buf);
  const out = cases.map((c) => ({
    validate: core.validate(c.plan, c.files),
    status: core.computeStatus(c.plan, c.decisions),
    build: core.build(c.plan, c.files, c.decisions),
    closure: Object.fromEntries(c.plan.chunks.map((k) => [k.id, core.closure(c.plan, k.id)])),
    dependents: Object.fromEntries(c.plan.chunks.map((k) => [k.id, core.dependents(c.plan, k.id)])),
  }));
  process.stdout.write(JSON.stringify(out));
});
"""


def py_result(c):
    return {
        "validate": rr.validate(c["plan"], c["files"]),
        "status": rr.compute_status(c["plan"], c["decisions"]),
        "build": rr.build(c["plan"], c["files"], c["decisions"]),
        "closure": {k["id"]: rr.closure(c["plan"], k["id"]) for k in c["plan"]["chunks"]},
        "dependents": {k["id"]: rr.dependents(c["plan"], k["id"]) for k in c["plan"]["chunks"]},
    }


def make_cases(n_graphs=150, n_dec=6, seed=7):
    rnd = random.Random(seed)
    base = load_plan()
    files = load_files()
    ids = [c["id"] for c in base["chunks"]]
    cases = []
    for g in range(n_graphs):
        plan = copy.deepcopy(base)
        if g > 0:  # g == 0: đồ thị gốc
            for c in plan["chunks"]:
                k = rnd.choice([0, 0, 1, 1, 2, 3])
                c["requires"] = [{"chunk": x, "why": "r"} for x in rnd.sample(ids, k)]
                if not c["requires"]:
                    del c["requires"]
            if rnd.random() < 0.3:
                plan["questions"][0]["chunks"] = rnd.sample(ids, rnd.choice([1, 2, 3]))
                plan["questions"][0]["options"][0]["apply"] = plan["questions"][0]["chunks"][:1]
        for _ in range(n_dec):
            dec = {"answers": {}, "choices": {}}
            r = rnd.random()
            if r < 0.4:
                dec["answers"]["Q1"] = rnd.choice(["A", "B"])
            for i in ids:
                if rnd.random() < 0.25:
                    dec["choices"][i] = rnd.choice(["target", "apply", "rt"])
            cases.append({"plan": plan, "files": files, "decisions": dec})
    # vài plan lỗi cho validate
    bads = []
    for mut in range(6):
        plan = copy.deepcopy(base)
        if mut == 0:
            plan["chunks"][0]["target"]["end"] = 99
        elif mut == 1:
            plan["chunks"][1]["target"] = {"start": 4, "end": 12, "text": "x\n"}
        elif mut == 2:
            plan["chunks"][2]["requires"] = [{"chunk": "K99", "why": "x"}]
        elif mut == 3:
            plan["questions"][0]["options"][0]["apply"] = ["K3"]
        elif mut == 4:
            plan["chunks"][0]["rt"] = plan["chunks"][0]["apply"]
            plan["chunks"][3]["file"] = "nope.c"
        elif mut == 5:
            plan["chunks"][2]["target"]["text"] = "    total = page * 2;"
        bads.append({"plan": plan, "files": files, "decisions": {}})
    bads.append({"plan": base, "files": {"src/eco.c": files["src/eco.c"]}, "decisions": {}})
    return cases + bads


@unittest.skipUnless(NODE, "không có node")
class TestParityWithJs(unittest.TestCase):
    def test_python_equals_js(self):
        cases = make_cases()
        r = subprocess.run([NODE, "-e", JS_RUNNER, str(TOOLS / "review_core.js")], input=json.dumps(cases),
                           capture_output=True, text=True, check=True)
        js = json.loads(r.stdout)
        self.assertEqual(len(js), len(cases))
        n_status = {"BLOCKED": 0, "FOLLOW": 0, "errors": 0}
        for i, (c, j) in enumerate(zip(cases, js)):
            p = py_result(c)
            self.assertEqual(p, j, f"case {i}: decisions={c['decisions']}")
            for v in p["status"].values():
                if v["status"] in n_status:
                    n_status[v["status"]] += 1
            n_status["errors"] += bool(p["validate"])
        # bảo đảm bộ ca có phủ BLOCKED / FOLLOW / lỗi validate
        self.assertTrue(all(n_status.values()), n_status)


if __name__ == "__main__":
    unittest.main()
