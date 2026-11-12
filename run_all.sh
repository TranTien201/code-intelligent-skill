#!/usr/bin/env bash
# Chạy toàn bộ quy trình cho cả 2 builder (tree-sitter & Doxygen) rồi chấm điểm.
set -euo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python

$PY dataset/make_dataset.py
rm -rf out

for B in ts doxygen; do
  echo; echo "===== Builder: $B ====="
  start=$(date +%s)
  for T in A_latest feature_before feature_after B_latest; do
    if [ "$B" = ts ]; then
      $PY tools/build_graph_ts.py data/$T out/$B/$T.json
    else
      DEF=MODEL_A; [ "$T" = B_latest ] && DEF=MODEL_B
      $PY tools/build_graph_doxygen.py data/$T out/$B/$T.json --define $DEF
    fi
  done
  $PY tools/seed.py out/$B/feature_before.json out/$B/feature_after.json out/$B/seed.json
  $PY tools/analyze.py --graph-a out/$B/A_latest.json --graph-b out/$B/B_latest.json \
                       --seed out/$B/seed.json --out-dir out/$B
  echo "Thời gian: $(( $(date +%s) - start ))s"
done

echo; echo "===== Chấm điểm so với data/expected.json ====="
$PY tools/evaluate.py data/expected.json out/ts/manifest.json out/doxygen/manifest.json

echo; echo "===== Apply sang B + build kiểm chứng (dùng manifest tree-sitter) ====="
$PY tools/apply.py --work out/ts --a data/A_latest --b data/B_latest \
    --before data/feature_before --after data/feature_after --out data/B_ported \
    --b-config config/model_b.h --build "make -s MODEL=B" --run ./printer_B
echo "--- Để so sánh, output của A_latest:"
(cd data/A_latest && make -s MODEL=A && ./printer_A && rm -f printer_A)
