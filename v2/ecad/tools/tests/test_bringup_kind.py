"""The bring-up page's classification of a rail's declared source (27 September 2026, MESHSAT-1357 set 5, from the
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
