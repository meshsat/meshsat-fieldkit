#!/usr/bin/env python3
"""DRAFT for the integrator (stream w5si, second pass, 27 September 2026, RE-ISSUED 28 September 2026 by stream w5si2,
MESHSAT-1357, layer 9): record the makers' IBIS models in v2/vendor/SOURCES.yaml. It replaces the draft of 27
September and the first pass's, filed as recovered under ../recovery/pass1-drafts/.

RE-ISSUED BECAUSE THE MODELS ARE NOT IN THE REPOSITORY (the drafts check's B1 and M5). The thirteen models
edge_length.py reads for rule SI-001 are withheld; v2/vendor/ibis-manifest.yaml pins each and
v2/ecad/tools/ibis_fetch.py fetches them. So this draft:
  * takes every row's address, revision, date and sha256 FROM THE MANIFEST of the tree it runs on, never from a list
    typed here, and works whether the models are in the tree or not (where one is present it must be the file pinned);
  * says in every row that the file is not held in the repository, which maker's address serves it, how the `.ibs` is
    taken out of what the address serves, and which wording its header carries;
  * gives the FOUR models whose part has no entry here (sn74lvc08a, sn74lvc32a, ina226, tmp117) their address and
    full sha256 in the owed line, and says exactly what is owed for each: a PART ENTRY (the part as the schematic names
    it, the order code it resolves to, its grade against the envelope), which is an identity audit and the parts
    stream's, not a document row.
A row's `sha256` is of the extracted `.ibs`, as the manifest's is; where the address serves a zip the row says so.

It appends one document row to each of the nine part entries a model belongs to, by entry id, and one `owed` line.
    python3 v2/docs/records/w5si/apply/apply_sources_yaml_ibis.py [--root <tree>] [--dry-run]
It asserts the stream is merged, every entry id exists once and has a `documents:` list, that no row for the file is
there already, and that the manifest pins every model named. The new text is parsed and COMPARED WITH THE OLD ONE AS
STRUCTURE before anything is written: every top-level key and every part entry is unchanged but for the nine entries
named, each of which has every document row it had, in the same order, plus exactly one; and `owed` has every line it
had plus exactly one. A second run is refused ("already applied").
"""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _apply as AP

ROOT = AP.root_of(HERE) if "--root" not in sys.argv or sys.argv.index("--root") + 1 < len(sys.argv) else os.path.abspath(".")
TARGET = os.path.join(ROOT, "v2", "vendor", "SOURCES.yaml")
HELD = ("NOT in the repository (the makers' models are withheld; publication is the owner's decision): pinned by "
        "v2/vendor/ibis-manifest.yaml and fetched by v2/ecad/tools/ibis_fetch.py")

# (the part entry that carries the model, the model, whether it describes the fitted variant)
ROWS = [
    ("io-supervisor-mcu", "v2/vendor/st/ibis/stm32h742_743_750_753_lqfp100.ibs",
     "yes: [Component] stm32h7_450_lqfp100_l covers STM32H742/743/750/753 in LQFP100, the fitted STM32H743VIT6 and the schematic's named H753 alike"),
    ("can-transceiver", "v2/vendor/ti/ibis/tcan33x.ibs",
     "the model's component is TCAN334DCN (SOT-23); the fitted TCAN334DR is the SOIC-8 D package with the same pin numbers (TI SLLSEQ7 Table 4-1)"),
    ("usb3-hub", "v2/vendor/ti/ibis/tusb8041rgc.ibs", "yes: [Component] TUSB8041, the RGC (VQFN-64) package of the fitted TUSB8041IRGCR"),
    ("io-expander-pca9555", "v2/vendor/ti/ibis/pca9555.ibs", "yes: [Component] PCA9555_PW, the TSSOP (PW) 24 of the fitted PCA9555PWR"),
    ("outlet-interlock-nand", "v2/vendor/ti/ibis/sn74lvc1g00.ibs", "yes: [Component] LVC1G00_DBV, the SOT-23-5 of the fitted SN74LVC1G00DBVR"),
    ("panel-emcon-lamp-gate", "v2/vendor/ti/ibis/sn74lvc1g57.ibs", "yes: [Component] LVC1G57_DBV, the SOT-23-6 of the fitted SN74LVC1G57DBVR"),
    ("bbm-xor", "v2/vendor/ti/ibis/sn74lvc86a.ibs", "yes: [Component] LVC86A_PW, the TSSOP-14 of the fitted SN74LVC86APWR"),
    ("board-d-flange-adc", "v2/vendor/ti/ibis/ads1x1x.ibs", "yes: [Component] ADS1X15IDGS, the VSSOP-10 of the fitted ADS1115IDGSR"),
    ("logic-held-sheets-round-8", "v2/vendor/ti/ibis/sn74lvc1g04.ibs", "yes for SN74LVC1G04DBVR: [Component] LVC1G04_DBV"),
]
# the models whose part has no entry in SOURCES.yaml: (the model, the part and where it sits)
NO_ENTRY = [
    ("v2/vendor/ti/ibis/sn74lvc08a.ibs", "SN74LVC08APWR, board B's voters U70 to U75 and board A's U26"),
    ("v2/vendor/ti/ibis/sn74lvc32a.ibs", "SN74LVC32APWR, board B's voters U76 to U79, U84 and U85"),
    ("v2/vendor/ti/ibis/ina226.ibs", "INA226, board A's six rail monitors"),
    ("v2/vendor/ti/ibis/tmp117.ibs", "TMP117AIDRVR, board B's temperature sensor U10"),
]
MARK = "stream w5si2): four makers' IBIS models read for rule SI-001"


