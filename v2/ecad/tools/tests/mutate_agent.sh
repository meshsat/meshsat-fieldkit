#!/usr/bin/env bash
# Every text rule in test_agent_contract.py must FAIL on a tree carrying the defect it was written for.
# A rule that passes on the tree it was written to fail is worse than no rule (the record's standing
# discipline, and this file exists because the agent's rules are all text checks).
#
# 12 September 2026: each mutation now PROVES it changed the tree before the rule is run. The first
# version did not, and when the revise round moved an anchor in loop.py one mutation silently became a
# no-op and its rule "passed" against a tree that never carried the defect. That is the same shape as
# the BooleanIntersection guard of 10 September, where a fix that changed nothing looked applied.
set -uo pipefail
SRC="$(cd "$(dirname "$0")/.." && pwd)"
WORK=$(mktemp -d)
pass=0; fail=0

run_case () {   # name, test-name-substring, python mutation operating on $T
  local name="$1" tsub="$2" mut="$3"
  rm -rf "$WORK/t"; cp -r "$SRC" "$WORK/t"
  cat > "$WORK/mut.py" <<'HEAD'
import sys, os, hashlib
T = sys.argv[1]
def _h(d):
    h = hashlib.sha256()
    for root, _, fs in os.walk(d):
        for f in sorted(fs):
            if f.endswith(".py"):
                h.update(open(os.path.join(root, f), "rb").read())
    return h.hexdigest()
before = _h(T)
HEAD
  printf '%s\n' "$mut" >> "$WORK/mut.py"
  cat >> "$WORK/mut.py" <<'TAIL'
if _h(T) == before:
    raise SystemExit("the mutation changed NOTHING: its anchor has moved, so this would prove nothing")
TAIL
  if ! python3 "$WORK/mut.py" "$WORK/t" >/dev/null 2>&1; then
    echo "  NOT PROVED  $name  -> the mutation did not apply (its anchor has moved)"
    fail=$((fail+1)); return
  fi
  out=$(cd "$WORK/t" && python3 tests/run.py "$tsub" 2>&1 | tail -1)
  if echo "$out" | grep -q " 0 failed"; then
    echo "  NOT PROVED  $name  -> the rule still passed with the defect in place: $out"; fail=$((fail+1))
  else
    echo "  proved      $name"; pass=$((pass+1))
  fi
}

run_case "a flag may be given a threshold" t_a_flag_given_a_threshold_is_refused '
p = os.path.join(T, "agent", "schema.py"); s = open(p).read()
s = s.replace("                if t.startswith(\"flag\") and str(v).strip() not in", "                if False and str(v).strip() not in", 1)
open(p, "w").write(s)'

run_case "the count is the whole objective again" t_the_pair_count_alone_is_not_the_objective '
p = os.path.join(T, "arms.py"); s = open(p).read()
s = s.replace("    if row.get(\"hard\") is not None and row[\"hard\"] > hard_baseline:",
              "    if False:", 1)
open(p, "w").write(s)'

echo "mutation proof: each rule must FAIL on a tree carrying its defect"

run_case "proposer gains a subprocess call" t_the_proposer_cannot_actuate '
p = os.path.join(T, "agent", "propose.py"); s = open(p).read()
s = s.replace("def ask(", "def _sneak():\n    import subprocess\n    subprocess.run([\"true\"])\n\n\ndef ask(", 1)
open(p, "w").write(s)'

run_case "client gains a default endpoint" t_the_client_carries_no_default_endpoint_or_key '
p = os.path.join(T, "agent", "client.py"); s = open(p).read()
s = s.replace("REQUIRED = (", "FALLBACK = os.environ.get(\"MESHSAT_LLM_BASE\", \"http://example.invalid:4000\")\nREQUIRED = (", 1)
open(p, "w").write(s)'

run_case "client stops recording the prompt hash" t_every_call_records '
p = os.path.join(T, "agent", "client.py"); s = open(p).read()
s = s.replace("\"prompt_sha\": sha(system + \"\\n\" + user), ", "")
open(p, "w").write(s)'

run_case "the reviewer writes an arm grade" t_the_judge_is_never_the_model '
p = os.path.join(T, "agent", "loop.py"); s = open(p).read()
s = s.replace("            if rev[\"verdict\"] == \"APPROVE\"",
              "            rows[0][\"verdict\"] = rev[\"verdict\"]\n            if rev[\"verdict\"] == \"APPROVE\"", 1)
open(p, "w").write(s)'

run_case "the loop stops grading mechanically" t_the_judge_is_never_the_model '
p = os.path.join(T, "agent", "loop.py"); s = open(p).read()
s = s.replace("v, note = armsmod.grade(r)", "v, note = \"MET\", \"the model says so\"", 1)
open(p, "w").write(s)'

run_case "a gate imports the agent" t_no_gate_or_chain_imports_the_agent '
p = os.path.join(T, "hardset.py"); s = open(p).read()
s = s.replace("import ", "from agent.client import Client  # a model on a verdict path\nimport ", 1)
open(p, "w").write(s)'

# The address is assembled at runtime so this file never itself carries one: the rule it proves scans
# this file too, after tier 2b pointed out that the first version published an estate-shaped hostname.
run_case "a host name lands in the tree" t_nothing_about_the_endpoint '
p = os.path.join(T, "agent", "evidence.py"); s = open(p).read()
addr = "10." + "0.0." + "1"
s = s.replace("HERE = ", "ENDPOINT = \"http://%s:4000\"\nHERE = " % addr, 1)
open(p, "w").write(s)'

run_case "the config mode check is dropped" t_the_client_refuses_a_config_anyone_can_read '
p = os.path.join(T, "agent", "client.py"); s = open(p).read()
s = s.replace("    if mode & 0o077:", "    if False:", 1)
open(p, "w").write(s)'

run_case "arms accepts any name" t_arms_refuses_an_unsafe_arm_name '
p = os.path.join(T, "arms.py"); s = open(p).read()
s = s.replace("    return isinstance(n, str) and bool(ARM_NAME.match(n)) and len(n) <= ARM_NAME_MAX",
              "    return True", 1)
open(p, "w").write(s)'

run_case "the knob arrival guard is removed" t_a_knob_that_never_arrived '
p = os.path.join(T, "arms.py"); s = open(p).read()
s = s.replace("    if not seen:\n        return (\"the pre-router printed no knob echo",
              "    if True:\n        return \"\"\n    if not seen:\n        return (\"the pre-router printed no knob echo", 1)
open(p, "w").write(s)'

echo "mutation proof: $pass proved, $fail NOT proved"
rm -rf "$WORK"
[ "$fail" -eq 0 ]
