#!/usr/bin/env python3
"""The reviewed sets of boards A, D and E, written from the netlists the review of decision 31 read and the external
declarations it corrected (MESHSAT-1357, worker d8dec31, 28 September 2026; the fresh check's item B1, open item S-88).

It writes v2/ecad/tools/pcb_port_reviews.json: for each board the external pins the review enumerated, pin by pin with
the net each carried, read from the netlist and never typed; the review document; the netlist's sha256/16; the reason.
port_protect.py holds every declaration against this file (its `reconcile`). The external entries are taken from
apply_port_declarations.py (board A's corrected list; boards D and E as declared), so the set here is the set the tool
reads PASS of 42, 21 and 13 on once that script has run; before it runs, board A's committed declaration disagrees
with it and TRN-001 on A reads what it should, not PASS.

Usage: make_port_reviews.py <tree root> [--check]      --check compares and writes nothing
"""
import hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import netread
import apply_port_declarations as APD

REVIEW = "v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md"
OUT = "v2/ecad/tools/pcb_port_reviews.json"
WHAT = ("The external pins of each board as a review enumerated them from the board's netlist, held by port_protect.py "
        "(rule TRN-001) against the board table's declaration pin by pin: a reviewed pin declared internal, left out or "
        "moved to ground, and a declared external pin no review holds, each read INCONCLUSIVE by name until this file "
        "is changed with its reason and the review it rests on (a `changes` entry: entry, was, now, why of 40 characters "
        "or more, review, on). One writer: the review that enumerated the set, filed by the integrator. A change here "
        "makes the readings of TRN-001 stale, as a change to a board table does (rules_status.CONFIG_INPUTS).")


def reviewed_external(root, letter, entries):
    comps, _nets = netread.read(os.path.join(root, APD.NETLIST[letter]))
    ext = {}
    for e in entries:
        ref = e["ref"]
        assert ref in comps, (letter, ref)
        want = [str(x) for x in (e.get("pins") or [])]
        for pin, net in sorted(comps[ref]["pins"].items(), key=lambda kv: (len(kv[0]), kv[0])):
            if APD.conductor(net) and (not want or pin in want): ext.setdefault(ref, {})[pin] = net
        assert ref in ext, "board %s: %s carries no supply or signal" % (letter.upper(), ref)
    return ext


def build(root):
    boards = {}
    for letter in ("a", "d", "e"):
        p = os.path.join(root, "v2", "ecad", "tools", "boards", "%s.json" % letter)
        t = json.load(open(p, encoding="utf-8"))
        ext_old = t.get("external_ports") or []
        if letter == "a":
            entries = APD.a_external(ext_old) if [e.get("ref") for e in ext_old] == ["J_DOCK", "J_USBW", "J_USBC_OUT"] else ext_old
            assert [e["ref"] for e in entries] == (["J_VR1", "J_VR2", "J_VR3", "J_VR4", "J_USBW", "J_USBC_OUT", "J_MAINSW"]
                                                   + ["J_BM%d" % k for k in range(1, 12)]), [e["ref"] for e in entries]
        else:
            assert [e.get("ref") for e in ext_old] == APD.EXPECT_EXT[letter], (letter, ext_old)
            entries = ext_old
        raw = open(os.path.join(root, APD.NETLIST[letter]), "rb").read()
        boards[letter] = {
            "review": REVIEW,
            "reviewed_on": "2026-09-28",
            "netlist": APD.NETLIST[letter],
            "netlist_sha256_16": hashlib.sha256(raw).hexdigest()[:16],
            "why": ("the review of decision 31 (an AI review, stream d8dec31) enumerated every connector pin of this "
                    "board's netlist that carries a supply or a signal and classed each as external or internal; the "
                    "external pins are these, and the declaration is corrected to them by "
                    "v2/docs/records/d8dec31/apply_port_declarations.py"),
            "external": reviewed_external(root, letter, entries),
            "changes": [],
        }
    return {"_what": WHAT, "boards": boards}


def main(argv):
    if not argv: print(__doc__); return 2
    root, dry = os.path.abspath(argv[0]), "--check" in argv
    d = build(root)
    text = json.dumps(d, indent=1, ensure_ascii=False) + "\n"
    out = os.path.join(root, OUT)
    for letter, rec in sorted(d["boards"].items()):
        print("make_port_reviews: board %s %d connector(s), %d pin(s), netlist %s" % (
            letter.upper(), len(rec["external"]), sum(len(v) for v in rec["external"].values()), rec["netlist_sha256_16"]))
    if dry:
        if os.path.exists(out):
            same = open(out, encoding="utf-8").read() == text
            print("make_port_reviews: %s is %s what this script would write" % (OUT, "exactly" if same else "NOT"))
            return 0 if same else 1
        print("make_port_reviews: %s is not in the tree (checked, not written)" % OUT); return 1
    with open(out, "w", encoding="utf-8") as f: f.write(text)
    assert json.load(open(out, encoding="utf-8"))["boards"]["a"]["external"]["J_VR1"] == {"1": "VIN_RAW"}
    print("make_port_reviews: wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
