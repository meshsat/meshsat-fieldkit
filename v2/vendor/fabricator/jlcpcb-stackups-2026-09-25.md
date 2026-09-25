# JLCPCB stackups at 2 oz outer copper (four layers) and at eight layers

A companion to `jlcpcb-impedance-stackups-2026-09-16.md`, which transcribed only the impedance page's default
selector state (1.6 mm, 1 oz outer, 0.5 oz inner); the page's selectors serve further rows, including these.

**Source.** Read anonymously on 25 September 2026 between 21:24 and 21:38 UTC (MESHSAT-1357), and transcribed here.
- `https://jlcpcb.com/impedance`, four-layer section, with the visitor's "Outer Copper Weight 2oz" button clicked in a
  headless browser. The page then POSTs
  `https://jlcpcb.com/api/overseas-core-platform/shoppingCart/getImpedanceTemplateSettings` with
  `{stencilLayer: 4, stencilPly: 1.6, cuprumThickness: 2, insideCuprumThickness: 0.5}` and lists the stackups below.
- `https://cart.jlcpcb.com/quote` (the order form), Layers 8, "Specify Stackup: Yes", 1.6 mm, 1 oz outer, 0.5 oz inner.
  The form calls the same endpoint with `stencilLayer: 8`; its "Layer Stackup" dialog lists the default ("No
  requirement") and twelve distinct codes, thirteen entries in all.
  The impedance page itself has no eight-layer section (its page state holds only a four-layer and a six-layer form).
- JLC's impedance calculator template endpoint `https://jlcpcb.com/api/jlcTools/impedance/selectPageImpedanceDefaultTemplate`,
  which returns each code's layers with a dielectric constant per layer and JLC's finished-thickness label.
- `https://jlcpcb.com/capabilities/pcb-capabilities` for the 2 oz rows.

Evidence captures (held with the session record, not in this repository; sha256 given so a copy can be checked):
the 4-layer 2 oz page render `impedance_4L_outer2oz_2026-09-25.png` (`6050fa84da8c806f...`), its request and response
`impedance_4L_outer2oz_xhr_2026-09-25.json` (`096ea7b58f835dbd...`), the order-form response for 4 layers at 2 oz
`quoteform_4L_1.6_2oz_inner0.5_2026-09-25.json` (`5c4898769602792f...`), the 8-layer dialog render
`quote_8L_specify_stackup_2026-09-25.png` (`53d6aad43ac44388...`) and its response `quote_8L_specify_xhr_2026-09-25.json`
(`f92d585d901847c7...`), the full endpoint sweeps `impedance_template_sweep_2026-09-25.json` (`a1203fb1a064223a...`) and
`calculator_template_sweep_2026-09-25.json` (`b5a618d5f839fb6a...`), and the capability text
`text_capabilities_2026-09-25.txt` (`7daa6b0ae51d392b...`).

**Prototype work.** No board of the V2 set has been built or ordered; these rows are what the fabricator publishes, not a record of a build.

**The same caution as its companions.** A fabricator's page is not a controlled document and can change without
notice. The date travels with every number, and a board ordered on these numbers has them confirmed on the order.

## Four layers, 1.6 mm, 2 oz outer copper, 0.5 oz inner: JLC04162H-7628 (the default)

The page and the order form list five enabled entries for this combination, all with no fixed fee: four distinct codes
(JLC04162H-7628, JLC04162H-3313A, JLC04162H-3313 and JLC04162H-2116) plus the default, "No requirement", which is itself
the template JLC04162H-7628 with the same layer table. The default:

| layer | material | thickness (mm) | Dk (calculator) |
|---|---|---|---|
| top | copper, 2 oz | 0.070 | |
| prepreg | 7628 x 1 | 0.2104 | 4.4 |
| inner L2 | copper | 0.0152 | |
| core | 1.1 mm H/HOZ with copper | 1.065 | 4.38 |
| inner L3 | copper | 0.0152 | |
| prepreg | 7628 x 1 | 0.2104 | 4.4 |
| bottom | copper, 2 oz | 0.070 | |

Layer sum 1.6562 mm, which is the response's own `compressionThickness` for the code; JLC's label "JLC04162H-7628
(general, finished board thickness 1.66 mm +-10%)". The layer table gives the core as "1.1mm H/HOZ with copper": 1.065 mm
of dielectric between the two 0.0152 mm inner copper rows. The impedance page prints 4.6 for the core where the
calculator gives 4.38 (see the last section).

The other codes at 4 layers, 1.6 mm, 2 oz outer (layer sums; the order form returns the same lists):
- 0.5 oz inner: JLC04162H-3313 (3313 prepreg 0.0994, core 1.265; 1.6342), JLC04162H-3313A (3313 0.107 plus 1080 0.0764,
  core 1.065; 1.6022, marked special), JLC04162H-2116 (2116 0.124 plus 1080 0.084 plus 1080 0.0764, core 0.865; 1.6042,
  marked special).
- 1 oz inner: JLC041621-7628 (default, 1.636), -3313, -2116, -1080, -1080A, -7628B, and -7628A (fixed fee 330, unit not
  stated).
- 2 oz inner: JLC041622-3313 (default, 1.589), -1080, and -7628 (fixed fee 110, unit not stated).

This is the row board P's decision 28 (four layers at 2 oz outer) was waiting for. Which inner copper weight to record
is an engineering choice; 0.5 oz is the fabricator's default. Board P needs no controlled impedance.

## Eight layers, 1.6 mm, 1 oz outer, 0.5 oz inner: JLC08161H-2116 (the default)

The order form's response holds thirteen enabled entries: twelve distinct codes plus the default. The default, "No
requirement", is itself the template JLC08161H-2116 (template code 20220913081702559), with the same eleven-row layer
table as that code's own entry (template code 20211110043453), which JLC's impedance calculator names "JLC08161H-2116
(general free, finished board thickness 1.6 mm +-10%)". The twelve distinct codes are JLC08161H-2116, -2313, -3313,
-2313A, -2116C, -7628 (fixed fee 330), -2116B, -1080A (550), -1080 (330), -2116A (550), -1080C and -1080B; the rest
carry no fixed fee, and the fee's unit is not stated. The default:

| layer | material | thickness (mm) | Dk (calculator) |
|---|---|---|---|
| L1 | copper, 1 oz | 0.035 | |
| prepreg | 2116 x 1, RC 54 % | 0.1164 | 4.16 |
| inner L2 | copper | 0.0152 | |
| core | 0.3 mm H/HOZ without copper | 0.3 | 4.41 |
| inner L3 | copper | 0.0152 | |
| prepreg | 1080 x 1, RC 67 % | 0.0764 | 3.91 |
| prepreg | 1080 x 1, RC 67 % | 0.0764 | 3.91 |
| inner L4 | copper | 0.0152 | |
| core | 0.3 mm H/HOZ without copper | 0.3 | 4.41 |
| inner L5 | copper | 0.0152 | |
| prepreg | 1080 x 1, RC 67 % | 0.0764 | 3.91 |
| prepreg | 1080 x 1, RC 67 % | 0.0764 | 3.91 |
| inner L6 | copper | 0.0152 | |
| core | 0.3 mm H/HOZ without copper | 0.3 | 4.41 |
| inner L7 | copper | 0.0152 | |
| prepreg | 2116 x 1, RC 54 % | 0.1164 | 4.16 |
| L8 | copper, 1 oz | 0.035 | |

Layer sum 1.5996 mm, which is the response's own `compressionThickness` for the code. The fabricator's layer table
gives each core as "0.3mm H/HOZ without copper" with 0.0152 mm of copper on each side, so the inner copper is listed
here as its own rows and counted once. Two 1080 plies sit between L3 and L4 and two between L5 and L6. Blind and buried
vias are not offered (capability page); through vias only.

## The 2 oz rows of the capability page (read the same day)

- Minimum track width and spacing at 2 oz, multilayer: 0.15 / 0.15 mm (6 / 6 mil).
- Solder-mask bridge, minimum pad spacing: 1 oz 0.10 mm (green, red, yellow, blue, purple) or 0.13 mm (black, white);
  2 oz 0.20 mm (any colour).
- PTH annular ring at 2 oz: 0.254 mm or above, on two-layer and on multilayer boards. The companion transcription
  `jlcpcb-pcb-capabilities-2026-09-16.md` records this row as "NOT STATED FOR 2 oz"; the page carried it on 13 September
  2026 (Wayback capture 20260913020451), so that was an omission of the transcription, not a page change.
- Minimum SMD pad: 0.25 x 0.25 mm.
- Via-in-pad (epoxy or copper-paste filled and capped) is the default at six layers and above, vias 0.15 to 0.55 mm.

## Where JLC's own sources disagree: the core dielectric constant

The impedance page prints a single core Dk of 4.6 in its tables. The calculator gives 4.38 for JLC04161H-7628's and
JLC04162H-7628's 1.065 mm core, 4.41 for JLC06161H-3313's 0.55 mm cores and for JLC08161H-2116's 0.3 mm cores.
`v2/ecad/tools/stackup_write.py` writes the page's 4.6 in its JLC04161H-7628 and JLC06161H-3313 rows; its rows for
JLC04162H-7628 and JLC08161H-2116, added on 26 September 2026 under owner decisions 28 and 43, carry the calculator's
values from the two tables above. The estimated effect on a stripline's impedance is about 2 percent
(sqrt(4.6 / 4.41) = 1.021), INFERRED, not computed with `impedance_2d.py`; it is inside the +-10 percent the fabricator
controls to. Which value JLC designs to is the one stackup question still worth asking the fabricator; it does not block recording the row.
