#!/usr/bin/env python3
"""bench_report: the markdown report of the Freerouting quality programme, generated from results.jsonl and baseline.json only (counts are never typed).

For every board in the results: the baseline row, then every experiment row (config name, verdict, Q, router vias, length, segments, detour, pairs
over 1 mm, autoroute minutes, wall seconds), sorted by Q with INELIGIBLE and no-session rows last. Ends with the knob classification: a knob has an
effect when it moves router vias or length by at least 5 percent against the base config on at least two boards.
Usage: bench_report.py <results.jsonl> <baseline.json> [--out report.md]"""
import sys, json, collections

def arg(name, default=None): return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default

rows0 = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]; base = json.load(open(sys.argv[2]))
last = {}
for r in rows0: last[r["key"]] = r            # the last row per configuration key wins (a re-finished row replaces its predecessor)
rows = list(last.values())
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__))); import bench_compare
for r in rows:                                 # verdicts and Q recomputed from the stored metrics with the current rules, so a rule change needs no re-route
    if r.get("metrics") and r["board_key"] in base:
        v, note, q = bench_compare.compare(base[r["board_key"]], r["metrics"]); r["verdict"], r["note"], r["Q"] = v, note, q
out = ["%d rows (%d configuration keys); verdicts recomputed at report time from the stored metrics" % (len(rows0), len(rows))]
by_board = collections.defaultdict(list)
for r in rows: by_board[r["board_key"]].append(r)
for key in sorted(by_board):
    b = base.get(key, {}); out.append("\n### %s (%d experiment rows; baseline: %s router vias, %s mm, %s segments)\n" % (key, len(by_board[key]), b.get("vias_router", "?"), b.get("length_mm", "?"), b.get("tracks", "?")))
    out.append("| config | pre-route | jar | verdict | Q | router vias | length mm | segments | detour med / p90 | pairs > 1 mm | raw hard / open | stub closed | autoroute min | wall s |"); out.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    def sk(r): return (0 if r.get("verdict") == "MET" else 1 if r.get("verdict") == "REGRESSION" else 2, r.get("Q") if r.get("Q") is not None else 9)
    for r in sorted(by_board[key], key=sk):
        m = r.get("metrics") or {}
        raw = r.get("raw") or {}
        out.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s / %s | %s | %s / %s | %s of %s | %s | %s |" % (r["config"], r["preroute_hash"][:6], (r.get("jar") or "")[12:17], r.get("verdict", "NO_SESSION"), "%.3f" % r["Q"] if r.get("Q") is not None else "-", m.get("vias_router", "-"), m.get("length_mm", "-"), m.get("tracks", "-"), m.get("detour_median", "-"), m.get("detour_p90", "-"), m.get("pairs_over_1mm", "-"), raw.get("hard", "-"), raw.get("unrouted", "-"), r.get("stub_closed", "-"), r.get("stub_open", "-"), m.get("autoroute_minutes", "-"), r.get("wall_s", "-")))
# knob classification: compare each non-base config with the base config of the same board and preroute
out.append("\n### Knob classification (effect = router vias or length moved by at least 5 percent against the base config on at least two boards)\n")
effects = collections.defaultdict(list)
for key, rs in by_board.items():
    bases = {r["preroute_hash"]: r for r in rs if r["config"] == "base" and r.get("metrics")}
    for r in rs:
        if r["config"] == "base" or not r.get("metrics"): continue
        b0 = bases.get(r["preroute_hash"])
        if not b0: continue
        dv = (r["metrics"]["vias_router"] - b0["metrics"]["vias_router"]) / max(1, b0["metrics"]["vias_router"]); dl = (r["metrics"]["length_mm"] - b0["metrics"]["length_mm"]) / max(1e-9, b0["metrics"]["length_mm"])
        effects[r["config"]].append((key, dv, dl, r.get("verdict")))
out.append("| config | boards | router vias delta | length delta | verdicts | class |"); out.append("|---|---|---|---|---|---|")
for cfg, lst in sorted(effects.items()):
    moved = sum(1 for _, dv, dl, _ in lst if abs(dv) >= 0.05 or abs(dl) >= 0.05); harmful = sum(1 for _, _, _, v in lst if v in ("REGRESSION", "INELIGIBLE"))
    cls = "HARMFUL" if harmful == len(lst) else "EFFECT" if moved >= 2 else "NO_EFFECT" if moved == 0 else "WEAK (one board)"
    out.append("| %s | %s | %s | %s | %s | %s |" % (cfg, ", ".join(k for k, _, _, _ in lst), ", ".join("%+.1f%%" % (dv * 100) for _, dv, _, _ in lst), ", ".join("%+.1f%%" % (dl * 100) for _, _, dl, _ in lst), ", ".join(str(v) for _, _, _, v in lst), cls))
