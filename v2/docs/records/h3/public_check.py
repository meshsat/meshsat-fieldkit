#!/usr/bin/env python3
"""Which commits the handover pages name are on the public repository, asked now (MESHSAT-1357, 27 September 2026).

Written by the H3 pages worker for correction 7 of the H3 pages. H2's SOURCE.txt marks its source commit b89b50b4 and
the fnd/h2 commits before it `public no`: that is what the building clone knew when H2 was built, and it stays true of
that build. RELEASE-H2.md says both of H2's commits are on the public repository's main. This script asks the question
again, two ways, and prints the time it asked:

  1. in this clone: is the commit an ancestor of refs/remotes/origin/main (the test handover_pack.py's timeline uses);
  2. on the public repository itself: the HTTP status of https://github.com/meshsat/meshsat-fieldkit/commit/<full id>,
     and the head of its main branch from the public API.

It reads only and writes nothing but standard output. It needs git and network access; `--no-network` asks question 1
alone. An answer is true at the time printed on its first line, not later.

Usage (from the repository root): python3 v2/docs/records/h3/public_check.py [--no-network] [commit ...]
"""
import datetime, json, subprocess, sys, urllib.error, urllib.request

REPO = "https://github.com/meshsat/meshsat-fieldkit"
API = "https://api.github.com/repos/meshsat/meshsat-fieldkit/commits/main"
DEFAULT = [
    ("b89b50b4", "H2's source commit"),
    ("174d8466", "H2's snapshot commit"),
    ("62f26a44", "the newest commit H2's timeline marks public yes"),
    ("cecfd0f1", "fnd/h2: the targeted fix (S-77's closing commit)"),
    ("3e4799eb", "fnd/h2: the registry baselined at the targeted fix"),
    ("6b2a9965", "fnd/h2: the narrow verification, layer 1 baselined"),
    ("763bccdf", "fnd/h2: the claims screen re-taken, the H2 exports' commit"),
    ("c5d09c78", "fnd/h2: the H2 exports filed"),
    ("a54b793b", "layer 3: S-80's wording fix, the commit the registry is baselined at"),
    ("2c12be91", "layer 3: the baseline written"),
    ("24e7bf5a", "layer 3: the re-check filed, layer 3 COMPLETE"),
    ("a9f212c7", "layers 1 and 2: the check of the definition restructure filed, the re-stamp's commit"),
    ("a54b1f4d", "after H2, on main: the packer's repo subcommand"),
    ("90314d99", "after H2, on main: pcb_interfaces.yaml read_at re-anchored"),
    ("ed988ba8", "after H2, on main: INT-001's readings re-taken"),
    ("ecfe5414", "after H2, on main: the layout constraint sheets re-bound"),
    ("5d568a66", "after H2, on main: the H2 minor findings answered in the pages"),
    ("9d2f8dce", "after H2, on main: H2-RESPONSE.md"),
    ("992f2bc2", "branch h2m-backup: the same patch as a54b1f4d"),
    ("248b951d", "branch h2m-backup: the same patch as 90314d99"),
    ("2a3a1451", "branch h2m-backup: the same patch as ed988ba8"),
    ("1221262e", "branch h2m-backup: the same patch as ecfe5414"),
    ("44b87208", "branch h2m-backup: the same patch as 5d568a66"),
    ("6ec37197", "main when the H3 pages were written"),
]


def git(*a):
    r = subprocess.run(["git"] + list(a), capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


def status(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method="GET",
                                                           headers={"User-Agent": "meshsat-fieldkit-public-check"}),
                                    timeout=30) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception as e:                               # no network, a refused connection: said, never guessed
        return "no answer (%s)" % type(e).__name__, b""


def main():
    args = [a for a in sys.argv[1:] if a != "--no-network"]
    net = "--no-network" not in sys.argv[1:]
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print("public_check: asked at %s" % now)
    rc, ref = git("rev-parse", "--verify", "--quiet", "refs/remotes/origin/main")
    print("this clone's refs/remotes/origin/main: %s" % (ref if rc == 0 else "absent"))
    if net:
        st, body = status(API)
        try:
            j = json.loads(body.decode("utf-8")) if body else {}
        except ValueError:
            j = {}
        print("the public repository's main (%s): HTTP %s, head %s, committed %s" % (
            API, st, j.get("sha") or "-", ((j.get("commit") or {}).get("committer") or {}).get("date") or "-"))
    rows = [(a, "named on the command line") for a in args] or DEFAULT
    print("%-9s %-26s %-22s %s" % ("commit", "ancestor of origin/main", "github.com commit page", "what it is"))
    for c, what in rows:
        rc, full = git("rev-parse", "--verify", "--quiet", "%s^{commit}" % c)
        if rc != 0:
            print("%-9s %-26s %-22s %s" % (c, "not in this clone", "-", what))
            continue
        anc = "yes" if git("merge-base", "--is-ancestor", full, "refs/remotes/origin/main")[0] == 0 else "no"
        page = "HTTP %s" % status("%s/commit/%s" % (REPO, full))[0] if net else "not asked"
        print("%-9s %-26s %-22s %s" % (c, anc, page, what))
    return 0


if __name__ == "__main__":
    sys.exit(main())
