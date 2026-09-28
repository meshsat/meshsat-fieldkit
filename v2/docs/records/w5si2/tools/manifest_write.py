#!/usr/bin/env python3
"""Writes v2/vendor/ibis-manifest.yaml from the models held locally (stream w5si2, 28 September 2026, MESHSAT-1357).

Run ONCE by the author with the thirteen models present; the manifest is a tracked file and is maintained by hand
afterwards (a new model is a new row; tools/ibis_fetch.py --check holds every row to the file it names). Kept in the
record so that a reader can see where each field came from: the digest, the byte count, [File Rev] and [Date] are read
from the file; the URL, the container and the member are the first author's fetch records (v2/vendor/sources.txt at
231b52b4 and RECOVERY.md); the notice is the file's own [Disclaimer] and [Copyright] text, of which the sentences that
speak of copying or distribution are quoted, with the lines they stand on.

Usage: manifest_write.py <repository root> [--stdout]
"""
import os, re, sys, hashlib

ROWS = [
    # id, maker, part, file, literature, url, container, member
    ("ti-sn74lvc08a", "Texas Instruments", "SN74LVC08A", "v2/vendor/ti/ibis/sn74lvc08a.ibs", "SCEM010, SN74LVC08A IBIS Model (Rev. A)",
     "https://www.ti.com/lit/zip/SCEM010", "zip", "sn74lvc08a.ibs"),
    ("ti-sn74lvc32a", "Texas Instruments", "SN74LVC32A", "v2/vendor/ti/ibis/sn74lvc32a.ibs", "SCEM055, SN74LVC32A IBIS Model (Rev. B)",
     "https://www.ti.com/lit/ibs/SCEM055", "ibs", None),
    ("ti-sn74lvc86a", "Texas Instruments", "SN74LVC86A", "v2/vendor/ti/ibis/sn74lvc86a.ibs", "SCEM060, SN74LVC86A IBIS Model (Rev. B)",
     "https://www.ti.com/lit/zip/SCEM060", "zip", "SN74LVC86A_IBIS/sn74lvc86a.ibs"),
    ("ti-sn74lvc1g00", "Texas Instruments", "SN74LVC1G00", "v2/vendor/ti/ibis/sn74lvc1g00.ibs", "SCEM165, SN74LVC1G00 IBIS Model (Rev. A)",
     "https://www.ti.com/lit/zip/SCEM165", "zip", "SN74LVC1G00_IBIS/lvc1g00.ibs"),
    ("ti-sn74lvc1g04", "Texas Instruments", "SN74LVC1G04", "v2/vendor/ti/ibis/sn74lvc1g04.ibs", "SCEM216, SN74LVC1G04 IBIS Model (Rev. C)",
     "https://www.ti.com/lit/zip/SCEM216", "zip", "SN74LVC1G04_IBIS/sn74lvc1g04.ibs"),
    ("ti-sn74lvc1g57", "Texas Instruments", "SN74LVC1G57", "v2/vendor/ti/ibis/sn74lvc1g57.ibs", "SCEM292, SN74LVC1G57 IBIS Model (Rev. A)",
     "https://www.ti.com/lit/ibs/SCEM292", "ibs", None),
    ("ti-pca9555", "Texas Instruments", "PCA9555", "v2/vendor/ti/ibis/pca9555.ibs", "SCPM035, PCA9555 IBIS Model",
     "https://www.ti.com/lit/zip/SCPM035", "zip", "PCA9555/Release_TI/IBIS/PCA9555_IBIS/pca9555.ibs"),
    ("ti-tcan33x", "Texas Instruments", "TCAN330 to TCAN337", "v2/vendor/ti/ibis/tcan33x.ibs", "SLLM313, TCAN33X IBIS Model",
     "https://www.ti.com/lit/zip/SLLM313", "zip", "TCAN33x_IBIS/tcan33x.ibs"),
    ("ti-ina226", "Texas Instruments", "INA226", "v2/vendor/ti/ibis/ina226.ibs", "SBOM458, INA226 IBIS Model",
     "https://www.ti.com/lit/zip/SBOM458", "zip", "INA226/Release_TI/IBIS/INA226_IBIS/ina226.ibs"),
    ("ti-tmp117", "Texas Instruments", "TMP117", "v2/vendor/ti/ibis/tmp117.ibs", "SNOM652, TMP117 IBIS Model",
     "https://www.ti.com/lit/zip/SNOM652", "zip", "tmp117.ibs"),
    ("ti-ads1x1x", "Texas Instruments", "ADS1013 to ADS1015, ADS1113 to ADS1115", "v2/vendor/ti/ibis/ads1x1x.ibs",
     "SBAM025, ADS1013-5, ADS1113-5 IBIS Model", "https://www.ti.com/lit/zip/SBAM025", "zip", "ads1x1x.ibs"),
    ("ti-tusb8041", "Texas Instruments", "TUSB8041 (RGC)", "v2/vendor/ti/ibis/tusb8041rgc.ibs", "SLLC445, TUSB8041 IBIS Model",
     "https://www.ti.com/lit/zip/SLLC445", "zip", "TUSB8041RGC.ibs"),
    ("st-stm32h7-lqfp100", "STMicroelectronics", "STM32H742, H743, H750, H753 in LQFP100", "v2/vendor/st/ibis/stm32h742_743_750_753_lqfp100.ibs",
     "stm32h7_ibis.zip, ST's STM32H7 IBIS models", "https://www.st.com/resource/en/ibis_model/stm32h7_ibis.zip", "zip",
     "stm32h742_743_750_753_lqfp100.ibs"),
]
ARCHIVE = {"st-stm32h7-lqfp100": ("https://web.archive.org/web/20250911224858id_/https://www.st.com/resource/en/ibis_model/stm32h7_ibis.zip",
                                  "st.com refuses this host (both fetches of 27 September 2026); the Internet Archive's capture of 11 September 2025 "
                                  "serves the zip gzip-wrapped, 35.1 MB, the wrapper's sha256/16 d0ecb57c18b83077 on both fetches")}
