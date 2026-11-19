#!/usr/bin/env python3
"""merge_ui.py — dựng UI review merge (Phase 4) và áp quyết định của người dùng.

Dùng để:
  - render: đọc merge_view.json (Phase 3 xuất) + file Target gốc, sinh 1 file HTML tự chứa.
            HTML hiện 2 cột: trái = diff (new) (- đỏ / + xanh), phải = FOMULAR.
            Người dùng bật/tắt từng hunk, trả lời NEED_CONFIRM, rồi tải decisions.json
            hoặc tải luôn file đã merge.
  - apply:  đọc decisions.json, áp lên file Target gốc, ghi ra thư mục kết quả
            (giữ encoding và kiểu xuống dòng của file gốc).
  - check:  áp quyết định mặc định (MERGED* / DELETED = lấy, NEED_CONFIRM = chưa lấy)
            rồi so với WORK/target_out/. Khớp hết nghĩa là merge_view.json mô tả
            đúng và đủ mọi thay đổi Phase 3 đã làm.

Cách gọi:
  python3 merge_ui.py render <merge_view.json> [-o out.html] [--target-root DIR] [--force]
  python3 merge_ui.py apply  <merge_view.json> --decisions decisions.json -o OUT_DIR
                             [--target-root DIR] [--allow-pending]
  python3 merge_ui.py check  <merge_view.json> --target-out-root WORK/target_out
                             [--target-root DIR]

Đầu vào: merge_view.json (schema ở phases/phase-3-merge.md, Bước 9), thư mục Target gốc.
Đầu ra:  HTML (render), các file đã merge (apply), báo cáo khớp/không khớp (check).
Exit code: 0 = ổn, 1 = có lỗi dữ liệu / không khớp.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

TOGGLE_RESULTS = {"MERGED", "MERGED_NEW", "MERGED_DEP", "DELETED", "NEED_CONFIRM"}
ALL_RESULTS = TOGGLE_RESULTS | {"SKIP_EXISTS", "SKIP_NOT_IN_TARGET"}
ENCODINGS = ("utf-8", "cp932", "euc_jp", "latin-1")
TEMPLATE = Path(__file__).with_name("merge_ui_template.html")


# ---------------------------------------------------------------- đọc dữ liệu

def read_text_file(path: Path) -> dict:
    """Đọc file, nhận diện encoding + kiểu xuống dòng. Trả về dict lines/encoding/eol/final_newline."""
    raw = path.read_bytes()
    for enc in ENCODINGS:
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    eol = "\r\n" if "\r\n" in text else "\n"
    final_newline = text.endswith(eol)
    body = text[: -len(eol)] if final_newline else text
    lines = body.split(eol) if body else []
    return {"lines": lines, "encoding": enc, "eol": eol, "final_newline": final_newline}


def load_view(view_path: Path, target_root: str | None) -> dict:
    view = json.loads(view_path.read_text(encoding="utf-8"))
    root = Path(target_root) if target_root else view_path.parent / view.get("target_root", "target")
    view["_target_root"] = str(root)
    view["signature"] = hashlib.sha1(view_path.read_bytes()).hexdigest()[:12]
    for f in view["files"]:
        p = root / f["path"]
        if p.exists():
            info = read_text_file(p)
            f["target_missing"] = False
        else:
            info = {"lines": [], "encoding": "utf-8", "eol": "\n", "final_newline": True}
            f["target_missing"] = True
        f["target_lines"] = info["lines"]
        f["encoding"] = info["encoding"]
        f["eol"] = info["eol"]
        f["final_newline"] = info["final_newline"]
        f.setdefault("issues", [])
        for h in f["hunks"]:
            h.setdefault("minus", [])
            h.setdefault("plus", [])
            h.setdefault("target", None)
    return view


# ---------------------------------------------------------------- logic hunk
# Giữ giống hệt phần CORE trong merge_ui_template.html.

def hunk_kind(h: dict) -> str:
    t = h.get("target")
    if not t:
        return "unplaced"
    if "after" in t:
        return "insert"
    if not h["plus"]:
        return "delete"
    return "replace"


def is_toggleable(h: dict) -> bool:
    return bool(h.get("target")) and h["result"] in TOGGLE_RESULTS


def default_decision(h: dict) -> str | None:
    if not is_toggleable(h):
        return None
    return "pending" if h["result"] == "NEED_CONFIRM" else "accept"


def _pos_key(h: dict) -> float:
    t = h["target"]
    return t["after"] + 0.5 if "after" in t else float(t["start"])


def apply_file(f: dict, decisions: dict) -> list[str]:
    lines = list(f["target_lines"])
    edits = [(i, h) for i, h in enumerate(f["hunks"])
             if is_toggleable(h) and decisions.get(h["id"]) == "accept"]
    edits.sort(key=lambda x: (_pos_key(x[1]), x[0]), reverse=True)
    for _, h in edits:
        t = h["target"]
        if "after" in t:
            lines[t["after"]:t["after"]] = h["plus"]
        else:
            lines[t["start"] - 1:t["end"]] = h["plus"]
    return lines


def default_decisions(f: dict) -> dict:
    return {h["id"]: default_decision(h) for h in f["hunks"] if is_toggleable(h)}


# ---------------------------------------------------------------- kiểm tra

def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def validate(view: dict) -> tuple[list[str], list[str]]:
    """Trả về (errors, warnings)."""
    errors: list[str] = []
    warns: list[str] = []
    paths = set()
    for f in view["files"]:
        path = f["path"]
        if path in paths:
            errors.append(f"{path}: file bị lặp")
        paths.add(path)
        n = len(f["target_lines"])
        ids = set()
        ranges = []   # (start, end, id)
        inserts = []  # (after, id)
        for h in f["hunks"]:
            hid = h.get("id")
            where = f"{path} [{hid}]"
            if not hid:
                errors.append(f"{path}: hunk thiếu id")
                continue
            if hid in ids:
                errors.append(f"{where}: id bị lặp")
            ids.add(hid)
            if h.get("result") not in ALL_RESULTS:
                errors.append(f"{where}: result không hợp lệ: {h.get('result')}")
            t = h.get("target")
            if not t:
                if h.get("result") not in ("NEED_CONFIRM", "SKIP_NOT_IN_TARGET"):
                    errors.append(f"{where}: không có target nhưng result là {h.get('result')}")
                continue
            if "after" in t:
                if not (0 <= t["after"] <= n):
                    errors.append(f"{where}: after={t['after']} ngoài file (0..{n})")
                if not h["plus"]:
                    errors.append(f"{where}: hunk chèn nhưng không có dòng +")
                inserts.append((t["after"], hid))
                continue
            s, e = t.get("start"), t.get("end")
            if not (isinstance(s, int) and isinstance(e, int) and 1 <= s <= e <= n):
                errors.append(f"{where}: khoảng {s}-{e} không hợp lệ (file có {n} dòng)")
                continue
            ranges.append((s, e, hid))
            block = f["target_lines"][s - 1:e]
            if h["result"] == "SKIP_EXISTS":
                if [_norm(x) for x in block] != [_norm(x) for x in h["plus"]]:
                    warns.append(f"{where}: SKIP_EXISTS nhưng dòng {s}-{e} ở Target khác phía +")
            elif h.get("match") == "EXACT" and h["minus"]:
                if [_norm(x) for x in block] != [_norm(x) for x in h["minus"]]:
                    warns.append(f"{where}: match EXACT nhưng dòng {s}-{e} ở Target khác các dòng -")
        ranges.sort()
        for (s1, e1, a), (s2, e2, b) in zip(ranges, ranges[1:]):
            if s2 <= e1:
                errors.append(f"{path}: hunk {a} ({s1}-{e1}) chồng lên {b} ({s2}-{e2})")
        for after, hid in inserts:
            for s, e, rid in ranges:
                if s <= after < e:
                    errors.append(f"{path}: hunk chèn {hid} (sau dòng {after}) nằm giữa khoảng của {rid} ({s}-{e})")
    return errors, warns


def write_file(f: dict, lines: list[str], out: Path) -> None:
    text = f["eol"].join(lines) + (f["eol"] if f["final_newline"] and lines else "")
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        out.write_bytes(text.encode(f["encoding"]))
    except UnicodeEncodeError as exc:
        raise SystemExit(f"{f['path']}: không ghi được bằng encoding {f['encoding']}: {exc}")


# ---------------------------------------------------------------- lệnh

def cmd_render(args) -> int:
    view_path = Path(args.view)
    view = load_view(view_path, args.target_root)
    errors, warns = validate(view)
    for w in warns:
        print("CẢNH BÁO:", w)
    for e in errors:
        print("LỖI:", e)
    if errors and not args.force:
        print("Dừng vì dữ liệu lỗi (dùng --force để vẫn render).")
        return 1
    payload = {k: v for k, v in view.items() if not k.startswith("_")}
    payload["validation"] = {"errors": errors, "warnings": warns}
    data = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    html = TEMPLATE.read_text(encoding="utf-8").replace("/*__VIEW_DATA__*/null", data)
    out = Path(args.output) if args.output else view_path.with_suffix(".html")
    out.write_text(html, encoding="utf-8")
    print(f"Đã ghi {out}")
    return 0


def cmd_apply(args) -> int:
    view = load_view(Path(args.view), args.target_root)
    dec = json.loads(Path(args.decisions).read_text(encoding="utf-8"))
    if dec.get("signature") and dec["signature"] != view["signature"]:
        print("CẢNH BÁO: decisions.json được tạo từ một bản merge_view.json khác.")
    out_root = Path(args.output)
    status = 0
    for f in view["files"]:
        fdec = default_decisions(f)
        fdec.update(dec.get("files", {}).get(f["path"], {}).get("decisions", {}))
        pending = [hid for hid, d in fdec.items() if d == "pending"]
        if pending and not args.allow_pending:
            print(f"{f['path']}: còn hunk chưa quyết định: {', '.join(pending)}")
            status = 1
            continue
        lines = apply_file(f, fdec)
        write_file(f, lines, out_root / f["path"])
        acc = sum(1 for d in fdec.values() if d == "accept")
        print(f"{f['path']}: áp {acc} hunk, bỏ {len(fdec) - acc} → {out_root / f['path']}")
    return status


def cmd_check(args) -> int:
    view = load_view(Path(args.view), args.target_root)
    errors, warns = validate(view)
    for w in warns:
        print("CẢNH BÁO:", w)
    for e in errors:
        print("LỖI:", e)
    ok = not errors
    out_root = Path(args.target_out_root)
    for f in view["files"]:
        dec = {k: ("reject" if v == "pending" else v) for k, v in default_decisions(f).items()}
        expected = apply_file(f, dec)
        p = out_root / f["path"]
        if not p.exists():
            print(f"KHÔNG KHỚP {f['path']}: không có trong {out_root}")
            ok = False
            continue
        actual = read_text_file(p)["lines"]
        if actual == expected:
            print(f"KHỚP      {f['path']}")
            continue
        ok = False
        first = next((i for i, (a, b) in enumerate(zip(actual, expected)) if a != b),
                     min(len(actual), len(expected)))
        print(f"KHÔNG KHỚP {f['path']}: khác từ dòng {first + 1}"
              f" (target_out: {len(actual)} dòng, dựng từ JSON: {len(expected)} dòng)")
        print(f"    target_out : {actual[first] if first < len(actual) else '<hết file>'}")
        print(f"    từ JSON    : {expected[first] if first < len(expected) else '<hết file>'}")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render")
    r.add_argument("view")
    r.add_argument("-o", "--output")
    r.add_argument("--target-root")
    r.add_argument("--force", action="store_true")
    a = sub.add_parser("apply")
    a.add_argument("view")
    a.add_argument("--decisions", required=True)
    a.add_argument("-o", "--output", required=True)
    a.add_argument("--target-root")
    a.add_argument("--allow-pending", action="store_true", help="hunk chưa quyết định coi như giữ FOMULAR")
    c = sub.add_parser("check")
    c.add_argument("view")
    c.add_argument("--target-out-root", required=True)
    c.add_argument("--target-root")
    args = ap.parse_args(argv)
    return {"render": cmd_render, "apply": cmd_apply, "check": cmd_check}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
