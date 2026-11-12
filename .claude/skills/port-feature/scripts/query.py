"""Hỏi code graph thay vì đọc file - mỗi câu trả lời chỉ vài dòng.

Cách dùng (work = thư mục output của port_analyze.sh):
  python query.py <work> show <symbol>       vị trí + trạng thái ở B + code của symbol ở A
  python query.py <work> showb <symbol>      code của symbol ở B
  python query.py <work> callees <symbol>    symbol này dùng những gì (kèm trạng thái ở B)
  python query.py <work> callers <symbol>    ai đang dùng symbol này (ở A_latest)
  python query.py <work> callers-b <symbol>  ai đang dùng symbol này (ở B_latest)
  python query.py <work> find <chuỗi>        tìm symbol theo tên (cả A và B)
  python query.py <work> undefined <file_log_build>   map lỗi build "undefined ..." -> symbol ở A
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import load_graph, read_lines  # noqa: E402


def resolve(g, name):
    if name in g["nodes"]:
        return name
    hits = [k for k, n in g["nodes"].items() if n["name"] == name]
    return hits[0] if len(hits) == 1 else (hits or None)


def status(ga, gb, key):
    if key not in gb["nodes"]:
        return "MISSING_IN_B"
    return "IDENTICAL" if gb["nodes"][key]["hash"] == ga["nodes"][key]["hash"] else "DIFFERENT"


def main():
    work, cmd, arg = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
    ga, gb = load_graph(work / "A_latest.json"), load_graph(work / "B_latest.json")

    if cmd == "find":
        for side, g in (("A", ga), ("B", gb)):
            for k, n in g["nodes"].items():
                if arg.lower() in n["name"].lower():
                    print(f"{side}  {n['kind']:9} {k}  ({n['file']}:{n['start']})")
        return
    if cmd == "undefined":
        log = Path(arg).read_text()
        names = set(re.findall(r"(?:undefined reference to|undeclared identifier|implicit declaration of "
                               r"function|use of undeclared identifier|Undefined symbols.*?\n\s+)\s*[`'\"_]*"
                               r"([A-Za-z_]\w*)", log))
        for nm in sorted(names):
            k = resolve(ga, nm)
            print(f"{nm}: " + (f"{k} @ {ga['nodes'][k]['file']} [{status(ga, gb, k)}]"
                               if isinstance(k, str) else f"không tìm thấy/nhập nhằng ở A: {k}"))
        return

    g = gb if cmd in ("showb", "callers-b") else ga
    key = resolve(g, arg)
    if not isinstance(key, str):
        print(f"Không xác định được '{arg}' (ứng viên: {key}). Dùng dạng ten@file cho symbol static.")
        return
    n = g["nodes"][key]
    if cmd in ("show", "showb"):
        st = status(ga, gb, key) if key in ga["nodes"] else "ONLY_IN_B"
        print(f"{key}  [{n['kind']}]  {n['file']}:{n['start']}-{n['end']}  status={st}  guards={n['guards']}")
        print(read_lines(Path(g["root"]), n["file"], n["start"], n["end"]))
    elif cmd == "callees":
        for e in ga["edges"]:
            if e["src"] == key:
                st = status(ga, gb, e["dst"]) if e["dst"] in ga["nodes"] else "-"
                print(f"{e['type']:11} -> {e['dst']}  [{st}]")
    elif cmd in ("callers", "callers-b"):
        for e in g["edges"]:
            if e["dst"] == key:
                print(f"{e['src']}  -{e['type']}->")
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
