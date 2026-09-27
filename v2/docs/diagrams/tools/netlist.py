#!/usr/bin/env python3
"""Read the committed KiCad netlists of the V2 carrier set (MESHSAT-1357, handover layer 4, 27 September 2026).

Stdlib only, runner-safe: no KiCad import. The netlists are KiCad 9's `kicadsexpr` export ("(export (version "E") ...")
that each board's generator chain writes to `v2/ecad/pcb-*/out/*.net`. Every diagram tool in this folder reads the design
from here, so a diagram is derived from the artefact and not typed from a document.

Also carries the pin maps of the logic parts the control-line diagram follows through, each from a maker's sheet held
in `v2/vendor/` (cited per entry), and `sha16()`, the identity every generated file records for each input it read."""
import hashlib, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
ECAD = os.path.join(REPO, "v2", "ecad")

# the committed netlist of each schematic board (E5 has no schematic: its board file is its design)
BOARDS = {
    "A": "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net",
    "B": "v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net",
    "C": "v2/ecad/pcb-c-display-c8/out/pcb-c-display.net",
    "D": "v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs.net",
    "E": "v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net",
    "P": "v2/ecad/pcb-p-pack-p2/out/pcb-p-pack.net",
}
BOARD_TITLES = {"A": "A power and I/O", "B": "B compute", "C": "C panel backer", "D": "D VHF APRS",
                "E": "E dock strip", "E5": "E5 dock block", "P": "P pack BMS"}

# Logic gates: value prefix -> list of (inputs, output) pin numbers, and the held sheet that states them.
GATES = {
    "SN74LVC08APWR": ([((1, 2), 3), ((4, 5), 6), ((9, 10), 8), ((12, 13), 11)],
                      "v2/vendor/ti/ti-sn74lvc08a-quad-and.pdf, Table 4-1 (TSSOP column)"),
    "SN74LVC32APWR": ([((1, 2), 3), ((4, 5), 6), ((9, 10), 8), ((12, 13), 11)],
                      "v2/vendor/ti/ti-sn74lvc32a-quad-or.pdf, Table 4-1 (PW column)"),
    "74LVC1G08": ([((1, 2), 4)], "v2/vendor/techpublic/techpublic-74lvc1g08gv-c19829591.pdf, pin configuration (SOT23-5)"),
    "74LVC1G17": ([((2,), 4)], "v2/vendor/diodes/diodes-74lvc1g17.pdf, pin assignments (SOT25: 2 A, 4 Y)"),
    "74LVC1G06": ([((2,), 4)], "v2/vendor/ti/ti-sn74lvc1g06.pdf, Table 4-1 (DBV: 2 A, 4 Y)"),
    "74LVC1G34": ([((2,), 4)], "v2/vendor/diodes/diodes-74lvc1g34.pdf, pin assignments (SOT25: 2 A, 4 Y)"),
    "SN74LVC1G00DBVR": ([((1, 2), 4)], "v2/vendor/ti/ti-sn74lvc1g00.pdf, pin functions (DBV: 1 A, 2 B, 4 Y)"),
}


