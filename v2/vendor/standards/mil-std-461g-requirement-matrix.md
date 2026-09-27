# MIL-STD-461G, Table V (Requirement matrix): which tests apply to ground equipment

**What this file is.** A transcription of the one table this project CITES, not a copy of the standard. The
requirements registry's REQ-063 (the MIL-STD-461 characterisation runs TEST-PLAN M1 to M5) names the edition and the
installation row under a choice the session took on 27 September 2026 under the owner's standing rule of 26 September
2026: MIL-STD-461G, with the limits it gives for the "Ground, Army" installation of this table for each test M1 to M5
runs. Every run is characterisation (owner ruling D-04: no EMC claim for the prototype). Filed 27 September 2026
(MESHSAT-1357, layer 3 closer). The standard is a United States Department of Defense document; this folder transcribes
standards rather than copying them.

| | |
|---|---|
| document | MIL-STD-461G, Requirements for the Control of Electromagnetic Interference Characteristics of Subsystems and Equipment, 11 December 2015, superseding MIL-STD-461F of 10 December 2007 (280 pages in the file read) |
| source | the copy served by NASA's System Safety and Reliability knowledge base, `https://s3vi.ndc.nasa.gov/ssri-kb/static/resources/MIL-STD-461G.pdf` (its page footers read "Downloaded from http://www.everyspec.com") |
| fetched | 27 September 2026, curl from the runner, 3,456,938 bytes |
| sha256 of the file read | `491f015e386136b58af90e86066533ca073d31210913a766cb236cf05a876bb8` |
| clause transcribed | Table V, Requirement matrix (printed page 26, the PDF's page 40): the three ground rows, read by the column positions of the file's text layer |
| not checked | whether a later edition supersedes MIL-STD-461G; none is held in this tree |

## Table V, Requirement matrix (page 26), the ground rows

Legend, as printed: "A: Applicable. L: Limited as specified in the individual sections of this standard. S: Procuring
activity must specify in procurement documentation." A blank cell is a requirement that does not apply.

| Installation | CE101 | CE102 | CE106 | CS101 | CS103 | CS104 | CS105 | CS109 | CS114 | CS115 | CS116 | CS117 | CS118 | RE101 | RE102 | RE103 | RS101 | RS103 | RS105 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Ground, Army | | A | L | A | S | S | S | | A | A | A | S | A | | A | L | L | A | |
| Ground, Navy | | A | L | A | S | S | S | | A | A | A | S | A | | A | L | L | A | L |
| Ground, Air Force | | A | L | A | S | S | S | | A | A | A | | A | | A | L | | A | |

The rows for surface ships, submarines, aircraft and space systems are not transcribed.

## How this project uses it

- TEST-PLAN M1 to M5 run CE102, CS101, CS114, RE102 and RS103; each is "A" in the Ground, Army row, so each is read
  against the limit its own section of MIL-STD-461G gives for Army ground installations. Those limit figures are read
  from each test's section when the pre-compliance session of owner ruling D-09 is booked; they are not transcribed here.
- The row is chosen as the nearest class to a field kit carried in vehicles; D-16 records that the kit makes no vehicle
  surge claim, and D-04 that it makes no EMC claim.
