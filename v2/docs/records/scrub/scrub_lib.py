#!/usr/bin/env python3
"""The public-file scrub's patterns and its one redaction function (MESHSAT-1357, 30 September 2026).

WHY. The repository is public (GitLab project 64, mirrored to github.com/meshsat/meshsat-fieldkit). The owner's standing
rule is that public files carry no internal host names, user paths or addresses. Session records, readings and a few
pages carried the runner's user path, the paths of session scratch folders under the runner's temporary directory, the
runner's host name, the laptop's host name and the laptop's user path. This module holds the patterns and the ONE
function that rewrites a text, so the tree (apply_scrub.py) and the reissued handover snapshots (reissue_snapshots.py)
are redacted by the same rules and list the same token classes.

THE PATTERNS ARE STORED ENCODED. A module that spelled them out would itself be a public copy of the values it removes,
so each is kept base64-encoded and decoded in memory; nothing here writes one to disk. The encoding hides nothing from
a reader who decodes it: it keeps the values out of a plain search of the tree, which is what the rule asks.

TOKEN CLASSES (the words records/scrub/MAP.md uses; a removed value is never repeated there):
  runner path prefix     the runner's user path: <worktrees> (the folder that holds the worktrees), <repo> (the main
                         clone), <projects> (the folder that holds the MeshSat repositories), <runner home>
  session temp path      a session's scratch folder under the runner's temporary directory: /tmp/<scratchpad>, or
                         /tmp/<session temp> when the text names only the session's temporary root. The leading /tmp/
                         is kept on purpose: rules_status.py classes a reading whose input sits under a temporary
                         directory TEMP_INPUT, and a redacted reading must keep the class it had
  host name              the runner's host name: "the runner"
  laptop host name       the laptop's host name: "the laptop"
  laptop user path       the laptop's user path: <laptop home>
In Markdown a token with angle brackets is written inside a code span (the path it starts is wrapped in backticks when
it was not in one), because a renderer drops an unknown <tag> in running text; in XML it is written escaped.
"""
import base64, re

_E = {"home": "L2hvbWUvY2xhdWRlLXJ1bm5lcg==", "tmproot": "L3RtcC9jbGF1ZGUt",
      "mangled": "LWhvbWUtY2xhdWRlLXJ1bm5lci1naXRsYWItcHJvZHVjdHMtbWVzaHNhdC1tZXNoc2F0LWZpZWxka2l0",
      "host": "bmxsZWkwMQ==", "laptop": "YW5raA==", "lhome": "L2hvbWUva3lyaWFrb3Nw"}


def _d(k):
    return base64.b64decode(_E[k]).decode()


HOME, TMPROOT, MANGLED, HOST, LAPTOP, LHOME = (_d(k) for k in ("home", "tmproot", "mangled", "host", "laptop", "lhome"))

RUNNER, TEMP, HOSTC, LAPTOPC, LHOMEC = ("runner path prefix", "session temp path", "host name", "laptop host name",
                                       "laptop user path")
CLASSES = (RUNNER, TEMP, HOSTC, LAPTOPC, LHOMEC)

# DETECTION: one instance per path or name, never counted twice (the session temp path carries the runner's account in
# its mangled middle part, never the runner's path prefix itself).
DETECT = [(TEMP, re.compile(re.escape(TMPROOT))), (RUNNER, re.compile(re.escape(HOME))),
          (HOSTC, re.compile(re.escape(HOST))), (LAPTOPC, re.compile(r"\b" + re.escape(LAPTOP) + r"\b")),
          (LHOMEC, re.compile(re.escape(LHOME)))]
ANY = re.compile("|".join("(?:%s)" % p.pattern for _, p in DETECT))


class Refused(Exception):
    """A text holds a form the rules below do not know; it is handled by hand, never guessed."""


# REDACTION RULES, ordered: the first rule that matches at a position decides it. (pattern, token, class, note)
_T = re.escape(TMPROOT) + r"[0-9]+"
_RULES = [
    (_T + "/" + re.escape(MANGLED) + r"/[0-9a-f]+(?:-[0-9a-f]+)+/scratchpad", "/tmp/<scratchpad>", TEMP, ""),
    (_T + "/" + re.escape(MANGLED) + r"/[0-9a-f][0-9a-f-]*", "/tmp/<scratchpad>", TEMP, "the original was cut short here"),
    (_T + "/" + re.escape(MANGLED), "/tmp/<session temp>", TEMP, ""),
    (_T, "/tmp/<session temp>", TEMP, ""),
    (re.escape(HOME) + r"/worktrees/meshsat-fieldkit", "<worktrees>", RUNNER, ""),
    (re.escape(HOME) + r"/gitlab/products/meshsat/meshsat-fieldkit", "<repo>", RUNNER, ""),
    (re.escape(HOME) + r"/gitlab/products/meshsat", "<projects>", RUNNER, ""),
    (re.escape(HOME), "<runner home>", RUNNER, ""),
    (r"(?:runner|host) " + re.escape(HOST) + r"claude01", "the runner", HOSTC, ""),
    (re.escape(HOST) + r"claude01", "the runner", HOSTC, ""),
    (r"\(" + re.escape(LAPTOP) + r", ", "(", LAPTOPC, "the sentence already names the laptop session; the name is dropped"),
    (r"\bon " + re.escape(LAPTOP) + r"\b", "on the laptop", LAPTOPC, ""),
    (re.escape(LHOME), "<laptop home>", LHOMEC, ""),
]
_RX = re.compile("|".join("(%s)" % p for p, _, _, _ in _RULES))
_TAIL = re.compile(r"[^\s`'\"()\[\]<>|,;]*")


def _in_code_span(line, col):
    return line[:col].count("`") % 2 == 1


def redact(text, kind="text"):
    """(new text, events) for one file's text. kind: "md", "xml", "json" or "text". An event is a dict with the 1-based
    line, the class, the token as written and a note. Raises Refused on a form no rule knows."""
    out_lines, events, fence = [], [], False
    for n, line in enumerate(text.split("\n"), 1):
        if kind == "md" and line.lstrip().startswith("```"):
            fence = not fence
        pos, buf = 0, []
        for m in _RX.finditer(line):
            k = next(i for i, g in enumerate(m.groups()) if g is not None)
            _, token, cls, note = _RULES[k]
            start, end = m.start(), m.end()
            written = token
            if kind == "xml":
                written = token.replace("<", "&lt;").replace(">", "&gt;")
            if kind == "md" and "<" in token and not fence and not _in_code_span(line, start):
                t = _TAIL.match(line, end)
                tail = t.group(0) if t else ""
                while tail and tail[-1] in ".:": tail = tail[:-1]
                written = "`" + token + tail + "`"
                end = end + len(tail)
                note = (note + "; " if note else "") + "written in a code span"
            buf.append(line[pos:start]); buf.append(written); pos = end
            events.append({"line": n, "class": cls, "token": token, "note": note})
        buf.append(line[pos:])
        new = "".join(buf)
        left = ANY.search(new)
        if left:
            raise Refused("line %d keeps a form no rule knows (class %s)" % (
                n, next(c for c, p in DETECT if p.search(new))))
        out_lines.append(new)
    return "\n".join(out_lines), events


def kind_of(path):
    p = path.lower()
    if p.endswith(".md"): return "md"
    if p.endswith(".xml"): return "xml"
    if p.endswith(".json"): return "json"
    return "text"


def count(data):
    """{class: instances} in bytes or text."""
    if isinstance(data, bytes): data = data.decode("utf-8", "replace")
    return {c: len(p.findall(data)) for c, p in DETECT if p.findall(data)}
