#!/usr/bin/env python3
"""The final gate pass: every deliverable folder in the tree, judged by the gates that already exist.

Usage: final_gate.py [--boards a,b,c] [--json out.json]

15 September 2026 (red team report 1, P0): the verdict used to depend on the deliverable failures and the contracts alone,
so it could read PASS while parts certification was OPEN, while a board was held as quote-only, or while a board had no
folder at all (the table listed what existed and a board could vanish from the denominator). The set is a MANIFEST now:
every letter with a boards/<letter>.json plus E5 must have a folder, a quote folder is a held board and fails the set, an
OPEN certification fails it, and an unjudgeable component (contracts with no netlist here, certification that could not ask
JLCPCB) is INCONCLUSIVE and never PASS. `--boards` narrows the table for a look; a subset is never the set, so its verdict
is INCONCLUSIVE at best.

It runs nothing new. For each board's newest deliverable folder it runs `verify_deliverable.py`, then
`check_contracts.py` once across the set and `jlc_certify.py` once over the parts, and prints ONE table with a
verdict per board and the denominator each came from. The point is that a release is read off a single page
instead of seven logs, and that a folder nobody re-read since it was cut cannot pass by being forgotten: a
folder is judged today, by today's rules, or it is not judged at all (14 September 2026, MESHSAT-862).

Every verdict here is a re-reading of a written artefact. It does not open a board, route anything or touch a
host, so it is safe to run on a host with no KiCad python at all.
"""
import sys, os, re, glob, json, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
BOARDS = os.path.normpath(os.path.join(HERE, "..", "..", "release", "revA", "boards"))   # tools -> ecad -> v2
sys.path.insert(0, HERE)
import verdict as _v


def newest_folders(only=None):
    """{letter: (phase number, folder)} for the newest phase of each board, quote folders included."""
    best = {}
    for d in sorted(glob.glob(os.path.join(BOARDS, "meshsat-pcb-*"))):
        m = re.match(r"meshsat-pcb-([a-z0-9]+)-revA-([A-Z]+)(\d+)", os.path.basename(d))
        if not m: continue
        letter, num = m.group(1), int(m.group(3))
        if only and letter not in only: continue
        if letter not in best or num > best[letter][0]: best[letter] = (num, d)
    return best


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def _declared_phase(letter, boards_dir=None):
    """The phase `boards/<letter>.json` declares, which is what the generators stamp and the chains cut; E5 declares none."""
    p = os.path.join(boards_dir or os.path.join(HERE, "boards"), "%s.json" % letter)
    try: return (json.load(open(p)).get("phase") or "").strip()
    except Exception: return ""


def required_letters(boards_dir=None):
    """The manifest: every letter that has a boards/<letter>.json, plus e5 (the bare dock block has no chain)."""
    d = boards_dir or os.path.join(HERE, "boards")
    ls = {os.path.basename(f)[:-5] for f in glob.glob(os.path.join(d, "*.json"))}
    return sorted(ls | {"e5"})


def _holds(path=None):
    """The boards held by an open decision, and the reason a failure to READ that file is not a pass.

    A hold lives outside the rule results on purpose: a held board can pass every rule it has. If the file
    exists and cannot be parsed (no PyYAML on this host, a typo, a partial entry), the honest answer is that
    this gate does not know whether a board is held, which is INCONCLUSIVE and never PASS. Returning an empty
    map there would release a held board on a host that is missing a library, which is the 16 September
    defect in a new place."""
    import rules_lib as R
    p = path or R.HOLDS
    if not os.path.exists(p): return {}, None
    try:
        return R.board_holds(p), None
    except Exception as e:
        return {}, "the hold file exists and could not be read (%s: %s), so this gate cannot say whether a " \
                   "board is held" % (type(e).__name__, e)


