# ECSS-Q-ST-30-11C Rev.2 (23 June 2021), clause 6.32 and Annex C: the wire rating this record reads

Transcribed 3 October 2026 by the Layer 7 author (stream l7pwr, MESHSAT-1357) from the free PDF at
`https://ecss.nl/wp-content/uploads/2022/07/ECSS-Q-ST-30-11C-Rev.2(23June2021).pdf` (988,694 bytes, sha256
10cf7066fad0314918c6a7d38517bbcf7cb00e206480fc10377e9fdb83e7db6e, the same file `v2/vendor/standards/ecss-q-st-30-11c-rev2-2021-06-23.md`
cites for clause 6.17), fetched from ecss.nl with curl, HTTP 200. The PDF itself is not filed (the project transcribes the
clauses it uses, never redistributes the standard). A SPACE standard: its values are a published, conservative basis for
the dock lead's continuous rating, reported as such, never a requirement this project claims the standard sets.

## 6.32.4 Single wire sizing (page 85)

> a. Parameters of Wires and cables from family-group code 13-01 to 13-03 shall be rated as follows:
> 1. Voltage: 50 %
> 2. The surface temperature of the wire remains 50 C lower than the manufacturer's maximum rating.
>
> b. The following formula may be used to rate the maximum current in a single wire (ISW), specified in requirement
> 6.32.4a in vacuum, for an environment temperature of Tenv, to reach a wire surface temperature of Twire, providing [five
> conditions: a negligible radial gradient, no axial transfer, an opaque dielectric, no external radiative source, no
> overshield or braid]

The formula is a radiative balance in vacuum (ISW from the Stefan-Boltzmann constant, Twire, Tenv, the wire's diameter and
its resistance RTref corrected by Ct); its worked values are Annex C's.

## Annex C (informative): example of single wires rating currents (pages 101 and 102)

- C.2 typical conservative parameters: emissivity of the wire surface E = 0.75; Ct = 0.00396 per K for copper, Tref 293.15 K.
- Table C-1, parameters for copper and copper alloy wires, the AWG 24 column: resistance at 20 C **105 mOhm/m**, minimum
  diameter **0.8 mm** (the minimum diameter is taken "because it represents the worst case as it minimizes the radiative
  surface of the wire").
- C.3: "The values in Table C-3, Table C-4 were calculated using the above formula and list of parameters, for an
  environment temperature of 70 C. Copper wires: Maximum wire temperature: 150 C".
- Table C-3, single wire rated current for a copper conductor, the AWG 24 column: **ISW 3.4 A** (AWG 28 1.9, 26 2.7, 22 5.6,
  20 7.7, 18 10.6, 16 14, 14 18.1, 12 26.7 A).

What this record takes from it: 3.4 A is the standard's example rating of a single AWG 24 copper wire in vacuum (radiation
alone) at a 70 C environment reaching 150 C; in the kit's sealed air the wire also convects, so the figure is the
conservative side. The 50 K rule of 6.32.4a is applied against the maker's maximum rating of the harness wire actually
fitted, which ASSEMBLY.md does not yet name (the dock's twelve signal wires are "24 AWG, 60 mm each"): that name is a Layer 7
harness item of this record.
