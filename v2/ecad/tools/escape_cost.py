#!/usr/bin/env python3
"""What the decoupling seats cost the escape pass, per part and per cause (decision 42, T4; MESHSAT-1357).

Decision 42 opens the escape fan in two places and admits a third seat, and each is allowed only while it costs no
escape the part needs (DECOUPLING.md section 6, D3, R2 and D5):

  window     a class D or L capacitor, on the part's own side, declared against the part itself: its own-pin window
  stage      a converter's own power-stage parts inside that converter's fan: its class R capacitors, and the
             capacitors and parts of the power loops declared for it
  far_side   a declared capacitor on the side OPPOSITE the part, whichever part it is declared against (on D12,
             C15 and C16 serve U4 and sit inside U7's fan)

So the escape pass has to say, per part, which refused escapes it would have laid without each. It does not
estimate that: `escape.py` hands over, for every pad it refused, the exact probes of every attempt it made (the
via and the points of its track, with their radii and the lane rule of that attempt), and `ask()` puts the same
probes to the same `clear()` with one cause's parts left out. A pad is LOST TO a cause when an attempt that was
refused passes without that cause's parts, and to nothing here when no cause changes the answer.

A part the escape pass does not escape has no refused escape to count, and D5 asks about it all the same: a
far-side capacitor under a SOT-23-5 or an SOIC-8 can take a via site of that part's pins, and nothing reserves one
there. `pin_sites()` answers with the sites this pass would have used for a part of that pitch.

This file holds no KiCad call. `escape.py` gives it the board's facts as plain data:
    cost = escape_cost.Cost(intent, side_of)        side_of: reference -> "F" or "B" (None when not on the board)
    cost.ask(part, pad, tried, clear)               tried: [(lane, [(point, radius), ...]), ...]
    cost.pin_sites(part, pad, sites, clear)         sites: [(point, radius)], the standard sites at one pin
    cost.site_refused(part, by_ref)                 a via site of an exposed pad refused by `by_ref`'s pad
    cost.lines()                                    what to print
    cost.record(part_at)                            the JSON escape.py writes beside the board, with `close`

WHAT IS CLOSED AGAIN (D3 and T4: "A window that costs an escape the part needs is closed again", "An R2 opening that
costs an escape the converter needs is closed again for the part that costs it"). For a pad lost to a cause, each of
that cause's parts is asked alone: the parts whose absence alone lets an attempt pass are the ones that cost it. When
no single part does, every part of the cause is named, because together they cost it. `record()` lists them under
`close`, window and stage, each with the part whose escape it cost and where that part stood; the placers
(`bypass_search.Context`) read the list on the next placement and seat those capacitors with that one opening shut,
while the part stands where it stood (a moved part makes the entry stale, and a stale entry is said and not applied)."""

CAUSES = ("window", "stage", "far_side")
WHAT = {"window": "its own-pin windows (D3)", "stage": "its own power-stage parts inside its fan (R2)",
        "far_side": "declared capacitors on the side opposite it (D5)"}


