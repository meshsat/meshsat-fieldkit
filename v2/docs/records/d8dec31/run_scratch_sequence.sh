#!/bin/bash
# The integrator's sequence, rehearsed on a scratch tree (MESHSAT-1357, worker d8dec31, 28 September 2026). Never run
# it against a worktree: the first argument is a scratch root holding main's v2/ecad/tools, v2/docs, the netlists and
# v2/vendor (real files or read-only links), with this branch's files copied over it. It runs every apply script in the
# order the integrator runs them, the validator after the registry, the regression on the three real corrected tables,
# and every refusal of the S-88 closure stage, then the closure on a reading it takes itself (which in the real tree
# is the KiCad host's re-take, committed). Output is the reading v2/docs/records/d8dec31/readings/apply-scratch.txt.
set -u
ROOT="$1"; D="$ROOT/v2/docs/records/d8dec31"; T="$ROOT/v2/ecad/tools"
step() { echo; echo "== $*"; }
step 1 apply_port_declarations;            python3 "$D/apply_port_declarations.py" "$ROOT"; echo "rc=$?"
step 2 make_port_reviews --check;          python3 "$D/make_port_reviews.py" "$ROOT" --check; echo "rc=$?"
step 3 apply_config_inputs_port_reviews;   python3 "$D/apply_config_inputs_port_reviews.py" "$ROOT"; echo "rc=$?"
step 4 apply_registry_d31 stage 1;         python3 "$D/apply_registry_d31.py" "$ROOT"; echo "rc=$?"
step 4b second run refused;                python3 "$D/apply_registry_d31.py" "$ROOT"; echo "rc=$?"
step 5 rules_lib requirements;             (cd "$T" && python3 rules_lib.py requirements 2>&1 | grep -v "^warn  closed item" | tail -3)
step 6 apply_sources_d31;                  python3 "$D/apply_sources_d31.py" "$ROOT"; echo "rc=$?"
step 7 apply_holds_review_pin;             python3 "$D/apply_holds_review_pin.py" "$ROOT"; echo "rc=$?"
step 8 apply_interfaces_mainsw, refused on today\'s netlist; python3 "$D/apply_interfaces_mainsw.py" "$ROOT"; echo "rc=$?"
step 8b apply_interfaces_mainsw --force-netlist --check; python3 "$D/apply_interfaces_mainsw.py" "$ROOT" --force-netlist --check; echo "rc=$?"
step 9 regress_reclassify on the corrected tables; python3 "$D/regress_reclassify.py" "$ROOT" | grep "^ok\|^FAIL\|^regress"
step 10 close-s88 refusals;                mkdir -p "$ROOT/v2/ecad/out"; rm -f "$ROOT/v2/ecad/out/port_protect_a.verdict.json"
python3 "$D/apply_registry_d31.py" "$ROOT" --close-s88 0123456789ab; echo "rc=$?"
python3 - "$ROOT/_regress_verdicts/a/baseline/port_protect_a.verdict.json" "$ROOT/v2/ecad/out/port_protect_a.verdict.json" <<'EOF'
import json, sys
v = json.load(open(sys.argv[1])); v["inputs"]["netlist"]["sha256_16"] = "0000000000000000"; json.dump(v, open(sys.argv[2], "w"), indent=1)
EOF
python3 "$D/apply_registry_d31.py" "$ROOT" --close-s88 0123456789ab; echo "rc=$?"
python3 - "$ROOT/_regress_verdicts/a/baseline/port_protect_a.verdict.json" "$ROOT/v2/ecad/out/port_protect_a.verdict.json" <<'EOF'
import json, sys
v = json.load(open(sys.argv[1])); v["writer"]["sha16"] = "2d69facd3c25c8a4"; v["code_bundle"]["files"]["port_protect.py"] = "2d69facd3c25c8a4"; json.dump(v, open(sys.argv[2], "w"), indent=1)
EOF
python3 "$D/apply_registry_d31.py" "$ROOT" --close-s88 0123456789ab; echo "rc=$?"
cp "$ROOT/_regress_verdicts/a/reclassified/port_protect_a.verdict.json" "$ROOT/v2/ecad/out/port_protect_a.verdict.json"
python3 "$D/apply_registry_d31.py" "$ROOT" --close-s88 0123456789ab 2>&1 | cut -c1-160; echo "rc=${PIPESTATUS[0]}"
step 11 close-s88 on the re-taken reading; cp "$ROOT/_regress_verdicts/a/baseline/port_protect_a.verdict.json" "$ROOT/v2/ecad/out/port_protect_a.verdict.json"
python3 "$D/apply_registry_d31.py" "$ROOT" --close-s88 0123456789ab --check; echo "rc=$?"
python3 "$D/apply_registry_d31.py" "$ROOT" --close-s88 0123456789ab; echo "rc=$?"
python3 "$D/apply_registry_d31.py" "$ROOT" --close-s88 0123456789ab; echo "second run rc=$?"
step 12 rules_lib requirements after the closure; (cd "$T" && python3 rules_lib.py requirements 2>&1 | grep -v "^warn  closed item" | tail -3)