def served(row):
    """How the `.ibs` is had from the maker's address, in words."""
    how = "the address serves the model itself" if row["container"] == "ibs" else "the address serves a zip; the model is its %s" % row["member"]
    if row.get("archive_url"): how += "; where the maker refuses a host: %s" % row["archive_url"]
    return how


def q(s):
    """A YAML double-quoted scalar."""
    return json.dumps(str(s), ensure_ascii=False)


def rows_and_owed(man):
    import ibis_manifest as IM
    rows = []
    for eid, path, match in ROWS:
        r = IM.pin(man, path)
        AP.need(r is not None, "the manifest %s does not pin %s, the model this draft files under the entry %s" % (man["path"], path, eid))
        st, held = IM.state_of(ROOT, r)
        AP.need(st != IM.DIFFERS, "%s is in this tree and is not the file the manifest pins (sha256 %s held, %s pinned)" % (path, held, r["sha256"]))
        rows.append((eid, path, '      - {path: %s, doc_id: %s, revision: %s, url: %s, served: %s, fetched: %s, sha256: %s, held: %s, notice: %s, '
                     'matches_fitted: %s, cited_by: "v2/ecad/tools/pcb_edge_rates.yaml (rule SI-001)"}' % (
                         q(path), q("%s %s" % (r["maker"], r["literature"])), q("file rev %s, %s" % (r["file_rev"], r["file_date"])),
                         q(r["url"]), q(served(r)), q(r["fetched"]), q(r["sha256"]), q(HELD), q(r["notice"]["kind"]), q(match))))
    parts = []
    for path, part in NO_ENTRY:
        r = IM.pin(man, path)
        AP.need(r is not None, "the manifest %s does not pin %s" % (man["path"], path))
        parts.append("%s (%s; %s, %s; %s; sha256 %s; header: %s)" % (path, part, r["maker"], r["literature"], r["url"], r["sha256"], r["notice"]["kind"]))
    owed = ("28 September 2026 (" + MARK + " and cited by v2/ecad/tools/pcb_edge_rates.yaml have NO PART ENTRY here to carry "
            "them. What is owed for each is the part entry itself (the part as the generator names it, the order code it resolves to, its "
            "grade against the envelope), an identity audit that is the parts stream's and is not made by filing a model; the model's "
            "row follows that entry. None of the four files is in the repository: v2/vendor/ibis-manifest.yaml pins them and "
            "v2/ecad/tools/ibis_fetch.py fetches them. " + "; ".join(parts))
    return rows, owed


