#!/usr/bin/env python3
"""render_review.py — Phase 4 (port-changelog-v7): dựng trang duyệt merge-plan.json và ghi file output.

Hai chế độ:
  render (mặc định): đọc merge-plan.json + file Target, sinh MỘT file HTML tự chứa (mở offline bằng double-click).
      python3 render_review.py --plan merge-plan.json --target-root target -o review.html [--decisions decisions.json]
  apply: áp decisions.json lên Target, ghi file output với encoding + kiểu xuống dòng của file gốc.
      python3 render_review.py --plan merge-plan.json --target-root target --decisions decisions.json --apply -o OUT_DIR
                               [--allow-pending]

Logic validate / computeStatus / build ở đây là bản Python của tools/review_core.js
(hợp đồng: ../schema/README.md mục 4 và 6). Hai bản phải giống hệt nhau; tests/test_render_review.py so sánh.

Exit code:
  0 = ổn
  1 = plan không qua kiểm tra mục 6 (render vẫn ghi HTML, trang hiện banner đỏ; apply không ghi gì)
  2 = lỗi đầu vào: JSON không đọc được, thiếu file Target, không decode/encode được, thiếu node...
  3 = apply nhưng còn câu hỏi chưa trả lời (NEED_CONFIRM) mà không có --allow-pending
"""
from __future__ import annotations

import argparse
import codecs
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "review_template.html"
CORE_JS = HERE / "review_core.js"

CHOICE_VALUES = ("target", "apply", "rt")
UTF8_LIKE = {"utf-8", "utf8", "ascii", "us-ascii", "utf_8"}


class InputError(Exception):
    """Lỗi đầu vào → exit 2."""


# ====================================================================== bản Python của review_core.js

def split_lines(text: str) -> list[str]:
    if not text:
        return []
    parts = text.split("\n")
    if parts[-1] == "":
        parts.pop()
    return parts


def _is_int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _chunks(plan) -> list:
    c = plan.get("chunks") if isinstance(plan, dict) else None
    return c if isinstance(c, list) else []


def _questions(plan) -> list:
    q = plan.get("questions") if isinstance(plan, dict) else None
    return q if isinstance(q, list) else []


def _files(plan) -> dict:
    f = plan.get("files") if isinstance(plan, dict) else None
    return f if isinstance(f, dict) else {}


def chunk_index(plan) -> dict:
    m: dict = {}
    for c in _chunks(plan):
        if isinstance(c.get("id"), str) and c["id"] not in m:
            m[c["id"]] = c
    return m


def question_map(plan) -> dict:
    m: dict = {}
    for q in _questions(plan):
        for k in q.get("chunks") or []:
            m.setdefault(k, q)
    return m


def requires_ids(chunk) -> list[str]:
    out: list[str] = []
    for r in chunk.get("requires") or []:
        k = r.get("chunk") if isinstance(r, dict) else None
        if isinstance(k, str) and k not in out:
            out.append(k)
    return out


def reverse_index(plan) -> dict:
    idx = chunk_index(plan)
    rev = {k: [] for k in idx}
    for k, c in idx.items():
        for r in requires_ids(c):
            if r in rev and k not in rev[r]:
                rev[r].append(k)
    return rev


def _js_num(v) -> str:
    """In số giống JS khi nối chuỗi ('undefined' khi thiếu)."""
    if v is None:
        return "undefined"
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)


