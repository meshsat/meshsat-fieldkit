# The decoupling declarations' maker clauses, looked up in the held documents (d6dec, 29 September 2026)

Written by `make_basis_md.py` from `basis.json`, which `box/basis_check.py` wrote on this host (bounded: pdftotext on 428 held PDFs, two jobs at the lowest priority) from the six boards' COMMITTED intent files, `v2/ecad/pcb-*-<phase>/out/*-intent.json` at this branch's merge of main 9147db5d. It reads what each `basis` puts in quotation marks and searches the document the basis names for those words. It judges the quotation, not the engineering: a FOUND row says the maker wrote those words, not that the class drawn from them is right.

**What a result means.** FOUND: every quoted passage is in the named document word for word after the normalisation of the tool's docstring (case, white space, typographic quotes and dashes, the micro sign, a line-end hyphen). PAGE: found, on another page than the basis states (a basis may count printed pages where the tool counts the PDF's own; the RP2040 datasheet's printed page is one less than its PDF page, which is every PAGE row of boards C and E). ELSEWHERE: found in a held document the basis does not name. NOT_FOUND: a quoted passage is in no held document as written. NO_QUOTE: the basis quotes nothing (most say the maker states no capacitor and the generator's own count stands, rule D1), so nothing can be looked up.

440 declarations and power-loop rows read, 125 distinct bases; 13 held PDFs have no text layer (drawings and one schematic; none is named by a basis that reads NOT_FOUND).

## Counts per board (each declaration counted once, with its basis's result)

| board | what | FOUND | PAGE | ELSEWHERE | NOT_FOUND | NO_QUOTE | total |
|---|---|---|---|---|---|---|---|
| A | bypass entries | 51 | 0 | 0 | 1 | 4 | 56 |
| A | power loops (`power_loops`) | 15 | 0 | 0 | 0 | 0 | 15 |
| B | bypass entries | 157 | 19 | 0 | 1 | 104 | 281 |
| C | bypass entries | 5 | 12 | 0 | 0 | 7 | 24 |
| D | bypass entries | 17 | 0 | 0 | 0 | 14 | 31 |
| E | bypass entries | 13 | 11 | 0 | 1 | 4 | 29 |
| P | bypass entries | 4 | 0 | 0 | 0 | 0 | 4 |
| all | | 262 | 42 | 0 | 3 | 133 | 440 |

## Every NOT_FOUND row

### board A C4 at U1.1 class D

- basis: ADI 2954fb (LTC2954) pin functions p.6: 'VIN: Power Supply Input: 2.7V to 26.4V'; the sheet states no capacitor, class D by role, the generator's own 1 uF (decision 42 D1)
- document named: `v2/vendor/power/ltc2954.pdf`
- passage NOT_FOUND: "VIN: Power Supply Input: 2.7V to 26.4V"; pieces not found: ['vin: power supply input: 2.7v to 26.4v']
- reading of the held text: The held v2/vendor/power/ltc2954.pdf reads "VIN (Pin 1/Pin 4): Power Supply Input: 2.7V to 26.4V." The basis drops "(Pin 1/Pin 4)" inside its quotation marks with no ellipsis. The substance is the maker's; the quotation is not verbatim. Next action: board A's writer quotes it whole (gen_sch_a.py, on the set 9 line).

### board B C71 at U10.4 class D

- basis: TI TMP117 SNOSD82D (v2/vendor/ti/ti-tmp117-temperature.pdf) Power Supply Recommendations: "The recommended value for this supply bypass capacitor is 100 nF" (p.35)
- document named: `v2/vendor/ti/ti-tmp117-temperature.pdf`
- passage NOT_FOUND: "The recommended value for this supply bypass capacitor is 100 nF"; pieces not found: ['the recommended value for this supply bypass capacitor is 100nf']
- reading of the held text: The held v2/vendor/ti/ti-tmp117-temperature.pdf (SNOSD82D) reads "A recommended value for this supply bypass capacitor is 100 nF" (Power Supply Recommendations). The basis writes "The" where the maker writes "A". The value and the clause are the maker's. Next action: board B's writer corrects the article in gen_sch_b.py.

### board E C58 at U17.5 class D

- basis: Sensirion SGP41 version 1.0: 2.5 "The required decoupling for VDDH depends on the power supply network ... a capacitor of 1 uF is recommended" (p.7)
- document named: `v2/vendor/sensirion/sgp41-datasheet.pdf`
- passage NOT_FOUND: "The required decoupling for VDDH depends on the power supply network ... a capacitor of 1 uF is recommended"; pieces not found: ['a capacitor of 1uf is recommended']
- reading of the held text: The held v2/vendor/sensirion/sgp41-datasheet.pdf, section 2.5, reads in its text layer "... a capacitor of 1 F is recommended": the micro sign is not in the text layer, so the words cannot be matched as written. The first piece of the quotation is found. This is the document's text layer, not a misquote; no action.