# the sentences that speak of copying or distribution, searched in each header as written here
PROHIBITS = ["Unauthorized reproduction and/or distribution is strictly prohibited.",
             "You and your company shall not distribute, sell or give these models to anyone else without prior written permission from TI."]
FETCHED = "2026-09-27T17:00Z and again 2026-09-27T20:33Z (after the first copy was lost with its worktree), the same bytes both times"


def header(path):
    """[(line number, text without a leading comment bar)] of the [Disclaimer] and [Copyright] keywords, up to the first
    [Component]."""
    out, on = [], False
    for i, l in enumerate(open(path, encoding="utf-8", errors="replace").read().splitlines(), 1):
        if re.match(r"^\[Component\]", l, re.I): break
        if re.match(r"^\[(Disclaimer|Copyright)\]", l, re.I): on = True
        elif re.match(r"^\[", l): on = False
        if on: out.append((i, re.sub(r"^\s*\|+\s?", "", l).strip()))
    return out


def find(hdr, sentence):
    """The first and last line a sentence stands on in the header, whitespace collapsed, or None."""
    want, best = " ".join(sentence.split()), None
    for a in range(len(hdr)):
        acc = []
        for b in range(a, min(a + 6, len(hdr))):
            acc += hdr[b][1].split()
            if want in " ".join(acc):
                if best is None or (b - a) < (best[1] - best[0]): best = (a, b)      # the tightest window
                break
    return (hdr[best[0]][0], hdr[best[1]][0]) if best else None


def keyword(path, name):
    m = re.search(r"(?im)^\[%s\]\s*(.*)$" % re.escape(name), open(path, encoding="utf-8", errors="replace").read())
    return " ".join(m.group(1).split()) if m else None


def q(s): return '"%s"' % str(s).replace("\\", "\\\\").replace('"', '\\"')


def main():
    root = os.path.abspath(sys.argv[1])
    out = [HEAD]
    for rid, maker, part, rel, lit, url, cont, member in ROWS:
        p = os.path.join(root, rel)
        raw = open(p, "rb").read()
        hdr = header(p)
        quotes = []
        for s in PROHIBITS:
            at = find(hdr, s)
            if at: quotes.append((s, at))
        cp = [(i, t) for i, t in hdr if re.search(r"copyright", t, re.I) and re.search(r"\d{4}", t)]
        out.append("  - id: %s" % rid)
        out.append("    maker: %s" % q(maker))
        out.append("    part: %s" % q(part))
        out.append("    file: %s" % rel)
        out.append("    literature: %s" % q(lit))
        out.append("    url: %s" % url)
        out.append("    container: %s" % cont)
        if member: out.append("    member: %s" % q(member))
        if rid in ARCHIVE:
            out.append("    archive_url: %s" % ARCHIVE[rid][0])
            out.append("    archive_note: %s" % q(ARCHIVE[rid][1]))
        out.append("    sha256: %s" % q(hashlib.sha256(raw).hexdigest()))
        out.append("    bytes: %d" % len(raw))
        out.append("    file_rev: %s" % q(keyword(p, "File Rev")))
        out.append("    file_date: %s" % q(keyword(p, "Date")))
        out.append("    fetched: %s" % q(FETCHED))
        out.append("    notice:")
        if quotes:
            out.append("      kind: PROHIBITS_DISTRIBUTION")
            out.append("      says: %s" % q("the header forbids reproduction and distribution without the maker's written permission"))
        else:
            out.append("      kind: COPYRIGHT_NO_GRANT")
            out.append("      says: %s" % q("the header carries a disclaimer of warranty and a copyright line and NO sentence on copying or "
                                            "distribution: nothing in the file grants a right to redistribute it, and nothing in it forbids it in words"))
        out.append("      quotes:")
        for s, (a, b) in quotes:
            out.append("        - {lines: %s, text: %s}" % (q("%d to %d" % (a, b) if b != a else "%d" % a), q(s)))
        for i, t in cp[:2]:
            out.append("        - {lines: %s, text: %s}" % (q("%d" % i), q(" ".join(t.split()))))
    text = "\n".join(out) + "\n"
    if "--stdout" in sys.argv: sys.stdout.write(text); return
    dst = os.path.join(root, "v2", "vendor", "ibis-manifest.yaml")
    open(dst, "w", encoding="utf-8").write(text)
    import yaml
    d = yaml.safe_load(open(dst, encoding="utf-8"))
    assert len(d["models"]) == len(ROWS)
    print("%s: %d models, %d whose header forbids distribution, %d with a copyright line and no grant" % (
        os.path.relpath(dst, root), len(d["models"]),
        sum(1 for m in d["models"] if m["notice"]["kind"] == "PROHIBITS_DISTRIBUTION"),
        sum(1 for m in d["models"] if m["notice"]["kind"] == "COPYRIGHT_NO_GRANT")))


