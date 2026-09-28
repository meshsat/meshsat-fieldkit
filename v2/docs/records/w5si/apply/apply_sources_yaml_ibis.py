#!/usr/bin/env python3
"""DRAFT for the integrator (stream w5si, second pass, 27 September 2026, MESHSAT-1357, layer 9): record the makers'
IBIS models in v2/vendor/SOURCES.yaml. It replaces the first pass's draft, filed as recovered under
../recovery/pass1-drafts/; the rows are the first pass's, which the independent check confirmed against the files.

The thirteen IBIS files filed under v2/vendor/ti/ibis/ and v2/vendor/st/ibis/ (sources.txt and vendor-status.txt carry a
line for each) are cited by v2/ecad/tools/pcb_edge_rates.yaml for rule SI-001. This appends one document row to each
part entry the model belongs to, by entry id, and one `owed` line for the four models whose part has no entry yet.

Applied by the integrator on the integrated tree (after set 6), from anywhere:
    python3 v2/docs/records/w5si/apply/apply_sources_yaml_ibis.py [--root <tree>] [--dry-run]
It asserts every entry id exists once and has a `documents:` list, that no row for the file is there already, and each
file's sha256 against the held file. The new text is parsed and COMPARED WITH THE OLD ONE AS STRUCTURE before anything
is written: every top-level key and every part entry is unchanged but for the nine entries named, each of which has
every document row it had, in the same order, plus exactly one; and `owed` has every line it had plus exactly one. A
second run is refused.
"""
import os, sys, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
if "--root" in sys.argv: ROOT = os.path.abspath(sys.argv[sys.argv.index("--root") + 1])
TARGET = os.path.join(ROOT, "v2", "vendor", "SOURCES.yaml")
FETCHED = "2026-09-27T17:00Z by stream w5si, and again 2026-09-27T20:33Z after the first copy was lost with its worktree, the same bytes"

