#!/usr/bin/env python3
"""The standing check over every chained ledger in a tree (MESHSAT-862, stage 1).

`ledger.py verify` re-walks one chain and returns a tuple; `routeflow.py selftest` exercises it on three rows it
makes up. Neither produces a verdict for the channel the supervisor decides on, and neither looks at the ledgers
this project has actually written.

Its first version globbed every .jsonl under the tree and called the benchmark results table 708 broken rows.
That file carries no chain and never claimed one, and a checker that calls an unchained file a broken chain is
crying wolf at the one place a real break has to be visible.
"""
import os, sys, json, tempfile, shutil, subprocess

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import ledger


def _tree(rows=3, tamper=False, chained=True):
    d = tempfile.mkdtemp(prefix="ledger-verify-")
    out = os.path.join(d, "pcb-x", "out", "routeflow"); os.makedirs(out)
    p = os.path.join(out, "journal.jsonl")
    if chained:
        for i in range(rows): ledger.append(p, {"stage": "t", "n": i})
        if tamper:
            lines = open(p).read().splitlines()
            r = json.loads(lines[1]); r["n"] = 99; lines[1] = json.dumps(r, sort_keys=True)
            open(p, "w").write("\n".join(lines) + "\n")
    else:
        with open(p, "w") as f:
            for i in range(rows): f.write(json.dumps({"n": i}) + "\n")
    return d, p


def _run(d, *extra):
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "ledger_verify.py"), d, *extra],
                       capture_output=True, text=True, cwd=d)
    return r.returncode, r.stdout + r.stderr


def t_a_sound_chain_passes_and_counts_its_rows():
    d, _ = _tree(4)
    rc, out = _run(d); shutil.rmtree(d, ignore_errors=True)
    assert rc == 0, out
    assert "4 row(s) OK" in out, out


def t_a_row_edited_after_the_fact_fails():
    d, _ = _tree(4, tamper=True)
    rc, out = _run(d); shutil.rmtree(d, ignore_errors=True)
    assert rc == 1, out
    assert "content changed after it was written" in out, out


def t_a_file_with_no_chain_is_not_called_a_broken_chain():
    d, _ = _tree(3, chained=False)
    rc, out = _run(d); shutil.rmtree(d, ignore_errors=True)
    assert "carries no chain" in out, out
    assert "content changed" not in out, out
    assert rc == 3, (rc, out)   # nothing chained was found, which is INCONCLUSIVE and never a pass


def t_no_ledger_at_all_is_inconclusive_not_a_pass():
    d = tempfile.mkdtemp(prefix="ledger-verify-empty-")
    rc, out = _run(d); shutil.rmtree(d, ignore_errors=True)
    assert rc == 3, (rc, out)
    assert "nothing was re-walked" in out, out


def t_a_witness_catches_a_whole_file_rewrite():
    """Rows reordered or replaced wholesale still chain to each other; only a head recorded elsewhere catches it."""
    d, p = _tree(4)
    rc, out = _run(d, "--witness"); assert rc == 0, out
    assert os.path.exists(p + ".witness.json"), out
    os.remove(p)
    for i in range(4): ledger.append(p, {"stage": "t", "n": i + 100})   # a different history, internally sound
    rc2, out2 = _run(d); shutil.rmtree(d, ignore_errors=True)
    assert rc2 == 1, out2
    assert "the witness says" in out2, out2


def t_a_file_that_starts_chained_and_continues_unchained_is_not_a_ledger():
    """is_ledger looked only at the first row. A file that starts chained and continues unchained is neither a
    ledger nor a plain table, and calling it a ledger turns its whole tail into false breaks."""
    d, p = _tree(2)
    with open(p, "a") as f: f.write(json.dumps({"n": 99}) + "\n")   # one unchained row appended
    rc, out = _run(d); shutil.rmtree(d, ignore_errors=True)
    assert "carries no chain" in out, out
    assert "content changed" not in out and "names prev" not in out, out
    assert rc == 3, (rc, out)
