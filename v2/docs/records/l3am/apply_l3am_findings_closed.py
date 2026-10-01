#!/usr/bin/env python3
"""The coordinator's step after the layer 3 amendment is checked (MESHSAT-1357; v2/docs/records/l3am/README.md): close
l3r2.yaml's `review_findings` with a NEW accepted check bound to this amendment. It sets `state: CLOSED`, names the check
(`checked_by`) and restates `status`; nothing else changes. The baseline is then accepted again at the revision that holds
it (apply_l3r5_accept.py --supersede), which refuses while the state is OPEN and verifies the check again, by `verify`,
against the revision it accepts. Not run by the amendment's author.

THE CHECK RECORD'S FORMAT (B2 of the amendment's check astra-check-l3am-1: the first version accepted any newest
accepted check, so check-l3r5-3, which its own fifth line limits to round 5's B2 correction of 30 September, would have
closed the findings with no check of the amendment). The record's first three lines, exactly:

    accepted: yes
    scope: Layer 3 amendment l3am (L3-R01 to L3-R05)
    reviewed-revision: <the full 40-hex commit the check read>

then a blank line and the check's own text. The record is filed in l3r2.yaml's `independent_check` as the newest entry,
`{record: <path>, sha16: <its sha256/16>, verdict: ACCEPTED, scope: "..."}`, before this script runs.

`verify` refuses, and nothing is written, unless every one of these holds:
  1. the record is the newest `independent_check`, filed at its sha256/16 with the verdict ACCEPTED (render_l3r2's
     handover_checks verifies the first line against the verdict), and its first line reads "accepted: yes";
  2. its second line is the scope line above, word for word;
  3. its third line names a reviewed revision that is a commit of this repository and an ancestor of the tip (HEAD, or the
     revision being accepted when apply_l3r5_accept.py asks), or the tip itself;
  4. the amendment's content is unchanged since that revision: the requirements, the owner brief and the change record as
     the acceptance's manifest hashes them (render_l3r2.manifest_at against content_manifest); l3r2.yaml as the
     acceptance policy hashes it, also without `independent_check` and `review_findings`, which filing the check and
     closing the findings change; and every file of l3amlib.AMENDMENT_FILES byte for byte;
  5. the record is none of the checks l3r2.yaml already listed at the amendment's base (l3amlib.BASE): check-l3r5-3 and
     every earlier check are refused, whatever their lines read.

Usage: python3 v2/docs/records/l3am/apply_l3am_findings_closed.py --check-record <path> [--check] [--data PATH]
       [--head REV]
  --data   a copy of l3r2.yaml (the tests); on a copy a fixture record may be named by an absolute path
  --head   the revision taken as the tip (default HEAD; the tests pass a fixture commit holding the tree's content)"""
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import l3amlib as L  # noqa: E402

sys.path.insert(0, os.path.join(L.TOP, "v2", "docs", "handover", "layer3"))
sys.path.insert(0, os.path.join(L.TOP, "v2", "ecad", "tools"))

SCOPE_LINE = "scope: Layer 3 amendment l3am (L3-R01 to L3-R05)"
REV_RX = re.compile(r"^reviewed-revision: ([0-9a-f]{40})$")
AMENDMENT_EXCLUDE = ("independent_check", "review_findings")
STATUS = "Layer 3 amendment checked; independent review findings dispositioned (L3-R01 to L3-R05)"


def _git(*args):
    return subprocess.run(["git", "-C", L.TOP] + list(args), capture_output=True)


def _rev(name):
    r = _git("rev-parse", "--verify", "%s^{commit}" % name)
    if r.returncode != 0: L.refuse("%s is not a commit of this repository" % name)
    return r.stdout.decode().strip()


def amendment_policy(data):
    import render_l3r2 as RL
    return RL.policy_digest({k: v for k, v in data.items() if k not in AMENDMENT_EXCLUDE})


