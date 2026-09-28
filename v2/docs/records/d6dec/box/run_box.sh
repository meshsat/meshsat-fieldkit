#!/usr/bin/env bash
# run_box.sh <clone name> <run name>: the three box jobs of stream d6dec, one after another, in /root/d6dec only.
#   1. the test files this branch adds or changes, and every test file that names a tool it changed (one run.py call)
#   2. escape_parity.py: the escape pass of the base 73ae2f21 (/root/d6dec/base) against this clone's, six bare boards
#   3. dec001_read.py: what DEC-001 reads on each committed candidate, outside the tree (NOT EVIDENCE)
# Each job writes /root/d6dec/<run>/done-<job> with its exit code. No cd: env -C.
set -u
C=/root/d6dec/$1; O=/root/d6dec/$2; mkdir -p $O
TESTS="test_decoupling_rules test_decoupling_board test_escape_cost test_intent_bypass_class test_board_gates test_bypass_place test_bypass_slots_duplicate test_bypass_seats test_carry_placed test_dead_pour_islands test_closer_audit test_exposed_pad_vias test_agent_contract test_barrel_sites test_driver_hygiene test_gate_crash_guard test_kb_isolation test_finish_order test_fanout_in_pad test_netlist_provenance test_netclass test_prelay_pairs test_last_net test_part_room test_pair_legality test_rails_census test_rails_netlist test_return_rules test_sweep_placement test_rule_windows test_signal_class test_stackup_reader test_verdict_channel"
env -C $C/v2/ecad/tools/tests python3 run.py $TESTS > $O/tests.log 2>&1; echo $? > $O/done-tests
python3 $C/v2/docs/records/d6dec/box/escape_parity.py /root/d6dec/base $C $O/parity $O/escape_parity.json > $O/escape_parity.log 2>&1; echo $? > $O/done-parity
python3 $C/v2/docs/records/d6dec/box/dec001_read.py $C $O/read $O/dec001_read.json > $O/dec001_read.log 2>&1; echo $? > $O/done-dec001
echo finished > $O/done-all