## Every PAGE row (found, on another page than stated)

| declaration(s) | stated | found (document, PDF page) | passage |
|---|---|---|---|
| board B C174 at L104.2 class B1; board B C274 at L204.2 class B1; board B C374 at L304.2 class B1 | [37] | ti-tusb8041.pdf p.[38] | the large bulk capacitors associated with each power rail should be placed as close as pos |
| board B C520 at J_M2C2.2 class D; board B C521 at J_M2C2.70 class D; board B C522 at J_M2C2.2 class D; board B C523 at J_M2C2.2 class D; board B C524 at J_M2C2. | [29] | quectel-rm520n-series-hardware-design-v1.1.pdf p.[30] | two bypass capacitors of 220 uF with low ESR should be used, and a multi-layer ceramic chi |
| board B C72 at U11.22 class D; board B C73 at U11.22 class D; board B C74 at U11.22 class D | [25] | lg290p03-hardware-design-v1.1.pdf p.[26] | It is recommended to place a TVS and a combination of a 4.7 uF, a 100 nF and a 33 pF decou |
| board B C37 at U3.1 class D; board B C38 at U4.1 class D | [18] | ti-ts3dv642.pdf p.[23] | Decoupling capacitors should be used between power supply pin and ground pin |
| board C C7 at U3.1 class D; board C C8 at U3.10 class D; board C C9 at U3.22 class D; board C C10 at U3.33 class D; board C C11 at U3.42 class D; board C C12 at | [151] | rpi-rp2040-datasheet.pdf p.[152] | IOVDD should be decoupled with a 100nF capacitor close to each of the chip's IOVDD pins |
| board C C14 at U3.45 class L | [156] | rpi-rp2040-datasheet.pdf p.[157] | The regulator must have 1uF capacitors placed close to its input (VREG_VIN) and output (VR |
| board C C15 at U3.50 class D; board C C44 at U3.23 class D | [151] | rpi-rp2040-datasheet.pdf p.[152] | DVDD should be decoupled with a 100nF capacitor close to each of the chip's DVDD pins |
| board C C16 at U3.44 class D | [151] | rpi-rp2040-datasheet.pdf p.[152] | A 1uF capacitor should be connected between VREG_VIN and ground close to the chip's VREG_V |
| board C C42 at U3.43 class D | [152] | rpi-rp2040-datasheet.pdf p.[153] | ADC_AVDD should be decoupled with a 100nF capacitor close to the chip's ADC_AVDD pin |
| board C C43 at U3.48 class D | [151] | rpi-rp2040-datasheet.pdf p.[152] | USB_VDD should be decoupled with a 100nF capacitor close to the chip's USB_VDD pin |
| board E C38 at U10.1 class D; board E C39 at U10.10 class D; board E C40 at U10.22 class D; board E C41 at U10.33 class D; board E C42 at U10.42 class D; board  | [151] | rpi-rp2040-datasheet.pdf p.[152] | IOVDD should be decoupled with a 100nF capacitor close to each of the chip's IOVDD pins |
| board E C45 at U10.45 class L | [156] | rpi-rp2040-datasheet.pdf p.[157] | The regulator must have 1uF capacitors placed close to its input (VREG_VIN) and output (VR |
| board E C46 at U10.50 class D | [151] | rpi-rp2040-datasheet.pdf p.[152] | DVDD should be decoupled with a 100nF capacitor close to each of the chip's DVDD pins |
| board E C47 at U10.44 class D | [151] | rpi-rp2040-datasheet.pdf p.[152] | A 1uF capacitor should be connected between VREG_VIN and ground close to the chip's VREG_V |
| board E C60 at U10.43 class D | [152] | rpi-rp2040-datasheet.pdf p.[153] | ADC_AVDD should be decoupled with a 100nF capacitor close to the chip's ADC_AVDD pin |
| board E C61 at U10.48 class D | [151] | rpi-rp2040-datasheet.pdf p.[152] | USB_VDD should be decoupled with a 100nF capacitor close to the chip's USB_VDD pin |

Every PAGE row but one is a one-page offset between the page the basis states and the PDF's own page (the RP2040 datasheet on boards C and E, the TUSB8041, RM520N and LG290P documents on board B). The one that is not, read with `pdftotext -f <page> -l <page>`: board B's C37 and C38 at the TS3DV642. The quoted "Decoupling capacitors should be used between power supply pin and ground ..." is on PDF page 23 (layout guidelines); page 18 carries a different sentence, "Decoupling capacitors may be used to reduce noise and improve power supply integrity". DECOUPLING.md G5 cites SCDS343F pp.18 and 23, so the record names both pages and the basis states only the first. It changes no value and no class; it is board B's writer's basis text to correct.

