#!/usr/bin/env python3
"""The adopted envelope as data, and the pin that keeps it honest (rule ENV-001, 21 September 2026).

Decision 34 adopted `v2/docs/OPERATING-ENVELOPE.md` section 4 and section 6's first row. Four rules resolve
against that envelope (CMP-001, THM-001, ISO-001, REL-001) and until today each would have had to read prose,
so `tools/pcb_envelope.yaml` carries the same numbers in a form a rule can use.

The danger of a second copy is that it drifts from the record, and drift here is invisible: a rule would keep
passing against a number nobody adopted. Two rules stop that, and they are the fixtures of this file:

  * EVERY NUMBER IN THE FILE APPEARS IN THE DOCUMENT, with its sign. The defective fixtures are a copy with an
    ambient limit the record does not carry, and one with a storage margin whose sign-less digits happen to be
    in the text; both must be refused.
  * THE DOCUMENT IS PINNED BY CONTENT, with the same sha256 the coverage map pins for ENV-001. An edit to the
    record takes this file's authority away until someone re-reads it and re-pins it, which is exactly what
    the coverage map says about the record itself.
"""
import os, re, sys, hashlib, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
ECAD = os.path.dirname(TOOLS)
DOC = os.path.join(os.path.dirname(ECAD), "docs", "OPERATING-ENVELOPE.md")
SPEC = os.path.join(TOOLS, "pcb_envelope.yaml")


def _load(path=None):
    import yaml
    return yaml.safe_load(open(path or SPEC, encoding="utf-8"))


def _numbers(d):
    """(label, value) for every number this file claims the document states."""
    a = d["ambient_c"]
    out = [("ambient in use min", a["in_use"]["min"]), ("ambient in use max", a["in_use"]["max"]),
           ("storage 3 months min", a["storage_3_months"]["min"]), ("storage 3 months max", a["storage_3_months"]["max"]),
           ("storage 1 year min", a["storage_1_year"]["min"]), ("storage 1 year max", a["storage_1_year"]["max"]),
           ("esd contact kV", d["transient"]["esd"]["contact_kv"]),
           ("esd air kV", d["transient"]["esd"]["air_kv"]),
           ("esd level", d["transient"]["esd"]["level"]),
           ("one module rise K", d["inside_air_rise_k"]["one_module_lid_open"]),
           ("three modules rise K", d["inside_air_rise_k"]["three_modules_loaded_lid_open"])]
    for co in a["carve_outs"]:
        for k in ("below_c", "above_c"):
            if k in co: out.append(("carve-out %s" % k, co[k]))
    # THE OWNER'S RULINGS OF 25 AND 26 SEPTEMBER 2026 ARE NUMBERS IN THIS FILE TOO (the document's section 8), so
    # the rule that every number here appears in the record has to see them, or they are the one drift it misses.
    # EVERY numeric leaf of the block is read, not a list of known keys: a number added under a key this helper
    # has never heard of (a g-level under the severities, say) is held to the record like the rest.
    out += _leaves("owner_rulings", d.get("owner_rulings") or {})
    return out


def _leaves(label, node):
    """(label, value) for every number under a node. A YAML boolean is an int in Python and is not a number the
    document states, so it is left out; a string is prose and is judged by the document's own reader."""
    if isinstance(node, bool): return []
    if isinstance(node, (int, float)): return [(label, node)]
    if isinstance(node, dict):
        return [x for k, v in sorted(node.items()) for x in _leaves("%s.%s" % (label, k), v)]
    if isinstance(node, list):
        return [x for i, v in enumerate(node) for x in _leaves("%s[%d]" % (label, i), v)]
    return []


def _in_document(value, text):
    """Does the document state this number, with its sign?

    A NEGATIVE NUMBER MUST CARRY ITS SIGN (26 September 2026). This helper used to accept a negative value's
    absolute form anywhere in the text, so -33 C was "stated" by any 33 and a mutation to -34 passed on the
    words "decision 34" (the challenger of round 3 showed both). The record writes every negative temperature
    with a hyphen-minus; a true minus sign and the word are accepted as the same thing. A value that is not a
    whole number is looked for as written, never truncated, so 7.7 is not found in a 7."""
    if isinstance(value, float) and not value.is_integer():
        forms = {("%g" % value)}
        if value < 0: forms = {"-%g" % -value, "\u2212%g" % -value, "minus %g" % -value}
    else:
        v = int(value)
        forms = {"-%d" % -v, "\u2212%d" % -v, "minus %d" % -v} if v < 0 else {"%d" % v, "+%d" % v}
    # Nor is a number glued to a letter a statement of it: "samsung-35e" in a file name is not -35 C.
    return any(re.search(r"(?<![\d.])%s(?![\d.A-Za-z])" % re.escape(f), text) for f in forms)


def t_every_number_in_the_envelope_file_appears_in_the_adopted_document():
    """The acceptable fixture is the real file against the real record."""
    d = _load()
    text = open(DOC, encoding="utf-8").read()
    bad = [lbl for lbl, v in _numbers(d) if not _in_document(v, text)]
    assert not bad, "the envelope file states numbers the record does not: %s" % bad