def sha16(relpath):
    """First 16 hex characters of the file's sha256, the identity the tree's records use."""
    with open(os.path.join(REPO, relpath), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def git_rev(paths=None):
    """The commit the working tree was checked out at, and which of `paths` (the files a tool read) differ from it."""
    paths = list(paths) if paths is not None else ["v2/ecad", "v2/docs/ARCHITECTURE.md", "v2/docs/review-packets",
                                                   "v2/vendor/peli", "v2/docs/CASE-MARGINS.md"]
    try:
        head = subprocess.run(["git", "-C", REPO, "rev-parse", "--short=8", "HEAD"], capture_output=True, text=True).stdout.strip()
        dirty = [p for p in paths if modified(p)]
        return head, dirty
    except OSError:
        return "unknown", paths


def tree_line(head, dirty):
    """The sentence a generated page states about the tree it read."""
    return "Tree read at `%s`%s." % (head, "" if not dirty else "; these inputs differed from it (not a committed state): " +
                                      ", ".join("`%s`" % p for p in dirty))


def modified(relpath):
    """True when the working file differs from the checked-out commit (or is not tracked)."""
    try:
        r = subprocess.run(["git", "-C", REPO, "status", "--porcelain", "--", relpath], capture_output=True, text=True)
        return bool(r.stdout.strip())
    except OSError:
        return True


def last_commit(relpath):
    try:
        return subprocess.run(["git", "-C", REPO, "log", "-1", "--format=%h", "--", relpath],
                              capture_output=True, text=True).stdout.strip() or "uncommitted"
    except OSError:
        return "unknown"


def _tokens(s):
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c in "()":
            yield c; i += 1
        elif c.isspace():
            i += 1
        elif c == '"':
            j, buf = i + 1, []
            while s[j] != '"':
                if s[j] == "\\":
                    buf.append(s[j + 1]); j += 2
                else:
                    buf.append(s[j]); j += 1
            yield ("S", "".join(buf)); i = j + 1
        else:
            j = i
            while j < n and s[j] not in '() \t\r\n"':
                j += 1
            yield ("A", s[i:j]); i = j


def _parse(s):
    st = [[]]
    for t in _tokens(s):
        if t == "(":
            st.append([])
        elif t == ")":
            x = st.pop(); st[-1].append(x)
        else:
            st[-1].append(t[1])
    return st[0][0]


def _find(node, key):
    return [x for x in node if isinstance(x, list) and x and x[0] == key]


def _val(node, key):
    f = _find(node, key)
    return f[0][1] if f and len(f[0]) > 1 else None


class Netlist:
    """One board's netlist: parts (ref -> value, footprint, properties) and nets (name -> nodes)."""

    def __init__(self, board):
        self.board = board
        self.path = BOARDS[board]
        self.sha = sha16(self.path)
        self.commit = last_commit(self.path) + (" plus uncommitted changes" if modified(self.path) else "")
        t = _parse(open(os.path.join(REPO, self.path), encoding="utf-8").read())
        self.parts = {}
        for c in _find(_find(t, "components")[0], "comp"):
            props = {_val(p, "name"): _val(p, "value") for p in _find(c, "property")}
            self.parts[_val(c, "ref")] = dict(value=_val(c, "value") or "", footprint=_val(c, "footprint") or "", props=props)
        self.nets, self.pins, self.fn = {}, {}, {}
        for n in _find(_find(t, "nets")[0], "net"):
            name = _val(n, "name")
            nodes = [dict(ref=_val(d, "ref"), pin=_val(d, "pin"), fn=_val(d, "pinfunction"), type=_val(d, "pintype"))
                     for d in _find(n, "node")]
            self.nets[name] = nodes
            for d in nodes:
                self.pins.setdefault(d["ref"], {})[d["pin"]] = name
                self.fn[(d["ref"], d["pin"])] = d["fn"]

    def net(self, name):
        """The nodes of a net, accepting the name with or without KiCad's leading '/' for a local label."""
        for k in (name, "/" + name.lstrip("/"), name.lstrip("/")):
            if k in self.nets:
                return k, self.nets[k]
        return None, []

    def value(self, ref):
        return self.parts.get(ref, {}).get("value", "")

    def mpn(self, ref):
        """The part's identity as the value text leads with it (the generators write the MPN or the part class first)."""
        v = self.value(ref)
        return re.split(r"[ :,(]", v, 1)[0] if v else ""

    def other_pin_nets(self, ref, pin):
        return {p: n for p, n in self.pins.get(ref, {}).items() if p != pin}


def short(net):
    return net.lstrip("/") if net else net


def gate_output(nl, ref, pin):
    """For a logic gate whose input pin sits on a net: (gate description, output net) from the held pin map, else None."""
    v = nl.value(ref)
    for key, (gates, src) in GATES.items():
        if v.startswith(key):
            for ins, out in gates:
                if int(pin) in ins:
                    return "%s gate %s->%s" % (key, "+".join(map(str, ins)), out), nl.pins.get(ref, {}).get(str(out)), src
    return None


def load_all(boards=("A", "B", "C", "D", "E", "P")):
    return {b: Netlist(b) for b in boards}