def main(argv, run=None, boards_dir=None, holds_path=None):
    run = run or globals()["run"]
    only = set(argv[argv.index("--boards") + 1].split(",")) if "--boards" in argv else None
    held_boards, holds_unreadable = _holds(holds_path)
    required = required_letters(boards_dir)
    found = newest_folders(only)
    rows = []
    for letter, (num, folder) in sorted(found.items()):
        name = os.path.basename(folder)
        quote = name.endswith("-quote")
        # verify_deliverable takes the folder, the board's stem and the copper layer count, and every one of
        # the three is IN the folder: the stem is the board file's name and the layer count is what the gerber
        # zip carries, which is the same reading the gate itself does against the board (3 September's bug).
        # The stem comes from the GERBER ZIP's name, not from globbing the folder for a board: a tool that
        # picks a board by globbing is the trap of 11 September (a nine-day-old b5m.kicad_pcb sorted first in
        # a project directory and a whole BOM was exported from it), and the rule against it is mechanical.
        stem = next((os.path.basename(f)[:-len("-gerbers.zip")] for f in sorted(glob.glob(os.path.join(folder, "*-gerbers.zip")))), None)
        if stem is None: stem = re.sub(r"^meshsat-(pcb-[a-z0-9]+)-revA-.*$", r"\1", name)
        cu = 0
        for z in glob.glob(os.path.join(folder, "*-gerbers.zip")):
            try:
                import zipfile
                cu = len([n for n in zipfile.ZipFile(z).namelist() if re.search(r"(\.g[0-9]+$|Cu\.g|-F_Cu|-B_Cu|_Cu\.)", n, re.I)])
            except Exception:
                cu = 0
        args = [sys.executable, os.path.join(HERE, "verify_deliverable.py"), folder, stem, str(cu or 4)]
        # The board this folder is supposed to be, so the gate writes its reading under that board's name as
        # well. A folder that is NOT the phase the board declares is overwritten below with the reason: this
        # run still judges it, because its own properties are worth knowing, but they are not an answer about
        # a board this set is not building.
        args += ["--board", letter.lower()]
        # A BARE board carries no BOM and no CPL by design (E5 is the dock block: copper, holes and targets),
        # and a quote folder carries no board file. Both are declared to the gate rather than read as failures
        # of the FOLDER; a quote folder still fails the SET below, because a held board is not a released one.
        if quote or not glob.glob(os.path.join(folder, "*-bom.csv")): args.append("--bare")
        rc, out = run(args)
        sm = [l for l in out.splitlines() if l.startswith("verify_deliverable:") and ("ALL PASS" in l or " of " in l)]
        summary = (sm[-1].replace("verify_deliverable: ", "") if sm else "no summary line")
        # THE FOLDER MUST BE THE PHASE THE BOARD DECLARES (15 September 2026 after the return-current rules: every
        # folder in the tree was cut before those gates existed, and each one passed here, because verify_deliverable
        # judges a folder against ITSELF. `boards/<letter>.json` carries the phase the generators stamp and the chains
        # cut; a folder naming an earlier one is a board this set is not building, whatever its own properties say.)
        declared = _declared_phase(letter, boards_dir)
        stale = bool(declared) and not name.upper().endswith(declared.upper()) and not name.upper().endswith(declared.upper() + "-QUOTE")
        if stale:
            summary = "the tree declares %s and this folder is %s: re-cut it, the folder is judged against itself and cannot know" % (declared, name.split("-")[-1])
        hold = held_boards.get(letter)
        v = ("QUOTE" if quote else ("STALE" if stale else ("PASS" if rc == 0 else "FAIL")))
        if hold:
            # THE HOLD OUTRANKS THE FOLDER'S OWN VERDICT, in both directions: a held board whose folder passes
            # is still not releasable, and the reason is named rather than hidden inside a rule result.
            import rules_lib as R
            summary = "held by owner decision %s: %s (its folder reads %s)" % (hold["decision"], R.hold_banner(hold), v)
            v = "HELD"
        rows.append(dict(board=letter.upper(), phase=num, folder=name, quote=quote, stale=stale, declared=declared,
                         held=bool(hold), verdict=v, summary=summary.strip(),
                         vd_rc=rc, vd_summary=(sm[-1].replace("verify_deliverable: ", "") if sm else "")))
    want = [l for l in required if not only or l in only]
    missing = [l for l in want if l not in found]
    subset = bool(only) and set(only) != set(required)
    # `check_contracts` compares the NETLISTS the chains write into each project's out/, which is untracked:
    # on a host where no chain has run it reports every board absent, and absent is INCONCLUSIVE rather than
    # broken (11 September). Say which it is, so a table read on the runner is not mistaken for a failure.
    rc_c, out_c = run([sys.executable, os.path.join(HERE, "check_contracts.py")])
    contracts = next((l for l in out_c.splitlines() if "contracts" in l.lower()), "no contracts line")
    contracts_absent = rc_c == 3 or "absent" in contracts or "missing_boards" in contracts
    rc_j, out_j = run([sys.executable, os.path.join(HERE, "jlc_certify.py")] + (["--boards", ",".join(sorted(only))] if only else []))
    certify = next((l for l in out_j.splitlines() if l.startswith("jlc_certify:")), "no certification line")
    # Rule ENV-002: the release package is a set of DOCUMENTS as much as a set of folders, and the documents go
    # public on the mirror within minutes. A rating claimed in them without the test that establishes it is a
    # promise to whoever would carry the kit, and nothing has been fabricated or powered.
    rc_m, out_m = run([sys.executable, os.path.join(HERE, "claims_check.py")])
    claims = next((l for l in out_m.splitlines() if l.startswith("claims_check:")), "no claims line")

    print("final_gate: %d deliverable folder(s), %d required" % (len(rows), len(want)))
    for r in rows:
        print("  %-3s %-34s %-6s %s" % (r["board"], r["folder"], r["verdict"], r["summary"][:90]))
    for l in missing: print("  %-3s %-34s %-6s %s" % (l.upper(), "(no deliverable folder)", "FAIL", "a required board with no folder is a failure of the set"))
    print("  contracts : %s" % contracts.strip()[:120])
    print("  parts     : %s" % certify.strip()[:120])
    print("  claims    : %s" % claims.strip()[:120])
    bad = [r for r in rows if r["verdict"] in ("FAIL", "STALE")]
    held = [r for r in rows if r["quote"] or r.get("held")]
    c_word = "PASS" if rc_c == 0 else ("NOT JUDGED HERE (no netlist in this tree)" if contracts_absent else "FAIL")
    j_word = "PASS" if rc_j == 0 else ("NOT JUDGED (certification could not ask)" if rc_j == 3 else "OPEN")
    print("final_gate: %d of %d folder(s) pass, %d quote-only, %d missing, contracts %s, parts %s%s"
          % (len(rows) - len(bad) - len(held), len(rows), len(held), len(missing), c_word, j_word, " (a subset, never the set)" if subset else ""))
    if "--json" in argv:
        json.dump(dict(rows=rows, missing=missing, contracts=contracts.strip(), certify=certify.strip(),
                       claims=claims.strip(), contracts_rc=rc_c, certify_rc=rc_j, claims_rc=rc_m),
                  open(argv[argv.index("--json") + 1], "w"), indent=1)
    # THE DECISION, fail closed: any failure is FAIL; anything unjudged with no failure is INCONCLUSIVE; PASS is the
    # whole manifest present, every folder passing, no held board, contracts PASS and certification PASS.
    failed = bool(bad or held or missing or (rc_c == 1) or (rc_j == 1) or (rc_m == 1))
    unjudged = bool(subset or contracts_absent or rc_j == 3 or rc_m == 3 or holds_unreadable
                    or rc_c not in (0, 1, 3) or rc_j not in (0, 1, 3) or rc_m not in (0, 1, 3))
    if holds_unreadable: print("  holds     : %s" % holds_unreadable)
    res = _v.FAIL if failed else (_v.INCONCLUSIVE if unjudged else _v.PASS)
    evidence = (["%s %s: %s" % (r["board"], r["folder"], r["summary"][:60]) for r in rows if r["verdict"] != "PASS"]
                + ["%s: no deliverable folder" % l.upper() for l in missing]
                + (["contracts: %s" % contracts.strip()[:80]] if rc_c != 0 else [])
                + (["parts: %s" % certify.strip()[:80]] if rc_j != 0 else [])
                + (["claims: %s" % claims.strip()[:80]] if rc_m != 0 else []))
    # AND THE DELIVERABLE'S OWN READING, PER BOARD (17 September 2026). Rule DFM-001 is verified by
    # `verify_deliverable`, which writes under ONE name, and this loop runs it once per folder: the last
    # folder's reading stood as every board's, so six boards read "taken on board p, which is not a board this
    # project directory holds" and DFM-001 was unanswered on all of them. The run has already happened here,
    # so each board's own reading is written from it, and a folder that is not the phase the board declares
    # says that instead of answering for a board this set is not building.
    for r in rows:
        _l = r["board"].lower()
        if r["stale"]:
            _v.write("verify_deliverable_%s" % _l, _v.INCONCLUSIVE, counts={"folder": 1}, denominator=0, quiet=True,
                     inputs={"folder": r["folder"], "declared_phase": r.get("declared")},
                     evidence=[r["summary"][:160]],
                     missing_input=("the folder judged here is %s and this board declares %s, so its properties "
                                    "are a reading of a board this set is not building"
                                    % (r["folder"], r.get("declared") or "nothing")))
            continue
        _v.write("verify_deliverable_%s" % _l,
                 _v.PASS if r.get("vd_rc") == 0 else (_v.INCONCLUSIVE if r.get("vd_rc") == 3 else _v.FAIL),
                 counts={"folder": 1, "quote": int(bool(r["quote"]))}, denominator=1, quiet=True,
                 inputs={"folder": r["folder"]},
                 evidence=[r.get("vd_summary", "")[:160]] if r.get("vd_summary") else [],
                 note="this board's own deliverable folder, read by verify_deliverable in this run")
    # A PER-BOARD VERDICT AS WELL AS THE SET'S (16 September 2026). DOC-001 and OUT-001 are verified by this
    # gate, and this gate judges the SET, so every board inherited the set's failure: board E5's own folder is
    # the one folder that passes and it was reading FAIL on both rules because six other folders are stale.
    # Fourteen rule-board pairs said the wrong thing about the wrong boards. The set verdict is unchanged and
    # still decides the release; these say which board's paperwork is actually behind.
    for r in rows:
        _v.write("final_gate_%s" % r["board"].lower(),
                 _v.PASS if r["verdict"] == "PASS" else (_v.INCONCLUSIVE if r["verdict"] in ("QUOTE", "HELD") else _v.FAIL),
                 counts={"folder": 1, "stale": int(bool(r["stale"])), "quote": int(bool(r["quote"])),
                         "held": int(bool(r.get("held")))},
                 denominator=1, evidence=[r["summary"][:160]] if r["summary"] else [],
                 inputs={"folder": r["folder"]}, quiet=True,
                 note=("this board is HELD by an open owner decision, so its paperwork is not current and "
                       "cannot be made current while the hold stands" if r.get("held") else
                       "this board's own deliverable folder, judged on its own; the set's verdict is final_gate"))
    for l in missing:
        _v.write("verify_deliverable_%s" % l.lower(), _v.INCONCLUSIVE, counts={"folder": 0}, denominator=0,
                 quiet=True, missing_input="this board has no deliverable folder at all, so nothing was read")
        _v.write("final_gate_%s" % l.lower(), _v.FAIL, counts={"folder": 0}, denominator=1, quiet=True,
                 evidence=["a required board with no deliverable folder"],
                 note="this board has no deliverable folder at all")
    return _v.write("final_gate", res,
                    counts={"pass": len(rows) - len(bad) - len(held), "fail": len(bad), "quote": len(held),
                            "held": len([r for r in rows if r.get("held")]), "missing": len(missing),
                            "contracts_rc": rc_c, "certify_rc": rc_j, "claims_rc": rc_m},
                    denominator=len(want),
                    evidence=evidence,
                    note="deliverable folders re-read today; contracts %s; parts %s; claims %s; %s"
                         % (c_word, j_word, "PASS" if rc_m == 0 else "OPEN", certify.strip()[:80]))


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
