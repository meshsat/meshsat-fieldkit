"""r8int5, w3de check 2 blocking item 2, done as stated: rules_render.py's bring-up classification treats a list source
whose every element is an input designator (J..., F<n>) as an input, with a fixture both ways
(tests/test_bringup_kind.py). The classification moves out of bringup_doc into bringup_kind() so a test can reach it,
and the page's 'at' column prints a list source as its designators, not as a Python list. Run from the worktree root."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'common'))
from edlib import once
RR = 'v2/ecad/tools/rules_render.py'
once(RR, '''        def kind(r):
            """input, derived, or ASK: what a rail's declared source says about where it comes from.

            A connector or a fuse is an input; the board receives that rail. A part is a converter output; the
            board makes it. AN INDUCTOR OR A FERRITE IS NEITHER, and pretending otherwise is how a first draft
            of this page told a bench supply to put 3.3 V onto board A's logic rail: L7 is a buck's OUTPUT
            inductor there, and L2 on board E is a filter choke on the incoming 12 V. The tool cannot tell those
            apart from the declaration, so it says so instead of choosing.
            """
            src = str((r or {}).get("source") or "")
            if not src: return "input"
            if src.startswith("J"): return "input"
            if re.match(r"^F\\d", src): return "input"
            if re.match(r"^(L|FB)\\d", src): return "ask"
            return "derived"

        by = {"input": [], "derived": [], "ask": []}
        for k, v in rails.items(): by[kind(v)].append((k, v))''',
'''        by = {"input": [], "derived": [], "ask": []}
        for k, v in rails.items(): by[bringup_kind(v)].append((k, v))''', marker="by[bringup_kind(v)]")
once(RR, '''                     % (n, net.lstrip("/"), float(r.get("volts") or 0), float(r.get("amps_typ") or 0),
                        r.get("source") or "another board or the pack", loads))''',
'''                     % (n, net.lstrip("/"), float(r.get("volts") or 0), float(r.get("amps_typ") or 0),
                        _source_text(r) or "another board or the pack", loads))''', marker='_source_text(r) or "another board or the pack"')
once(RR, '''                     % (n, net.lstrip("/"), v, v * 0.95, v * 1.05, r.get("source") or "?", loads))''',
'''                     % (n, net.lstrip("/"), v, v * 0.95, v * 1.05, _source_text(r) or "?", loads))''', marker='_source_text(r) or "?"')
once(RR, '''                         % (net.lstrip("/"), float(r.get("volts") or 0), float(r.get("amps_typ") or 0),
                            r.get("source"), loads))''',
'''                         % (net.lstrip("/"), float(r.get("volts") or 0), float(r.get("amps_typ") or 0),
                            _source_text(r), loads))''', marker="_source_text(r), loads))")
once(RR, '''def bringup_doc(reg, cov):''',
'''def _source_one(src):
    """The kind of one designator: see bringup_kind."""
    src = str(src or "")
    if not src: return "input"
    if src.startswith("J"): return "input"
    if re.match(r"^F\\d", src): return "input"
    if re.match(r"^(L|FB)\\d", src): return "ask"
    return "derived"


def bringup_kind(r):
    """input, derived, or ASK: what a rail's declared source says about where it comes from.

    A connector or a fuse is an input; the board receives that rail. A part is a converter output; the
    board makes it. AN INDUCTOR OR A FERRITE IS NEITHER, and pretending otherwise is how a first draft
    of this page told a bench supply to put 3.3 V onto board A's logic rail: L7 is a buck's OUTPUT
    inductor there, and L2 on board E is a filter choke on the incoming 12 V. The tool cannot tell those
    apart from the declaration, so it says so instead of choosing.

    A LIST SOURCE (27 September 2026, set 5, w3de check 2): a rail whose current enters at several designators at
    once declares them as a list, as board A's VIN_RAW does since EQ-16 (J_VR1 to J_VR4). It is an input only when
    EVERY element is an input designator (J..., F<n>); one inductor or ferrite among them makes it ASK, and any
    other part makes it derived. Before, the list was read through str(), which starts with '[', so board A's main
    input moved out of 'Applied, in this order' and the page told the reader it is never applied from the bench."""
    src = (r or {}).get("source")
    if isinstance(src, (list, tuple)):
        if not src: return "input"
        kinds = [_source_one(x) if str(x or "") else "derived" for x in src]
        if all(k == "input" for k in kinds): return "input"
        if "ask" in kinds: return "ask"
        return "derived"
    return _source_one(src)


def _source_text(r):
    """A rail's declared source as the page prints it: a list as its designators joined by commas."""
    src = (r or {}).get("source")
    if isinstance(src, (list, tuple)): return ", ".join(str(x) for x in src)
    return src


def bringup_doc(reg, cov):''', marker="def bringup_kind(r):")
T = 'v2/ecad/tools/tests/test_bringup_kind.py'
if not os.path.exists(T):
    open(T, 'w').write('''"""The bring-up page's classification of a rail's declared source (27 September 2026, MESHSAT-1357 set 5, from the
independent check of stream w3de): a list source whose every element is an input designator is an input, both ways.

THE DEFECT: board A's VIN_RAW declares its source as the four Mill-Max power pins J_VR1 to J_VR4 since EQ-16. The page
read the source through str(), which begins with '[', so the rail was classed derived and moved out of 'Applied, in
this order' into 'Measured after the inputs are up', whose text says a derived rail is never applied from the bench:
the current-limited application of the board's main input was lost from its bring-up procedure."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rules_render as RR


def t_a_list_whose_every_element_is_an_input_designator_is_an_input():
    for src in (["J_VR1", "J_VR2", "J_VR3", "J_VR4"], ["F1", "J_X1"], ("J_CP1",)):
        assert RR.bringup_kind({"source": src}) == "input", src


def t_a_list_with_a_part_or_a_filter_in_it_is_not_an_input():
    assert RR.bringup_kind({"source": ["J_VR1", "U3"]}) == "derived"
    assert RR.bringup_kind({"source": ["U3", "Q2"]}) == "derived"
    assert RR.bringup_kind({"source": ["J_VR1", "L2"]}) == "ask"
    assert RR.bringup_kind({"source": ["J_VR1", "FB1"]}) == "ask"
    assert RR.bringup_kind({"source": ["J_VR1", ""]}) == "derived"


def t_a_single_source_reads_as_it_did():
    for src, want in (("J_DOCK", "input"), ("F3", "input"), ("", "input"), (None, "input"), ("U39", "derived"),
                      ("R213", "derived"), ("L7", "ask"), ("FB1", "ask"), ("FE_OUT", "derived")):
        assert RR.bringup_kind({"source": src}) == want, (src, want)


def t_the_str_reading_would_have_misread_the_list():
    """The mutation: the pre-fix rule, str() of the source, classes the input list as derived."""
    src = ["J_VR1", "J_VR2", "J_VR3", "J_VR4"]
    assert not str(src).startswith("J")
    assert RR._source_one(str(src)) == "derived" and RR.bringup_kind({"source": src}) == "input"


def t_the_page_prints_a_list_source_as_its_designators():
    assert RR._source_text({"source": ["J_VR1", "J_VR2"]}) == "J_VR1, J_VR2"
    assert RR._source_text({"source": "J_DOCK"}) == "J_DOCK"
''')
print("fix_bringup_kind_r8int5: applied")