def validate(plan, files: dict) -> list[str]:
    errs: list[str] = []
    files = files or {}
    pfiles = _files(plan)
    line_cache: dict = {}
    for k in pfiles:
        if not isinstance(files.get(k), str):
            errs.append(f'File "{k}" có trong plan.files nhưng không có nội dung Target')
        else:
            line_cache[k] = split_lines(files[k])

    seen: dict = {}
    for c in _chunks(plan):
        if c.get("id") in seen:
            errs.append(f"Trùng id chunk {c.get('id')}")
        seen[c.get("id")] = True
    qseen: dict = {}
    for q in _questions(plan):
        if q.get("id") in qseen:
            errs.append(f"Trùng id câu hỏi {q.get('id')}")
        qseen[q.get("id")] = True

    ranges: dict = {}
    for c in _chunks(plan):
        cid = c.get("id")
        if c.get("file") not in pfiles:
            errs.append(f'{cid}: file "{_js_num(c.get("file"))}" không có trong plan.files')
        else:
            t = c.get("target") or {}
            s, e = t.get("start"), t.get("end")
            lines = line_cache.get(c["file"])
            if lines is not None:
                n = len(lines)
                if not (_is_int(s) and _is_int(e) and 1 <= s <= e <= n):
                    errs.append(f"{cid}: khoảng dòng {_js_num(s)}-{_js_num(e)} không hợp lệ ({c['file']} có {n} dòng)")
                else:
                    ranges.setdefault(c["file"], []).append((s, e, cid))
                    want = lines[s - 1:e]
                    text = t.get("text")
                    got = split_lines(text if isinstance(text, str) else "")
                    ok = isinstance(text, str) and text.endswith("\n") and want == got
                    if not ok:
                        i = 0
                        while i < len(want) and i < len(got) and want[i] == got[i]:
                            i += 1
                        at = s + i if (i < len(want) or i < len(got)) else e
                        errs.append(f"{cid}: target.text không khớp Target dòng {s}-{e} (lệch từ dòng {at})")
        if isinstance(c.get("rt"), str) and c.get("rt") == c.get("apply"):
            errs.append(f"{cid}: rt giống hệt apply (chỉ ghi rt khi khác apply)")

    for f in pfiles:
        rs = sorted(ranges.get(f, []), key=lambda x: (x[0], x[1]))
        for (s1, e1, a), (s2, e2, b) in zip(rs, rs[1:]):
            if s2 <= e1:
                errs.append(f"{f}: {a} ({s1}-{e1}) chồng lên {b} ({s2}-{e2})")

    for c in _chunks(plan):
        for r in c.get("requires") or []:
            if r.get("chunk") not in seen:
                errs.append(f"{c.get('id')}: requires trỏ tới chunk không tồn tại {r.get('chunk')}")
    for q in _questions(plan):
        qc = q.get("chunks") if isinstance(q.get("chunks"), list) else []
        for k in qc:
            if k not in seen:
                errs.append(f"{q.get('id')}: chunks trỏ tới chunk không tồn tại {k}")
        for o in q.get("options") or []:
            for k in o.get("apply") or []:
                if k not in seen:
                    errs.append(f"{q.get('id')}/{o.get('id')}: apply trỏ tới chunk không tồn tại {k}")
                elif k not in qc:
                    errs.append(f"{q.get('id')}/{o.get('id')}: apply có {k} không thuộc chunks của câu hỏi")

    owner: dict = {}
    for q in _questions(plan):
        mine: set = set()
        for k in q.get("chunks") or []:
            if k in mine:
                continue
            mine.add(k)
            if k in owner:
                errs.append(f"{k} thuộc hai câu hỏi: {owner[k]}, {q.get('id')}")
            else:
                owner[k] = q.get("id")
    return errs


def normalize_decisions(plan, decisions) -> dict:
    d = decisions or {}
    idx = chunk_index(plan)
    answers: dict = {}
    choices: dict = {}
    if isinstance(d.get("answers"), dict):
        for q in _questions(plan):
            a = d["answers"].get(q.get("id"))
            if isinstance(a, str) and any(o.get("id") == a for o in q.get("options") or []):
                answers[q["id"]] = a
    if isinstance(d.get("choices"), dict):
        for k, v in d["choices"].items():
            if k in idx and v in CHOICE_VALUES:
                choices[k] = v
    return {"rt": plan.get("rt") or d.get("rt") or "", "answers": answers, "choices": choices}


