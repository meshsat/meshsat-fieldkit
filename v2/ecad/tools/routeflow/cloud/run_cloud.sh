#!/usr/bin/env bash
# The Freerouting quality programme on the vast.ai box (6 Sep 2026): every experiment named on the command line runs as its own routeflow
# process with its own lock file, P configurations at once inside each, all side by side; then bench_report.py writes the report from
# results.jsonl. Every JVM is capped at 5 GB (B15 needs about 3.5 GB); route timeouts are stretched by ROUTEFLOW_TIMEOUT_SCALE (default 2,
# the EPYC core is slower than the VM's i9). Log ~/cloud.log, marker CLOUD-EXIT. Usage: run_cloud.sh <parallel per experiment> <experiment names...>
P=${1:-12}; shift; R=/root/gitlab/products/meshsat/meshsat-fieldkit; T=$R/v2/ecad/tools; L=/root/logs; mkdir -p $L
export JAVA_TOOL_OPTIONS="-Xmx5g" ROUTEFLOW_TIMEOUT_SCALE="${ROUTEFLOW_TIMEOUT_SCALE:-2}" LANG=C.UTF-8
date; echo "host $(hostname): $(nproc) threads, $(free -g | awk '/Mem:/ {print $2}') GB; experiments: $*; $P configurations at once per experiment; timeout scale $ROUTEFLOW_TIMEOUT_SCALE"
cd $R || exit 1
for e in "$@"; do
  [ -f $T/routeflow/experiments/$e.json ] || { echo "no experiment $e"; continue; }
  ROUTEFLOW_LOCK=/root/.routeflow.$e.lock python3 $T/routeflow.py experiment $T/routeflow/experiments/$e.json --budget-hours 8 --no-services --parallel $P > $L/$e.log 2>&1 &
  echo "started $e (pid $!)"; sleep 8
done
wait; date
python3 $T/bench_report.py $T/routeflow/bench/results.jsonl $T/routeflow/bench/baseline.json --out $T/routeflow/bench/report.md 2>&1 | tail -100
wc -l $T/routeflow/bench/results.jsonl; date; echo CLOUD-EXIT
