#!/usr/bin/env python3
"""No rating or capability is claimed in a shipped document without the evidence that establishes it
(rule ENV-002, MESHSAT-862, 16 September 2026).

Nothing in this project has been fabricated or powered. Every public document therefore has to say what the
hardware IS (a design, a prototype, an intent) and never what it has been shown to do, and every protection
or environmental rating has to carry the test that establishes it or be written as an intention. The owner's
standing rule is the same sentence from the other direction: never say the kit works.

The check is a screen, not a language model: it finds the sentences that make a claim and asks each one for a
qualifier or an evidence reference in the same sentence. A legitimate claim declares itself in
`claims-allow.txt` with a reason, one entry per line as `<file>:<substring>  # reason`, the `erc-allow.txt`
idiom this project already uses.

Usage: claims_check.py [<file> ...]      default: the public documents of this repository
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))   # tools -> ecad -> v2 -> the repository root
ALLOW = os.path.join(HERE, "claims-allow.txt")
DEFAULT = ["README.md", "v1/README.md", "v1/BUILD.md", "v2/README.md", "v2/BUILD.md",
           "v2/docs/ASSEMBLY.md", "v2/docs/PANEL.md", "v2/docs/V2-SPEC.md",
           # the envelope names every rating this kit is designed to and is the document most likely to be
           # read as a promise, so it is screened with the rest (16 September 2026)
           "v2/docs/OPERATING-ENVELOPE.md",
           # the foundation baseline's product documents and the generated requirements trace (MESHSAT-1357, 26
           # September 2026): the brief and the concept of operations say what the kit is for, and the trace page
           # states every requirement, so each is a place a rating could be read as a promise
           "v2/docs/PRODUCT-BRIEF.md", "v2/docs/CONOPS.md", "v2/docs/REQUIREMENTS-TRACE.md"]

# A claim word makes an assertion about the built hardware's behaviour or its rating.
CLAIM = re.compile(r"\b(IP6[78]|IP\s?6[78]|waterproof|weatherproof|submersible|MIL-STD-\d+|"
                   r"certified|compliant|qualified|rated for|proven|field.?(?:deployed|tested|proven)|"
                   r"survives|withstands|guarantee[sd]?)\b", re.I)
# A qualifier turns an assertion into an intention, which is what this project is allowed to say.
QUALIFY = re.compile(r"\b(designed|intended|intent|aim|target|untested|not tested|no rating is claimed|"
                     r"prototype|to be tested|planned|would|class construction|-class|is not claimed|owed|"
                     r"before any rating)\b", re.I)
# A negation in the same sentence is the strongest qualifier there is: "nothing here has been built or field
# deployed" is the opposite of a claim, and the first version of this screen flagged it as one.
NEGATED = re.compile(r"\b(nothing|none|never|not|no)\b[^.]{0,80}?\b(been|is|are|has|have|claimed|built|"
                     r"powered|fabricated|deployed|tested|proven)\b", re.I)
# A negation directly in front of the claim word ("is not rated for sun", "never qualified") says the opposite of a
# claim. NEGATED above needs its verb AFTER the negation, so "its sheath is not rated for sun, rain or frost" (v1/BUILD.md,
# a cable the kit does NOT use outdoors) read as an unqualified rating and failed the whole screen (26 September 2026).
NEGATED_BEFORE = re.compile(r"\b(not|never|no|nor|without)\s+(?:\w+\s+){0,2}$", re.I)
# An evidence reference: a test record, a measurement section, a vendor document.
EVIDENCE = re.compile(r"(appendix\s+3?2?\.\d+|section\s+\d+|v2/vendor/|TEST-PLAN|test record|measured on)", re.I)


def allow():
    out = []
    if os.path.exists(ALLOW):
        for line in open(ALLOW):
            line = line.split("#")[0].strip()
            if ":" in line: out.append(tuple(line.split(":", 1)))
    return out


def sentences(text):
    for para in text.split("\n"):
        if para.strip().startswith(("|", "```", "    ")): continue          # tables and code carry their own context
        for s in re.split(r"(?<=[.!?])\s+", para):
            if s.strip(): yield s.strip()


def check(paths):
    al = allow(); bad = []; n = 0
    for rel in paths:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p): continue
        for s in sentences(open(p, errors="replace").read()):
            ms = list(CLAIM.finditer(s))
            if not ms: continue
            n += 1
            if all(NEGATED_BEFORE.search(s[:m.start()]) for m in ms): continue      # every claim word is negated
            if QUALIFY.search(s) or EVIDENCE.search(s) or NEGATED.search(s): continue
            if any(f in rel and frag.strip() in s for f, frag in al): continue
            bad.append("%s: %s" % (rel, s[:150]))
    return n, bad


def main(a):
    paths = [x for x in a if not x.startswith("-")] or DEFAULT
    n, bad = check(paths)
    print("claims_check: %d claim sentence(s) in %d document(s), %d without a qualifier, an evidence reference or a declared reason"
          % (n, len(paths), len(bad)))
    for b in bad[:20]: print("  FAIL %s" % b)
    return _v.write("claims_check", _v.FAIL if bad else _v.PASS, counts={"claims": n, "unqualified": len(bad)},
                    denominator=n, evidence=bad[:20], inputs={"documents": ",".join(paths)},
                    note="a rating claimed without its test is a promise to whoever carries the kit")


if __name__ == "__main__":
    import verdict as _vg   # a gate that crashes writes INCONCLUSIVE, never nothing (18 September 2026)
    sys.exit(_vg.guard("claims_check", main, sys.argv[1:]))
