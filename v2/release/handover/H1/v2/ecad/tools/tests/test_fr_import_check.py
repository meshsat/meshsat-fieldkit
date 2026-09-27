#!/usr/bin/env python3
"""fr_import_check.py, fixtures both ways (MESHSAT-1357 round 8, review finding F of 26 September 2026).

The review asked that unattended routing stop pressing Return on a Freerouting warning nobody had read: capture what it
says, continue only past a known harmless one, confirm that the board the router holds is the board the DSN declares,
and fail anything else. Every rule below has an input that must pass and an input that must fail. The real inputs are
board B's: the seven "normalization failed" warnings its committed pre-route board raises (read off the box on
26 September 2026, identical to the dialog's screenshot), and the two defects the round found in Freerouting 1.9.0's
import itself, a settings scope placed after a keep-out that silently drops the rest of the DSN, and spikes that
normalisation shortens inside a pad.
"""
import json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
import fr_import_check as F

TOOL = os.path.join(TOOLS, "fr_import_check.py")

# ------------------------------------------------------------------------------------------------ logs
B_LOG = """2026-09-26 21:48:59.332 [main] INFO  Freerouting v1.9.0 (build-date: 2026-09-25)
2026-09-26 21:48:59.379 [main] INFO  Settings were loaded from freerouting.json
2026-09-26 21:49:00.399 [main] INFO  Opening '/root/r8-fr/b/run/S3/job.dsn'...
2026-09-26 21:49:00.719 [ForkJoinPool.commonPool-worker-1] INFO  New version available: v2.4.1
2026-09-26 21:49:03.831 [main] WARN  The normalization of net '/ETH2_P2_N' failed.
2026-09-26 21:49:03.868 [main] WARN  The normalization of net '/ETH3_P2_N' failed.
2026-09-26 21:49:04.049 [main] WARN  The normalization of net '/HOST3_1D_N' failed.
2026-09-26 21:49:04.130 [main] WARN  The normalization of net '/LIME_SSRX_P' failed.
2026-09-26 21:49:04.154 [main] WARN  The normalization of net '/LIME_SSTX_N' failed.
2026-09-26 21:49:04.239 [main] WARN  The normalization of net '/PCIE3_CLK_N' failed.
2026-09-26 21:49:04.418 [main] WARN  The normalization of net '/SWP4_C_N' failed.
"""
ROUTING = """2026-09-26 21:49:10.336 [Thread-33] INFO  Starting auto-routing...
WARNING: Runtime environment or build system does not support multi-release JARs. This will impact location-based features.
2026-09-26 21:49:11.990 [Thread-33] ERROR The normalization of net '/PCIE3_CLK_N' failed.
java.lang.Exception: We reached the maximum normalization depth (16).
\tat app.freerouting.board.PolylineTrace.normalize(PolylineTrace.java:677) ~[freerouting-1.9.0-mesh.jar:unspecified]
2026-09-26 21:49:40.000 [Thread-33] INFO  MeshSat: session written after pass 1 to /x/route.ses
2026-09-26 21:50:10.000 [Thread-33] INFO  MeshSat: session written after pass 2 to /x/route.ses
2026-09-26 21:50:20.000 [Thread-33] INFO  Auto-routing was completed in 1 minute(s) 9.66 seconds.
2026-09-26 21:50:20.100 [Thread-33] INFO  Starting route optimization on 1 thread...
2026-09-26 21:50:50.100 [Thread-33] INFO  Route optimization was completed in 30.00 seconds.
"""
DSN_PATH = "/root/r8-fr/b/run/S3/job.dsn"


def _tmp(text, suffix=".log"):
    fd, p = tempfile.mkstemp(suffix=suffix); os.write(fd, text.encode()); os.close(fd); return p


def _classify(log, stage="dialog", dsn=DSN_PATH):
    out = _tmp("", ".json")
    r = subprocess.run([sys.executable, TOOL, "classify", _tmp(log), dsn, "--stage", stage, "--json", out],
                       capture_output=True, text=True, timeout=60)
    return r.returncode, json.load(open(out))


