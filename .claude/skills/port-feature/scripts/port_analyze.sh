#!/usr/bin/env bash
# Phân tích port feature (bước 0-5), hoàn toàn bằng công cụ, KHÔNG tốn token LLM.
#
# Cách dùng:
#   port_analyze.sh --a <A_latest> --b <B_latest> --before <feature_before> --after <feature_after> \
#                   --out <work_dir> [--builder ts|doxygen] [--config-dir config] \
#                   [--define-a MODEL_A] [--define-b MODEL_B]
# Output trong <work_dir>: report.md, llm_review.md, manifest.json, *_latest.json (graph)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"

BUILDER=ts; CONFIG_DIR=config; DEF_A=""; DEF_B=""
while [ $# -gt 0 ]; do
  case "$1" in
    --a) A="$2"; shift 2;;
    --b) B="$2"; shift 2;;
    --before) BEFORE="$2"; shift 2;;
    --after) AFTER="$2"; shift 2;;
    --out) OUT="$2"; shift 2;;
    --builder) BUILDER="$2"; shift 2;;
    --config-dir) CONFIG_DIR="$2"; shift 2;;
    --define-a) DEF_A="$2"; shift 2;;
    --define-b) DEF_B="$2"; shift 2;;
    *) echo "Tham số lạ: $1"; exit 1;;
  esac
done
for v in A B BEFORE AFTER OUT; do
  [ -n "${!v:-}" ] || { echo "Thiếu --$(echo $v | tr A-Z a-z)"; exit 1; }
  [ "$v" = OUT ] || [ -d "${!v}" ] || { echo "Không thấy thư mục ${!v}"; exit 1; }
done

# Python có tree-sitter: ưu tiên $PORT_PY, rồi .venv của project, rồi python3
PY="${PORT_PY:-}"
[ -z "$PY" ] && [ -x .venv/bin/python ] && PY=.venv/bin/python
[ -z "$PY" ] && PY=python3
$PY -c "import tree_sitter, tree_sitter_c" 2>/dev/null || {
  echo "Thiếu tree-sitter. Cài: uv venv .venv && uv pip install --python .venv/bin/python tree-sitter tree-sitter-c"
  exit 1; }

mkdir -p "$OUT"
build() {  # $1=src $2=name $3=define
  if [ "$BUILDER" = ts ]; then
    $PY "$HERE/build_graph_ts.py" "$1" "$OUT/$2.json"
  else
    $PY "$HERE/build_graph_doxygen.py" "$1" "$OUT/$2.json" --define "$3"
  fi
}
build "$A" A_latest "$DEF_A"
build "$B" B_latest "$DEF_B"
build "$BEFORE" feature_before "$DEF_A"
build "$AFTER" feature_after "$DEF_A"
$PY "$HERE/seed.py" "$OUT/feature_before.json" "$OUT/feature_after.json" "$OUT/seed.json"
$PY "$HERE/analyze.py" --graph-a "$OUT/A_latest.json" --graph-b "$OUT/B_latest.json" \
    --seed "$OUT/seed.json" --out-dir "$OUT" --config-dir "$CONFIG_DIR"
echo "Xong. Đọc $OUT/report.md rồi $OUT/llm_review.md"
