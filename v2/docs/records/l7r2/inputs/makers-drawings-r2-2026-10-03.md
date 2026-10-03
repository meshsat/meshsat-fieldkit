# The makers' drawings read by record l7r2, transcribed (MESHSAT-1357, Layer 7 round 2, 3 October 2026)

Each document was fetched from its maker's own site (or the Internet Archive's copy of the maker's own page where the maker refused
this host), with curl from the runner, on 3 October 2026 between 14:20 and 14:50 UTC. The documents are held back from the public
tree by their terms, read conservatively (every one carries a maker's copyright or a reserved-rights notice): `fetch_held_back.py`
fetches them into this record's `held/` folder and checks each sha256 below; this page carries the figures the record reads, each
exactly as printed (inches converted only where the maker prints both). A figure read off a drawing's dimension lines (no text
layer) says so. Nothing has been bought or measured.

## D1. Glenair 233-330, RJ45 Cat 5e/6A feed-through receptacle, MIL-DTL-38999 Series III type (SuperSeal catalogue pages B-22 and B-23)

- URL `https://www.glenair.com/superseal/superseal-rj45-cat-5e-6a-ip67-open-face-rated/pdf/233-330.pdf`, 597,327 bytes, sha256
  05280f3e6eff592b3ed9b450e24008ed8c06563a9ef797000a6458b14c0061d7; Rev. 01.14.22 (page B-22), Rev. 03.28.2018 and 01.14.22 (page B-23).
- Shell size: **17 or 19** only. Finishes: NF aluminium/cadmium olive drab, ME aluminium/electroless nickel, MT aluminium/nickel PTFE,
  ZR aluminium/black zinc-nickel. Styles: 00 wall mount slotted holes, 07 jam nut rear panel mount, D0 wall mount round holes, CM wall
  mount metric clinch nuts. RJ45 category 5H (Cat 5e) or 6A.
- Wall mount, shell 17: **B square 1.323 (33.60) max, 1.299 (32.99) min**; C bsc 1.062 (26.97); D bsc 0.969 (24.61); E 0.136 (3.45) /
  0.120 (3.05); F 0.202 (5.13) / 0.186 (4.72); **H holes 0.136 (3.45) / 0.120 (3.05)**. Shell 19: B 1.449 (36.80) / 1.425 (36.20); C 1.156 (29.36).
- Side view (00, D0, CM): **1.550 (39.37) max** overall; **.650 (16.51) / .600 (15.24)** behind the flange; flange .098 (2.49) / .083 (2.11);
  "2x A Thread", shell 17 **1.1875-.1P-.3L-TS-2A**; panel accommodation **.0625/.250 (1.59/6.35)** "(This Side Only)".
- Notes: "2. front panel mount only"; "3. Meets IP67 in unmated condition, IP68 mated"; "4. Feed-thru receptacle is jack-to-jack
  configuration"; "All external dimensions, features, etc. compliant with D38999/20, /24, & /26."
- **Not printed:** a voltage or current rating; whether the RJ45 jacks' shields are joined to the shell; a panel cut-out (note 1
  refers to "Section A").

## D2. Bulgin PX0888, shielding backshell accessory for PX0833 series couplers

- The maker's datasheet service refused this host (HTTP 403); read from the Internet Archive's copy of the maker's own page,
  `https://web.archive.org/web/20230702120446id_/https://www.bulgin.com/pdf/pdf.php?sku=PX0888`, 163,499 bytes, sha256
  e190b66fe9fe17e24c7632581c80cf235cf2e7c6c0fe266a8c6ae3b3a7b461f2 (captured 2 July 2023).
- "PX0888 Shielding Backshell available separately - fits to rear of connector to maintain RJ45 coupler shielding directly to panel";
  "PX0833/E (Cat5e) or PX0893/E (Cat6a) versions has additional Earth wire"; Body Material **SS 304**; Diameter Over Coupling Ring
  38.1mm; IP68, IP69K; -20 to +70 C. **No dimension of the backshell is printed.**
- The coupler's own sheet is held in the tree (`v2/vendor/bulgin/bulgin-px0833-sealed-rj45-coupler.pdf`): Body Material Polyester
  (PET), Plastic Body; Current Max 1.5A; **Voltage Max 42V**; Diameter Over Coupling Ring 38.1mm.

## D3. Amphenol LTW RCP-5SPFFH-SCM7001, RJ45 receptacle, middle size, screw thread (the maker's product page)

- URL `https://amphenolltw.com/product-info/RJ/RJ.MiddleSize/RCP-5SPFFH-SCM7001`, the page's HTML sha256
  5e2a20a617d93a15b928e725d933e331aca3f08244eb8f37394ce77f3110a9a2 (read 3 October 2026, 14:31 UTC). Not filed (served by script).
- As printed in its Specifications block: Nominal Current 1.5A; Connector Type Receptacle; **Shielded: "Plastic, Shielded"**; Mating
  Style Screw Thread; IP Rating IP67; **Operating voltage 44 ~ 57V**; Salt Spray 48h; **Receptacle Nut Thread 13/16 inch - 28 UNS**;
  Fasten Style Front; **Panel Thickness "With Cap: 4.20; Without Cap: 3.00"**; Net Weight 18.75 g.
- The 2D drawing, the 3D models and the "ALTW RJ Middle C Size Product Specification" are behind a download form: **not read**.

## D4. Radiall R125.172.001, SMA right angle plug, crimp type, cable 2.6/50 S (RG 316, RG 188, KX 22A)