def compute_status(plan, decisions) -> dict:
    dec = normalize_decisions(plan, decisions)
    idx = chunk_index(plan)
    qmap = question_map(plan)
    rev = reverse_index(plan)
    st: dict = {}
    choice: dict = {}
    by: dict = {}
    for k, c in idx.items():
        q = qmap.get(k)
        by[k] = []
        if k in dec["choices"]:
            v = dec["choices"][k]
            if v == "rt" and not isinstance(c.get("rt"), str):
                v = "apply"
            choice[k] = v
            st[k] = "KEPT" if v == "target" else "APPLIED"
        elif q is not None and q["id"] in dec["answers"]:
            opt = next(o for o in q.get("options") or [] if o.get("id") == dec["answers"][q["id"]])
            on = k in (opt.get("apply") or [])
            choice[k] = "apply" if on else "target"
            st[k] = "APPLIED" if on else "KEPT"
        elif q is not None:
            choice[k] = "target"
            st[k] = "NEED_CONFIRM"
            by[k] = [q["id"]]
        else:
            choice[k] = "apply"
            st[k] = "APPLIED"

    changed = True
    while changed:
        changed = False
        nxt = dict(st)
        for k in idx:
            if st[k] != "APPLIED":
                continue
            reqs = [r for r in requires_ids(idx[k]) if r in idx]
            if any(st[r] != "APPLIED" for r in reqs):
                nxt[k] = "BLOCKED"
                changed = True
                continue
            deps = rev[k]
            if (k not in dec["choices"] and k not in qmap and deps
                    and all(st[d] != "APPLIED" for d in deps)):
                nxt[k] = "FOLLOW"
                changed = True
        st = nxt

    out: dict = {}
    for k in idx:
        s, b, ch = st[k], by[k], choice[k]
        if s == "BLOCKED":
            ch = "target"
            b = [r for r in requires_ids(idx[k]) if r in idx and st[r] not in ("APPLIED", "FOLLOW")]
        elif s == "FOLLOW":
            ch = "target"
            b = list(rev[k])
        out[k] = {"status": s, "choice": ch, "by": b}
    return out


def _replacement(chunk, choice):
    if choice == "rt" and isinstance(chunk.get("rt"), str):
        return chunk["rt"]
    if choice in ("apply", "rt"):
        return chunk["apply"] if isinstance(chunk.get("apply"), str) else ""
    return None


def build_file(plan, key: str, text: str, status: dict) -> dict:
    lines = split_lines(text)
    final_nl = text == "" or text.endswith("\n")
    lst = [(c, i) for i, c in enumerate(c for c in _chunks(plan) if c.get("file") == key
                                        and isinstance(c.get("target"), dict)
                                        and _is_int(c["target"].get("start")) and _is_int(c["target"].get("end")))]
    lst.sort(key=lambda x: (x[0]["target"]["start"], x[1]))
    out: list[str] = []
    regions: list[dict] = []
    pos = 0
    for c, _ in lst:
        s, e = c["target"]["start"] - 1, c["target"]["end"]
        if s < pos or s < 0 or e > len(lines) or e <= s:
            continue
        out.extend(lines[pos:s])
        reg_start = len(out) + 1
        stc = status.get(c["id"]) if status else None
        rep = _replacement(c, stc["choice"] if stc else "target")
        if rep is None:
            out.extend(lines[s:e])
        else:
            out.extend(split_lines(rep))
        regions.append({"chunk": c["id"], "start": reg_start, "end": len(out), "origStart": s + 1, "origEnd": e})
        pos = e
    out.extend(lines[pos:])
    result = "\n".join(out) + ("\n" if out and final_nl else "")
    return {"text": result, "lines": out, "regions": regions}


def build(plan, files: dict, decisions) -> dict:
    status = compute_status(plan, decisions)
    res = {}
    for key in _files(plan):
        if isinstance((files or {}).get(key), str):
            res[key] = build_file(plan, key, files[key], status)["text"]
    return res


def _bfs(start: str, nxt) -> list[str]:
    seen = {start}
    out: list[str] = []
    queue = [start]
    while queue:
        cur = queue.pop(0)
        for n in nxt(cur):
            if n in seen:
                continue
            seen.add(n)
            out.append(n)
            queue.append(n)
    return out


