#!/usr/bin/env python3
"""Layer 5 closer hc5 (MESHSAT-1357, 27 September 2026): edits to v2/ecad/tools/pcb_interfaces.yaml, section
board_to_board, written as a script so it applies to main e3aedb25 or to the tree after round 8's integration
(fnd/r8int1) alike. Idempotent: every edit checks whether it is already made, and otherwise asserts that its anchor occurs
exactly once. Text edits only; the file's own formatting is kept. After it runs the file must still load as YAML and the
section must hold every contract once.

  1. appends the eighteen contracts of drafts/hc5/pcb_interfaces-new-contracts.yaml after the last contract;
  2. the five hot-plug rules marked "(proposed)" become the session's choice SC-HF-04 (v2/docs/HW-FW-CONTRACT.md section 8);
  3. IF-PE-PACK's SMBus judged_by names check_contracts.py section 15c, which judges the lead since 93138ac1;
  4. IF-EXT-USB's stale_text, fixed in ASSEMBLY.md at 9a151c78, is retired;
  5. every judged_by that cited check_contracts.py by line cites it by section number, which survives edits above it;
  6. IF-BC-PANEL's bus text and findings carry the kit bus budget (HF-F01) and the session's segment choice (SC-HF-02).

Run from the repository root:  python3 drafts/hc5/apply_interfaces.py
Then:  python3 -m pytest-free runner of the two test files that read the file (see drafts/hc5/README.md)."""
import os, sys, yaml

ROOT = os.getcwd()
P = os.path.join(ROOT, "v2/ecad/tools/pcb_interfaces.yaml")
NEW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pcb_interfaces-new-contracts.yaml")
s = open(P, encoding="utf-8").read()
done = []


def rep(old, new, marker=None):
    """Replace old by new once; skip when `marker` (default: new) is already in the file."""
    global s
    m = marker or new
    if m in s:
        done.append("already: " + m[:70]); return
    n = s.count(old)
    assert n == 1, "anchor found %d times, expected 1: %r" % (n, old[:100])
    s = s.replace(old, new); done.append("edited: " + old[:70])


# 1. the new contracts, after the last contract (IF-EXT-USB is last on main and on fnd/r8int1)
new_block = open(NEW, encoding="utf-8").read()
new_ids = list(yaml.safe_load(new_block).keys())
have = [i for i in new_ids if ("\n    %s:\n" % i) in s]
if len(have) == len(new_ids):
    done.append("already: the %d new contracts" % len(new_ids))
else:
    assert not have, "some new contracts are present and some are not: %s" % have
    assert "\n    IF-EXT-USB:\n" in s, "IF-EXT-USB, the last contract on main, is not in the file"
    tail = s[s.index("\n    IF-EXT-USB:\n"):]
    assert "\n    IF-" not in tail[1:], "IF-EXT-USB is no longer the last contract: insert by hand after the last one"
    s = s.rstrip("\n") + "\n" + new_block.rstrip("\n") + "\n"
    done.append("appended %d contracts" % len(new_ids))

# 2. hot-plug rules: the session's choice SC-HF-04
SC4 = "(the session's choice SC-HF-04 of 27 September 2026 under the owner's standing rule, v2/docs/HW-FW-CONTRACT.md section 8)"
for old in ['hot_plug: "not hot-pluggable (proposed): mate and unmate with the kit off;',
            'hot_plug: "not hot-pluggable (proposed): no power crosses it,',
            'hot_plug: "not hot-pluggable (proposed): crimped leads, mate with the kit off"',
            'hot_plug: "never unplug J_PA with the kit on (proposed): 13.8 V at up to 6 A"',
            'only with the kit off (proposed)"']:
    rep(old, old.replace("(proposed)", SC4))

# 3. IF-PE-PACK's SMBus lead is judged
rep('judged_by: "none yet: the check_contracts P/E lead check is held in round 7 (458b2873\'s record)"',
    'judged_by: "check_contracts.py section 15c since 93138ac1: J_SMB at both ends, one family, pitch and pin count, and each pin\'s role; PASS of 96 across the set on the e3aedb25 netlists (the layer 5 audit\'s scratch re-run)"')

# 4. IF-EXT-USB's stale text is fixed in ASSEMBLY.md
rep('''      stale_text: "ASSEMBLY.md section 4's wall USB host row still routes the Glenair lead to 'B16 J_USBX', which no generator
        defines"''',
    '''      stale_text: "none: ASSEMBLY.md section 4's wall USB host row names A22 J_USBW since 9a151c78 (it named a B16 J_USBX until then)"''')

# 5. judged_by by section, not by line (check_contracts.py's sections at e3aedb25: 1 J_PANEL, 3 rails, 4 and 5 dock,
#    7 J_AB1, 7b J_AB2, 8 J_MEZZ1/J_HARN1, 10 the wall pair, 15b the pack leads, 15c the SMBus lead)
for old, new in [
        ('judged_by: "check_contracts.py:196-207"}', 'judged_by: "check_contracts.py section 1 (the J_PANEL map)"}'),
        ('judged_by: "check_contracts.py:267-269"}', 'judged_by: "check_contracts.py section 7 (the J_AB1 map)"}'),
        ('judged_by: "check_contracts.py:274-278 (map), :292 (the pair reaches A\'s J_USBW)"}',
         'judged_by: "check_contracts.py sections 7b (the J_AB2 map) and 10 (the pair reaches A\'s J_USBW)"}'),
        ('judged_by: "check_contracts.py:281-283"}', 'judged_by: "check_contracts.py section 8 (J_MEZZ1 and J_HARN1)"}'),
        ('judged_by: "check_contracts.py:236-241; block_contract.py (needs pcbnew) for E5"}',
         'judged_by: "check_contracts.py sections 4 and 5 (the dock signal and power contacts); block_contract.py (needs pcbnew) for E5"}'),
        ('judged_by: "check_contracts.py:357-380",', 'judged_by: "check_contracts.py section 15b (the pack leads)",'),
        ('judged_by: "check_contracts.py:292 (the wall pair reaches A\'s J_USBW)"',
         'judged_by: "check_contracts.py section 10 (the wall pair reaches A\'s J_USBW)"')]:
    rep(old, new)

# 6. the kit bus budget and the segment choice on IF-BC-PANEL
rep('''address 0x30: the supervisors take 0x34 to 0x36 (I3-F01, the session's choice, firmware only)"''',
    '''address 0x30: the supervisors take 0x34 to 0x36 (I3-F01, the session's choice, firmware only). Speed, pull-ups and
        the capacitance budget: v2/docs/HW-FW-CONTRACT.md section 6. Standard-mode, 100 kHz programmed (SC-HF-03); as one
        segment the bus cannot meet the 300 ns rise its BQ25731, TPS23861 and ATECC608B require (HF-F01), so the session took
        three segments behind two TCA9517A (SC-HF-02), owed on boards A and B"''')
rep('findings: [W5-F4, I3-F01, FAB-04, EMCON-L1, EMCON-L2, B_PANEL_5V]',
    'findings: [W5-F4, I3-F01, FAB-04, EMCON-L1, EMCON-L2, B_PANEL_5V, HF-F01]')

d = yaml.safe_load(s)
c = d["board_to_board"]["contracts"]
for i in new_ids + ["IF-BC-PANEL", "IF-EXT-USB", "IF-PE-PACK"]:
    assert i in c, "contract %s missing after the edit" % i
assert "(proposed)" not in s, "a (proposed) rule is left"
open(P, "w", encoding="utf-8").write(s)
print("\n".join(done))
print("board_to_board contracts: %d" % len(c))
