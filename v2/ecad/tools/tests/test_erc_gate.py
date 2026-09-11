#!/usr/bin/env python3
"""The ERC gate: an error blocks, and it stops blocking only when the project says why in writing.

`build_sch.sh` used to turn kicad-cli's exit code into an echo and no chain read it (appendix 32.64). The rule that replaced
it is the one tested here: an allow-list line without a reason waves nothing through."""
import os, json, tempfile, subprocess, sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _project(violations, allow=None):
    d = tempfile.mkdtemp(prefix="erc-gate-test-"); os.makedirs(os.path.join(d, "out"))
    json.dump({"sheets": [{"violations": violations}]}, open(os.path.join(d, "out", "b-erc.json"), "w"))
    if allow is not None: open(os.path.join(d, "erc-allow.txt"), "w").write(allow)
    return d


def _run(d):
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "erc_gate.py"), d, "b"], capture_output=True, text=True)
    status = open(os.path.join(d, "out", "b-erc.status")).read().strip() if os.path.exists(os.path.join(d, "out", "b-erc.status")) else ""
    return r.returncode, r.stdout + r.stderr, status


def _err(t, desc):
    return {"type": t, "severity": "error", "description": desc, "items": [{"description": desc}]}


def t_a_clean_erc_passes():
    rc, out, st = _run(_project([]))
    assert rc == 0 and st.startswith("clean"), (rc, st, out)


def t_an_error_blocks():
    rc, out, st = _run(_project([_err("power_pin_not_driven", "Input power pin not driven by any Output Power pins: /+3V3_AB")]))
    assert rc == 1 and st.startswith("BLOCK"), (rc, st, out)


def t_a_warning_never_blocks():
    rc, out, st = _run(_project([{"type": "unconnected_wire_endpoint", "severity": "warning", "description": "w", "items": []}]))
    assert rc == 0, (rc, st, out)


def t_an_allow_line_with_a_reason_lets_that_one_through():
    v = [_err("power_pin_not_driven", "Input power pin not driven by any Output Power pins: /+3V3_AB")]
    rc, out, st = _run(_project(v, allow="power_pin_not_driven|+3V3_AB   # the gated rail comes from A22 over the harness\n"))
    assert rc == 0, (rc, st, out)


def t_an_allow_line_without_a_reason_is_ignored():
    """A line with no `#` reason must not silence anything: an exemption in this pipeline is always written down."""
    v = [_err("power_pin_not_driven", "Input power pin not driven by any Output Power pins: /+3V3_AB")]
    rc, out, st = _run(_project(v, allow="power_pin_not_driven|+3V3_AB\n"))
    assert rc == 1 and st.startswith("BLOCK"), (rc, st, out)


def t_an_allow_line_does_not_cover_a_different_net():
    v = [_err("power_pin_not_driven", "Input power pin not driven by any Output Power pins: /+5V_DEV")]
    rc, out, st = _run(_project(v, allow="power_pin_not_driven|+3V3_AB   # the gated rail\n"))
    assert rc == 1, (rc, st, out)


def t_a_missing_erc_report_is_inconclusive_and_still_blocks():
    """11 September 2026: this used to assert exit 1, which said "ERC failed" about a run where ERC never
    happened. The gate now exits 3 (INCONCLUSIVE) there. Both are non-zero, so nothing downstream loosens;
    what changes is that a skipped bar can no longer be read back as a bar that was tested and held."""
    d = tempfile.mkdtemp(prefix="erc-gate-test-"); os.makedirs(os.path.join(d, "out"))
    rc, out, st = _run(d)
    assert rc == 3, (rc, st, out)
    assert rc != 0, "a missing ERC report must never pass"
    rec = json.load(open(os.path.join(d, "out", "erc_gate.verdict.json")))
    assert rec["verdict"] == "INCONCLUSIVE", rec
    assert rec["denominator"] == 0, rec
    assert "no ERC output" in rec["note"], rec


def t_every_erc_verdict_carries_its_denominator():
    """A verdict without the count it rests on is the defect verdict.py exists to remove: 0 blocking errors
    of 0 violations and 0 blocking errors of 41 are different claims and used to print identically."""
    v = [{"type": "power_pin_not_driven", "severity": "error", "description": "x", "items": []}]
    d = _project(v, allow="power_pin_not_driven   # the gated rail is driven by the module\n")
    rc, out, st = _run(d)
    rec = json.load(open(os.path.join(d, "out", "erc_gate.verdict.json")))
    assert rc == 0 and rec["verdict"] == "PASS", (rc, rec)
    assert rec["denominator"] == 1 and rec["counts"]["allowed"] == 1, rec