def t_board_bs_seven_normalisation_warnings_are_known_and_continue():
    rc, rec = _classify(B_LOG)
    assert rc == 0 and rec["decision"] == "CONTINUE", rec
    assert rec["warnings"] == 7 and rec["known"] == ["FR-NORMALISE-NET"], rec
    assert "/PCIE3_CLK_N" in rec["warned_nets"] and len(rec["warned_nets"]) == 7
    assert rec["conditions"], "the known warning's condition (its copper must survive) is not carried"


def t_an_unknown_warning_is_refused():
    log = B_LOG + "2026-09-26 21:49:04.500 [main] WARN  Wiring.read_via_scope: net with name 'NOPE' not found at 'NOPE'\n"
    rc, rec = _classify(log)
    assert rc == 3 and rec["decision"] == "REFUSE", rec
    assert any("UNKNOWN warning" in x and "NOPE" in x for x in rec["reasons"]), rec["reasons"]


def t_an_error_is_refused_even_with_known_text():
    """An ERROR makes the dialog an error dialog; the reader returned something it could not read."""
    log = B_LOG + "2026-09-26 21:49:04.500 [main] ERROR The normalization of net '/X' failed.\n"
    rc, rec = _classify(log)
    assert rc == 3 and any("ERROR" in x for x in rec["reasons"]), rec


def t_a_dialog_that_nothing_in_the_log_explains_is_refused():
    log = "".join(l + "\n" for l in B_LOG.splitlines() if " WARN " not in l)   # the same import without its warnings
    rc, rec = _classify(log)
    assert rc == 3 and "explains" in " ".join(rec["reasons"]), rec
    rc2, rec2 = _classify(log, stage="import")                         # and the same import with no dialog is fine
    assert rc2 == 0, rec2


def t_the_window_is_this_dsns_import_only():
    """A warning before this DSN was opened, or after routing began, is not the import's."""
    before = "2026-09-26 21:48:00.000 [main] WARN  Something about another file\n"
    rc, rec = _classify(before + B_LOG + ROUTING, stage="import")
    assert rc == 0, rec
    rc, rec = _classify(B_LOG, dsn="/some/other.dsn")
    assert rc == 3 and "Opening" in rec["reasons"][0], rec


def t_a_warning_that_raised_no_dialog_is_still_read_when_routing_starts():
    """A rules file is read after the dialog and before the autorouter starts; its warnings raise nothing."""
    log = B_LOG + "2026-09-26 21:49:05.000 [main] WARN  RulesFile.read: net class not found\n" + ROUTING
    rc, rec = _classify(log, stage="import")
    assert rc == 3 and "RulesFile" in rec["reasons"][0], rec


def t_an_exception_outside_the_log_format_is_refused():
    log = B_LOG + 'Exception in thread "AWT-EventQueue-0" java.lang.NullPointerException\n'
    rc, rec = _classify(log)
    assert rc == 3, rec
    rc, rec = _classify(B_LOG + "WARNING: Runtime environment or build system does not support multi-release JARs.\n")
    assert rc == 0, "log4j's own status line is known and carries nothing: %s" % rec


