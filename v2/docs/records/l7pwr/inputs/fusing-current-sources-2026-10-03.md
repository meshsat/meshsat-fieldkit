# The published fusing-current relations this record uses (Onderdonk, Preece), with their sources

Read 3 October 2026 by the Layer 7 author (stream l7pwr, MESHSAT-1357). Neither document is filed; both are public pages
cited by URL, and the relations are reproduced in `l7pwr_fans_th1.py`.

1. Douglas Brooks, "Onderdonk's and Preece's Equations: How Do They Compare?", Printed Circuit Design and Fab online,
   2 June 2023, `https://pcdandf.com/pcdesign/index.php/editorial/menu-features/17314-onderdonk-s-and-preece-s-equations-how-do-they-compare`.
   As the article prints them: Preece for copper I = 12277 x A^(3/4) with A in square inches; Onderdonk in its simplified
   form t = 0.0346 x ((dT x A) / I)^2 with t in seconds, dT the temperature rise, A in square mils and I in amperes. The
   article states Onderdonk's time estimates are "only accurate up to about 10 sec" because the relation assumes a wire
   suspended in air with no cooling (adiabatic heating); it cites no standard as the equation's publisher and notes that
   Onderdonk never published under his own name (the earliest reference is Stauffacher, 1928).
2. Jefferson Lab Hall A technical note, "Fusing Currents, Melting Temperature, Copper, Aluminum, Magnet Wire", R2 of
   16 January 2009, `https://hallaweb.jlab.org/tech/Detectors/public_html/hall_a/miscellaneous_info/Fusing_Currents_Melting_Temperature_Copper_Aluminum_Magnet_Wire_R2.011609.pdf`
   (583,184 bytes, sha256 b3064839ac0bc8c672dd85f7ff9aa334b058d10775c06c47dd2e3e9cc2245330). As it prints them: Preece
   i = A x D^1.5 with A a constant for the metal (10244 for copper) and D the wire diameter in inches; Onderdonk
   Ifuse = Area x SQRT(LOG((Tmelt - Tambient) / (234 + Tambient) + 1) / (Time x 33)) with Area in circular mils, Time in
   seconds, Tmelt the melting temperature (1083 C for copper), LOG the common logarithm; its worked example (2581 cmil,
   5 s, 25 C) gives 178 A.

Why two sources: the two forms are the same relation (the general form with the 234 and 33 constants, and Brooks's
simplification at copper's melting point); the record computes the general form and checks it against the simplified one
and against the note's worked example. The project's own standards transcription (`v2/vendor/standards/ecss-q-st-70-12c-2014-07-14.md`,
Annex D) carries the steady-state current-rating fits of IPC-2221A, IPC-2152 and CNES for board copper, not a fusing-time
relation; the dock lead is a wire, and its steady rating basis is ECSS-Q-ST-30-11C Rev.2 Annex C (this folder's transcription).
