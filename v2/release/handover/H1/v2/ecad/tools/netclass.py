#!/usr/bin/env python3
"""Which net class a net is in, answered once (MESHSAT-862, 13 September 2026).

KiCad 9 writes `net_settings.netclass_assignments` as a map from net name to a LIST of class names, because a
net may sit in several classes. Five tools read that map and they did not agree about it:

  - `impedance_check.py`, `intent_checks.py` and `pair_preroute.py` each carried their own copy of the same
    three-line expression, with the same comment, written three times.
  - `straighten.py` used the value as a dict KEY and died on board C with `TypeError: unhashable type: 'list'`.
    Its whole straighten stage has never run on that board: C10's quality pass reports "straighten+via_merge
    FAILED" and "straighten only FAILED" and accepted via_merge alone.
  - `stub_router.py` compared the value with a class NAME, which a list never equals, so it silently kept its
    default track width and via size for every net on every board whose project carries assignments. A crash
    is recoverable; this one answers.

So this file is the one answer, in the shape `hardset.py` has for the hard DRC set: when the format changes,
one place changes. The name lookup tries the name as written, with a leading slash and without one, because a
root-sheet label is `/NAME` in the board and both forms appear in project files of different ages.
"""

def class_of(assign, netname, default=None):
    """The class name assigned to `netname`, or `default`.

    `assign` is the project file's `netclass_assignments` map (or None). A list value yields its first entry,
    which is the primary class and the one every reader here has always wanted; a string value is returned as
    it stands; anything else, including an empty list, yields `default`.
    """
    if not assign or not netname: return default
    n = str(netname)
    v = assign.get(n)
    if v is None: v = assign.get("/" + n.lstrip("/"))
    if v is None: v = assign.get(n.lstrip("/"))
    if isinstance(v, (list, tuple)): return v[0] if v else default
    if isinstance(v, str): return v or default
    return default


def classes_by_name(ns):
    """The project's `net_settings.classes` as a map from name to the class dict."""
    return {c["name"]: c for c in ((ns or {}).get("classes") or []) if c.get("name")}
