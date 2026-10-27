#!/usr/bin/env bash
# Benchmark the OpenCode /audit command across local models.
# Usage: scripts/bench_opencode.sh [model ...]   (default: the 3 models in opencode.json)
# Results: output/bench/<model-slug>/ (artifacts, log, score.txt) + one CSV line per run in output/bench/results.csv
set -uo pipefail
cd "$(dirname "$0")/.."
set -a; source .env; set +a

models=("$@")
[ ${#models[@]} -eq 0 ] && models=(google/gemma-4-26b-a4b google/gemma-4-e4b qwen/qwen3-coder-30b)
target=examples/sample-app
mkdir -p output/bench
[ -f output/bench/results.csv ] || echo "date,model,seconds,exit,score,files_written,target_modified" > output/bench/results.csv

for model in "${models[@]}"; do
  slug=${model//\//_}
  dir=output/bench/$slug
  rm -rf output/opencode-audit "$dir"; mkdir -p "$dir"
  m="lmstudio/$model"
  # Run every agent (orchestrator + subagents) on the same model.
  export OPENCODE_CONFIG_CONTENT="{\"agent\":{\"architect\":{\"model\":\"$m\"},\"developer\":{\"model\":\"$m\"},\"security-qa\":{\"model\":\"$m\"}}}"
  echo ">> $model"
  start=$(date +%s)
  opencode run -m "$m" --command audit "$target" > "$dir/run.log" 2>&1
  code=$?
  secs=$(( $(date +%s) - start ))
  [ -d output/opencode-audit ] && cp -R output/opencode-audit/. "$dir/"
  files=$(find output/opencode-audit -type f ! -name report.md 2>/dev/null | wc -l | tr -d ' ')
  if [ -f "$dir/report.md" ]; then
    poetry run score-audit "$dir/report.md" > "$dir/score.txt"
    score=$(head -1 "$dir/score.txt" | awk '{print $2}')
  else
    score="0/14 (no report)"
  fi
  modified=$(git status --porcelain "$target" | wc -l | tr -d ' ')
  echo "$(date +%F),$model,$secs,$code,$score,$files,$modified" | tee -a output/bench/results.csv
  git checkout -q -- "$target" 2>/dev/null
done
unset OPENCODE_CONFIG_CONTENT
