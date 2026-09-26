# Draft request to Diodes Incorporated: PI7C9X2G404SL power decoupling (NOT SENT)

Prepared 26 September 2026 by the session for MESHSAT-1357 (wording of the board checked 16:42 CEST: "non-commercial prototype" is the owner's ruling D-04 of 26 September,
`v2/docs/CONOPS.md:395` and `v2/docs/PRODUCT-BRIEF.md:23`; the licence is `README.md:71`), decision 42 (`v2/docs/feasibility/DECOUPLING.md`, section
10). This stream does not contact outside parties. The session that handles outside contact sends it, through
Diodes' technical support form or a distributor FAE, and files the reply under `v2/vendor/diodes/` with its date,
revision and sha256.

---

Subject: PI7C9X2G404SL (LQFP-128 EP): recommended power-pin decoupling and reference schematic

Hello,

We are designing a non-commercial, open-hardware prototype carrier board (CERN Open Hardware Licence Version 2,
Strongly Reciprocal) that uses the PI7C9X2G404SL PCIe 2.0 packet switch in
the 128-pin LQFP with exposed pad (JLCPCB part C500767), one per compute slot, three on the board. The data sheet we
hold, DS40068 Rev 5-2, lists the power pins in section 3.5 (VDDC, VDDCAUX and AVDD at 1.0 V; VDDR, CVDDR, VAUX and
AVDDH at 3.3 V) but gives no recommendation for their decoupling.

Could you share, or point us to, any of the following for this part:

1. the recommended decoupling per supply pin or pin group (values, count, dielectric), including bulk per rail;
2. any placement guidance (same side as the device or the opposite side, via arrangement, filtering such as ferrite
   beads on AVDD, AVDDH or CVDDR);
3. the evaluation board's schematic and layout, or a hardware design guide, if they are available to customers.

Our present design places six 100 nF capacitors and one 10 uF on the 3.3 V pins and the same on the 1.0 V pins,
for 26 supply pads, which we want to check against your recommendation before the board is built.

Thank you,
[name of the sender, filled in by the session that sends it]
