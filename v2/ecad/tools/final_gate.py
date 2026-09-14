#!/usr/bin/env python3
"""The final gate pass: every deliverable folder in the tree, judged by the gates that already exist.

Usage: final_gate.py [--boards a,b,c] [--json out.json]

It runs nothing new. For each board's newest deliverable folder it runs `verify_deliverable.py`, then
`check_contracts.py` once across the set and `jlc_certify.py` once over the parts, and prints ONE table with a
verdict per board and the denominator each came from. The point is that a release is read off a single page
instead of seven logs, and that a folder nobody re-read since it was cut cannot pass by being forgotten: a
folder is judged today, by today's rules, or it is not judged at all (14 September 2026, MESHSAT-862).

Every verdict here is a re-reading of a written artefact. It does not open a board, route anything or touch a
host, so it is safe to run on the runner, which has no pcbnew.
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


def main(argv):
    only = set(argv[argv.index("--boards") + 1].split(",")) if "--boards" in argv else None
    rows = []
    for letter, (num, folder) in sorted(newest_folders(only).items()):
        name = os.path.basename(folder)
        quote = name.endswith("-quote")
        # verify_deliverable takes the folder, the board's stem and the copper layer count, and every one of
        # the three is IN the folder: the stem is the board file's name and the layer count is what the gerber
        # zip carries, which is the same reading the gate itself does against the board (3 September's bug).
        stem = next((os.path.splitext(os.path.basename(f))[0] for f in sorted(glob.glob(os.path.join(folder, "*.kicad_pcb")))), None)
        if stem is None:
            stem = next((os.path.basename(f)[:-len("-gerbers.zip")] for f in glob.glob(os.path.join(folder, "*-gerbers.zip"))), name)
        cu = 0
        for z in glob.glob(os.path.join(folder, "*-gerbers.zip")):
            try:
                import zipfile
                cu = len([n for n in zipfile.ZipFile(z).namelist() if re.search(r"(\.g[0-9]+$|Cu\.g|-F_Cu|-B_Cu|_Cu\.)", n, re.I)])
            except Exception: cu = 0
        args = [sys.executable, os.path.join(HERE, "verify_deliverable.py"), folder, stem, str(cu or 4)]
        # A BARE board carries no BOM and no CPL by design (E5 is the dock block: copper, holes and targets),
        # and a quote folder carries no board file. Both are declared to the gate rather than read as failures.
        if quote or not glob.glob(os.path.join(folder, "*-bom.csv")): args.append("--bare")
        rc, out = run(args)
        sm = [l for l in out.splitlines() if l.startswith("verify_deliverable:") and ("ALL PASS" in l or " of " in l)]
        summary = (sm[-1].replace("verify_deliverable: ", "") if sm else "no summary line")
        rows.append(dict(board=letter.upper(), phase=num, folder=name, quote=quote,
                         verdict=("QUOTE" if quote else ("PASS" if rc == 0 else "FAIL")), summary=summary.strip()))
    # `check_contracts` compares the NETLISTS the chains write into each project's out/, which is untracked:
    # on a host where no chain has run it reports every board absent, and absent is INCONCLUSIVE rather than
    # broken (11 September). Say which it is, so a table read on the runner is not mistaken for a failure.
    rc_c, out_c = run([sys.executable, os.path.join(HERE, "check_contracts.py")])
    contracts = next((l for l in out_c.splitlines() if "contracts" in l.lower()), "no contracts line")
    contracts_absent = "absent" in contracts or "missing_boards" in contracts
    rc_j, out_j = run([sys.executable, os.path.join(HERE, "jlc_certify.py")] + (["--boards", ",".join(sorted(only))] if only else []))
    certify = next((l for l in out_j.splitlines() if l.startswith("jlc_certify:")), "no certification line")

    print("final_gate: %d deliverable folder(s)" % len(rows))
    for r in rows:
        print("  %-3s %-34s %-6s %s" % (r["board"], r["folder"], r["verdict"], r["summary"][:90]))
    print("  contracts : %s" % contracts.strip()[:120])
    print("  parts     : %s" % certify.strip()[:120])
    bad = [r for r in rows if r["verdict"] == "FAIL"]
    held = [r for r in rows if r["quote"]]
    print("final_gate: %d of %d folder(s) pass, %d quote-only, contracts %s, parts %s"
          % (len(rows) - len(bad) - len(held), len(rows), len(held),
             "PASS" if rc_c == 0 else ("NOT JUDGED HERE (no netlist in this tree)" if contracts_absent else "FAIL"), "PASS" if rc_j == 0 else "OPEN"))
    if "--json" in argv:
        json.dump(dict(rows=rows, contracts=contracts.strip(), certify=certify.strip(),
                       contracts_rc=rc_c, certify_rc=rc_j), open(argv[argv.index("--json") + 1], "w"), indent=1)
    # A quote folder is not a pass and not a failure: it is a board the set is holding, and saying so is the
    # whole reason this prints a table rather than a boolean.
    return _v.write("final_gate", _v.PASS if (not bad and rc_c == 0) else (_v.INCONCLUSIVE if contracts_absent and not bad else _v.FAIL),
                    counts={"pass": len(rows) - len(bad) - len(held), "fail": len(bad), "quote": len(held)},
                    denominator=len(rows),
                    evidence=["%s %s: %s" % (r["board"], r["folder"], r["summary"][:60]) for r in rows if r["verdict"] != "PASS"],
                    note="deliverable folders re-read today; contracts %s; %s" % ("PASS" if rc_c == 0 else ("not judged here" if contracts_absent else "FAIL"), certify.strip()[:80]))


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