def closure(plan, chunk_id: str) -> list[str]:
    idx = chunk_index(plan)
    return _bfs(chunk_id, lambda k: [r for r in requires_ids(idx[k]) if r in idx] if k in idx else [])


def dependents(plan, chunk_id: str) -> list[str]:
    rev = reverse_index(plan)
    return _bfs(chunk_id, lambda k: rev.get(k, []))


# ====================================================================== đọc / ghi file

def load_json(path: Path, what: str):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        raise InputError(f"Không thấy {what}: {path}")
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InputError(f"{what} không phải JSON hợp lệ ({path}): {exc}")


def read_target(path: Path, encoding: str) -> tuple[str, dict]:
    """Đọc file Target. Trả về (text với '\\n', meta {encoding, eol, bom, mixed_eol})."""
    try:
        codecs.lookup(encoding)
    except LookupError:
        raise InputError(f"{path}: encoding không biết: {encoding}")
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        raise InputError(f"Thiếu file Target: {path}")
    except OSError as exc:
        raise InputError(f"Không đọc được {path}: {exc}")
    bom = False
    if encoding.lower().replace("_", "-") in ("utf-8", "utf8") and raw.startswith(codecs.BOM_UTF8):
        raw = raw[len(codecs.BOM_UTF8):]
        bom = True
    try:
        text = raw.decode(encoding)
    except UnicodeDecodeError as exc:
        raise InputError(f"{path}: không decode được bằng {encoding}: {exc}")
    crlf = text.count("\r\n")
    lf = text.count("\n") - crlf
    eol = "crlf" if crlf and crlf >= lf else "lf"
    meta = {"encoding": encoding, "eol": eol, "bom": bom, "mixed_eol": bool(crlf and lf)}
    return text.replace("\r\n", "\n"), meta


def encode_output(text: str, meta: dict, key: str) -> bytes:
    if meta["eol"] == "crlf":
        text = text.replace("\n", "\r\n")
    try:
        data = text.encode(meta["encoding"])
    except UnicodeEncodeError as exc:
        raise InputError(f"{key}: không ghi được bằng {meta['encoding']}: {exc}")
    return (codecs.BOM_UTF8 if meta.get("bom") else b"") + data


def load_inputs(plan_path: Path, target_root: Path):
    plan = load_json(plan_path, "merge-plan.json")
    if not isinstance(plan, dict) or not isinstance(plan.get("files"), dict) or not isinstance(plan.get("chunks"), list):
        raise InputError(f"{plan_path}: thiếu 'files' hoặc 'chunks' — không phải merge-plan v7")
    plan.setdefault("questions", [])
    plan.setdefault("skipped", [])
    files: dict = {}
    meta: dict = {}
    for key, info in plan["files"].items():
        enc = (info or {}).get("encoding") or "utf-8"
        files[key], meta[key] = read_target(target_root / key, enc)
    return plan, files, meta


# ====================================================================== lệnh

def _script_safe_json(obj) -> str:
    s = json.dumps(obj, ensure_ascii=False)
    return s.replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def render_html(plan, files, meta, decisions, plan_name: str, target_root: str) -> str:
    core = CORE_JS.read_text(encoding="utf-8")
    if "</script" in core.lower():
        raise InputError("review_core.js chứa '</script' — không nhúng được")
    payload = {
        "plan": plan,
        "files": files,
        "meta": meta,
        "decisions": decisions,
        "source": {"plan": plan_name, "targetRoot": target_root},
    }
    html = TEMPLATE.read_text(encoding="utf-8")
    for marker in ("/*__REVIEW_CORE__*/", "/*__PAYLOAD__*/null"):
        if html.count(marker) != 1:
            raise InputError(f"review_template.html: marker {marker} phải xuất hiện đúng 1 lần")
    html = html.replace("/*__REVIEW_CORE__*/", core)
    html = html.replace("/*__PAYLOAD__*/null", _script_safe_json(payload))
    return html


