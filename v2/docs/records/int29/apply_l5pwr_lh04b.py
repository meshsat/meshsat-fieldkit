#!/usr/bin/env python3
"""apply_l5pwr_lh04b.py: Layer 5's row LH-04b restated after L4-E9's rounds 7 and 8 (MESHSAT-1357, integration set 29, 4 October
2026; the coordinator's integration correction, finding L5-F13).

What happened: L4-E9's round 7 corrected LH-04's pointer in LAYER5-HANDOVER.md (it had read rv-pwr's PS-ALLTX PLAN line, an 11.48 V
stack, as if it were decision D-11's all-transmit basis) and round 8 restated it on Layer 9's final drafts. Record l5pwr's row
LH-04b cites the two withdrawn stack voltages, so on set 29's merged tree `l5pwr_contracts.py` refused ("figures not printed by
l4e9md, hand") and its output could not be regenerated.

What this script does, with the record's own restatement mechanism (RESTATED, section 1a of its output) and nothing else:
  1. `l5pwr_contracts.py`: `restate()` takes the set a row was restated at (default set 28, finding F-12, so every existing line of
     the output and the page reads as before), the output and the page name it per row, and LH-04b is restated: its two withdrawn
     figures, why, the replacing Layer 4 texts as patterns with no typed number (their figures are parsed from the tree), the
     contract value, mark, trigger and where, and the target's state.
  2. `L5-POWER-CONTRACTS.md`: the table and the section 4a block rewritten from the script (the tests compare them), one paragraph
     under 4a, and finding L5-F13 in section 9.
The contract text itself (`pcb_interfaces.yaml`, IF-AE-DOCK `pack_pins` and IF-PE-PACK `power`, the `service` strings) is NOT
changed here: it still carries the withdrawn pointer, which is finding L5-F13 for Layer 5's next round. Changing the registry would
re-pin the Layer 4 readers after set 29's freeze.

Run from the repository root: apply_l5pwr_lh04b.py [--check | --write]. Each old text must occur exactly once; a second run
reads "already applied" and exits 3. After --write, regenerate `l5pwr_contracts.out` through `_bin/regen_out.py`."""
import ast
import importlib.util
import os
import re
import sys

SCRIPT = "v2/docs/records/l5pwr/l5pwr_contracts.py"
PAGE = "v2/docs/records/l5pwr/L5-POWER-CONTRACTS.md"


def refuse(msg):
    sys.stderr.write("apply_l5pwr_lh04b: REFUSED: %s\n" % msg)
    sys.exit(1)


def once(t, old, new, where):
    if t.count(old) != 1:
        refuse("%s: %d occurrence(s) of %r, one expected" % (where, t.count(old), old[:70]))
    if old == new:
        refuse("%s: the new text does not differ" % where)
    return t.replace(old, new)


NEW_ENTRY = '''restate("LH-04b", ["11.48", "10.42"],
        "L4-E9's round 7 corrected LH-04's pointer, which had read rv-pwr's PS-ALLTX PLAN line and not the floor's basis (decision "
        "D-11's all-transmit basis), and its round 8 restated it on Layer 9's final drafts",
        [("hand", r"decision D-11's all-transmit basis at \\d+ A from a \\d+\\.\\d+ V stack as drawn and \\d+\\.\\d+ V on the final drafts, OCD1's \\d+ A only below a \\d+\\.\\d+ V stack there"),
         ("l4e9md", r"decision D-11's all-transmit basis at \\d+ A from a \\d+\\.\\d+ V stack as drawn, \\d+\\.\\d+ V on the final drafts, needing \\d+\\.\\d+ V rest against REQ-018's \\d+\\.\\d+ V \\(D-17 OPEN")],
        "CHANGES: the pointer is no longer the PS-ALLTX PLAN line's stack voltages; it is decision D-11's all-transmit basis and OCD1's "
        "stack as parsed above, and that basis is not supplied from REQ-018's pass line (D-17 OPEN); the continuous and the peak "
        "service currents stand",
        "MODELED (L4-E9 out 30, on Layer 9's final drafts); PROVISIONAL; D-17 OPEN",
        "PWR-F12 (FEA-004): the chain's short-time rating at the peak service current and F2 near its hot corner; D-17 (L4-E9 8a): "
        "the all-transmit basis against REQ-018's pass line",
        "1d row IF-10; LH-04 as L4-E9's rounds 7 and 8 corrected it (out 30)",
        [("stale", "yaml", r"PS-ALLTX's \\d+ A at an \\d+\\.\\d+ V stack and OCD1's \\d+ A below \\d+\\.\\d+ V")],
        finding="L5-F13", at=("set 29, L5-F13", "SET 29 (L5-F13)", "L5-F13"))

'''

