#!/usr/bin/env python3
"""The manifest of the makers' IBIS models, read (MESHSAT-1357, layer 9, stream w5si2, 28 September 2026).

WHY THIS EXISTS. The models rule SI-001 reads are the makers' files and are NOT in the repository (five of thirteen
forbid distribution in their own header, the others carry a copyright line and no grant; publication is the owner's
decision and the standing decision is to hold them back). What is tracked in their place is
v2/vendor/ibis-manifest.yaml: per model the maker's address, how the `.ibs` is taken out of what the address serves,
and the sha256 of the extracted file. This module reads that file and answers three questions, and nothing else:
  * which file pins a model (`load`, `pin`);
  * is the model in this tree, and is it the file pinned (`state_of`: PRESENT, ABSENT or DIFFERS);
  * does the file present say what the manifest quotes from its header (`notice_holds`).
It opens no network connection (tools/ibis_fetch.py does, and only when a person runs it with --fetch) and it judges
no board. edge_length.py asks it before it reads a model; rules_status asks it when it dates a reading.

A ROW THAT CANNOT STAND IS REFUSED AND NAMED (`refusals`), and a model whose row is refused is not pinned: the record
that cites it decides nothing. A manifest that cannot be read pins nothing at all (`why`).
"""
import os, re, hashlib

MANIFEST_REL = "v2/vendor/ibis-manifest.yaml"
KINDS = ("PROHIBITS_DISTRIBUTION", "COPYRIGHT_NO_GRANT")
CONTAINERS = ("ibs", "zip")
PRESENT, ABSENT, DIFFERS = "PRESENT", "ABSENT", "DIFFERS"
_CACHE = {}


def sha256_of(path):
    try: return hashlib.sha256(open(path, "rb").read()).hexdigest()
    except OSError: return None


def _refuse(r):
    """None, or why a row cannot stand."""
    if not isinstance(r, dict) or not r.get("id"): return "no id"
    f = str(r.get("file") or "")
    if not re.fullmatch(r"v2/vendor/[A-Za-z0-9_.-]+/ibis/[A-Za-z0-9_.-]+\.ibs", f):
        return "file %r is not v2/vendor/<maker>/ibis/<name>.ibs, the one place the ignore rule covers" % f
    if not re.fullmatch(r"[0-9a-f]{64}", str(r.get("sha256") or "")): return "no full sha256 of the extracted file"
    if not (isinstance(r.get("bytes"), int) and r["bytes"] > 0): return "no byte count"
    if not str(r.get("url") or "").startswith("https://"): return "no https address of the maker's"
    if r.get("container") not in CONTAINERS: return "container %r is not one of %s" % (r.get("container"), ", ".join(CONTAINERS))
    if r["container"] == "zip" and not str(r.get("member") or "").strip(): return "a zip with no member named"
    if r.get("archive_url") and not str(r["archive_url"]).startswith("https://web.archive.org/web/"):
        return "archive_url is not an Internet Archive capture"
    for k in ("maker", "part", "fetched"):
        if not str(r.get(k) or "").strip(): return "no %s" % k
    n = r.get("notice")
    if not isinstance(n, dict) or n.get("kind") not in KINDS: return "notice.kind is not one of %s" % ", ".join(KINDS)
    q = n.get("quotes")
    if not (isinstance(q, list) and q and all(isinstance(x, dict) and str(x.get("text") or "").strip()
                                                 and str(x.get("lines") or "").strip() for x in q)):
        return "notice.quotes must quote the header's own words with the lines they stand on"
    return None


def load(repo, rel=MANIFEST_REL):
    """{"path": rel, "sha256_16": of the manifest or None, "models": {file: row}, "refusals": [text], "why": None or why
    nothing is pinned}. Cached by the manifest's content."""
    p = os.path.join(repo, rel)
    out = {"path": rel, "sha256_16": None, "models": {}, "refusals": [], "why": None}
    try:
        raw = open(p, "rb").read()
    except OSError:
        out["why"] = "%s is not in this tree" % rel
        return out
    h = hashlib.sha256(raw).hexdigest()
    if h in _CACHE: return dict(_CACHE[h], path=rel)
    out["sha256_16"] = h[:16]
    try:
        import yaml
        doc = yaml.safe_load(raw.decode("utf-8")) or {}
        rows = doc.get("models")
        assert isinstance(rows, list) and rows, "it names no models"
    except Exception as e:
        out["why"] = "%s cannot be read (%s: %s)" % (rel, type(e).__name__, str(e)[:100])
        return out
    ids = set()
    for i, r in enumerate(rows):
        why = _refuse(r)
        if not why and r["id"] in ids: why = "the id %s is used twice" % r["id"]
        if not why and r["file"] in out["models"]: why = "the file %s is pinned twice" % r["file"]
        if why:
            out["refusals"].append("%s models[%d] (%s): %s" % (rel, i, (r or {}).get("id") if isinstance(r, dict) else None, why))
            continue
        ids.add(r["id"]); out["models"][r["file"]] = r
    _CACHE[h] = out
    return out


def pin(man, file):
    """The row that pins a model, or None."""
    return (man.get("models") or {}).get(file)


def state_of(repo, row):
    """(PRESENT | ABSENT | DIFFERS, the full sha256 of the file present or None)."""
    h = sha256_of(os.path.join(repo, row["file"]))
    if h is None: return ABSENT, None
    return (PRESENT if h == row["sha256"] else DIFFERS), h


def set_state(states):
    """One word for a set of models: PRESENT (every one is the file pinned), ABSENT (none is in the tree), PARTIAL
    (some are), DIFFERS (at least one file present is not the one pinned), NOT_ASKED (the set is empty)."""
    s = list(states)
    if not s: return "NOT_ASKED"
    if DIFFERS in s: return DIFFERS
    if all(x == PRESENT for x in s): return PRESENT
    if all(x == ABSENT for x in s): return ABSENT
    return "PARTIAL"


def header_text(path):
    """The model's [Disclaimer] and [Copyright] keywords as words: comment bars dropped, whitespace collapsed."""
    out, on = [], False
    try: lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    except OSError: return None
    for l in lines:
        if re.match(r"^\[Component\]", l, re.I): break
        if re.match(r"^\[(Disclaimer|Copyright)\]", l, re.I): on = True
        elif re.match(r"^\[", l): on = False
        if on: out.append(re.sub(r"^\s*\|+\s?", "", l).strip())
    return " ".join(" ".join(out).split())


FORBIDS = re.compile(r"(?i)\b(redistribut\w*|distribut\w*|reproduc\w*)\b")


def notice_holds(repo, row):
    """None when the file present says what the manifest quotes from its header and is of the kind the manifest gives
    it; else why not. A model that is absent cannot be asked: None, and the caller knows its state."""
    t = header_text(os.path.join(repo, row["file"]))
    if t is None: return None
    for q in row["notice"]["quotes"]:
        if " ".join(str(q["text"]).split()) not in t:
            return "the header of %s does not say %r" % (row["file"], str(q["text"])[:70])
    speaks = bool(FORBIDS.search(t))
    if row["notice"]["kind"] == "COPYRIGHT_NO_GRANT" and speaks:
        return "the header of %s speaks of reproduction or distribution and the manifest says it carries a copyright line only" % row["file"]
    if row["notice"]["kind"] == "PROHIBITS_DISTRIBUTION" and not speaks:
        return "the header of %s does not speak of distribution and the manifest says it forbids it" % row["file"]
    return None