def verify(record, data, head="HEAD", req=None, allow_abs=False):
    """The reviewed revision (40-hex) when `record` is a new accepted check of this amendment, bound to content the tree
    still holds (the five conditions of this module's docstring); refuses otherwise."""
    import render_l3r2 as RL
    import rules_lib as R
    if os.path.isabs(record) and not allow_abs: L.refuse("%s is not a repository path" % record)
    if not os.path.isabs(record) and (".." in record.split("/")): L.refuse("%s is not a repository path" % record)
    try:
        chks = RL.handover_checks(data)
    except RL.RenderError as e:
        L.refuse(str(e))
    if not chks or str(chks[-1]["record"]) != record or str(chks[-1].get("verdict")).upper() != "ACCEPTED":
        L.refuse("%s is not the newest independent check, filed and ACCEPTED" % record)
    lines = open(os.path.join(L.TOP, record), encoding="utf-8").read().split("\n")
    if lines[0].strip() != "accepted: yes": L.refuse("%s's first line does not read 'accepted: yes'" % record)
    if len(lines) < 3 or lines[1] != SCOPE_LINE:
        L.refuse("%s does not declare this amendment's scope on its second line (%r)" % (record, SCOPE_LINE))
    m = REV_RX.match(lines[2])
    if not m: L.refuse("%s does not name its reviewed revision on its third line ('reviewed-revision: <40-hex>')" % record)
    rev, tip = m.group(1), _rev(head)
    if _git("cat-file", "-e", rev + "^{commit}").returncode != 0: L.refuse("the reviewed revision %s is not a commit" % rev[:12])
    if _git("merge-base", "--is-ancestor", rev, tip).returncode != 0:
        L.refuse("the reviewed revision %s is not the tip %s nor an ancestor of it" % (rev[:12], tip[:12]))
    base = _git("show", "%s:%s" % (L.BASE, RL.DATA_REL))
    if base.returncode != 0: L.refuse("the amendment's base %s is not in this repository" % L.BASE[:12])
    old = {str(c.get("record")) for c in (RL._yaml_load(base.stdout).get("independent_check") or [])}
    if record in old or os.path.basename(record) in {os.path.basename(x) for x in old}:
        L.refuse("%s is a check filed before the amendment (listed at %s): it does not check the amendment" % (record, L.BASE[:8]))
    # the content: unchanged since the reviewed revision
    at, why = RL.manifest_at(rev)
    if at is None: L.refuse("the reviewed revision %s does not hold the reviewed content: %s" % (rev[:12], why))
    now = RL.content_manifest(req or R.load_requirements(), data)
    diff = [k for k in ("requirements", "owner_brief", "change_record") if at[k] != now[k]]
    then = _git("show", "%s:%s" % (rev, RL.DATA_REL))
    if then.returncode != 0 or amendment_policy(RL._yaml_load(then.stdout)) != amendment_policy(data): diff.append("l3r2.yaml")
    for path in L.AMENDMENT_FILES:
        b = _git("show", "%s:%s" % (rev, path))
        cur = os.path.join(L.TOP, path)
        if b.returncode != 0 or not os.path.isfile(cur) or b.stdout != open(cur, "rb").read(): diff.append(path)
    if diff: L.refuse("the amendment changed since the reviewed revision %s: %s" % (rev[:12], ", ".join(diff)))
    return rev


def build(raw, record, head="HEAD", allow_abs=False):
    d = L.E.parse(raw)
    rf = d.get("review_findings")
    if not rf: L.refuse("review_findings is not filed: apply_l3am_findings.py comes first")
    if str(rf.get("state")) != "OPEN": L.refuse("review_findings reads %s: this script has run" % rf.get("state"))
    verify(record, d, head, allow_abs=allow_abs)
    lines = [l for l in raw.split("\n") if l.startswith("review_findings: {")]
    if len(lines) != 1: L.refuse("review_findings is not one flow line")
    old_tail = ", state: OPEN, status: \"%s\"}" % rf["status"]
    new_line = L.once(lines[0], old_tail, ", state: CLOSED, checked_by: %s, status: \"%s\"}" % (record, STATUS), "review_findings")
    new = L.once(raw, lines[0] + "\n", new_line + "\n", "l3r2.yaml")
    a, b = L.only_keys_changed(raw, new, {"review_findings": "changed"})
    ch = sorted(k for k in set(a["review_findings"]) | set(b["review_findings"]) if a["review_findings"].get(k) != b["review_findings"].get(k))
    if ch != ["checked_by", "state", "status"]: L.refuse("review_findings changed on %s" % ch)
    return new


def main(argv):
    path = argv[argv.index("--data") + 1] if "--data" in argv else L.DATA
    rec = argv[argv.index("--check-record") + 1] if "--check-record" in argv else None
    head = argv[argv.index("--head") + 1] if "--head" in argv else "HEAD"
    old = open(path, encoding="utf-8").read()
    try:
        if not rec: L.refuse("no --check-record named")
        new = build(old, rec, head, allow_abs=os.path.realpath(path) != os.path.realpath(L.DATA))
    except L.Refused as e:
        print("apply_l3am_findings_closed: REFUSED: %s" % e); return 2
    print("apply_l3am_findings_closed: review_findings CLOSED, checked by %s%s" % (rec, " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv: L.write(path, old, new)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
