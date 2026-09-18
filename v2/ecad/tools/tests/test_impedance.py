"""The impedance gate's own numbers: where they come from and what says so (MESHSAT-862, 18 September 2026).

`impedance_check.py` judges a pair against a target, and the number it judges with is either a field solver's
result for that exact cross-section or a measured bias applied to a closed form. Both are legitimate and they
are not the same thing, so the run says which and how many millimetres rode on each. These rules hold the two
halves of that honesty: the caution about the weaker half counts the table it describes rather than repeating a
literal that goes stale, and the run names the cross-sections themselves so the next solve is chosen rather than
guessed. Both were written the day six cross-sections were solved and the last of them found that board B routes
1,677 mm of its 100 ohm pairs 0.55 mm from their reference, which is 140 ohm and not 100.
"""

def t_the_stripline_caution_counts_its_own_table():
    """A sentence that states a count drifts from the table it describes (18 September 2026).

    The impedance gate's caution said the stripline correction "rests on two solved geometries (the solver reads
    0.74 and 0.80)" and stayed that way when two more were solved, which is a number in prose disagreeing with
    the number in the data three lines above it. It counts the table now."""
    import os
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "impedance_check.py"),
               encoding="utf-8").read()
    assert '_sl = len([c for c in CAL if c[0] == "stripline"])' in src, "the caution does not count the table"
    assert "rests on %d solved" in src, "the caution states a literal count again"
    assert "0.74 and 0.80 of IPC-2141" not in src, "the stale two-point sentence is still in the file"


def t_the_impedance_run_names_the_cross_section_carrying_a_factor():
    """A run that says "4,674 mm judged by the microstrip factor" names a quantity and not a cross-section, so
    the next solve is a guess. Boards A and B were each carrying a factor over the geometry they actually route
    (w 0.13 with the legs 0.14 to 0.15 apart against a solved 0.127/0.127), and nothing said so until the run
    listed the cross-sections themselves (18 September 2026)."""
    import os
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "impedance_check.py"),
               encoding="utf-8").read()
    assert "GEOMETRIES = {}" in src and "def _note(" in src, "the run does not record the cross-sections it judged"
    assert '"--geometries" in sys.argv' in src, "there is no way to ask for them"
    assert "solve this one: impedance_2d.py" in src, "the report does not say how to solve an unsolved cross-section"
