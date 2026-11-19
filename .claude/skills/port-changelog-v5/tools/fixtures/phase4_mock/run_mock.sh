#!/usr/bin/env bash
# Chạy thử Phase 4 trên dữ liệu mock (RT9001 giả lập).
#
# Cách gọi:  bash run_mock.sh [THƯ_MỤC_CHẠY]
#   THƯ_MỤC_CHẠY mặc định là một thư mục tạm. Mock gốc không bị sửa.
#
# Các bước (giống phases/phase-4-review.md):
#   1. check  : merge_view.json phải KHỚP WORK/target_out (đầu ra Phase 3)
#   2. render : sinh WORK/phase4/merge_view.html  (mở file này để xem UI)
#   3. apply  : áp decisions.mock.json → WORK/target_out
#   4. so WORK/target_out với expected/target_out_final
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
TOOLS="$(cd "$HERE/../.." && pwd)"
RUN="${1:-$(mktemp -d)}"

mkdir -p "$RUN"
cp -R "$HERE/target" "$HERE/WORK" "$RUN/"
mkdir -p "$RUN/WORK/phase4"
cp "$HERE/decisions.mock.json" "$RUN/WORK/phase4/decisions.json"
cd "$RUN"

echo "== Bước 1: check"
python3 "$TOOLS/merge_ui.py" check WORK/phase3/merge_view.json --target-out-root WORK/target_out

echo "== Bước 2: render"
python3 "$TOOLS/merge_ui.py" render WORK/phase3/merge_view.json -o WORK/phase4/merge_view.html

echo "== Bước 6: apply"
python3 "$TOOLS/merge_ui.py" apply WORK/phase3/merge_view.json \
        --decisions WORK/phase4/decisions.json -o WORK/target_out

echo "== So với kết quả mong đợi"
if diff -r "$HERE/expected/target_out_final" WORK/target_out; then
  echo "OK: WORK/target_out giống expected/target_out_final"
else
  echo "KHÁC: xem diff ở trên"; exit 1
fi

echo
echo "UI:          $RUN/WORK/phase4/merge_view.html"
echo "Kết quả:     $RUN/WORK/target_out"
