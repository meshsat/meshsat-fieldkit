#!/usr/bin/env python3
"""r8int6 (the integrator of set 6 of the handover, 27 September 2026): writes apply_registry_r8int6.py,
patch_coverage_r8int6.py and patch_test_plan_r8int6.py beside stream w4dp's drafts, by asserted text replacement, so the
filed copies are whole scripts. Why each change:

apply_registry_r8int6.py
  - TEST-PLAN.md moved on main after 91894cd7 (fnd/rel2), so the pair TP_OLD/TP_NEW is read at run time (HEAD's file and
    the patched file) and DIFF_TP's line arithmetic is computed from the two files, where the stream typed 91894cd7's.
  - The stream wrote placeholders (SC-a, SC-b, SC-c, S-x) into some texts; they are replaced by the ids taken, and every
    `drafts/w4dp/` path by the filed record's path (the independent check, w4dp check 2, an AI check).
  - S-76: stream w4ae, which lands ahead of this one in the same integration, answered board E's half (FAN1_SW and
    FAN2_SW) and this stream answers board D's (D2, RLY_K), so S-76 is closed here by the D2 choice with both halves
    named, where the stream recorded board D's half and left the item open for board E.
  - REQ-044's and REQ-046's source lines: the registry reads a `source` file:line at the commit `sources_read_at` names
    unless the entry says otherwise, so the stream's renumbering in place would make the old citations point at other
    text there; the old citations are kept and the new lines are added naming the file they were read on.
  - It writes the ids it took to ids.json beside itself.
patch_coverage_r8int6.py
  - BAT-001's remediation names the open item by the id taken; PWR-001's note says board E's two nets are declared by
    stream w4ae in the same integration (S-76 closed), where it said they stay UNDECIDED.
patch_test_plan_r8int6.py
  - row 10 gains the level check the independent check asked for (TP11 = COUT x 51/71 with JP1 open, so 4.3 to 5.46 V
    reads COUT between 6 and 7.6 V, the basis of FUSE_G's and FUSE_GQ's declared bounds).
Usage: derive_w4dp_r8int6.py <kit dir>"""
import os, sys

K = sys.argv[1]


def derive(src, dst, swaps, head, tail=""):
    s = open(os.path.join(K, src), encoding="utf-8").read()
    for old, new in swaps:
        assert s.count(old) == 1, "%s: %d of %r" % (src, s.count(old), old[:90])
        s = s.replace(old, new)
    first = s.index('"""')
    s = s[:first + 3] + head + "\n\n" + s[first + 3:] + tail
    compile(s, dst, "exec")
    open(os.path.join(K, dst), "w", encoding="utf-8").write(s)
    print("wrote", dst)


