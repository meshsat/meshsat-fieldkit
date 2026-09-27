#!/usr/bin/env python3
"""Evidence about a board this directory no longer holds is not evidence (MESHSAT-862, 17 September 2026).

WHY. A phase directory holds ONE board and its `routed/` snapshot holds the verdicts about it. When a new
board is adopted into that directory, the chain that produced it writes its own verdicts and everything the
PREVIOUS board's sweep left behind stays, beside a board it was never taken on. `rules_status` reads the
directory, cannot tell the two apart unless the verdict names its board, and answers the registry's question
with the older reading. Board B's snapshot carries a gate reading taken on the 951-footprint B19 board while
the design being routed is the 957-footprint B21; nothing in either file says which board it is about.

WHAT IT REMOVES, and nothing else: a verdict that decides a BOARD-SPECIFIC rule (one whose evidence_scope
names board_sha256 in the registry, 29 of the 57) and that does not name the board this directory holds. A
verdict that names no board is removed only with --unnamed, because until 17 September no gate named one and
removing all of them would throw away the evidence of every board cut before today.

WHAT IT NEVER REMOVES: a set-level verdict (the contracts, the parts certification, the energy chain, the
final gate, the order set), because those are judged on the netlists and the folders and are as true beside
one board as another; and anything whose rules the registry does not call board-specific.

Usage: prune_stale_evidence.py <project dir> [--apply] [--unnamed] [--json]
Nothing is deleted without --apply: the default is the list.
"""
import os, sys, json, glob, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rules_lib as R
import rules_status as _S
import verdict as _v


def board_specific_verdicts(cov=None, rules=None):
    """{verdict name} that decides at least one rule whose evidence is about a particular board."""
    cov = cov or (R._yaml().safe_load(open(os.path.join(HERE, "pcb_rules_coverage.yaml"))) or {}).get("coverage", {})
    by = rules or R.by_id(R.load())
    out = set()
    for rid, row in cov.items():
        rule = by.get(rid) or {}
        if "board_sha256" not in (rule.get("evidence_scope") or []): continue
        names = ((row.get("verification") or {}).get("verdict") or "")
        for n in names.split(","):
            n = n.strip()
            if not n: continue
            if "<letter>" in n:
                # `check_pcb_<letter>` and `energy_chain_<letter>`: the registry's way of writing one verdict
                # per board. Expanded here, because the file on disk is check_pcb_d and the rule is about
                # exactly one board's own.
                for L in ("a", "b", "c", "d", "e", "e5", "p"): out.add(n.replace("<letter>", L))
            elif "<" not in n:
                out.add(n)
    return out


def sha16(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()[:16]


def named_board(rec):
    b = (rec.get("inputs") or {}).get("board")
    if isinstance(b, dict): return b.get("sha256_16")
    if isinstance(b, str) and b.strip(): return b.strip().lower()
    return None


def _letter_of_dir(project_dir):
    """The letter whose project this directory is, from the readiness manifest.

    The manifest is the place that says which project belongs to which board, and it names board E5, which has
    no chain and so no boards/e5.json: E5 is the board whose own sensitive_nodes verdict this tool called
    stale the first time it ran."""
    base = os.path.basename(os.path.abspath(project_dir).rstrip("/"))
    try:
        m = json.load(open(os.path.join(HERE, "readiness_manifest.json"), encoding="utf-8"))
    except (ValueError, OSError):
        return ""
    best = ""
    for letter, row in (m.get("boards") or {}).items():
        proj = row.get("project") or ""
        if proj and base.startswith(proj) and len(proj) > len(best):
            best, out = proj, str(letter).lower()
    return out if best else ""


def judge(project_dir, unnamed=False):
    """(stale, kept, unknown): which verdict files in <project>/routed are about another board."""
    # ONE ANSWER TO "WHICH BOARDS DOES THIS DIRECTORY HOLD", and it is `rules_status`'s, because that is the
    # reader whose question this tool exists to keep honest. It constructs the board's path from the board
    # table rather than globbing the directory (a tool that globs takes whichever board ran last, the
    # 11 September trap), and it counts the LETTER as an identity, because a gate given `--board d` writes "d"
    # where another writes a sha and both are saying which board they judged.
    letter = _letter_of_dir(project_dir)
    if not letter:
        # A DIRECTORY NOBODY CAN NAME IS NOT A DIRECTORY TO DELETE FROM. Without this the tool has no
        # identities to compare against, so every verdict that names its board reads as another board's and
        # the whole snapshot is offered for removal: absence must never become a deletion any more than it
        # becomes a pass.
        return [], [], [(os.path.basename(os.path.abspath(project_dir).rstrip("/")),
                         "the readiness manifest names no board for this directory, so nothing was judged")]
    # The board's path is CONSTRUCTED from the manifest's project name, never globbed: a tool that globs a
    # project directory takes whichever board ran last (11 September). The letter counts as an identity
    # because a gate given `--board d` writes "d" where another writes a sha.
    proj = ((_S.manifest().get("boards") or {}).get(letter) or {}).get("project") or ""
    here = {letter}
    for cand in (os.path.join(project_dir, proj + ".kicad_pcb"),
                 os.path.join(project_dir, "routed", proj + ".kicad_pcb")):
        if os.path.isfile(cand): here.add(sha16(cand))
    names = board_specific_verdicts()
    stale, kept, unknown = [], [], []
    for p in sorted(glob.glob(os.path.join(project_dir, "routed", "*.verdict.json"))):
        tool = os.path.basename(p)[:-len(".verdict.json")]
        base = tool.rsplit("_", 1)[0] if tool.rsplit("_", 1)[-1] in ("a", "b", "c", "d", "e", "e5", "p") else tool
        if not (tool in names or base in names): kept.append((tool, "not board-specific")); continue
        try: rec = json.load(open(p, encoding="utf-8"))
        except Exception: unknown.append((tool, "unreadable")); continue
        nb = named_board(rec)
        if nb is None:
            (stale if unnamed else unknown).append((tool, "names no board"))
        elif nb in here:
            kept.append((tool, "names this board"))
        else:
            stale.append((tool, "taken on board %s" % nb))
    return stale, kept, unknown


def main(argv):
    if not argv or argv[0].startswith("-"): print(__doc__); return 2
    d = argv[0]
    stale, kept, unknown = judge(d, unnamed="--unnamed" in argv)
    print("prune_stale_evidence: %s | %d about another board, %d about this one, %d board-specific and anonymous"
          % (os.path.basename(d.rstrip("/")), len(stale), len([k for k in kept if k[1] == "names this board"]),
             len(unknown)))
    for t, why in stale[:20]: print("  STALE %-36s %s" % (t, why))
    for t, why in unknown[:10]: print("  ANON  %-36s %s (kept: no gate named its board before 17 September)" % (t, why))
    if "--apply" in argv:
        for t, _why in stale:
            os.remove(os.path.join(d, "routed", t + ".verdict.json"))
        print("  removed %d file(s)" % len(stale))
    if "--json" in argv: print(json.dumps(dict(stale=stale, kept=kept, unknown=unknown), indent=1))
    return 0


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
