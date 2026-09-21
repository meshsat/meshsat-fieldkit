#!/usr/bin/env python3
"""The adopted envelope as data, and the pin that keeps it honest (rule ENV-001, 21 September 2026).

Decision 34 adopted `v2/docs/OPERATING-ENVELOPE.md` section 4 and section 6's first row. Four rules resolve
against that envelope (CMP-001, THM-001, ISO-001, REL-001) and until today each would have had to read prose,
so `tools/pcb_envelope.yaml` carries the same numbers in a form a rule can use.

The danger of a second copy is that it drifts from the record, and drift here is invisible: a rule would keep
passing against a number nobody adopted. Two rules stop that, and they are the fixtures of this file:

  * EVERY NUMBER IN THE FILE APPEARS IN THE DOCUMENT. The defective fixture is a copy with an ambient limit
    the record does not carry, and it must be refused.
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
    return out


def _in_document(value, text):
    """Does the document state this number? Signed, and in either sign convention the prose uses."""
    v = int(value)
    forms = {"%d" % v, "%+d" % v, "%d" % abs(v)} if v < 0 else {"%d" % v, "+%d" % v}
    return any(re.search(r"(?<![\d.])%s(?![\d.])" % re.escape(f), text) for f in forms)


def t_every_number_in_the_envelope_file_appears_in_the_adopted_document():
    """The acceptable fixture is the real file against the real record."""
    d = _load()
    text = open(DOC, encoding="utf-8").read()
    bad = [lbl for lbl, v in _numbers(d) if not _in_document(v, text)]
    assert not bad, "the envelope file states numbers the record does not: %s" % bad


def t_a_number_the_record_does_not_carry_is_refused():
    """The defective fixture: an ambient limit nobody adopted."""
    import yaml
    d = _load()
    d["ambient_c"]["in_use"]["max"] = 71          # a number the document does not contain anywhere
    t = tempfile.mkdtemp(prefix="env-")
    p = os.path.join(t, "pcb_envelope.yaml")
    with open(p, "w") as fh: yaml.safe_dump(d, fh)
    text = open(DOC, encoding="utf-8").read()
    bad = [lbl for lbl, v in _numbers(_load(p)) if not _in_document(v, text)]
    assert bad, "an ambient maximum of 71 C, which the record never states, was accepted"


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


def t_what_the_record_leaves_open_is_not_invented_here():
    """The document leaves the altitude, the vibration and shock severities and the service life open, and
    says so. A rule that needs one of them must not find a number here instead."""
    d = _load()
    assert set(d["open_in_the_document"]) >= {"altitude", "service life"}, d["open_in_the_document"]
    flat = str(d)
    for word in ("altitude_m", "vibration_g", "service_life"):
        assert word not in flat, "the envelope file invents %s, which the record leaves open" % word
    assert d["transient"]["eft"]["adopted"] is False, "the electrical fast transient row has no authority and is not adopted"