ROWS = [
    ("io-supervisor-mcu", "v2/vendor/st/ibis/stm32h742_743_750_753_lqfp100.ibs", "ST STM32H7 IBIS models (stm32h7_ibis.zip)",
     "file rev 2.3, 6 March 2024", "https://www.st.com/resource/en/ibis_model/stm32h7_ibis.zip via https://web.archive.org/web/20250911224858id_/ (st.com refuses this host)",
     "0fb7767c1ee034db0cd4d9c92334f4860ddb1980d3fba950c3109f0fc5bc1bc8",
     "yes: [Component] stm32h7_450_lqfp100_l covers STM32H742/743/750/753 in LQFP100, the fitted STM32H743VIT6 and the schematic's named H753 alike"),
    ("can-transceiver", "v2/vendor/ti/ibis/tcan33x.ibs", "TI SLLM313 (TCAN33X IBIS Model)", "file rev 1.0, 9 June 2016",
     "https://www.ti.com/lit/zip/SLLM313", "0e5a9429146148c11252dcea4c5dacc3386634c4cb492bd641a24a1d31fe508b",
     "the model's component is TCAN334DCN (SOT-23); the fitted TCAN334DR is the SOIC-8 D package with the same pin numbers (TI SLLSEQ7 Table 4-1)"),
    ("usb3-hub", "v2/vendor/ti/ibis/tusb8041rgc.ibs", "TI SLLC445 (TUSB8041 IBIS Model)", "file rev 1.0, 22 May 2014",
     "https://www.ti.com/lit/zip/SLLC445", "925a6c7f6917401ed6252237ee8fc9c2e4106771d177832dfe5f7dabe11c2f7d",
     "yes: [Component] TUSB8041, the RGC (VQFN-64) package of the fitted TUSB8041IRGCR"),
    ("io-expander-pca9555", "v2/vendor/ti/ibis/pca9555.ibs", "TI SCPM035 (PCA9555 IBIS Model)", "file rev 1.0 (x_die), 8 March 2011",
     "https://www.ti.com/lit/zip/SCPM035", "56c19a4da921e38cdfb67c3c24d2ea98ce63beae787de611d5e50378e497b300",
     "yes: [Component] PCA9555_PW, the TSSOP (PW) 24 of the fitted PCA9555PWR"),
    ("outlet-interlock-nand", "v2/vendor/ti/ibis/sn74lvc1g00.ibs", "TI SCEM165 (SN74LVC1G00 IBIS Model, Rev. A)", "file rev 1.2 (d_die), 24 April 2013",
     "https://www.ti.com/lit/zip/SCEM165", "e085986b1ed2969ed7312e201a68197865a8342e576793408dcd7e19ea92abb4",
     "yes: [Component] LVC1G00_DBV, the SOT-23-5 of the fitted SN74LVC1G00DBVR"),
    ("panel-emcon-lamp-gate", "v2/vendor/ti/ibis/sn74lvc1g57.ibs", "TI SCEM292 (SN74LVC1G57 IBIS Model, Rev. A)", "file rev 1.2 (x_die), 3 December 2002",
     "https://www.ti.com/lit/ibs/SCEM292", "7abbc41dad6b027a0061534f7ba31dfa74e827b8d339381b1e9daf653078198d",
     "yes: [Component] LVC1G57_DBV, the SOT-23-6 of the fitted SN74LVC1G57DBVR"),
    ("bbm-xor", "v2/vendor/ti/ibis/sn74lvc86a.ibs", "TI SCEM060 (SN74LVC86A IBIS Model, Rev. B)", "file rev 1.2 (k_die), 3 January 2012",
     "https://www.ti.com/lit/zip/SCEM060", "0f9780c8d3fd9b898438a57c8624469e46df247ccbda073fc14db15b79a53eb8",
     "yes: [Component] LVC86A_PW, the TSSOP-14 of the fitted SN74LVC86APWR"),
    ("board-d-flange-adc", "v2/vendor/ti/ibis/ads1x1x.ibs", "TI SBAM025 (ADS1013-5, ADS1113-5 IBIS Model)", "file rev 1.0, 23 September 2009",
     "https://www.ti.com/lit/zip/SBAM025", "c9975d3cb6ad0161d4c41a26e18316c4d3c6fb61b839121032b1de16f68a1ac2",
     "yes: [Component] ADS1X15IDGS, the VSSOP-10 of the fitted ADS1115IDGSR"),
    ("logic-held-sheets-round-8", "v2/vendor/ti/ibis/sn74lvc1g04.ibs", "TI SCEM216 (SN74LVC1G04 IBIS Model, Rev. C)", "file rev 1.4 (d_die), 5 March 2014",
     "https://www.ti.com/lit/zip/SCEM216", "03033638d7fe8bf268428be133a5aad63aae0145980113561b20ab92063e2c00",
     "yes for SN74LVC1G04DBVR: [Component] LVC1G04_DBV"),
]
OWED = ("27 September 2026 (stream w5si): four makers' IBIS models filed for rule SI-001 and cited by "
        "v2/ecad/tools/pcb_edge_rates.yaml have no part entry here to carry them: v2/vendor/ti/ibis/sn74lvc08a.ibs (TI SCEM010, "
        "SN74LVC08APWR, board B's voters and board A's U26), v2/vendor/ti/ibis/sn74lvc32a.ibs (TI SCEM055, SN74LVC32APWR, board "
        "B's voters), v2/vendor/ti/ibis/ina226.ibs (TI SBOM458, board A's rail monitors) and v2/vendor/ti/ibis/tmp117.ibs (TI "
        "SNOM652, board B's U10); sources.txt and vendor-status.txt carry a line for each")


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    import yaml
    s = open(TARGET, encoding="utf-8").read()
    before = yaml.safe_load(s)
    assert OWED not in (before.get("owed") or []) and not any(
        isinstance(x, dict) and x.get("path") in {r[1] for r in ROWS}
        for e in before.get("parts") or [] for x in e.get("documents") or []), "already applied"
    for eid, path, doc_id, rev, url, h, match in ROWS:
        assert sha(os.path.join(ROOT, path)) == h, "%s is not the file this draft recorded" % path
        head = "\n  - id: %s\n" % eid
        assert s.count(head) == 1, "entry %s is not found exactly once" % eid
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
        row = ('      - {path: "%s", doc_id: "%s", revision: "%s", url: "%s", fetched: "%s", sha256: "%s", '
               'matches_fitted: "%s", cited_by: "v2/ecad/tools/pcb_edge_rates.yaml (rule SI-001)"}'
               % (path, doc_id, rev, url, FETCHED, h, match))
        lines.insert(k, row)
        block = block[:di + 1] + "\n".join(lines)
        s = s[:a] + block + s[b:]
    oi = s.find("\nowed:\n")
    assert oi != -1 and OWED not in s
    s = s[:oi + len("\nowed:\n")] + '  - "%s"\n' % OWED + s[oi + len("\nowed:\n"):]
    d = yaml.safe_load(s)
    ents = {e.get("id"): e for e in d.get("parts") or []}
    for eid, path, *_ in ROWS:
        assert any(isinstance(x, dict) and x.get("path") == path for x in ents[eid].get("documents") or []), (eid, path)
    assert any(OWED == x for x in d.get("owed") or [])
    # THE STRUCTURE, before against after: nothing but the intended rows moved
    assert set(d) == set(before), "a top-level key was added or lost"
    for k in before:
        if k not in ("parts", "owed"): assert d[k] == before[k], "the top-level key %s changed" % k
    assert d["owed"][1:] == before["owed"] and d["owed"][0] == OWED, "owed is not the old list with the one line added"
    mine = {}
    for eid, path, *_ in ROWS: mine.setdefault(eid, []).append(path)
    assert [e.get("id") for e in d["parts"]] == [e.get("id") for e in before["parts"]], "a part entry was added, lost or moved"
    for a, b in zip(before["parts"], d["parts"]):
        if a.get("id") not in mine:
            assert a == b, "the entry %s changed and was not to" % a.get("id")
            continue
        assert {k: v for k, v in a.items() if k != "documents"} == {k: v for k, v in b.items() if k != "documents"}, a.get("id")
        kept = [x for x in b["documents"] if not (isinstance(x, dict) and x.get("path") in mine[a["id"]])]
        assert kept == a["documents"], "the entry %s lost or changed a document row" % a.get("id")
        assert len(b["documents"]) == len(a["documents"]) + len(mine[a["id"]]), a.get("id")
    if "--dry-run" in sys.argv:
        print("dry run, nothing written: SOURCES.yaml would gain %d document rows and one owed line" % len(ROWS)); return
    open(TARGET, "w", encoding="utf-8").write(s)
    print("SOURCES.yaml: %d document rows and one owed line added" % len(ROWS))


if __name__ == "__main__":
    main()
