#!/usr/bin/env python3
"""Fetch the makers' IBIS models named by v2/vendor/ibis-manifest.yaml into the ignored folders, and verify them
(MESHSAT-1357, layer 9, stream w5si2, 28 September 2026).

THE MODELS ARE NOT IN THE REPOSITORY (see the manifest's header for why). This is how a clean clone, the public
repository or a handover ZIP gets them: from each maker's own address, never from this project.

  ibis_fetch.py --check              fetches NOTHING. Says, per model, PRESENT (the file pinned), ABSENT or DIFFERS, holds
                                     each file present to the words the manifest quotes from its header, and prints
                                     the state of the set. Exit 0 unless a file present differs from its pin, a
                                     quoted notice is not in the file, or the manifest refuses a row.
  ibis_fetch.py --fetch [--only ID ...] [--replace] [--dest DIR]
                                     downloads every model that is ABSENT (with --replace also one that DIFFERS),
                                     takes the `.ibs` out of the zip where the address serves a zip, verifies the
                                     sha256 and the byte count against the manifest and only then writes the file,
                                     through a temporary name. --dest writes under another root (a scratch check of
                                     the manifest itself) and leaves the tree alone.

IT IS NEVER RUN BY A TEST, A GATE OR ANOTHER TOOL. It opens network connections and brings third-party files into the
tree; both are a person's act. Whoever runs --fetch takes the files under the makers' own terms, which each file
states in its header and the manifest quotes. The files land in folders `.gitignore` ignores
(v2/vendor/*/ibis/*.ibs); never `git add -f` one.

WHERE IT LOOKS, in this order, and it says which one answered:
  1. the maker's address (`url`), with an ordinary browser's User-Agent;
  2. where that is refused or fails (st.com refuses this project's runner with HTTP 403, as it did on both fetches of
     27 September 2026): the capture the row names (`archive_url`), then the newest capture the Internet Archive
     holds of the maker's address, https://web.archive.org/web/2026id_/<url> (the `id_` form serves the bytes as
     captured, without the archive's banner).
What arrives is unwrapped by what it IS, not by its name: gzip (the archive may serve a file gzip-wrapped) is
unwrapped once; a zip gives its `member`, by the path the manifest names and, failing that, by that path's file name
where exactly one entry has it. The sha256 of the extracted `.ibs` is the only authority: a file that is not the one
pinned is never written, from whichever source it came. A maker who has revised a model serves other bytes; then the
fetch fails and says so, and pinning the new file is an engineering change (the record of tools/pcb_edge_rates.yaml
that reads it is checked against it), not a fetch.
"""
import os, sys, io, gzip, zipfile, hashlib, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ibis_manifest as M
from verdict import opt as _opt

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
ARCHIVE_NEWEST = "https://web.archive.org/web/2026id_/%s"
TIMEOUT = 180
LIMIT = 80 * 1024 * 1024          # no model's download is near this; a larger answer is refused, not held in memory


def sources(row):
    """[(label, address)] in the order they are tried."""
    out = [("the maker's address", row["url"])]
    if row.get("archive_url"): out.append(("the Internet Archive capture the manifest names", row["archive_url"]))
    out.append(("the Internet Archive's newest capture", ARCHIVE_NEWEST % row["url"]))
    return out


