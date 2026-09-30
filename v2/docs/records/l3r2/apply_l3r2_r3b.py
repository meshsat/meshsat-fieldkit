#!/usr/bin/env python3
"""The session's closures of L3-R2's round 3b (MESHSAT-1357, 30 September 2026), on CHECK-2 of L3-R2 minors 4 and 8.
Applied once: a second run refuses.

  1. REQ-072 gains a qualifying evidence entry (minor 4). Its s119 entry, which stays as written (history is not edited),
     names two of the model's cases "typical" and "adverse". The new entry says what they are, in the words of the
     records read: model results on the September reference day (a1int RECONCILE.md), and the second renamed WAB by the
     energy basis, which the filed check of that basis reads as "a build case on the same mean day, not weather". Neither
     word names a weather condition. Its bindings gain the two files read.
  2. REQ-054's acceptance names the unit of the antenna's gain (minor 8). The limits of its source (appendix item 4) are
     ERP, which is referenced to a half-wave dipole, so the gain applied is in dBd (a gain in dBi less 2.15 dB). No limit is
     added or removed; the old text is kept in `history`.
Every document sentence is asserted in its file first; the result validates (0 errors) or nothing is written.

Usage: python3 apply_l3r2_r3b.py [--check] [--registry PATH]
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import l3edit as E  # noqa: E402

CHK1 = "v2/docs/records/l3r2/checks/energy-basis-check-1/CHECK-1.md"
RECON = "v2/docs/records/a1int/RECONCILE.md"
ASSERT = {
    CHK1: ["only as an explained rename", "WAB is defined as a build case on the same mean day, not weather"],
    RECON: ["Model results on the September reference day", "(typical and adverse;"],
    "v2/docs/MESHSAT-709-geometry-appendix.md": ["EU power capped in software (14 dBm ERP, 27 dBm on the 869.4 to 869.65 MHz sub-band at 10 percent duty)"],
}
MARK = "the words 'typical' and 'adverse' in the s119 entry above"
REQ072_ENTRY = (
    CHK1 + " and " + RECON + " read on 30 September 2026 (L3-R2, round 3b, CHECK-2 of L3-R2 minor 4): " + MARK + " name "
    "two of the model's cases, whose results are model results on the September reference day (" + RECON + "), not "
    "weather conditions. The energy basis renames the second WAB, which the filed check of that basis reads as a build "
    "case on the same mean day, not weather (" + CHK1 + ", its 'explained rename'). No weather worse than SC-37's mean "
    "day is modelled in that entry, and its figures stay the model's on the 20.7 V bus (the entry after it). This entry "
    "changes no result, statement or acceptance: the verdict stays FAIL.")
OLD_054 = ("Configuration review: meshtasticd's region, channel, transmit power and duty-cycle settings, with the antenna "
           "gain applied, give at most 14 dBm ERP on every configured channel outside 869.4 to 869.65 MHz, and at most 27 "
           "dBm ERP at a duty cycle of at most 10 % on a channel inside 869.4 to 869.65 MHz. Prototype: the conducted "
           "output measured at each configured channel, plus the antenna's gain, is at or under the limit of the band the "
           "channel is in, and the duty cycle measured on 869.4 to 869.65 MHz is at most 10 %.")
NEW_054 = ("Configuration review: meshtasticd's region, channel, transmit power and duty-cycle settings, with the antenna's "
           "gain in dBd applied (the limits are ERP, referenced to a half-wave dipole: a gain in dBi less 2.15 dB), give at "
           "most 14 dBm ERP on every configured channel outside 869.4 to 869.65 MHz, and at most 27 dBm ERP at a duty cycle "
           "of at most 10 % on a channel inside 869.4 to 869.65 MHz. Prototype: the conducted output measured at each "
           "configured channel, plus the antenna's gain in dBd, is at or under the limit of the band the channel is in, and "
           "the duty cycle measured on 869.4 to 869.65 MHz is at most 10 %.")
HIST_054 = ("Acceptance restated on 30 September 2026 (L3-R2 round 3b, v2/docs/records/l3r2/apply_l3r2_r3b.py, CHECK-2 of "
            "L3-R2 minor 8): the antenna's gain is named in dBd, the unit ERP is referenced to, with no limit added or "
            "removed. It read: '" + OLD_054 + "'")


def build(raw):
    d = E.parse(raw)
    recs = {r["id"]: r for r in d["records"]}
    if any(MARK in " ".join(str(e).split()) for e in recs["REQ-072"].get("evidence") or []):
        E.refuse("REQ-072 already carries the qualifying entry: this script has run")
    if " ".join(str(recs["REQ-054"]["acceptance"]).split()) != OLD_054: E.refuse("REQ-054's acceptance is not the text restated")
    for rel, n in ASSERT.items(): E.assert_in(rel, n)
    for t in (REQ072_ENTRY, NEW_054, HIST_054): E.screen(t, "an added text")
    binds = ['"%s@%s"' % (p, E.sha16(os.path.join(E.TOP, p))) for p in (CHK1, RECON)]
    def f072(b):
        b = E.add_list_entry(b, "evidence", REQ072_ENTRY)
        lines, a, z = E._field_lines(b, "evidence_bound_to")
        cur = [l.strip()[2:].strip() for l in lines[a + 1:z]]
        return "\n".join(lines[:a] + ["    evidence_bound_to:"] + ["      - %s" % x for x in cur + [x for x in binds if x not in cur]] + lines[z:])
    raw = E.replace_entry(raw, "REQ-072", f072, "records")
    raw = E.replace_entry(raw, "REQ-054", lambda b: E.append_folded(E.set_folded(b, "acceptance", NEW_054), "history",
                                                                    HIST_054), "records")
    return raw


def main(argv):
    path = argv[argv.index("--registry") + 1] if "--registry" in argv else E.REGISTRY
    old = open(path, encoding="utf-8").read()
    try:
        new = build(old)
        before, after = E.parse(old), E.parse(new)
        got = set(E.diff_entries(before, after))
        want = {("records", "REQ-072", "changed"), ("records", "REQ-054", "changed")}
        if got != want: E.refuse("the entries changed are not the list: %s" % sorted(got))
        if set(E.changed_fields(before, after, "records", "REQ-072")) != {"evidence", "evidence_bound_to"}:
            E.refuse("REQ-072 changed beyond its evidence and bindings")
        if set(E.changed_fields(before, after, "records", "REQ-054")) != {"acceptance", "history"}:
            E.refuse("REQ-054 changed beyond its acceptance and history")
        errs, warns = E.validate(new)
        if errs: E.refuse("the result does not validate: %s" % "; ".join(errs[:5]))
    except E.Refused as e:
        print("apply_l3r2_r3b: REFUSED: %s" % e)
        return 2
    for sec, eid, kind in sorted(got):
        print("%-14s %-8s %s %s" % (sec, eid, kind, ",".join(E.changed_fields(before, after, sec, eid))))
    print("apply_l3r2_r3b: 2 entries, validator 0 errors, %d warnings%s" % (len(warns), " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv:
        E.commit_text(path, old, new)
        print("apply_l3r2_r3b: written %s" % os.path.relpath(path, E.TOP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
