"""Bước 6-7 - Apply sang B + build kiểm chứng.

Cách dùng:
  python apply.py --work <out_dir của port_analyze.sh> --a <A_latest> --b <B_latest> \
                  --before <feature_before> --after <feature_after> --out <B_ported> \
                  --b-config config/model_b.h --build "make MODEL=B" [--run ./printer_B]
  KHÔNG bao giờ sửa trực tiếp B_latest: luôn ghi ra thư mục --out (bản sao của B).

- File mới            -> copy nguyên từ A_latest (đã gồm bug-fix drift)
- File dùng chung     -> git merge-file 3 chiều: base=feature_before, ours=B, theirs=feature_after
                         => chỉ hunk của feature đi sang, giữ nguyên phần riêng của B,
                            KHÔNG kéo code của feature khác (vd Eco Report) từ A_latest
- Guard #ifdef        -> thêm #define vào file cấu hình của B
- Xung đột SAFE_REPLACE (B không dùng) -> thay file bằng bản A
- Xung đột NEEDS_REVIEW -> dừng, để người/LLM quyết
- Build B, lỗi build/link được in ra để quay lại bước phân tích
"""
import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True, help="thư mục output của port_analyze.sh")
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--b-config", default="", help="file cấu hình model của B, vd config/model_b.h")
    ap.add_argument("--build", default="", help='lệnh build B, vd "make MODEL=B"')
    ap.add_argument("--run", default="", help="lệnh chạy thử sau khi build (tuỳ chọn)")
    ap.add_argument("--skip-conflict", action="append", default=[],
                    help="symbol xung đột đã được người/LLM xử lý tay -> bỏ qua")
    a = ap.parse_args()

    work = Path(a.work)
    m = json.loads((work / "manifest.json").read_text())
    A, B, FB, FA, OUT = (Path(a.a), Path(a.b), Path(a.before), Path(a.after), Path(a.out))
    if OUT.resolve() == B.resolve():
        raise SystemExit("--out không được trùng B_latest")
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(B, OUT)
    log, todo = [], []

    # 1. file mới
    for f in m["files"]["new"]:
        (OUT / f).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(A / f, OUT / f)
        log.append(f"COPY   {f}")

    # 2. merge 3 chiều
    for f in m["files"]["merge"]:
        r = subprocess.run(["git", "merge-file", "-L", "B", "-L", "base", "-L", "feature",
                            str(OUT / f), str(FB / f), str(FA / f)], capture_output=True, text=True)
        if r.returncode == 0:
            log.append(f"MERGE  {f}")
        else:
            log.append(f"CONFLICT {f} ({r.returncode} chỗ)")
            todo.append(f"Giải quyết conflict marker trong {f}")

    # 3. guard #ifdef -> define trong config B
    cfg = OUT / a.b_config if a.b_config else None
    for g in m["guards"]:
        if cfg is None or not cfg.exists():
            todo.append(f"Define guard {g['macro']} trong file cấu hình của B (chưa truyền --b-config)")
            continue
        src = (A / g["defined_in_a"]).read_text() if g["defined_in_a"] else ""
        line = next((ln for ln in src.splitlines() if re.match(rf"#define\s+{g['macro']}\b", ln)),
                    f"#define {g['macro']} 1")
        cfg.write_text(cfg.read_text() + line + "\n")
        log.append(f"DEFINE {g['macro']} -> {a.b_config}")

    # 4. xung đột
    for c in m["conflicts"]:
        if c["key"] in a.skip_conflict:
            log.append(f"SKIP   xung đột {c['key']} (đã xử lý tay)")
            continue
        if c["suggestion"] == "SAFE_REPLACE":
            # thay file chứa symbol + header đi kèm bằng bản A (B không có chỗ nào dùng)
            graph_a = json.loads((work / "A_latest.json").read_text())
            f = graph_a["nodes"][c["key"]]["file"]
            for ff in {f, f[:-2] + ".h"}:
                if (A / ff).exists():
                    shutil.copy2(A / ff, OUT / ff)
            log.append(f"REPLACE {c['key']} ({f}) - B không có chỗ nào dùng, thay bằng bản A")
        else:
            todo.append(f"Xung đột {c['key']}: B đang dùng ở {c['used_in_b_by']} -> người/LLM quyết")

    # 5. file .c mới phải có trong build
    mk = OUT / "Makefile"
    if mk.exists():
        text = mk.read_text()
        for f in m["files"]["new"]:
            if f.endswith(".c") and f not in text:
                text = text.replace("\nall:", f"SRCS += {f}\n\nall:", 1)
                log.append(f"BUILD  thêm {f} vào Makefile")
        mk.write_text(text)
    else:
        todo.append("Thêm các file .c mới vào build system của B")

    print("\n".join(log))
    if todo:
        print("\nCần người/LLM xử lý:\n- " + "\n- ".join(todo))

    # 6. build + chạy kiểm chứng
    if not a.build:
        print("\n(Không có --build: bỏ qua bước build)")
        return
    r = subprocess.run(a.build, shell=True, cwd=OUT, capture_output=True, text=True)
    if r.returncode != 0:
        print("\nBUILD LỖI (đưa lỗi này quay lại bước phân tích):\n" + r.stderr[-4000:])
        raise SystemExit(2)
    print("\nBUILD OK")
    if a.run:
        run = subprocess.run(a.run, shell=True, cwd=OUT, capture_output=True, text=True)
        print(f"Output khi chạy `{a.run}`:\n{run.stdout[-3000:]}")


if __name__ == "__main__":
    main()