def download(url):
    """(bytes, None) or (None, why)."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            raw = r.read(LIMIT + 1)
        if len(raw) > LIMIT: return None, "more than %d bytes" % LIMIT
        return raw, None
    except urllib.error.HTTPError as e:
        return None, "HTTP %s" % e.code
    except Exception as e:
        return None, "%s: %s" % (type(e).__name__, str(e)[:100])


def extract(raw, row):
    """(the `.ibs` bytes, how) or (None, why), by what the bytes are."""
    how = []
    if raw[:2] == b"\x1f\x8b":
        try: raw = gzip.decompress(raw)
        except Exception as e: return None, "a gzip wrapper that does not open (%s)" % type(e).__name__
        how.append("gzip-wrapped")
    if raw[:4] == b"PK\x03\x04":
        try:
            z = zipfile.ZipFile(io.BytesIO(raw))
            names = z.namelist()
        except Exception as e:
            return None, "a zip that does not open (%s)" % type(e).__name__
        want = str(row.get("member") or os.path.basename(row["file"]))
        hit = [n for n in names if n == want]
        if not hit:
            base = os.path.basename(want).lower()
            hit = [n for n in names if os.path.basename(n).lower() == base]
        if len(hit) != 1:
            return None, "the zip holds %d entries named %s (its %d entries: %s%s)" % (
                len(hit), want, len(names), ", ".join(names[:6]), " ..." if len(names) > 6 else "")
        how.append("the zip's %s" % hit[0])
        return z.read(hit[0]), ", ".join(how)
    if row["container"] == "zip":
        return None, "the manifest says the address serves a zip and what arrived is not one (it starts %r)" % raw[:16]
    return raw, ", ".join(how) or "the file as served"


def fetch_one(row, dest_root):
    """(True, what happened) or (False, why): tries each source until one gives the file pinned."""
    tried = []
    for label, url in sources(row):
        raw, why = download(url)
        if raw is None:
            tried.append("%s (%s): %s" % (label, url, why)); continue
        body, how = extract(raw, row)
        if body is None:
            tried.append("%s (%s): %s" % (label, url, how)); continue
        h = hashlib.sha256(body).hexdigest()
        if h != row["sha256"] or len(body) != row["bytes"]:
            tried.append("%s (%s): served %d bytes, sha256 %s, and the manifest pins %d bytes, sha256 %s: NOT WRITTEN" % (
                label, url, len(body), h, row["bytes"], row["sha256"]))
            continue
        dst = os.path.join(dest_root, row["file"])
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst + ".part", "wb") as f: f.write(body)
        os.replace(dst + ".part", dst)
        return True, "from %s (%s), sha256 verified, %d bytes%s" % (
            label, how, len(body), ("; refused before it: " + "; ".join(tried)) if tried else "")
    return False, "; ".join(tried)


def check(repo, man, only=None, quiet=False):
    """(states {id: state}, problems [text])."""
    states, bad = {}, list(man["refusals"])
    if man["why"]: bad.append(man["why"])
    for f, r in man["models"].items():
        if only and r["id"] not in only: continue
        st, h = M.state_of(repo, r)
        states[r["id"]] = st
        note = ""
        if st == M.DIFFERS:
            bad.append("%s: the file present is sha256 %s and the manifest pins %s" % (f, h, r["sha256"]))
        elif st == M.PRESENT:
            why = M.notice_holds(repo, r)
            if why: bad.append(why)
            note = "  notice %s" % r["notice"]["kind"]
        if not quiet: print("  %-8s %-22s %s%s" % (st, r["id"], f, note))
    return states, bad


def main(a):
    if not a or not ({"--check", "--fetch"} & set(a)): print(__doc__); return 2
    repo = REPO
    if "--root" in a: repo = os.path.abspath(_opt(a, "--root", repo))   # a flag given no value is answered, never raised (verdict.opt)
    dest = os.path.abspath(_opt(a, "--dest", repo)) if "--dest" in a else repo
    only = set()
    if "--only" in a:
        for x in a[a.index("--only") + 1:]:
            if x.startswith("--"): break
            only.add(x)
    man = M.load(repo)
    if man["why"]:
        print("ibis_fetch: %s" % man["why"]); return 1
    unknown = only - {r["id"] for r in man["models"].values()}
    if unknown:
        print("ibis_fetch: the manifest names no %s" % ", ".join(sorted(unknown))); return 2
    print("ibis_fetch: %s (sha256/16 %s), %d model(s)%s" % (man["path"], man["sha256_16"], len(man["models"]),
                                                          "; destination %s" % dest if dest != repo else ""))
    if "--fetch" in a:
        failed = 0
        for f, r in man["models"].items():
            if only and r["id"] not in only: continue
            st, _h = M.state_of(dest, r)
            if st == M.PRESENT:
                print("  kept     %-22s %s is the file pinned" % (r["id"], f)); continue
            if st == M.DIFFERS and "--replace" not in a:
                print("  REFUSED  %-22s %s is present and is not the file pinned; --replace overwrites it" % (r["id"], f))
                failed += 1; continue
            ok, what = fetch_one(r, dest)
            print("  %-8s %-22s %s" % ("fetched" if ok else "FAILED", r["id"], what))
            failed += 0 if ok else 1
        if failed:
            print("ibis_fetch: %d model(s) could not be fetched; every net that waits on one reads UNDECIDED and SI-001 "
                  "stays INCONCLUSIVE on the boards that carry it (the reading fails closed)" % failed)
    states, bad = check(dest, man, only or None)
    for b in bad: print("  PROBLEM %s" % b)
    n = list(states.values())
    print("ibis_fetch: state %s: %d present, %d absent, %d differ, of %d" % (
        M.set_state(n), n.count(M.PRESENT), n.count(M.ABSENT), n.count(M.DIFFERS), len(n)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