EDITS = [
    ("the docstring",
     "(SET28_COMMIT) to say whether record l5r2 restated them in place or a withdrawn text is still there (a finding).\"\"\"",
     "(SET28_COMMIT) to say whether record l5r2 restated them in place or a withdrawn text is still there (a finding).\n\n"
     "Set 29 (finding L5-F13, 4 October 2026, the coordinator's integration correction): L4-E9's rounds 7 and 8 corrected LH-04's pointer,\n"
     "so the two stack voltages row LH-04b cited are no longer printed. The row is restated the same way and named as restated at set 29;\n"
     "its contract text is NOT RESTATED in the targets (Layer 5's next round).\"\"\""),
    ("restate()",
     "def restate(i, withdrawn, why, now, value, mark, trigger, where, target=(), finding=None):\n"
     "    RESTATED[i] = dict(withdrawn=withdrawn, why=why, now=now, value=value, mark=mark, trigger=trigger, where=where,\n"
     "                       target=list(target), finding=finding)\n",
     "def restate(i, withdrawn, why, now, value, mark, trigger, where, target=(), finding=None,\n"
     "            at=(\"set 28, F-12\", \"SET 28 (F-12)\", \"F-12\")):\n"
     "    \"\"\"at: the set the row was restated at, as the page words it, as the output words it, and its finding.\"\"\"\n"
     "    RESTATED[i] = dict(withdrawn=withdrawn, why=why, now=now, value=value, mark=mark, trigger=trigger, where=where,\n"
     "                       target=list(target), finding=finding, at=at)\n"),
    ("the new entry",
     "# A parsed figure: a signed decimal, or an integer with its unit (a section number, a round or an id is not a figure).\n",
     NEW_ENTRY + "# A parsed figure: a signed decimal, or an integer with its unit (a section number, a round or an id is not a figure).\n"),
    ("prov",
     "prov = [(e[\"id\"], e[\"contract\"], e[\"trigger\"], bool(e[\"restated\"])) for e in results if \"PROVISIONAL\" in e[\"mark\"]]",
     "prov = [(e[\"id\"], e[\"contract\"], e[\"trigger\"], e[\"restated\"][\"at\"][2] if e[\"restated\"] else \"\") for e in results if \"PROVISIONAL\" in e[\"mark\"]]"),
    ("md_rows",
     "r[\"where\"] + \" (restated at set 28, F-12, section 4a; as written: \" + e[\"was\"][\"where\"] + \")\" if r else e[\"where\"])",
     "r[\"where\"] + \" (restated at \" + r[\"at\"][0] + \", section 4a; as written: \" + e[\"was\"][\"where\"] + \")\" if r else e[\"where\"])"),
    ("md_restated's header",
     "| why (set 27's Layer 4 change) |",
     "| why (the Layer 4 change: set 27's, or L4-E9's rounds 7 and 8 for a row restated at set 29) |"),
    ("the row's mark in section 1",
     "            p(\"      RESTATED AT SET 28 (F-12): section 1a\")\n",
     "            p(\"      RESTATED AT %s: section 1a\" % e[\"restated\"][\"at\"][1])\n"),
    ("section 1a's header",
     "    p(\"1a. RESTATED AT SET 28 (finding F-12; authority SESSION): %d rows whose cited figures set 27's Layer 4 corrections changed\" % len(rows))\n"
     "    for e in rows:\n"
     "        r = e[\"restated\"]\n"
     "        p(\"   %s | %s | %s\" % (e[\"id\"], e[\"contract\"], e[\"field\"]))\n",
     "    s28 = [e for e in rows if e[\"restated\"][\"at\"][2] == \"F-12\"]\n"
     "    p(\"1a. RESTATED AT SET 28 (finding F-12; authority SESSION): %d rows whose cited figures set 27's Layer 4 corrections changed\" % len(s28))\n"
     "    if len(rows) != len(s28):\n"
     "        p(\"    AND AT SET 29 (finding L5-F13; the coordinator's integration correction, authority SESSION): %d row whose cited figures\"\n"
     "          % (len(rows) - len(s28)))\n"
     "        p(\"    L4-E9's rounds 7 and 8 changed; it is marked 'restated at set 29' below\")\n"
     "    for e in rows:\n"
     "        r = e[\"restated\"]\n"
     "        p(\"   %s | %s | %s\" % (e[\"id\"], e[\"contract\"], e[\"field\"]))\n"
     "        if r[\"at\"][2] != \"F-12\":\n"
     "            p(\"      restated at %s\" % r[\"at\"][0])\n"),
    ("section 3's mark",
     "p(\"   %s (%s)%s: %s\" % (i, c, \" [restated, F-12]\" if rs else \"\", t))",
     "p(\"   %s (%s)%s: %s\" % (i, c, (\" [restated, %s]\" % rs) if rs else \"\", t))"),
]

