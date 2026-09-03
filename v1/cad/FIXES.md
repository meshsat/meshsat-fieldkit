# FIXES — `field_kit.step` Correctness Pass

Ran against the handoff prompt's list of suspected issues. Summary: most of the
hypothesized failures were not actually present. Three real gaps were fixed in
the first pass (colors, missing holes, case envelope), and then a much bigger
bug — silently broken placement — was caught in the second pass after the user
shared a PDF rendering that didn't match the intended layout.

## The placement bug (caught in second pass)

**`Box(...).locate(Location((x, y, z)))` and `Cylinder(...).locate(...)` inside
a `BuildPart` context were silently discarded.** Every primitive landed at its
default origin regardless of the intended location. All 11 components piled on
each other at (0,0,0); all 4 rods overlapped; all 3 floors stacked on top of
each other at the case center. Only the case envelope rendered correctly (it
had no `.locate()` call — it was built directly at origin).

Root cause: `.locate()` on a shape returns a *new* shape with the placement
applied, but chained onto `Box(...)` the returned shape is discarded rather
than fed back into the builder. The shape that was actually added to the
builder has no placement applied.

Verified with a minimal test:

```python
with BuildPart() as a:
    Box(10, 10, 10, align=Align.MIN).locate(Location((100, 0, 0)))
# a.part.bounding_box() → 0..10 in x (wrong)

with BuildPart() as b:
    with Locations(Location((100, 0, 0))):
        Box(10, 10, 10, align=Align.MIN)
# b.part.bounding_box() → 100..110 in x (correct)
```

**Fix:** Wrap every off-origin primitive in a `with Locations(Location((x, y,
z))):` block. Applied to the plate Box, both sets of plate holes (corner M3
and extras), every component, every rod, and the hollow-out subtraction on
the case. After the fix, bounding boxes of every part are exactly where the
code's coordinate math puts them, and plate volumes match the expected
`plate_size − Σ hole_volumes` to 0.0 mm³.

Kept the `NOTE on placement` comment at the top of `field_kit_step.py` so
future edits don't re-introduce the pattern.

---

## First-pass fixes (colors, holes, case)

## Validated via Flatpak FreeCAD 1.1.1

Command used for headless validation:

```
flatpak run --command=freecadcmd --filesystem=home org.freecad.FreeCAD -c "
import FreeCAD, Import
Import.open('/home/kyriakosp/Downloads/files/field_kit.step')
...
"
```

Result after the fixes: `Import.open` succeeds, 20 `App::Part` containers
appear in the tree (19 named parts + `Field_Kit` root), every part has a
non-zero volume and correct label.

## What the handoff prompt feared — but wasn't actually broken

| Suspected issue | Reality |
|---|---|
| "Parts may not be visible after import" | Not happening. All 19 parts import with correct bounding boxes. |
| "Labels may not be preserved (FreeCAD shows Solid_1, Solid_2)" | Not happening. FreeCAD shows `Floor_bottom`, `X1202_UPS`, `RockBLOCK_9603`, etc. — taken from the `PRODUCT(...)` entries build123d writes. |
| "Parts may all be merged into a single compound with no individual selection" | Not happening. Assembly hierarchy is explicit via `NEXT_ASSEMBLY_USAGE_OCCURRENCE` entries; each part is individually selectable. |
| "Units may be wrong (inches instead of mm)" | Not happening. STEP header declares `AUTOMOTIVE_DESIGN` schema and build123d emits mm; FreeCAD imports as mm. Dimensions verified on reopen. |

The build123d nests each labeled `App::Part` under a generic `SOLID`
`Part::Feature` child — cosmetic only, and common across all OCCT-based STEP
writers.

## What was actually broken — and fixed

### 1. Colors were not exported

The prior `field_kit_step.py` set no `Color(...)` anywhere. Only
`field_kit_build.py` (FreeCAD macro) assigned colors.

**Fix:** Defined a `CLR_*` palette at the top of `field_kit_step.py` and
assigned `part.color = CLR_X` before appending. Verified by `grep COLOUR_RGB
field_kit.step` → 14 distinct `COLOUR_RGB` entries plus matching
`STYLED_ITEM` bindings, one per distinct color (deduped across parts that
share a color — e.g. the three floors share `CLR_HDPE`).

Note: build123d encodes colors in linear space, then STEP writes the sRGB-
linear-equivalent values. The RGB numbers you see in FreeCAD will be a shade
lighter than what's in the `CLR_*` constants, but the hues survive. Tweak the
constants if a specific display appearance matters.

### 2. Top plate was missing LED and DSI holes; bottom/middle missing pass-throughs

`field_kit_build.py` drills five 8mm LED holes in a row, a 20mm DSI
pass-through on the top plate, a 15mm cable pass-through on the bottom plate,
and a 15mm center pass-through on the middle plate. `field_kit_step.py`
previously only drilled the four corner M3 clearance holes on each plate.

**Fix:** Added an `extra_holes` slot per floor in the `FLOORS` tuple, holding
`(x_plate_local, y_plate_local, diameter)` entries. The floor-build loop now
drills corner holes (M3 clearance) plus whatever extras the tuple provides.
Top plate gets its LED row computed from `LED_HOLE_DIAMETER` and plate
dimensions; all three floors now match `field_kit_build.py`'s hole patterns.

### 3. Case envelope was not exported

Previous `field_kit_step.py` built a hollow case with `BuildPart() as case_ref`
then deliberately did not append it, with the comment "creates visual
clutter". The handoff prompt wanted the case visible for fit checks.

**Fix:** Labeled the shell `Case_Boundary`, assigned `CLR_CASE`, and appended
it. It now ships as a 19th part. STEP doesn't carry transparency metadata, so
to see the internals in FreeCAD: right-click `Case_Boundary` → `Appearance…`
→ set Transparency to ~80%.

## Unrelated to this pass

- The handoff prompt suggested generating a native `.FCStd` via `freecadcmd`
  and the existing `field_kit_build.py`. Not done — STEP now covers every
  concern the prompt listed, and `.FCStd` would add a second artifact to keep
  in sync without a clear win over the STEP. Skipping unless there's a
  specific FreeCAD-only feature needed (e.g., parametric sketches editable in
  the GUI).
- The build123d `App::Part` → generic `SOLID` child nesting is an OCCT export
  quirk and would require either a different exporter or post-processing to
  remove. Not worth it for visualization.
