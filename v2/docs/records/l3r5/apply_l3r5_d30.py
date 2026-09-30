#!/usr/bin/env python3
"""Record the owner's instruction of 30 September 2026 on the Codex worker and the decision register as owner ruling D-30
(MESHSAT-1357, layer 3 round 5, the closure pass). Applied once: a second run refuses. It changes no requirement.

The instruction reached this work through the coordinating session and is filed, as quoted there, in
v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md; the quote is asserted in that file before anything is written.
That file and the registry's owner_rulings are, from this instruction on, the one decision register both agents consult
(v2/docs/CODEX-WORKER.md section 7 on main).

Usage: python3 apply_l3r5_d30.py [--check] [--registry PATH]
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "l3r2"))
import l3edit as E  # noqa: E402

INSTR = "v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md"
QUOTES = ['Upgrade the existing Codex/GPT-6-Astra integration from a limited pilot to a standing engineering collaborator. ... This authorises further bounded Astra assignments through the existing ChatGPT authentication and available subscription allowance. It replaces the exhausted pilot-call count. Preserve existing spending, sandbox and publication limits; no automatic paid-API fallback. Claude remains the coordinator and integrator. ... Both agents must consult the same authoritative decision register. Record my latest instructions there so I do not have to relay them repeatedly. ... Astra cannot change my requirements or approve its own authored work. Agreement between agents is not a substitute for calculations, sources or tests. Keep at most two active workers across Claude and Codex, with one author per worktree.']
RID = "D-30"
TITLE = "the owner's instruction on the Codex worker as a standing collaborator and on one decision register (30 September 2026)"
RULING = ("The owner's instruction of 30 September 2026, relayed by the coordinating session and quoted in " + INSTR + ", "
          "recorded in the decision register; it changes no requirement. In his words: \"" + QUOTES[0] + "\" The decision "
          "register both agents consult is that file together with this registry's owner_rulings.")
ENTRY = '''  - id: {rid}
    authority: OWNER
    ruled_on: "2026-09-30"
    title: "{title}"
    ruling: >-
{ruling}    source: ["owner ruling {rid}", "{instr}", "v2/docs/CODEX-WORKER.md section 7"]
'''


def build(raw):
    d = E.parse(raw)
    if any(r.get("title") == TITLE for r in d["owner_rulings"]): E.refuse("the instruction is already recorded: this script has run")
    if not any(r["id"] == "D-29" for r in d["owner_rulings"]): E.refuse("D-29 is not in the registry: run apply_l3r5_d28_d29.py first")
    nid = E.next_id(d, "D", ("owner_rulings",))
    if nid != RID: E.refuse("the next free owner ruling is %s, not %s: the pages cite %s" % (nid, RID, RID))
    E.assert_in(INSTR, QUOTES)
    for t in (TITLE, RULING): E.screen(t, RID)
    return E.insert_after_entry(raw, d["owner_rulings"][-1]["id"], ENTRY.format(rid=RID, title=TITLE, ruling=E.fold(RULING, 6),
                                                                                instr=INSTR), "owner_rulings")


def main(argv):
    path = argv[argv.index("--registry") + 1] if "--registry" in argv else E.REGISTRY
    old = open(path, encoding="utf-8").read()
    try:
        new = build(old)
        got = set(E.diff_entries(E.parse(old), E.parse(new)))
        if got != {("owner_rulings", RID, "added")}: E.refuse("the entries changed are not the list: %s" % sorted(got))
        errs, warns = E.validate(new)
        if errs: E.refuse("the result does not validate: %s" % "; ".join(errs[:5]))
    except E.Refused as e:
        print("apply_l3r5_d30: REFUSED: %s" % e)
        return 2
    print("owner_rulings  %s     added" % RID)
    print("apply_l3r5_d30: 1 entry, validator 0 errors, %d warnings%s" % (len(warns), " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv:
        E.commit_text(path, old, new)
        print("apply_l3r5_d30: written %s" % os.path.relpath(path, E.TOP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