class Cost:
    def __init__(self, intent, side_of):
        self.side_of = side_of
        self.window, self.stage, self.caps = {}, {}, set()
        self.lost, self.other, self.sites, self.pins = {}, {}, {}, {}
        self.culprits = {}
        self.declared = 0
        it = intent or {}
        for e in it.get("bypass", []) or []:
            cap, part, k = e.get("cap"), e.get("part"), e.get("class")
            if not cap or not part: continue
            self.declared += 1; self.caps.add(cap)
            if k in ("D", "L"): self.window.setdefault(part, set()).add(cap)
            elif k == "R": self.stage.setdefault(part, set()).add(cap)
        for lp in it.get("power_loops", []) or []:
            conv = lp.get("converter")
            if not conv: continue
            for r in lp.get("caps") or []: self.caps.add(r)
            self.stage.setdefault(conv, set()).update(list(lp.get("caps") or []) + list(lp.get("parts") or []))

    def refs(self, part, cause):
        """The references whose pads are left out when `cause` is asked of `part`."""
        ps = self.side_of(part)
        if ps is None: return set()
        if cause == "far_side":
            return {c for c in self.caps if self.side_of(c) not in (None, ps)}
        own = (self.window if cause == "window" else self.stage).get(part, set())
        return {r for r in own if self.side_of(r) == ps}

    def ask(self, part, pad, tried, clear):
        """The cause a refused pad is lost to, or None. `clear(point, radius, lane, ignore)` is escape.py's own
        test with `ignore` left out of its pads; an attempt passes when every one of its probes is clear."""
        def passes(ignore):
            return any(all(clear(pt, r, lane, ignore) for pt, r in probes) for lane, probes in tried)
        for cause in CAUSES:
            refs = self.refs(part, cause)
            if not refs: continue
            if passes(refs):
                self.lost.setdefault(part, {}).setdefault(cause, []).append(str(pad))
                # each part asked alone only where something is closed again on the answer (window, stage): a
                # far-side cause is reported, not closed, and its parts are every declared capacitor of the other
                # side of the board, which would be one more question per capacitor for every pad it cost
                alone = [x for x in sorted(refs) if passes({x})] if cause in ("window", "stage") and len(refs) > 1 else []
                self.culprits.setdefault(part, {}).setdefault(cause, set()).update(alone or refs)
                return cause
        self.other.setdefault(part, []).append(str(pad)); return None

    def pin_sites(self, part, pad, sites, clear, lane=0.75):
        """For a part the escape pass leaves to the router: how many of the standard via sites at one pin are
        refused only because of a far-side declared capacitor. Returns that count."""
        refs = self.refs(part, "far_side")
        if not refs: return 0
        n = 0
        for pt, r in sites:
            if not clear(pt, r, lane, None) and clear(pt, r, lane, refs): n += 1
        if n:
            d = self.pins.setdefault(part, {}); d[str(pad)] = (n, len(sites))
        return n

    def site_refused(self, part, by_ref):
        """A thermal via site of `part`'s exposed pad was refused by a pad of `by_ref`: counted when `by_ref` is a
        declared capacitor on the side opposite `part`."""
        if by_ref in self.refs(part, "far_side"):
            d = self.sites.setdefault(part, {}); d[by_ref] = d.get(by_ref, 0) + 1; return True
        return False

    def closing(self):
        """{"window": {capacitor: [parts whose escape its window cost]}, "stage": {part: [converters]}}."""
        out = {"window": {}, "stage": {}}
        for part, d in self.culprits.items():
            for cause in ("window", "stage"):
                for ref in d.get(cause, ()):
                    out[cause].setdefault(ref, []).append(part)
        return {k: {r: sorted(v) for r, v in sorted(d.items())} for k, d in out.items()}

    def record(self, part_at=None):
        """The cost as data, for the file escape.py writes beside the board (`out/<stem>-escape-cost.json`).
        `part_at(ref)` gives (x nm, y nm, orientation degrees, side) of a part, so a reader can tell a stale entry."""
        at = part_at or (lambda r: None)
        cl = self.closing()
        return {"what": "what the declared decoupling seats cost the escape pass, per part and cause (decision 42, T4)",
                "declared": self.declared,
                "lost": {p: {c: list(v) for c, v in d.items()} for p, d in sorted(self.lost.items())},
                "culprits": {p: {c: sorted(v) for c, v in d.items()} for p, d in sorted(self.culprits.items())},
                "close": {k: [{"ref": r, "cost": parts, "parts_at": {q: at(q) for q in parts}} for r, parts in d.items()]
                          for k, d in cl.items()},
                "far_side_sites": {p: d for p, d in sorted(self.sites.items())},
                "far_side_pins": {p: {k: list(v) for k, v in d.items()} for p, d in sorted(self.pins.items())},
                "other": {p: list(v) for p, v in sorted(self.other.items())}}

    def lines(self):
        out = []
        n_lost = sum(len(v) for d in self.lost.values() for v in d.values())
        out.append("escape: decoupling cost: %d refused pad(s) would have been escaped without a declared seat "
                   "(%d declaration(s) read); %d refused for another reason"
                   % (n_lost, self.declared, sum(len(v) for v in self.other.values())))
        for p in sorted(set(self.lost) | set(self.sites) | set(self.pins)):
            for cause in CAUSES:
                pads = (self.lost.get(p) or {}).get(cause) or []
                if pads:
                    out.append("escape: %s lost %d escape(s) to %s: pad(s) %s; the parts that cost them: %s"
                               % (p, len(pads), WHAT[cause], ", ".join(pads[:12]) + (" ..." if len(pads) > 12 else ""),
                                  ", ".join(sorted((self.culprits.get(p) or {}).get(cause) or self.refs(p, cause)))[:160]))
            for ref, n in sorted((self.sites.get(p) or {}).items()):
                out.append("escape: %s had %d via site(s) of its exposed pad refused by the far-side capacitor %s (D5)"
                           % (p, n, ref))
            pins = self.pins.get(p) or {}
            if pins:
                full = sorted(k for k, (n, m) in pins.items() if n == m)
                out.append("escape: %s is left to the router, and far-side declared capacitors refuse %d of the via "
                           "site(s) at %d of its pins (D5); pins with every site refused: %s"
                           % (p, sum(n for n, m in pins.values()), len(pins), ", ".join(full) or "none"))
        cl = self.closing()
        if cl["window"] or cl["stage"]:
            out.append("escape: closed again for the next placement (D3, T4): %s"
                       % "; ".join("%s's %s" % (r, "own-pin window" if k == "window" else "opening in its converter's fan")
                                   for k in ("window", "stage") for r in cl[k])[:400])
        return out
