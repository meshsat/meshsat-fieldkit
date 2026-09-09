#!/usr/bin/env python3
"""Keep the stub router's good closures, drop only the ones a DRC finds in a hard violation (7 Sep 2026: every finish used to revert ALL closures when one hurt,
so A22 lost 8 good closures over one bad one, E6 6 over 2). Usage: stub_accept.py <board before the stub router> <board after> <drc.json of the board after>.
Writes the "after" board with the offending closures removed; prints how many closures stayed."""
import sys, json, math, pcbnew
HARD = ("clearance", "shorting_items", "tracks_crossing", "hole_clearance", "hole_to_hole", "copper_edge_clearance")
pre, post, drc = pcbnew.LoadBoard(sys.argv[1]), pcbnew.LoadBoard(sys.argv[2]), json.load(open(sys.argv[3]))
old = {t.m_Uuid.AsString() for t in pre.GetTracks()}
added = {t.m_Uuid.AsString(): t for t in post.GetTracks() if t.m_Uuid.AsString() not in old}
if not added: print("stub_accept: nothing added"); sys.exit(0)
def ends(t): return [t.GetPosition()] if t.GetClass() == "PCB_VIA" else [t.GetStart(), t.GetEnd()]
def closure(t):
    """every added item of the same net chained to t (end to end within 20 um)"""
    out = {t.m_Uuid.AsString(): t}; frontier = [t]
    while frontier:
        cur = frontier.pop()
        for u, o in added.items():
            if u in out or o.GetNetCode() != cur.GetNetCode(): continue
            if any(math.hypot(e.x - f.x, e.y - f.y) < 20000 for e in ends(cur) for f in ends(o)): out[u] = o; frontier.append(o)
    return out
bad = set()
for v in drc.get("violations", []):
    if v["type"] not in HARD: continue
    for it in v.get("items", []):
        u = it.get("uuid", "")
        if u in added: bad.update(closure(added[u]).keys())
    if not any(it.get("uuid", "") in added for it in v.get("items", [])):
        # the violation names no added item by uuid: fall back to position (an added item within 60 um of the reported point)
        for it in v.get("items", []):
            x, y = it["pos"]["x"] * 1e6, it["pos"]["y"] * 1e6
            for u, o in added.items():
                if any(math.hypot(e.x - x, e.y - y) < 60000 for e in ends(o)): bad.update(closure(o).keys())
# 9 September 2026 (E7, appendix 32.89): a closure whose item count is out of proportion to the net it closes is not a
# closure, it is carpeting. E's board-wide stub run added 29,985 items for five open nets, and the quality pass could not
# digest them: an hour into straighten.py the finish had produced no verdict and was killed. A net's closure is refused
# here when it costs more than STUB_MAX_ITEMS (default 400) items, which is far above any honest stub (the accepted ones
# on A24 and D10 are tens of items) and far below a carpet. STUB_MAX_ITEMS=0 turns the rule off.
_cap = int(__import__("os").environ.get("STUB_MAX_ITEMS", "400"))
_bynet = {}
for u, t in added.items(): _bynet.setdefault(t.GetNetCode(), set()).add(u)
_fat = [n for n, g in _bynet.items() if _cap and len(g) > _cap]
for n in _fat:
    bad.update(_bynet[n])
    print("stub_accept: net %d refused, its closure costs %d items (cap %d): that is carpeting, not a closure" % (n, len(_bynet[n]), _cap))
for u in bad: post.Remove(added[u])
groups = {}
for u, t in added.items(): groups.setdefault(t.GetNetCode(), set()).add(u)
kept = sum(1 for g in groups.values() if not (g & bad)); dropped = sum(1 for g in groups.values() if g & bad)
pcbnew.SaveBoard(sys.argv[2], post)
print("stub_accept: %d closure nets kept, %d dropped (%d items removed of %d added)" % (kept, dropped, len(bad), len(added)))
