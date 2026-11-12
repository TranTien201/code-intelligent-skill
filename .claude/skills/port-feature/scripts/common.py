"""Phần dùng chung: schema graph, chuẩn hoá + hash code, đọc/ghi graph.

Schema graph (JSON) - cả tree-sitter và Doxygen đều xuất ra đúng schema này
để phần phân tích (analyze.py) dùng chung, so sánh công bằng:

{
  "builder": "treesitter" | "doxygen",
  "root": "<thư mục source>",
  "files": ["src/a.c", ...],
  "nodes": {
     "<key>": {"name", "kind", "file", "start", "end", "static", "hash", "guards": [...]}
  },
  "edges": [{"src": key, "dst": key, "type": "CALLS|REFERENCES|USES_TYPE|USES_MACRO|
             USES_CONST|USES_VAR|USES_FIELD|GUARDED_BY"}]
}
key = tên symbol; riêng symbol static = "tên@file" (vì static trùng tên ở nhiều file).
kind = function | var | type | macro | enumconst
"""
import hashlib
import json
import re
from pathlib import Path

CODE_EXT = {".c", ".h"}


def symbol_key(name: str, file: str, is_static: bool) -> str:
    return f"{name}@{file}" if is_static else name


_COMMENT = re.compile(r"/\*.*?\*/|//[^\n]*", re.S)


def normalize(code: str) -> str:
    """Bỏ comment + gộp khoảng trắng: để 2 đoạn code chỉ khác format vẫn được coi là giống."""
    code = _COMMENT.sub(" ", code)
    return re.sub(r"\s+", " ", code).strip()


def code_hash(code: str) -> str:
    return hashlib.sha1(normalize(code).encode()).hexdigest()[:12]


def list_files(root: Path):
    return sorted(str(p.relative_to(root)) for p in root.rglob("*")
                  if p.is_file() and not p.name.startswith("."))


def is_include_guard(name: str, value: str) -> bool:
    return name.endswith("_H") and not value.strip()


def save_graph(graph: dict, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(graph, indent=1, ensure_ascii=False))


def load_graph(path) -> dict:
    return json.loads(Path(path).read_text())


def read_lines(root: Path, file: str, start: int, end: int) -> str:
    lines = (root / file).read_text().splitlines()
    return "\n".join(lines[start - 1:end])