PAGE_4A_OLD = "finding of section 9. The figures that no longer stand are the ones the row cited; the replacing text is quoted from the file.\n"
PAGE_4A_NEW = PAGE_4A_OLD + (
    "\n**At set 29 (finding L5-F13, the coordinator's integration correction of 4 October 2026).** Row LH-04b is restated the same way.\n"
    "L4-E9's round 7 corrected LH-04's pointer (it had read rv-pwr's PS-ALLTX PLAN line as if it were decision D-11's all-transmit\n"
    "basis) and its round 8 restated it on Layer 9's final drafts, so the two stack voltages the row cited are no longer printed by\n"
    "L4-E9's page or handover. The `service` strings of IF-AE-DOCK `pack_pins` and IF-PE-PACK `power` in `pcb_interfaces.yaml` still\n"
    "carry the withdrawn pointer: NOT RESTATED, finding L5-F13 of section 9.\n")
F13 = ("| L5-F13 | Layer 5's contract owner (its next round), the integrator | At set 29 the `service` strings of IF-AE-DOCK `pack_pins` "
       "and IF-PE-PACK `power` in `pcb_interfaces.yaml` still carry the pointer L4-E9's round 7 withdrew (the PS-ALLTX PLAN line's stack "
       "voltages, read as if they were decision D-11's all-transmit basis). L4-E9's LH-04 now gives that basis on Layer 9's final drafts, "
       "and it is not supplied from REQ-018's pass line (D-17 OPEN). Found by the coordinator at set 29's integration, when this "
       "record's script refused on the merged tree; row LH-04b is restated in section 4a and the contract text is left as written | "
       "restate both `service` strings in place from L4-E9's LH-04 (a registry change: the Layer 4 readers that pin "
       "`pcb_interfaces.yaml` re-pin in that set) |\n")


def main(argv):
    write = "--write" in argv
    if not os.path.exists(SCRIPT):
        refuse("run from the repository root")
    t = open(SCRIPT, encoding="utf-8").read()
    if 'restate("LH-04b"' in t:
        sys.stderr.write("apply_l5pwr_lh04b: already applied\n")
        return 3
    for where, old, new in EDITS:
        t = once(t, old, new, SCRIPT + ": " + where)
    ast.parse(t)
    if re.search("[–—]", t):
        refuse("a dash character would be written")
    page = open(PAGE, encoding="utf-8").read()
    page = once(page, PAGE_4A_OLD, PAGE_4A_NEW, PAGE + ": section 4a")
    rows9 = [l for l in page.split("\n") if l.startswith("| L5-F11 |")]
    if len(rows9) != 1:
        refuse("%d L5-F11 row(s) in section 9" % len(rows9))
    page = once(page, rows9[0] + "\n", rows9[0] + "\n" + F13, PAGE + ": section 9")
    if not write:
        print("apply_l5pwr_lh04b: CHECK OK, %d edit(s) of the script, the page's 4a paragraph and finding L5-F13" % len(EDITS))
        return 0
    open(SCRIPT, "w", encoding="utf-8").write(t)
    # the page's two generated blocks, from the script as now written
    sp = importlib.util.spec_from_file_location("l5pwr_contracts_patched", SCRIPT)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    R = m.compute()
    for begin, end, lines in (("<!-- l5pwr-table:begin -->", "<!-- l5pwr-table:end -->", m.md_rows(R)),
                              ("<!-- l5pwr-restated:begin -->", "<!-- l5pwr-restated:end -->", m.md_restated(R))):
        i, j = page.index(begin), page.index(end)
        page = page[:i] + begin + "\n" + "\n".join(lines) + "\n" + page[j:]
    if re.search("[–—]", page):
        refuse("the page would carry a dash character")
    open(PAGE, "w", encoding="utf-8").write(page)
    lh = [e for e in R["rows"] if e["id"] == "LH-04b"][0]["restated"]
    print("apply_l5pwr_lh04b: WRITTEN. LH-04b %s; parsed: %s" % (lh["state"], "; ".join(c["text"] for c in lh["cites"])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