- URL `https://radiall-files.s3.amazonaws.com/tds/coaxialconnectors/R125172001%20R.pdf` (Radiall's own document store, the address
  radiall.com's catalogue links), 25,834 bytes, sha256 c94b970c9079cad54da38a7fd73439d197890cd8ddc453b054ec6c824f7a6cae; Issue 0122 R.
- Text layer: body stainless steel passivated; centre contact brass gold over nickel; insulator PTFE; gasket fluoro silicone; 50 Ohm,
  0 to 12.4 GHz; **voltage rating 250 Veff maxi**; mating torque 100 N.cm; operating temperature -65/+165 C; weight 4.328 g; crimp
  tool hexagon **3.25**; stripping a 2.80, b 7.00, c 12.8; cable retention 90 N mini.
- **Read off the drawing's dimension lines** (page 1, no text layer; rendered at 110 dpi and read): body 6.35 square; overall from the
  body's back face to the ferrule's end **19.6**; mating axis to the ferrule's end **15.2**; mating axis to the ferrule's start 11.5;
  ferrule **diameter 3.275** (before crimp); cable bore 1.63; total height from the body's top to the coupling nut's face **16.3**; the
  cable axis **13** above the nut's face and **10.1** above the reference plane; the coupling nut hex 8 across flats; 10.7 from the
  mating axis to the body side's ferrule shoulder. So the cable axis is 16.3 - 13 = **3.3** below the plug's inner end, and the plug's
  inner end stands 10.1 + 3.3 = **13.4** beyond the reference plane.

## D5. JST, solderless terminals, RING TONGUE (R type) non-insulated (JIS C 2805)

- URL `https://www.jst-mfg.com/product/pdf/eng/eRING1.pdf`, 555,629 bytes, sha256 807b12bd15d35d9e931d23c10cc4e5c99c608ea4347d3870d9b6ce6852898d71.
- Row 5.5-4 (JIS R5.5-4), applicable wire AWG 12 to 10 (2.63 to 6.64 mm2), stud #8 / M4: **d2 4.3, B 9.5, L 19.8, F 8.3**; the
  barrel D 5.6, d1 3.4, **T 1.0**; 500 per box.
- Row 5.5-6 (JIS R5.5-6), stud 1/4 / M6: **d2 6.4, B 12.0, L 25.8, F 13.0**; the same barrel.

## D6. JST PH connector (2.0 mm pitch), crimp style

- URL `https://www.jst-mfg.com/product/pdf/eng/ePH.pdf`, 103,369 bytes, sha256 447624f4f2f7d37c58c1eaa7ee314ad757fe7aff48f6186491ef6f69fbc00b96.
- Current rating 2 A AC/DC (AWG #24); voltage rating 100 V AC/DC; **temperature range -40 to +105 C** (including temperature rise);
  contact resistance 10 mOhm max initial; **applicable wire AWG #32 to #24**, insulation 0.5 to 1.5 mm; contacts **SPH-002T-P0.5S AWG
  #30 to #24** (insulation 0.8 to 1.5), SPH-002T-P0.5L AWG #28 to #24; housing **PHR-4** (A 6.0, B 9.8); header **B4B-PH-K-S** (top
  entry, A 6.0, B 9.9).

## D7. JST SH connector (1.0 mm pitch), crimp style

- URL `https://www.jst-mfg.com/product/pdf/eng/eSH.pdf`, 84,427 bytes, sha256 ea3071ca5ee5a6069eba534fa39a10f34c9fb742ee42135a69ab4156bfa0f5de.
- Current rating 1.0 A AC/DC (AWG #28); **temperature range -25 to +85 C**; **applicable wire AWG #32 to #28**; contact SSH-003T-P0.2-H
  (#32 to #28, insulation 0.4 to 0.8); housing SHR-04V-S; header **BM04B-SRSS-TB** (board B's J_FAN land).

## D8. Amphenol Socapex RJFIELD catalogue (128 pages, June 2023)

- URL `https://www.amphenolpcd.com/wp-content/uploads/2023/06/rj_field_catalog.pdf` (Amphenol's own site), 21,034,155 bytes, sha256
  917b95d5bee65d6638612c458207e88cc0b13b712e47954900501d0715df6f71.
- RJF: "Robust metallic shells based on MIL-DTL-26482 J - Shell size 18"; "The complete solution is metallized and united when
  connected in order to transmit the electrical continuity from the cordset to the panel"; IP68; -40/+85 C; cable 6 to 12 mm. RJFTV:
  MIL-DTL-38999 Series III, shell size 19. **No voltage rating is printed for RJF or RJFTV**; the only one is the ATEX range's "Voltage :
  60 Veff max" (pages 61 and 64). The square-flange drawings carry no text layer (not read).

## D9. Read from documents already in the tree

- `v2/vendor/d38999/amphenol-d38999-iii-federal.pdf` (Amphenol's Series III catalogue, the D38999/26 plug table): shell 13 Q max 1.157
  (29.4), shell 15 1.280 (32.5), **shell 17 1.406 (35.7)**.
- `v2/vendor/d38999/glenair-series-iii-iv-panel-cutouts.pdf` (Glenair, Rev. 09.01.20), shell code E (16-17): A dia (rear panel mount)
  **1.219 (30.96)**, AA dia (front panel mount) 1.016 (25.81), R1 1.062 (26.97).
- `v2/vendor/cm5/rpi-cm5-cooler-product-brief-2024-12.pdf` (record l7pwr): passive heatsink 56 x 41 x 12.7 mm, holes 48 x 33, "2.7"
  and "10" on the side view (the base and the fins), four M2.5 x 8 screws upward from beneath the carrier into the cooler.
