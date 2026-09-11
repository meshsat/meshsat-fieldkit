#!/usr/bin/env python3
"""The ledger: append-only rows, each carrying the hash of the one before.

MESHSAT-862, 11 September 2026, after Territory Grounder's `core/audit/ledger.go:85-105`. Every test here is a way
the chain could be broken, because a ledger that is only tested by appending to it and reading it back is testing
nothing: the whole point is what it does when a row is changed, removed, reordered or the file is rewritten.
"""
import os, sys, json, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import ledger


def _fresh(n=3):
    d = tempfile.mkdtemp(prefix="lg-"); p = os.path.join(d, "l.jsonl")
    for i in range(n): ledger.append(p, {"stage": "route", "board": "B", "i": i})
    return p


def t_a_fresh_chain_verifies():
    ok, n, probs = ledger.verify(_fresh())
    assert ok and n == 3, (ok, n, probs)


def t_the_first_row_chains_to_genesis_and_each_row_to_the_last():
    p = _fresh()
    rows = [json.loads(l) for l in open(p)]
    assert rows[0]["prev_sha"] == ledger.GENESIS, rows[0]
    for a, b in zip(rows, rows[1:]):
        assert b["prev_sha"] == a["sha"], (a["sha"], b["prev_sha"])
        assert b["seq"] == a["seq"] + 1


def t_length_prefixing_makes_the_encoding_injective():
    """Without it `{"a": "bc"}` and `{"ab": "c"}` are one string once the separators are gone, and a ledger whose
    rows can collide is decorative rather than tamper-evident."""
    assert ledger.canonical({"a": "bc"}) != ledger.canonical({"ab": "c"})
    assert ledger.row_sha({"a": "bc"}) != ledger.row_sha({"ab": "c"})
    assert ledger.canonical({"a": 1, "b": 2}) == ledger.canonical({"b": 2, "a": 1}), "key order must not matter"


def t_a_row_edited_in_place_is_caught():
    p = _fresh()
    rows = [json.loads(l) for l in open(p)]
    rows[1]["board"] = "A"                                   # the content changed, the sha did not
    open(p, "w").write("\n".join(json.dumps(r, sort_keys=True) for r in rows) + "\n")
    ok, n, probs = ledger.verify(p)
    assert not ok, probs
    assert any("content changed after it was written" in x for x in probs), probs


def t_a_row_removed_from_the_middle_is_caught():
    p = _fresh(4)
    rows = [json.loads(l) for l in open(p)]
    del rows[2]
    open(p, "w").write("\n".join(json.dumps(r, sort_keys=True) for r in rows) + "\n")
    ok, n, probs = ledger.verify(p)
    assert not ok, probs
    assert any("names prev" in x for x in probs), probs


def t_rows_reordered_are_caught():
    p = _fresh(3)
    rows = [json.loads(l) for l in open(p)]
    rows[0], rows[1] = rows[1], rows[0]
    open(p, "w").write("\n".join(json.dumps(r, sort_keys=True) for r in rows) + "\n")
    ok, n, probs = ledger.verify(p)
    assert not ok, probs


def t_a_whole_file_rewritten_re_chains_cleanly_and_only_the_witness_catches_it():
    """The case the chain alone cannot see, which is why the witness exists."""
    p = _fresh(3)
    _, real_head = ledger.head(p)
    d = os.path.dirname(p); w = os.path.join(d, "w.json")
    json.dump({"seq": 2, "sha": real_head}, open(w, "w"))

    os.remove(p)                                              # rewritten from scratch, different content
    for i in range(3): ledger.append(p, {"stage": "route", "board": "B", "i": i + 100})
    ok, n, probs = ledger.verify(p)
    assert ok, "a rewritten file re-chains cleanly, which is the point of the witness: %s" % probs

    ok2, n2, probs2 = ledger.verify(p, expect_head=real_head)
    assert not ok2, probs2
    assert any("the whole file may have been rewritten" in x for x in probs2), probs2


def t_an_empty_ledger_is_inconclusive_not_intact():
    d = tempfile.mkdtemp(prefix="lg2-"); p = os.path.join(d, "empty.jsonl"); open(p, "w").close()
    ok, n, probs = ledger.verify(p)
    assert n == 0
    import subprocess
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "ledger.py"), "verify", p],
                       capture_output=True, text=True, timeout=60, cwd=d)
    assert r.returncode == 3, (r.returncode, r.stdout + r.stderr)


def t_a_row_cannot_contain_its_own_hash():
    p = _fresh(1)
    r = json.loads(open(p).read().strip())
    assert "sha" in r
    assert ledger.row_sha(r) == r["sha"], "the hash must be over the row without its own sha"