def main():
    import yaml
    AP.need_stream(ROOT)
    AP.need(os.path.exists(TARGET), "v2/vendor/SOURCES.yaml is not in the tree %s" % ROOT)
    AP.tools_on_path(ROOT)
    import ibis_manifest as IM
    man = IM.load(ROOT)
    AP.need(not man["why"] and not man["refusals"], "the manifest does not stand: %s %s" % (man["why"], man["refusals"][:2]))
    named = {p for _e, p, _m in ROWS} | {p for p, _x in NO_ENTRY}
    AP.need(named == set(man["models"]), "the manifest pins %d models and this draft files %d: %s differ; re-read the draft's two lists" % (
        len(man["models"]), len(named), sorted(named ^ set(man["models"]))))
    rows, OWED = rows_and_owed(man)
    s = open(TARGET, encoding="utf-8").read()
    before = yaml.safe_load(s)
    AP.need(isinstance(before.get("owed"), list) and isinstance(before.get("parts"), list), "SOURCES.yaml has no parts list or no owed list")
    AP.need(not any(MARK in str(x) for x in before["owed"]) and not any(
        isinstance(x, dict) and x.get("path") in named
        for e in before.get("parts") or [] for x in e.get("documents") or []), "already applied")
    for eid, path, row in rows:
        head = "\n  - id: %s\n" % eid
        assert s.count(head) == 1, "the part entry %s is not found exactly once in SOURCES.yaml" % eid
        a = s.index(head) + 1
        nxt = [i for i in (s.find("\n  - id: ", a + 5), s.find("\nowed:", a)) if i != -1]
        b = min(nxt) if nxt else len(s)
        block = s[a:b]
        assert path not in block, "%s already has a row for %s" % (eid, path)
        di = block.find("\n    documents:\n")
        assert di != -1, "entry %s has no documents: list" % eid
        lines = block[di + 1:].split("\n")
        k = 1
        while k < len(lines) and (lines[k].startswith("      ") and lines[k].strip()):
            k += 1
        lines.insert(k, row)
        block = block[:di + 1] + "\n".join(lines)
        s = s[:a] + block + s[b:]
    oi = s.find("\nowed:\n")
    assert oi != -1 and OWED not in s, "SOURCES.yaml has no owed: list at its margin"
    s = s[:oi + len("\nowed:\n")] + "  - %s\n" % q(OWED) + s[oi + len("\nowed:\n"):]
    d = yaml.safe_load(s)
    ents = {e.get("id"): e for e in d.get("parts") or []}
    for eid, path, _row in rows:
        got = [x for x in ents[eid].get("documents") or [] if isinstance(x, dict) and x.get("path") == path]
        assert len(got) == 1, (eid, path)
        assert got[0]["sha256"] == IM.pin(man, path)["sha256"] and got[0]["url"] == IM.pin(man, path)["url"], (eid, path)
    assert any(OWED == x for x in d.get("owed") or []), "the owed line did not survive the YAML reader as it was written"
    # THE STRUCTURE, before against after: nothing but the intended rows moved
    assert set(d) == set(before), "a top-level key was added or lost"
    for k in before:
        if k not in ("parts", "owed"): assert d[k] == before[k], "the top-level key %s changed" % k
    assert d["owed"][1:] == before["owed"] and d["owed"][0] == OWED, "owed is not the old list with the one line added"
    mine = {}
    for eid, path, _row in rows: mine.setdefault(eid, []).append(path)
    assert [e.get("id") for e in d["parts"]] == [e.get("id") for e in before["parts"]], "a part entry was added, lost or moved"
    for a, b in zip(before["parts"], d["parts"]):
        if a.get("id") not in mine:
            assert a == b, "the entry %s changed and was not to" % a.get("id")
            continue
        assert {k: v for k, v in a.items() if k != "documents"} == {k: v for k, v in b.items() if k != "documents"}, a.get("id")
        kept = [x for x in b["documents"] if not (isinstance(x, dict) and x.get("path") in mine[a["id"]])]
        assert kept == a["documents"], "the entry %s lost or changed a document row" % a.get("id")
        assert len(b["documents"]) == len(a["documents"]) + len(mine[a["id"]]), a.get("id")
    assert "\u2014" not in OWED and all("\u2014" not in r for _e, _p, r in rows)
    states = [IM.state_of(ROOT, r)[0] for r in man["models"].values()]
    msg = ("SOURCES.yaml: %d document rows and one owed line added, every address, revision and sha256 read from %s; the models "
           "in this tree: %s (%d of %d present)\n  OWED after this draft: a part entry for each of %s (the parts stream's)" % (
               len(rows), man["path"], IM.set_state(states), states.count(IM.PRESENT), len(states),
               ", ".join(os.path.basename(p) for p, _x in NO_ENTRY)))
    if "--dry-run" in sys.argv:
        print("dry run, nothing written: " + msg); return 0
    AP.write(TARGET, s)
    assert yaml.safe_load(open(TARGET, encoding="utf-8").read()) == d, "the file read back is not the text that was written"
    print(msg)
    return 0


if __name__ == "__main__":
    AP.run(main)
