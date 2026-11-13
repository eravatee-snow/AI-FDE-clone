#!/usr/bin/env bash
# TC5 Step 4: run each measurement in turn, one log file per run.
# Usage: ./run_tc5.sh   (from anywhere; results go to use_case/evals/tc5_runs/<model>/)
#        LLM_MODEL=ollama_chat/qwen3.5:9b ./run_tc5.sh   for Ollama's native tool calling
set -u

cd "$(dirname "$0")"
MODEL="${LLM_MODEL:-ollama/qwen3.5:9b}"
# One folder per model string, so a run on another provider never overwrites an earlier one
OUT="../../use_case/evals/tc5_runs/$(echo "$MODEL" | tr '/:' '__')"
mkdir -p "$OUT"

# Keep the Mac awake for as long as this script runs; a sleeping laptop kills an overnight run.
caffeinate -i -w $$ &

if [ -z "${LLM_API_BASE:-}" ] && ! curl -sf http://localhost:11434/api/tags > /dev/null; then
  echo "Ollama is not answering on localhost:11434. Start it, then rerun." >&2
  exit 1
fi

COMMIT="$(git rev-parse --short HEAD)$(git diff --quiet || echo '-dirty')"

run() {
  local name="$1"; shift
  local file="$OUT/$name.log"
  echo "$(date '+%H:%M:%S') starting $name -> $file"
  {
    echo "# command: uv run python test.py $*"
    echo "# commit:  $COMMIT"
    echo "# model:   $MODEL"
    echo "# started: $(date '+%Y-%m-%d %H:%M:%S')"
    echo
  } > "$file"
  uv run python test.py "$@" >> "$file" 2>&1
  local code=$?
  {
    echo
    echo "# finished: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "# exit code: $code"
  } >> "$file"
  echo "$(date '+%H:%M:%S') finished $name (exit $code)"
}

run single  --single
run several --several
run batch   --batch

echo
echo "Summary lines:"
grep -h -E '^(Baseline|UTCP),' "$OUT"/*.log