HEAD = """# THE MAKERS' IBIS MODELS THIS PROJECT READS, AND WHERE EACH COMES FROM (rule SI-001, tools/pcb_edge_rates.yaml)
#
# Written 28 September 2026 (MESHSAT-1357, layer 9, stream w5si2). Prototype design work: nothing has been built or
# measured.
#
# THE MODELS ARE NOT IN THIS REPOSITORY. They are the makers' files. Five of the thirteen say in their own header that
# reproduction and distribution are forbidden without the maker's written permission; the other eight carry a
# copyright line and no grant (each row's `notice` quotes the words and the lines they stand on). This repository is
# mirrored publicly within minutes of a push, so committing a model would publish it. Whether any of them is published
# is the owner's decision; the standing decision is to hold them back (v2/docs/EXECUTION-PLAN.md). `.gitignore`
# ignores `v2/vendor/*/ibis/*.ibs`. NEVER `git add -f` a model.
#
# THIS FILE IS WHAT IS TRACKED IN THEIR PLACE, and it is a CONFIGURATION INPUT of the edge_length verdict: it is
# recorded by sha in every SI-001 reading (inputs.ibis_manifest) and declared in rules_status.CONFIG_INPUTS, so it is
# dated by its commit like any other input. It PINS each model by the sha256 of the extracted `.ibs` file:
#   * tools/edge_length.py reads a model only when the file present is the one pinned here (the full sha256), and the
#     record of tools/pcb_edge_rates.yaml that cites the model must cite the same file (its sha256/16);
#   * a model that is ABSENT decides nothing: every net that waits on it reads UNDECIDED naming the file, the reading
#     is INCONCLUSIVE, and it records which models were absent (inputs.model_N, `absent: true`) and the state of the
#     set (inputs.model_state: PRESENT, PARTIAL, ABSENT or NOT_ASKED);
#   * rules_status holds a reading to this file: a model the reading read must be the one pinned here, a model present
#     in the checkout must be the one pinned here, and a reading taken without a model that is present now is re-taken.
#     A model that is absent from the checkout never makes a reading taken WITH it read as changed: the pin is what
#     dates it (rules_status.PINNED_INPUTS, applied by v2/docs/records/w5si/apply/apply_rules_status_pinned_models.py).
#
# HOW TO GET THE MODELS: `python3 v2/ecad/tools/ibis_fetch.py --fetch` from anywhere. It downloads each file from the
# maker's own address below, takes the `.ibs` out of the zip where the address is a zip (`container: zip`, `member`
# the path inside it), verifies the sha256 and the byte count, and writes it to `file`. It never overwrites a file
# that differs from its pin without --replace, and it is never run by a test or by a gate. `--check` fetches nothing
# and says which state the tree is in. A maker's site may refuse a host (st.com refuses this project's): the script
# then tries the Internet Archive, first the capture a row names (`archive_url`), then the newest capture of the
# maker's address (https://web.archive.org/web/2026id_/<url>); the archive may serve a file gzip-wrapped, which the
# script unwraps. Whoever fetches a model does so under the maker's terms, which the file itself states.
#
# FIELDS: id; maker; part (what the model covers); file (where edge_length.py reads it, relative to the repository);
# literature (the maker's literature number and title); url (the maker's address); container (ibs: the address serves
# the model itself; zip: it serves an archive and `member` is the model's path in it); archive_url and archive_note
# (where the maker's address was refused); sha256 and bytes (of the extracted `.ibs`); file_rev and file_date (the
# model's own [File Rev] and [Date]); fetched; notice (kind, what it says, and the header's words with their lines).
schema_version: 1
written: "2026-09-28"
publication: "WITHHELD from the repository by the standing decision; publication is the owner's decision"
models:"""

if __name__ == "__main__":
    main()
