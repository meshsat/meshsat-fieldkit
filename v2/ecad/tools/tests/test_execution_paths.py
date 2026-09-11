#!/usr/bin/env python3
"""The pin on which files may produce a fab artefact.

MESHSAT-862, 11 September 2026, after finops-agora's `agora/validation/execution_paths.py`. The artefacts that leave
this repository and become money and fibreglass are the gerbers, the BOM, the CPL and the order set. A pinned
allowlist plus a scan plus a gate that fails on any difference is what keeps "only these files can do that" a fact
rather than a sentence in a document.

The rule has to bite in both directions, so both are tested: a new producer must fail the gate, and a pin entry that
no longer produces must fail it too, because a stale pin is how an allowlist quietly becomes decoration.
"""
import os, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import execution_paths as ep


def _tree(files):
    d = tempfile.mkdtemp(prefix="ep-")
    for name, body in files.items():
        p = os.path.join(d, name); os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(body)
    return d


def t_the_real_tree_matches_the_pin():
    found = ep.producers()
    unpinned = sorted(f for f in found if f not in ep.PIN and f not in ep.READERS)
    gone = sorted(f for f in ep.PIN if f not in found)
    assert not unpinned, "these produce a fab artefact and are pinned nowhere: %s" % unpinned
    assert not gone, "these are pinned as producers and no longer produce one: %s" % gone


def t_a_new_gerber_exporter_is_found():
    d = _tree({"sneaky.sh": "#!/bin/sh\nkicad-cli pcb export gerbers --output out/ b.kicad_pcb\n"})
    found = ep.producers(d)
    assert "sneaky.sh" in found, found
    assert any("gerbers" in w for w in found["sneaky.sh"]), found


def t_a_new_bom_writer_is_found():
    d = _tree({"quiet.py": "import csv\nw = csv.writer(open('x-bom.csv', 'w'))\nw.writerow(['Comment'])\n"})
    found = ep.producers(d)
    assert "quiet.py" in found, found


def t_a_file_that_only_reads_those_names_is_not_a_producer():
    """Reading is not actuating, and this is the distinction the whole pin rests on: `verify_deliverable.py` opens
    every gerber zip and `jlc_certify.py` reads every BOM, and neither may ever write one."""
    d = _tree({"reader.py": "import zipfile\nz = zipfile.ZipFile('b-gerbers.zip')\nrows = open('b-bom.csv').read()\n"})
    assert ep.producers(d) == {}, ep.producers(d)


def t_a_comment_mentioning_a_gerber_export_is_not_a_producer():
    d = _tree({"talky.sh": "#!/bin/sh\n# we used to kicad-cli pcb export gerbers here\necho nothing\n"})
    assert ep.producers(d) == {}, ep.producers(d)


def t_the_scanner_is_kept_out_of_its_own_scan():
    """It carries every pattern it looks for, so it matches itself. Same self-match the record pays for with
    `pkill -f`, and it flagged itself on the first run."""
    found = ep.producers()
    assert "execution_paths.py" not in found, found


def t_every_pin_entry_says_why():
    for f, why in ep.PIN.items():
        assert len(why) > 30, "%s is pinned without a reason worth reading: %r" % (f, why)
    for f, why in ep.READERS.items():
        assert len(why) > 30, "%s is declared a reader without a reason: %r" % (f, why)
