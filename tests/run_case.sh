#!/usr/bin/env bash
# Run the port-request skill headless on one test case, then score it.
# Usage: tests/run_case.sh <case_name> [run_id]
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT=$PWD
CASE=$1
RUN_ID=${2:-$(date +%Y%m%d-%H%M%S)}
CDIR=$ROOT/tests/cases/$CASE
RDIR=$ROOT/tests/runs/$RUN_ID/$CASE
mkdir -p "$RDIR"
BUILD_CMD=$(cat "$CDIR/build_cmd" 2>/dev/null || echo "make -s MODEL=B")

PROMPT="/port-request
SOURCE_ROOT=$CDIR/input/A_latest
TARGET_ROOT=$CDIR/input/B_latest
SOURCE_REQUEST=$CDIR/input/REQ
TARGET_REQUEST_ID=$CASE
OUTPUT_PARENT=$RDIR
APPROVAL_MODE=auto
BUILD_CMD=$BUILD_CMD
Run all checkpoints A to F without stopping (auto mode)."

start=$(date +%s)
claude -p "$PROMPT" \
  --output-format stream-json --verbose \
  --permission-mode acceptEdits \
  --allowedTools "Bash,Read,Write,Edit,Glob,Grep,Skill" \
  > "$RDIR/transcript.jsonl" 2> "$RDIR/stderr.log" || echo "claude exit=$?" >> "$RDIR/stderr.log"
echo "$(( $(date +%s) - start ))" > "$RDIR/duration_s"

python3 tests/score.py "$CDIR" "$RDIR/formula-source-$CASE" "$RDIR/score.json" > /dev/null
echo "done: $RDIR"
