#!/usr/bin/env python3
"""A session import leaves every via's drill undefined, and the session itself says what it was (18 September 2026).

E12 came back from `ImportSpecctraSES` with ten vias 0.6 mm wide and 0.6 mm drilled on CELL_F: the importer sets
the drill UNDEFINED, KiCad resolves that to the net class's via drill (BANK: 1.2/0.6), and a via the pre-router
laid at 0.6/0.3 lost its ring. The session names each via's padstack ("Via[0-3]_600:300_um") at its position, so
`ses_via_drill` reads the drill back; every importer in the tree calls it before the board is saved."""
import os, sys, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)

SES = """(session "x.ses"
  (base_design "x.dsn")
  (routes
    (resolution um 10)
    (parser (host_cad "KiCad's Pcbnew"))
    (network_out
      (net "/CELL_F"
        (via "Via[0-3]_600:300_um" 1016300 -2002750
          (type protect)
        )
        (via "Via[0-3]_1200:600_um" 542325 -2065050
        )
      )
    )
  )
)
"""


def t_the_session_parser_reads_width_and_drill_at_the_board_position():
    import ses_via_drill
    d = tempfile.mkdtemp(prefix="ses-"); p = os.path.join(d, "x.ses"); open(p, "w").write(SES)
    got = ses_via_drill.session_vias(p)
    def at(x, y): return next((v for (px, py), v in got.items() if abs(px - x) < 0.002 and abs(py - y) < 0.002), None)
    assert at(101.63, 200.275) == (0.6, 0.3), got
    assert at(54.2325, 206.505) == (1.2, 0.6), got


def t_every_session_importer_restores_the_drills_before_it_saves():
    for f, must in (("route_one.sh", "ses_via_drill.restore_board(b, sys.argv[2])"),
                    ("ses_import_lock.py", "ses_via_drill.restore_board(b, ses)"),
                    ("routeflow.py", "ses_via_drill.restore_board(b, sys.argv[2])")):
        s = open(os.path.join(TOOLS, f), encoding="utf-8").read()
        assert "ImportSpecctraSES" in s, f
        i = s.index("ImportSpecctraSES"); j = s.find("SaveBoard", i)
        assert j > 0 and must in s[i:j], "%s imports a session and saves the board without restoring the drills" % f