# Stage 4 gate (pre-registered, plan of 6 Sep 2026): 2.4.1 must write a session within the timeout on every board, reach at least 1.9.0's completion (finished opens
# and hard after the production finish) and score Q at least 5 percent better on three of five boards with none regressed; otherwise 1.9.0 stays the production jar.
out.append("\n### Stage 4 gate: Freerouting 2.4.1 against 1.9.0 (fr24_plain against fr19_plain per board, no settings block, on the board's newest pre-route; the finish is the production finish)\n")
out.append("| board | 1.9.0 session | 2.4.1 session | 1.9.0 hard / open (raw open) | 2.4.1 hard / open (raw open) | 1.9.0 router vias | 2.4.1 router vias | 1.9.0 Q | 2.4.1 Q | board verdict |"); out.append("|---|---|---|---|---|---|---|---|---|---|")
gate = []
for key in sorted(by_board):
    # the gate is graded on the PLAIN rows (no settings block, the production route) of the board's newest pre-route hash; the "base" rows carry a settings block
    # that costs the design's clearances on the dense boards (6 Sep 2026); they stay in the tables as knob rows
    plain = [r for r in by_board[key] if r["config"] == "fr19_plain"]
    if plain:
        pre = max(plain, key=lambda r: r.get("ts", ""))["preroute_hash"]
        r19 = next((r for r in by_board[key] if r["config"] == "fr19_plain" and r["preroute_hash"] == pre), None); r24 = next((r for r in by_board[key] if r["config"] == "fr24_plain" and r["preroute_hash"] == pre), None)
    else:
        r19 = next((r for r in by_board[key] if r["config"] == "fr19_base"), None); r24 = next((r for r in by_board[key] if r["config"] == "fr24_base"), None)
    if not r19 or not r24: continue
    def cell(r):
        m = r.get("metrics") or {}; raw = r.get("raw") or {}
        return ("yes" if r.get("verdict") != "NO_SESSION" else "NO"), "%s / %s (%s)" % (m.get("hard", "-"), m.get("unrouted", "-"), raw.get("unrouted", "-")), m.get("vias_router", "-"), ("%.3f" % r["Q"]) if r.get("Q") is not None else "-"
    s19, s24 = cell(r19), cell(r24); m19 = r19.get("metrics") or {}; m24 = r24.get("metrics") or {}
    if r24.get("verdict") == "NO_SESSION": v = "FAIL (no session)"
    elif (m24.get("unrouted", 999) > m19.get("unrouted", 999)) or (m24.get("hard", 999) > m19.get("hard", 999)): v = "FAIL (completion below 1.9.0)"
    elif r19.get("Q") is not None and r24.get("Q") is not None: v = "BETTER" if r24["Q"] <= r19["Q"] * 0.95 else "REGRESSED" if r24["Q"] > r19["Q"] else "SAME"
    else: v = "not rankable (a board is INELIGIBLE on both)"
    gate.append(v); out.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (key, s19[0], s24[0], s19[1], s24[1], s19[2], s24[2], s19[3], s24[3], v))
if gate:
    fails = sum(1 for v in gate if v.startswith("FAIL")); better = sum(1 for v in gate if v == "BETTER"); regressed = sum(1 for v in gate if v == "REGRESSED")
    out.append("\nGate verdict: %s (%d boards: %d FAIL, %d BETTER, %d REGRESSED; the gate needs 0 FAIL, 0 REGRESSED and BETTER on at least 3)." % ("PASS, 2.4.1 may become the production jar" if fails == 0 and regressed == 0 and better >= 3 else "NOT MET, 1.9.0 stays the production jar", len(gate), fails, better, regressed))
text = "# Freerouting quality programme: experiment report (generated %s)\n" % __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M") + "\n".join(out) + "\n"
if arg("--out"): open(arg("--out"), "w").write(text)
print(text)