def t_an_unreadable_log_is_refused():
    out = _tmp("", ".json")
    r = subprocess.run([sys.executable, TOOL, "classify", "/nonexistent/fr.log", DSN_PATH, "--json", out],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 3 and json.load(open(out))["decision"] == "REFUSE"


# ------------------------------------------------------------------------------------------------ DSNs
DSN = """(pcb "/tmp/fixture.dsn"
  (parser
    (string_quote ")
    (space_in_quoted_tokens on)
    (host_cad "KiCad's Pcbnew")
    (host_version "9")
  )
  (resolution um 10)
  (unit um)
  (structure
    (layer F.Cu (type signal) (property (index 0)))
    (layer B.Cu (type signal) (property (index 1)))
    (boundary (path pcb 0  0 0  20000 0  20000 -10000  0 -10000  0 0))
    (keepout "k (one)" (polygon F.Cu 0  1000 -1000  2000 -1000  2000 -2000  1000 -1000))
    (via "Via[0-1]_600:300_um")
    (rule (width 200) (clearance 200))
  )
  (placement
    (component R_0402 (place R1 5000 -5000 front 0 (PN "10k (0402)")) (place R2 15000 -5000 back 90 (PN 10k)))
  )
  (library
    (image R_0402 (pin Rect[T]Pad_500x600_um 1 -500 0) (pin Rect[T]Pad_500x600_um 2 500 0))
    (padstack Rect[T]Pad_500x600_um (shape (rect F.Cu -250 -300 250 300)) (attach off))
    (padstack "Via[0-1]_600:300_um" (shape (circle F.Cu 600)) (shape (circle B.Cu 600)) (attach off))
  )
  (network
    (net A (pins R1-1 R2-1))
    (net "B C" (pins R1-2 R2-2))
    (class kicad_default A "B C" (circuit (use_via "Via[0-1]_600:300_um")) (rule (width 200) (clearance 200)))
  )
  (wiring
    (wire (path F.Cu 200  4500 -5000  8000 -5000)(net A)(type fix))
    (via "Via[0-1]_600:300_um"  8000 -5000 (net A)(type fix))
    (wire (path F.Cu 200  5500 -5000  5500 -3000)(net "B C")(type route))
  )
)
"""
BACK = """(pcb back
  (parser (string_quote ") (space_in_quoted_tokens on) (host_cad "KiCad's Pcbnew") (host_version "9") (generated_by_freerouting))
  (resolution um 10)
  (unit um)
  (structure
    (layer F.Cu (type signal))
    (layer B.Cu (type signal))
    (boundary (rect pcb 0.0 -10000.0 20000.0 0.0))
    (via "Via[0-1]_600:300_um")
    (rule (width 200.0) (clearance 200.0) (clearance 200.0 (type "kicad_default")))
    (keepout (polygon F.Cu 0 1000.0 -1000.0 2000.0 -1000.0 2000.0 -2000.0 1000.0 -1000.0))
  )
  (network
    (net "A" 1 (pins "R1"-1 "R2"-1))
    (net "B C" 1 (pins "R1"-2 "R2"-2))
    (via "Via[0-1]_600:300_um-kicad_default" "Via[0-1]_600:300_um" "kicad_default")
    (via_rule "kicad_default" "Via[0-1]_600:300_um-kicad_default")
    (class "kicad_default" "A" "B C" (clearance_class "kicad_default") (via_rule "kicad_default") (rule (width 200.0)) (circuit (use_layer F.Cu B.Cu)))
  )
  (wiring
    (wire (polyline_path F.Cu 200.0  4500.0 -5000.0 4500.0 -5000.1  4500.0 -5000.0 8000.0 -5000.0  8000.0 -5000.0 8000.0 -5000.1) (net "A" 1) (type fix))
    (via "Via[0-1]_600:300_um" 8000.0 -5000.0 (net "A" 1) (type fix))
    (wire (polyline_path F.Cu 200.0  5500.0 -5000.0 5500.1 -5000.0  5500.0 -5000.0 5500.0 -3000.0  5500.0 -3000.0 5500.1 -3000.0) (net "B C" 1) (type protect))
  )
)
"""


def _import(dsn, back):
    out = _tmp("", ".json")
    r = subprocess.run([sys.executable, TOOL, "import", _tmp(dsn, ".dsn"), _tmp(back, ".dsn"), "--json", out],
                       capture_output=True, text=True, timeout=60)
    return r.returncode, json.load(open(out))


def t_the_written_back_board_that_holds_everything_survives():
    rc, rec = _import(DSN, BACK)
    assert rc == 0 and rec["decision"] == "SURVIVED", rec.get("findings")
    assert rec["nets"] == 2 and rec["pins"] == 4 and rec["wires"] == 2 and rec["vias"] == 1 and rec["keepouts"] == 1, rec


def _lost(back, check):
    rc, rec = _import(DSN, back)
    assert rc == 3 and rec["decision"] == "LOST", "%s was not caught: %s" % (check, rec.get("findings"))
    assert any(f["check"] == check for f in rec["findings"]), "%s not named: %s" % (check, rec["findings"])


def t_a_pin_that_did_not_come_back_is_a_loss():
    _lost(BACK.replace('(pins "R1"-1 "R2"-1)', '(pins "R1"-1)'), "net-pins")


def t_a_net_that_did_not_come_back_is_a_loss():
    _lost(BACK.replace('(net "B C" 1 (pins "R1"-2 "R2"-2))', ""), "net")


def t_a_class_width_that_changed_is_a_loss():
    _lost(BACK.replace("(rule (width 200.0)) (circuit", "(rule (width 250.0)) (circuit"), "class-width")


def t_class_vias_that_changed_are_a_loss():
    _lost(BACK.replace('"Via[0-1]_600:300_um-kicad_default" "Via[0-1]_600:300_um" "kicad_default"',
                       '"Via[0-1]_600:300_um-kicad_default" "Via[0-1]_800:400_um" "kicad_default"'), "class-vias")


def t_a_class_clearance_that_changed_is_a_loss():
    _lost(BACK.replace('(clearance 200.0 (type "kicad_default"))', '(clearance 150.0 (type "kicad_default"))'), "class-clearance")


def t_class_layers_that_changed_are_a_loss():
    _lost(BACK.replace("(use_layer F.Cu B.Cu)", "(use_layer F.Cu)"), "class-layers")


def t_a_layer_that_changed_type_is_a_loss():
    _lost(BACK.replace("(layer B.Cu (type signal))", "(layer B.Cu (type power))"), "layer")


def t_a_keepout_that_did_not_come_back_is_a_loss():
    _lost(BACK.replace("(keepout (polygon F.Cu 0 1000.0 -1000.0 2000.0 -1000.0 2000.0 -2000.0 1000.0 -1000.0))", ""), "keepout")


def t_a_fixed_wire_that_did_not_come_back_is_a_loss():
    i = BACK.index('(wire (polyline_path F.Cu 200.0  4500.0'); j = BACK.index('(type fix))', i) + len('(type fix))')
    _lost(BACK[:i] + BACK[j:], "wire")


def t_a_wire_that_came_back_with_another_fixed_state_is_a_loss():
    _lost(BACK.replace('(net "B C" 1) (type protect))', '(net "B C" 1))'), "wire-fixed")


def t_a_via_that_did_not_come_back_is_a_loss():
    _lost(BACK.replace('(via "Via[0-1]_600:300_um" 8000.0 -5000.0 (net "A" 1) (type fix))', ""), "via")


def t_a_spike_normalisation_shortens_inside_a_same_net_pad_is_not_a_loss():
    """Board B, 26 September 2026: a wire overshooting a via's centre (or pad C281-1's) and a stub coming back are merged
    and the overshoot is gone. Here: 30 um past the via at (8000, -5000), and 20 um past R2's pin 1, which a back-side
    part rotated 90 degrees puts at (15000, -4500) on B.Cu."""
    dsn = DSN.replace('(via "Via[0-1]_600:300_um"  8000 -5000 (net A)(type fix))',
                      '(via "Via[0-1]_600:300_um"  8000 -5000 (net A)(type fix))\n'
                      '    (wire (path F.Cu 200  8000 -5000  8030 -5000)(net A)(type fix))\n'
                      '    (wire (path B.Cu 200  15000 -4500  15000 -4480)(net A)(type fix))')
    rc, rec = _import(dsn, BACK)
    assert rc == 0, rec["findings"]
    assert rec["points_inside_same_net_via_pad"] >= 2, rec


def t_the_same_spike_away_from_any_pad_is_a_loss():
    dsn = DSN.replace('(via "Via[0-1]_600:300_um"  8000 -5000 (net A)(type fix))',
                      '(via "Via[0-1]_600:300_um"  8000 -5000 (net A)(type fix))\n'
                      '    (wire (path F.Cu 200  6500 -5000  6500 -5030)(net A)(type fix))')
    rc, rec = _import(dsn, BACK)
    assert rc == 3 and any(f["check"] == "wire" for f in rec["findings"]), rec


def t_a_back_side_pad_is_on_the_back_layer_only():
    """The spike at R2's pin is excused on B.Cu; the same geometry on F.Cu has no pad under it and is a loss."""
    dsn = DSN.replace('(via "Via[0-1]_600:300_um"  8000 -5000 (net A)(type fix))',
                      '(via "Via[0-1]_600:300_um"  8000 -5000 (net A)(type fix))\n'
                      '    (wire (path F.Cu 200  15000 -4500  15000 -4480)(net A)(type fix))')
    rc, rec = _import(dsn, BACK)
    assert rc == 3, rec


# ------------------------------------------------------------------------------------------------ the settings scope
def t_a_settings_scope_after_a_keepout_is_refused_because_1_9_0_drops_the_rest():
    """Structure.java:891-896 reads autoroute_settings only while no keep-out or plane has been read; otherwise its
    closing bracket ends the structure and placement, library, network and wiring are never read. Measured on the box
    with this tool's first probe copy of board E5: no warning, and the export failed on a null package list."""
    bad = DSN.replace('(via "Via[0-1]_600:300_um")\n', '(autoroute_settings (fanout off) (autoroute on))\n    (via "Via[0-1]_600:300_um")\n')
    assert F.structure_lint(bad)[0], "a misplaced settings scope was not seen"
    good = DSN.replace('    (boundary', '    (autoroute_settings (fanout off) (autoroute on))\n    (boundary')
    assert not F.structure_lint(good)[0], "a settings scope before any keep-out was refused"
    src, dst = _tmp(bad, ".dsn"), _tmp("", ".dsn")
    r = subprocess.run([sys.executable, TOOL, "probe-dsn", src, dst], capture_output=True, text=True, timeout=60)
    assert r.returncode == 3 and "silently dropped" in r.stdout, r.stdout
    rc, rec = _import(bad, BACK)
    assert rc == 3 and any(f["check"] == "structure" for f in rec["findings"]), rec


def t_the_probe_copy_changes_one_settings_scope_and_nothing_else():
    for base in (DSN, DSN.replace('    (boundary', '    (autoroute_settings (fanout on) (autoroute on) (via_costs 200))\n    (boundary')):
        src, dst = _tmp(base, ".dsn"), _tmp("", ".dsn")
        r = subprocess.run([sys.executable, TOOL, "probe-dsn", src, dst], capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stdout
        out = open(dst).read()
        assert out.count("(autoroute_settings") == 1 and F.PROBE_SETTINGS in out, out[:600]
        assert not F.structure_lint(out)[0], "the probe's own copy would be misread"
        # the settings sit before the first keep-out, and apart from them the file is the input
        assert out.index(F.PROBE_SETTINGS) < out.index("(keepout")
        a, b = F.read_dsn(src), F.read_dsn(dst)
        for k in ("layers", "nets", "classes", "keepouts"):
            assert a[k] == b[k], k
        assert len(a["wires"]) == len(b["wires"]) and len(a["vias"]) == len(b["vias"])


def t_a_quoted_bracket_does_not_move_a_scope_boundary():
    """The keep-out "k (one)" and the PN "10k (0402)" carry brackets inside quotes."""
    import re
    m = re.search(r"\(structure\b", DSN)
    kids = [k for k, b, e in F._children(DSN, m.start())]
    assert kids == ["layer", "layer", "boundary", "keepout", "via", "rule"], kids


# ------------------------------------------------------------------------------------------------ the session
SES = """(session fixture
  (base_design fixture.dsn)
  (placement (resolution um 10))
  (was_is)
  (routes
    (resolution um 10)
    (parser (host_cad "KiCad's Pcbnew") (host_version "9"))
    (library_out)
    (network_out
      (net "B C"
        (wire (path F.Cu 2000 55000 -50000 55000 -30000) (type protect))
        (wire (path F.Cu 2000 55000 -30000 145000 -30000))
        (via "Via[0-1]_600:300_um" 145000 -30000)
      )
    )
  )
)
"""


def _survive(ses, dsn=DSN, extra=()):
    out = _tmp("", ".json")
    r = subprocess.run([sys.executable, TOOL, "survive", _tmp(dsn, ".dsn"), _tmp(ses, ".ses"), "--json", out] + list(extra),
                       capture_output=True, text=True, timeout=60)
    return r.returncode, json.load(open(out))


def t_a_session_that_keeps_everything_survives():
    rc, rec = _survive(SES)
    assert rc == 0 and rec["decision"] == "SURVIVED", rec["findings"]
    assert rec["dsn_user_fixed_wires"] == 1 and rec["routed_nets"] == 1, rec


def _ses_lost(ses, check, dsn=DSN, extra=()):
    rc, rec = _survive(ses, dsn, extra)
    assert rc == 3, "%s was not caught: %s" % (check, rec.get("findings"))
    assert any(f["check"] == check for f in rec["findings"]), "%s not named: %s" % (check, rec["findings"])


def t_a_user_fixed_wire_missing_from_the_session_is_a_loss():
    _ses_lost(SES.replace("(wire (path F.Cu 2000 55000 -50000 55000 -30000) (type protect))", ""), "fixed-wire")


def t_a_router_wire_wider_than_its_class_is_a_loss():
    _ses_lost(SES.replace("(wire (path F.Cu 2000 55000 -30000 145000 -30000))", "(wire (path F.Cu 2500 55000 -30000 145000 -30000))"), "class-width")


def t_a_router_wire_on_a_layer_its_class_forbids_is_a_loss():
    dsn = DSN.replace('(circuit (use_via "Via[0-1]_600:300_um"))', '(circuit (use_via "Via[0-1]_600:300_um") (use_layer B.Cu))')
    _ses_lost(SES, "class-layer", dsn=dsn)


def t_a_router_via_its_class_does_not_list_is_a_loss():
    _ses_lost(SES.replace('(via "Via[0-1]_600:300_um" 145000 -30000)', '(via "Via[0-1]_800:400_um" 145000 -30000)'), "class-via")


def t_copper_on_a_net_the_dsn_does_not_declare_is_a_loss():
    _ses_lost(SES.replace('(net "B C"', '(net "Z"'), "net-declared")


def t_router_copper_on_an_ignored_class_is_a_loss_and_a_comma_class_is_named():
    """KiCad 9 joins a net's classes with commas and Freerouting splits -inc on commas (StartupOptions.java:188-190),
    so a class named "SIG,Default" is never ignored by a job that means to ignore it."""
    dsn = DSN.replace('    (class kicad_default', '    (net D (pins R1-1))\n    (class SIG,Default D (rule (width 200)))\n    (class kicad_default')
    ses = SES.replace('    (network_out\n', '    (network_out\n      (net D (wire (path F.Cu 2000 45000 -50000 45000 -60000)))\n')
    rc, rec = _survive(ses, dsn, ["--ignore-classes", "SIG,Default"])
    assert rc == 3 and any(f["check"] == "ignored-class" and "comma" in f["detail"] for f in rec["findings"]), rec
    assert rec["comma_classes_not_ignorable"] == ["SIG,Default"], rec
    rc, rec = _survive(SES, dsn, ["--ignore-classes", "SIG,Default"])      # no copper on D: nothing lost
    assert rc == 0, rec["findings"]


# ------------------------------------------------------------------------------------------------ timing
def t_the_stage_timing_separates_load_dialog_routing_and_optimiser():
    log = _tmp(B_LOG + ROUTING)
    ev = _tmp(json.dumps({"event": "start", "wall": 0}) + "\n")
    out = _tmp("", ".json")
    r = subprocess.run([sys.executable, TOOL, "timing", log, "--events", ev, "--json", out, "--label", "fixture"],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0 and r.stdout.startswith("fr_stage fixture:"), r.stdout
    rec = json.load(open(out))
    assert rec["jvm_to_open_s"] == 1.1 and rec["input_load_s"] == 4.0, rec
    assert rec["import_to_routing_s"] == 5.9 and rec["passes"] == 2 and rec["routing_finished"], rec
    assert rec["active_routing_s"] == 69.7 and rec["optimiser_s"] == 30.0, rec
    assert rec["routing_errors"] == 1 and "PCIE3_CLK_N" in rec["routing_error_lines"][0], rec