def t_a_number_the_record_does_not_carry_is_refused():
    """The defective fixture: an ambient limit nobody adopted.

    THE SENTINEL IS CHOSEN, NOT TYPED (26 September 2026). It was 71, "a number the document does not contain
    anywhere", until the owner ruled TEST-PLAN's +71 C storage level a qualification margin and the document
    began to quote it: the fixture's premise became false while its assertion kept its old meaning. The value
    is now the first one the document does not state, and the fixture checks that premise before relying on it."""
    import yaml
    d = _load()
    text = open(DOC, encoding="utf-8").read()
    absent = next(v for v in range(41, 200) if not _in_document(v, text))
    assert not _in_document(absent, text), "the fixture's own premise does not hold"
    d["ambient_c"]["in_use"]["max"] = absent      # a number the document does not contain anywhere
    t = tempfile.mkdtemp(prefix="env-")
    p = os.path.join(t, "pcb_envelope.yaml")
    with open(p, "w") as fh: yaml.safe_dump(d, fh)
    bad = [lbl for lbl, v in _numbers(_load(p)) if not _in_document(v, text)]
    assert bad, "an ambient maximum of %d C, which the record never states, was accepted" % absent


def t_the_document_is_pinned_by_content_and_the_pin_matches_the_coverage_map():
    """A second copy of a decision is only as good as its pin. This is the same sha256 ENV-001 carries, so a
    change to the record breaks BOTH in the same commit rather than leaving one of them quietly stale."""
    d = _load()
    have = hashlib.sha256(open(DOC, "rb").read()).hexdigest()
    assert d["document_sha256"] == have, \
        "the envelope file is pinned to a document that has changed: re-read it and re-pin (pinned %s, is %s)" \
        % (d["document_sha256"][:16], have[:16])
    cov = open(os.path.join(TOOLS, "pcb_rules_coverage.yaml"), encoding="utf-8").read()
    i = cov.index("ENV-001:")
    assert have in cov[i:i + 3000], "ENV-001's own pin in the coverage map names a different document"


# Keys that would carry a number the record does not give. The service life is TBD for prototype 1; the
# severities were ruled BY NAME (TEST-PLAN.md E1 and E2), so a g-level, a PSD or a drop count typed as a number
# here would be the file inventing what the owner ruled as a test. Round 3 had dropped the two severity words
# and an invented `vibration_g: 7.7` then passed every test in this file (found by its challenger).
_INVENTED = ("service_life", "vibration_g", "vibration_grms", "shock_g")


def _open_items_problems(d):
    bad = []
    if not set(d.get("open_in_the_document") or []) >= {"service life"}:
        bad.append("the service life is no longer listed as open: %s" % d.get("open_in_the_document"))
    flat = str(d)
    bad += ["the envelope file invents %s, which the record does not give as a number" % w
            for w in _INVENTED if w in flat]
    sev = (d.get("owner_rulings") or {}).get("severities") or {}
    bad += ["the severities were ruled by name and %s carries a number (%r)" % (lbl, v)
            for lbl, v in _leaves("severities", sev)]
    return bad


def t_what_the_record_leaves_open_is_not_invented_here():
    """The document leaves the service life open (TBD for prototype 1), and says so: a rule that needs it must
    not find a number here instead. The severities are ruled, but BY NAME, so they must not find a number here
    either. Until 26 September 2026 this also held the altitude open; the owner ruled it that day with numbers
    (the document's section 8), so the altitude is held to the record by the first rule of this file."""
    d = _load()
    bad = _open_items_problems(d)
    assert not bad, "; ".join(bad)
    assert d["transient"]["eft"]["adopted"] is False, "the electrical fast transient row has no authority and is not adopted"


def t_an_invented_severity_number_is_refused():
    """The defective fixture for the rule above: the copy the round-3 challenger built, a vibration g-level and a
    shock g-level added under the owner's severities. Both must be refused, by name and as numbers."""
    d = _load()
    d["owner_rulings"]["severities"]["vibration_g"] = 7.7
    d["owner_rulings"]["severities"]["shock_g"] = 75
    bad = _open_items_problems(d)
    assert any("vibration_g" in b for b in bad) and any("shock_g" in b for b in bad), bad
    assert any("carries a number" in b for b in bad), bad
    text = open(DOC, encoding="utf-8").read()
    assert not _in_document(7.7, text), "the fixture's premise does not hold: the record states 7.7"


def t_a_negative_number_needs_its_sign():
    """The defective fixture for the helper: a storage minimum moved from -33 to -34, which the old helper
    accepted because the record says "decision 34". It must be refused now, and -33 itself still found."""
    text = open(DOC, encoding="utf-8").read()
    assert _in_document(-33, text), "the record's -33 C storage margin is not found with its sign"
    assert "34" in text, "the fixture's premise does not hold: the record no longer contains a bare 34"
    assert not _in_document(-34, text), "a -34 the record never states was accepted on a bare 34"
    d = _load()
    d["owner_rulings"]["qualification_margins_c"]["storage_min"] = -34
    bad = [lbl for lbl, v in _numbers(d) if not _in_document(v, text)]
    assert bad, "a storage margin of -34 C, which the record never states, was accepted"
