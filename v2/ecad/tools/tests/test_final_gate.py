#!/usr/bin/env python3
"""The final gate pass reads the folders that exist and says what it could not judge (14 September 2026).

`final_gate.py` runs no new logic: it re-reads every deliverable folder with `verify_deliverable`, then
`check_contracts` and `jlc_certify` once each, and prints one table. Two properties make it worth having
rather than seven logs: a folder nobody re-read since it was cut cannot pass by being forgotten, and a check
that CANNOT run here says so instead of reading as a failure (`check_contracts` compares netlists that live in
each project's untracked out/, so on the runner every board is absent, which is inconclusive and not broken).
"""
import os

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = open(os.path.join(TOOLS, "final_gate.py")).read()


def t_it_judges_every_folder_it_finds():
    assert "newest_folders" in SRC and "verify_deliverable.py" in SRC


def t_a_bare_board_and_a_quote_folder_are_declared_not_failed():
    i = SRC.find('args.append("--bare")')
    assert i > 0, "nothing declares a bare board"
    blk = SRC[max(0, i - 300):i + 60]
    assert "quote" in blk and "bom.csv" in blk, "only one of the two cases is handled"


def t_an_unjudgeable_contract_check_is_not_a_failure():
    assert "contracts_absent" in SRC, "an absent netlist reads as a broken contract"
    assert "INCONCLUSIVE" in SRC, "the verdict cannot say it was not judged"


def t_it_opens_no_board_and_touches_no_host():
    for bad in ("pcbnew", "ssh ", "route_one", "freerouting"):
        assert bad not in SRC, "final_gate should read artefacts only, found %r" % bad


def t_the_summary_line_comes_from_the_gate_itself():
    assert 'l.startswith("verify_deliverable:")' in SRC, "the summary is reconstructed instead of read"
