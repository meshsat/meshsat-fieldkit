#!/usr/bin/env python3
"""LAYER-STATUS.md's layer 3 after the independent review the owner relayed on 1 October 2026 (MESHSAT-1357; the layer 3
amendment, v2/docs/records/l3am/). The layer reads "Layer 3 accepted baseline; independent review findings open (L3-R01 to
L3-R05)" until the baseline is accepted again at the amendment's revision; that wording is kept apart from "design
compliance verified" and "fab-ready", neither of which holds. The acceptance at `b4b199d0` carries no content manifest,
so since the binding of L3-R04 it binds no content and the status level reads "requirements drafted / decisions recorded"
(the renderer's live gate and level on REQUIREMENTS-L3-R2.md section 2 are the current ones). The solar-assisted figures
the section states (the closure paragraph's stop hour and finding F-01's results) are labelled with the case they were
computed with (L3-R01). Each replaced text is located by its own words and asserted to occur once; nothing else changes.
It refuses unless l3r2.yaml's `review_findings` is filed, and a second run is refused. No dash is written.

Usage: python3 v2/docs/records/l3am/apply_layer_status_l3am.py [--check] [--page PATH]   (--page: a copy, for the tests)"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import l3amlib as L  # noqa: E402

PAGE = os.path.join(L.TOP, "v2/docs/handover/LAYER-STATUS.md")
STATUS = "Layer 3 accepted baseline; independent review findings open (L3-R01 to L3-R05)"
LABEL = ("historical results of proposal P-03's array, 400 Wp in 2S2P into a 200 W stage window, which retained REQ-016 "
         "(D-34) does not admit, the unserved energy understated; the retained window's result awaits layer 4 task L4-E2, "
         "L3-R01")
EDITS = [
    ("**Now (30 September 2026): COMPLETE, the requirements baseline validated and accepted at `b4b199d0` (`baseline_acceptance` "
     "in `handover/layer3/l3r2.yaml`, authorised by D-39 once the gates passed).** Before that it was IN_PROGRESS, reopened "
     "for the current target configuration (L3-R2).",
     "**Now (1 October 2026): %s.** The requirements baseline was accepted at `b4b199d0` (`baseline_acceptance` in "
     "`handover/layer3/l3r2.yaml`, authorised by D-39 once the gates passed, recorded at `b45d1705`; the layer read COMPLETE "
     "on 30 September 2026). The independent review the owner relayed on 1 October 2026 "
     "(`v2/docs/records/l3am/REVIEW-AS-RECEIVED.md`) found five items, answered by the layer 3 amendment "
     "(`v2/docs/records/l3am/DISPOSITIONS.md`): the solar-assisted figures labelled with the case they were computed with "
     "(L3-R01), REQ-042's acceptance an end-to-end verification (L3-R02), the review export (L3-R03, the coordinator's), "
     "the acceptance bound to the reviewed content (L3-R04) and REQ-016's protection wording (L3-R05). The amendment changes "
     "the requirements registry, and the acceptance at `b4b199d0` carries no content manifest, so it binds no content: the "
     "tree reads \"requirements drafted / decisions recorded\" until the baseline is accepted again at the amendment's "
     "revision, after the amendment's check and the gates pass (D-39 remains the owner's conditional authorisation; the "
     "coordinator runs `apply_l3r5_accept.py --supersede`, the record at `b4b199d0` kept as history). Neither \"design "
     "compliance verified\" nor \"fab-ready\" holds. Before the acceptance it was IN_PROGRESS, reopened for the current "
     "target configuration (L3-R2)." % STATUS),
    ("\"Requirements baseline validated and accepted\" holds: every gate condition is MET and the acceptance is filed "
     "against the verified revision `b4b199d0` after its clean-clone check and box suite passed (`baseline_acceptance`; D-39 is "
     "the owner's conditional authorisation, not itself evidence that a gate passed); the re-issue is authorised "
     "(L3-C26) and its re-stamp is L3-C63.",
     "\"Requirements baseline validated and accepted\" held at `b4b199d0` (every gate condition MET and the acceptance filed "
     "against that verified revision after its clean-clone check and box suite passed; D-39 is the owner's conditional "
     "authorisation, not itself evidence that a gate passed) and does not hold for the amended registry: since the binding "
     "of 1 October 2026 (L3-R04) an acceptance holds only while its revision is a commit holding the content its manifest "
     "names and the tree still holds it, and the record at `b4b199d0` names none; the level reads \"requirements drafted / "
     "decisions recorded\" until the acceptance at the amendment's revision. The re-issue is authorised (L3-C26) and its "
     "re-stamp is L3-C63."),
    ("The requirements baseline: validated and accepted at `b4b199d0`.",
     "The requirements baseline: accepted at `b4b199d0`; %s, the amended registry accepted again only after the "
     "amendment's check and the gates." % STATUS),
    ("the studied in-case store stops the kit at 05 UTC of the first night (11 to 23 hours), as drawn and on the "
     "hypothetical corrected path alike, and D-06's pack alone",
     "the studied in-case store stops the kit at 05 UTC of the first night (11 to 23 hours), as drawn and on the "
     "hypothetical corrected path alike (%s), and D-06's pack alone" % LABEL),
    ("No figure is demonstrated capability.\n\n**Whose each remaining item is.**",
     "No figure is demonstrated capability. Every solar-assisted result of this finding was computed with proposal P-03's "
     "array (400 Wp in 2S2P into a 200 W stage window), which retained REQ-016 (D-34) does not admit, the unserved energy "
     "understated (L3-R01; `REQUIREMENTS-L3-R2.md` section 2.3 states the case).\n\n**Whose each remaining item is.**"),
]


def build(old):
    if STATUS in old: L.refuse("the page already reads %r: this script has run" % STATUS)
    d = L.E.parse(open(L.DATA, encoding="utf-8").read())
    rf = d.get("review_findings") or {}
    if rf.get("status") != STATUS: L.refuse("l3r2.yaml's review_findings is not filed with the status %r" % STATUS)
    sec_a = old.index("## Layer 3. Requirements\n"); sec_b = old.index("\n### History: layer 3 at H2 and H3", sec_a)
    new = old
    for a, b in EDITS:
        if old[sec_a:sec_b].count(a) != 1: L.refuse("%d occurrences in layer 3's section of %r, one expected" % (old[sec_a:sec_b].count(a), a[:70]))
        new = L.once(new, a, b, "LAYER-STATUS.md")
        L.screen(b, "LAYER-STATUS.md")
    na = new.index("## Layer 3. Requirements\n"); nb = new.index("\n### History: layer 3 at H2 and H3", na)
    if old[:sec_a] != new[:na] or old[sec_b:] != new[nb:]: L.refuse("the page changed outside layer 3's section")
    for c in ("\u2013", "\u2014"):
        if c in new and c not in old: L.refuse("a dash character was written")
    return new


def main(argv):
    path = argv[argv.index("--page") + 1] if "--page" in argv else PAGE
    old = open(path, encoding="utf-8").read()
    try:
        new = build(old)
    except L.Refused as e:
        print("apply_layer_status_l3am: REFUSED: %s" % e); return 2
    print("apply_layer_status_l3am: layer 3 reads %r; the status level and the completion status restated; the solar "
          "figures labelled%s" % (STATUS, " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv: L.write(path, old, new)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