derive("apply_registry.py", "apply_registry_r8int6.py", [
    ('TP_OLD, TP_NEW = "701c1020053e7903", "5ccadd6607a87df4"      # main\'s, and main\'s with drafts/w4dp/patch_test_plan.py applied\n'
     'tp_patched = sha16(TEST_PLAN) == TP_NEW\n'
     'if not tp_patched and sha16(TEST_PLAN) != TP_OLD:\n',
     '# r8int6: the pair is read at run time, HEAD\'s file and the patched one (TEST-PLAN.md moved on main after 91894cd7)\n'
     'import subprocess, difflib\n'
     '_TP_HEAD = subprocess.run(["git", "-C", ROOT, "show", "HEAD:" + TEST_PLAN], capture_output=True, text=True, check=True).stdout\n'
     'TP_OLD, TP_NEW = hashlib.sha256(_TP_HEAD.encode("utf-8")).hexdigest()[:16], sha16(TEST_PLAN)\n'
     'tp_patched = TP_NEW != TP_OLD and "second level cell over voltage" in open(os.path.join(ROOT, TEST_PLAN), encoding="utf-8").read()\n'
     'if not tp_patched and sha16(TEST_PLAN) != TP_OLD:\n'),
    ('DIFF_TP = ("TEST-PLAN.md changed by drafts/w4dp/patch_test_plan.py only in section 5: rows 10 to 14 after row 9 and its "\n'
     '           "closing paragraph\'s first two sentences and one clause restated; lines 1 to 81 are byte-identical and every "\n'
     '           "later line moves down by 10 with its text unchanged")',
     '_a = _TP_HEAD.split("\\n"); _b = open(os.path.join(ROOT, TEST_PLAN), encoding="utf-8").read().split("\\n")\n'
     '_ops = [o for o in difflib.SequenceMatcher(None, _a, _b, autojunk=False).get_opcodes() if o[0] != "equal"]\n'
     '_last = _ops[-1]\n'
     'DIFF_TP = ("TEST-PLAN.md changed by v2/docs/records/w4dp/patch_test_plan_r8int6.py only in section 5: rows 10 to 14 "\n'
     '           "after row 9 and its closing paragraph\'s first two sentences and one clause restated; lines 1 to %d are "\n'
     '           "byte-identical and every line after the file\'s line %d moves down by %d with its text unchanged"\n'
     '           % (_ops[0][1], _last[2], len(_b) - len(_a)))'),
    ('old76 = ("      sheet in v2/vendor. Open until the sheets are filed (and D2 has an order code, EQ-21\'s class) and the\\n"\n'
     '         "      three nets are declared nodes at the rail plus the maker\'s forward drop.\\n")\n'
     'once(old76)\n',
     '# r8int6: S-76 is closed here, both halves answered (board E by stream w4ae, board D by this stream)\n'
     'import re as _re\n'
     '_m76 = _re.search(r"(?ms)^  - id: S-76\\n    class: SESSION\\n    status: OPEN\\n    title: >-\\n(.*?)(?=^  - id: |^\\n# )", s)\n'
     'if not _m76: raise SystemExit("apply_registry: S-76 is not an OPEN SESSION item")\n'
     '_t76 = _m76.group(1)\n'
     'assert "Board E\'s half answered by" in " ".join(_t76.split()), "apply stream w4ae first: S-76 does not name board E\'s half"\n'
     's = s[:_m76.start()] + s[_m76.end():]\n'
     'old76 = None\n'),
    ('s = s.replace(old76, old76 + fold(add76, 6) + "\\n", 1)\n',
     'closed76 = ("  - id: S-76\\n    closed_by: %s\\n" % SCA\n'
     '            + block("closing_evidence",\n'
     '                    "Both halves answered on 27 September 2026, integrated together at r8int6. Board E: stream w4ae (" + _re.search(r"Board E\'s half answered by (SC-\\d+)", " ".join(_t76.split())).group(1) + ") filed D7 and D8\'s sheet with their "\n'
     '                    "code C51897884 and declared FAN1_SW and FAN2_SW nodes at 17.35 V. Board D: " + add76.replace("Progress, 27 September 2026 (stream w4dp): board D\'s half is done. ", "stream w4dp: ").split(" Still open:")[0])\n'
     '            + "    title: >-\\n" + _t76)\n'
     'anchor = "\\nrecords:\\n"\n'
     'once(anchor); s = s.replace(anchor, closed76 + anchor, 1)\n'),
    ('edit_record("REQ-044", [("    waits_on: [S-45, L-03]\\n", "    waits_on: [%s, L-03]\\n" % SX),\n'
     '                        (\'      - "v2/ecad/tools/pcb_pack_protection.yaml:17-40"\\n\',\n'
     '                         \'      - "v2/ecad/tools/pcb_pack_protection.yaml:17-67"\\n\')]\n'
     '            + ([(\'      - "v2/docs/TEST-PLAN.md:58-94"\\n\', \'      - "v2/docs/TEST-PLAN.md:58-104"\\n\')] if tp_patched else []))',
     '# r8int6: a source file:line is read at sources_read_at unless the entry says otherwise: the old citations stay and\n'
     '# the new lines are added, each naming the file it was read on\n'
     'edit_record("REQ-044", [("    waits_on: [S-45, L-03]\\n", "    waits_on: [%s, L-03]\\n" % SX),\n'
     '                        (\'      - "v2/ecad/tools/pcb_pack_protection.yaml:17-40"\\n\',\n'
     '                         \'      - "v2/ecad/tools/pcb_pack_protection.yaml:17-40"\\n\'\n'
     '                         \'      - "v2/ecad/tools/pcb_pack_protection.yaml:17-67 (the table as stream w4dp wrote it, 27 September 2026, not at sources_read_at)"\\n\')]\n'
     '            + ([(\'      - "v2/docs/TEST-PLAN.md:58-94"\\n\', \'      - "v2/docs/TEST-PLAN.md:58-94"\\n\'\n'
     '                 \'      - "v2/docs/TEST-PLAN.md:58-104 (section 5 with rows 10 to 14 as stream w4dp added them, not at sources_read_at)"\\n\')] if tp_patched else []))'),
    ('edit_record("REQ-046", [(\'"v2/ecad/tools/pcb_pack_protection.yaml:142-157 (CHARGE_ and DISCHARGE_TEMPERATURE_WINDOW)"\',\n'
     '                         \'"v2/ecad/tools/pcb_pack_protection.yaml:215-231 (CHARGE_ and DISCHARGE_TEMPERATURE_WINDOW)"\')])',
     'edit_record("REQ-046", [(\'      - "v2/ecad/tools/pcb_pack_protection.yaml:142-157 (CHARGE_ and DISCHARGE_TEMPERATURE_WINDOW)"\\n\',\n'
     '                         \'      - "v2/ecad/tools/pcb_pack_protection.yaml:142-157 (CHARGE_ and DISCHARGE_TEMPERATURE_WINDOW)"\\n\'\n'
     '                         \'      - "v2/ecad/tools/pcb_pack_protection.yaml:215-231 (CHARGE_ and DISCHARGE_TEMPERATURE_WINDOW, the table as stream w4dp wrote it, not at sources_read_at)"\\n\')])'),
    ('assert s != orig\nopen(REG, "w", encoding="utf-8").write(s)\n',
     'assert s != orig\n'
     '# r8int6: the placeholders the stream left in its texts, and its draft paths\n'
     'import re as _re2, json as _json\n'
     'assert not _re2.search(r"\\bSC-[abc]\\b|\\bS-[xy]\\b", orig), "the registry already holds a placeholder"\n'
     'for _ph, _id in (("SC-a", SCA), ("SC-b", SCB), ("SC-c", SCC), ("S-x", SX), ("S-y", SY)):\n'
     '    s = _re2.sub(r"\\b%s\\b" % _re2.escape(_ph), _id, s)\n'
     's = s.replace("drafts/w4dp/", "v2/docs/records/w4dp/")\n'
     'import yaml as _yaml; _yaml.safe_load(s)\n'
     'open(REG, "w", encoding="utf-8").write(s)\n'
     '_json.dump({"SC_D2": SCA, "SC_PWR_DP": SCB, "SC_BAT001": SCC, "S_BAT001_HW": SX, "S_BAT001_DOCS": SY},\n'
     '           open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ids.json"), "w"), indent=1)\n'),
    ('        line = ("re-read at the w4dp regeneration of 27 September 2026 (boards D and P and the pack-protection table, "\n',
     '        # r8int6: an evidence entry of a rebind starts with the path it rebinds (the integration recipe)\n'
     '        line = (" and ".join(sorted({x.split("@")[0] for x in touched})) + " re-read at the w4dp regeneration of 27 "\n'
     '                "September 2026 (boards D and P and the pack-protection table, "\n'),
], "r8int6 re-derivation of stream w4dp's apply_registry.py (beside it in this folder), written by derive_w4dp_r8int6.py: "
   "TEST-PLAN.md's pair and line arithmetic read at run time, the placeholders and draft paths replaced, S-76 closed with "
   "both halves answered, REQ-044's and REQ-046's new lines added beside the old citations, each rebind's evidence entry "
   "starting with the path it rebinds, the ids written to ids.json. "
   "The stream's text follows.")