def count_status(status: dict) -> dict:
    out = {k: 0 for k in ("APPLIED", "KEPT", "NEED_CONFIRM", "BLOCKED", "FOLLOW")}
    for v in status.values():
        out[v["status"]] += 1
    return out


def cmd_render(args) -> int:
    plan_path = Path(args.plan)
    plan, files, meta = load_inputs(plan_path, Path(args.target_root))
    decisions = load_json(Path(args.decisions), "decisions.json") if args.decisions else None
    errs = validate(plan, files)
    html = render_html(plan, files, meta, decisions, plan_path.name, str(args.target_root))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    st = compute_status(plan, decisions)
    cnt = count_status(st)
    print(f"{plan.get('rt')}: {len(plan['files'])} file, {len(plan['chunks'])} chunk, "
          f"{len(plan['questions'])} câu hỏi, {len(plan['skipped'])} skipped")
    print("Trạng thái: " + ", ".join(f"{k}={v}" for k, v in cnt.items()))
    for key, m in meta.items():
        if m["mixed_eol"]:
            print(f"CẢNH BÁO: {key} lẫn CRLF và LF; output dùng {m['eol'].upper()}")
    for e in errs:
        print("LỖI:", e)
    print(f"Đã ghi {out}")
    if errs:
        print(f"Plan có {len(errs)} lỗi kiểm tra — trang hiện banner đỏ và khóa nút xuất.")
        return 1
    return 0


def cmd_apply(args) -> int:
    if not args.decisions:
        raise InputError("--apply cần --decisions")
    plan, files, meta = load_inputs(Path(args.plan), Path(args.target_root))
    decisions = load_json(Path(args.decisions), "decisions.json")
    if not isinstance(decisions, dict):
        raise InputError("decisions.json phải là object {rt, answers, choices}")
    errs = validate(plan, files)
    if errs:
        for e in errs:
            print("LỖI:", e)
        print("Không ghi output vì plan không qua kiểm tra.")
        return 1
    if decisions.get("rt") and decisions["rt"] != plan.get("rt"):
        print(f"CẢNH BÁO: decisions.json của {decisions['rt']}, plan là {plan.get('rt')}")
    st = compute_status(plan, decisions)
    pending = sorted({q for v in st.values() if v["status"] == "NEED_CONFIRM" for q in v["by"]})
    if pending and not args.allow_pending:
        print("Còn câu hỏi chưa trả lời: " + ", ".join(pending) + " (dùng --allow-pending để coi như giữ Target)")
        return 3
    out_root = Path(args.output)
    built = {key: build_file(plan, key, files[key], st)["text"] for key in plan["files"]}
    data = {key: encode_output(text, meta[key], key) for key, text in built.items()}  # encode hết rồi mới ghi
    for key, raw in data.items():
        p = out_root / key
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(raw)
        print(f"Đã ghi {p} ({meta[key]['encoding']}, {meta[key]['eol'].upper()})")
    cnt = count_status(st)
    print("Trạng thái: " + ", ".join(f"{k}={v}" for k, v in cnt.items()))
    for k, v in st.items():
        if v["status"] in ("BLOCKED", "FOLLOW", "NEED_CONFIRM"):
            print(f"  {k}: {v['status']} ({', '.join(v['by'])}) — giữ Target")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", required=True, help="merge-plan.json")
    ap.add_argument("--target-root", required=True, help="thư mục Target gốc (khóa trong plan.files tính từ đây)")
    ap.add_argument("-o", "--output", required=True, help="render: file HTML; --apply: thư mục output")
    ap.add_argument("--decisions", help="decisions.json (render: nạp sẵn vào trang; apply: bắt buộc)")
    ap.add_argument("--apply", action="store_true", help="ghi file output thay vì HTML")
    ap.add_argument("--allow-pending", action="store_true", help="apply dù còn câu hỏi chưa trả lời (giữ Target)")
    args = ap.parse_args(argv)
    try:
        return cmd_apply(args) if args.apply else cmd_render(args)
    except InputError as exc:
        print("LỖI ĐẦU VÀO:", exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