derive("patch_coverage.py", "patch_coverage_r8int6.py", [
    ('import os, sys\n', 'import json, os, sys\n'),
    ('"remains is the three hardware functions that miss the cell maker\'s limits (the open item drafts/w4dp/apply_registry.py "\n'
     '  "calls S-x: a custom',
     '"remains is the three hardware functions that miss the cell maker\'s limits (open item " + _SX + ": a custom'),
    ('"of 11 (10 declared rails, 7 declared nodes, 0 undecided). Board E\'s FAN1_SW and FAN2_SW stay UNDECIDED (S-76).\\"}"),',
     '"of 11 (10 declared rails, 7 declared nodes, 0 undecided). Board E\'s FAN1_SW and FAN2_SW are declared by stream w4ae "\n'
     '  "in the same integration, which closes S-76.\\"}"),'),
    ('EDITS = [\n',
     '_SX = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ids.json")))["S_BAT001_HW"]   # r8int6\n'
     'EDITS = [\n'),
], "r8int6 re-derivation of stream w4dp's patch_coverage.py, written by derive_w4dp_r8int6.py: the open item named by the "
   "id taken (ids.json beside it, written by apply_registry_r8int6.py) and board E's two nets said declared by stream w4ae. "
   "Run after apply_registry_r8int6.py. The stream's text follows.")

derive("patch_test_plan.py", "patch_test_plan_r8int6.py", [
    ('"COUT through R29) goes high with that cell between 4.305 and 4.345 V at room temperature, 0.85 to 1.15 s after the "',
     '"COUT through R29) goes high, to between about 4.3 and 5.46 V (TP11 = COUT x 51/71 with JP1 open, so COUT reads between "\n'
     '    "6 and 7.6 V, the basis of FUSE_G\'s and FUSE_GQ\'s declared bounds; a higher reading reopens them), with that cell "\n'
     '    "between 4.305 and 4.345 V at room temperature, 0.85 to 1.15 s after the "'),
], "r8int6 re-derivation of stream w4dp's patch_test_plan.py, written by derive_w4dp_r8int6.py: row 10 checks the level "
   "COUT reaches, as the independent check asked, so the inference behind FUSE_G's and FUSE_GQ's bounds has an allocated "
   "prototype test. The stream's text follows.")
