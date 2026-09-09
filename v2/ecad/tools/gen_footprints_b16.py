#!/usr/bin/env python3
"""B16 footprints into meshsat.pretty (MESHSAT-830, appendix 32.58). Usage: gen_footprints_b16.py <meshsat.pretty dir>

- M2_M-Key_Socket_2242 and M2_B-Key_Socket_3052: the M.2 socket land pattern of the B14 E-key socket (75 positions at 0.5 mm, two rows 7.55 mm apart,
  0.3 x 1.55 pads, two anchor pads) with the key notch of the M.2 specification (M: positions 59 to 66 absent, B: 12 to 19 absent) and the plated
  M2.5 standoff hole at the card length minus 1.75 mm (2242: 40.25, 3052: 50.25).
- Quectel_LG290P: 12.2 x 16.0 LGA, 24 edge pads 1.5 x 0.8 (left column pins 1 to 12 top to bottom, right column 24 to 13; rows 1.0 + 1.1 k for k 0..6 and
  10.6 + 1.1 k for k 0..4 from the top edge) and the 5 x 11 ground matrix of 1.0 mm pads at 1.4 mm (pins 25 to 79), from the hardware design figure 18
  (recommended footprint) and Table 6 (pins 10, 12, 13, 24 to 79 are GND; 1, 2, 5, 17 reserved).
- Ebyte_E22-900M30S: 24.0 x 38.5 stamp-hole module, 22 half-hole pads at 2.54 mm (left column 12..19 then 20..22, right column 11..4 then 3..1 top to
  bottom; rows 2.61 + 2.54 k and 27.99 + 2.54 j from the top edge, manual section 3.3); host pads 3.2 x 1.4 reaching 1.2 mm under the module edge.
- Pulse_H5007NL: 24-pin 1000BASE-T magnetics, 17.53 x 12.20 body, 1.27 mm pitch, land pattern 0.76 x 1.9 on 12.70 / 16.51 (HC500 sheet page 1).
- LQFP-128_14x14mm_P0.4mm_EP6.0 (PI7C9X2G404SL, exposed pad drawn conservatively at 6.0 mm) and TQFP-128_14x14mm_P0.4mm_EP10.0 (KSZ9897R, the 10 x 10
  exposed pad of the Microchip TQFP-EP drawing): the KiCad library footprint with pad 129 added at the centre.
- Texas_RKS0020A_VQFN-20_2.5x4.5mm (TMUXHS4212) and Texas_RSE0010A_UQFN-10_1.5x2mm (TS3USB221A): TI land patterns 4222490/B and 4220307/A.
Every footprint ends in the self-test (pcbnew loads it and counts the pads; a file that pcbnew refuses stops the chain: the C6 run 1 lesson)."""
import os, sys
OUTDIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "meshsat.pretty")
os.makedirs(OUTDIR, exist_ok=True)
KLIB = "/usr/share/kicad/footprints/"
WRITTEN = {}

def head(name, descr, tags, ref_y, val_y):
    return ('(footprint "%s"\n\t(version 20240108)\n\t(generator "meshsat")\n\t(generator_version "9.0")\n\t(layer "F.Cu")\n\t(descr "%s")\n\t(tags "%s")\n'
            '\t(property "Reference" "REF**" (at 0 %.2f 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))\n'
            '\t(property "Value" "%s" (at 0 %.2f 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))\n'
            '\t(property "Footprint" "" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1.27 1.27))))\n'
            '\t(property "Datasheet" "" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1.27 1.27))))\n'
            '\t(property "Description" "" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1.27 1.27))))\n'
            '\t(attr smd)\n' % (name, descr, tags, ref_y, name, val_y))
def smd(num, x, y, w, h, shape="rect"): return '\t(pad "%s" smd %s (at %.3f %.3f) (size %.2f %.2f) (layers "F.Cu" "F.Paste" "F.Mask"))\n' % (num, shape, x, y, w, h)
def pth(num, x, y, size, drill): return '\t(pad "%s" thru_hole circle (at %.3f %.3f) (size %.2f %.2f) (drill %.2f) (layers "*.Cu" "*.Mask"))\n' % (num, x, y, size, size, drill)
def npth(x, y, drill): return '\t(pad "" np_thru_hole circle (at %.3f %.3f) (size %.2f %.2f) (drill %.2f) (layers "*.Cu" "*.Mask"))\n' % (x, y, drill, drill, drill)
def rect(x0, y0, x1, y1, layer, w=0.1): return '\t(fp_rect (start %.3f %.3f) (end %.3f %.3f) (stroke (width %.2f) (type solid)) (fill no) (layer "%s"))\n' % (x0, y0, x1, y1, w, layer)
def line(x0, y0, x1, y1, layer, w=0.12): return '\t(fp_line (start %.3f %.3f) (end %.3f %.3f) (stroke (width %.2f) (type solid)) (layer "%s"))\n' % (x0, y0, x1, y1, w, layer)
def circ(x, y, r, layer, w=0.12): return '\t(fp_circle (center %.3f %.3f) (end %.3f %.3f) (stroke (width %.2f) (type solid)) (fill no) (layer "%s"))\n' % (x, y, x + r, y, w, layer)
def write(name, body, expected_pads):
    if "%." in body: raise SystemExit("footprint %s carries an unfilled placeholder" % name)
    open(os.path.join(OUTDIR, name + ".kicad_mod"), "w").write(body + ")\n"); WRITTEN[name] = expected_pads

# ---------------------------------------------------------------- M.2 sockets (positions 1..75 at 0.5 mm; odd row y -5.275, even row y 2.275, as the B14 E-key file)
def m2_socket(key, notch, card_w, card_len):
    name = "M2_%s-Key_Socket_%d" % (key, card_len if card_len >= 1000 else card_len)
    name = "M2_%s-Key_Socket_%02d%02d" % (key, card_w, card_len)
    body = head(name, "M.2 %s-key socket (positions 1-75 without %d-%d), %d%02d card, component side up; land pattern of the B14 E-key socket (M.2 specification), plated M2.5 standoff at %.2f" % (key, notch[0], notch[1], card_w, card_len, card_len - 1.75),
                "M.2 NGFF %s key socket %d%02d" % (key, card_w, card_len), -8.5, card_len + 1.5)
    n = 0
    for pos in range(1, 76):
        if notch[0] <= pos <= notch[1]: continue
        if pos % 2: body += smd(pos, -9.25 + 0.25 * (pos - 1), -5.275, 0.3, 1.55)
        else: body += smd(pos, -9.0 + 0.25 * (pos - 2), 2.275, 0.3, 1.55)
        n += 1
    body += smd("S1", -10.35, -4.5, 1.2, 2.75) + smd("S2", 10.35, -4.5, 1.2, 2.75); n += 2
    body += pth("M1", 0.0, card_len - 1.75, 5.0, 2.7); n += 1
    body += rect(-11.0, -6.6, 11.0, 3.4, "F.Fab") + rect(-11.5, -7.1, 11.5, 3.9, "F.CrtYd", 0.05) + rect(-card_w / 2, 3.4, card_w / 2, card_len, "F.Fab")
    body += line(-11.0, -6.6, 11.0, -6.6, "F.SilkS") + line(-11.0, -6.6, -11.0, 3.4, "F.SilkS") + line(11.0, -6.6, 11.0, 3.4, "F.SilkS")
    body += line(-card_w / 2, card_len, card_w / 2, card_len, "Dwgs.User", 0.1) + line(-card_w / 2, 3.4, -card_w / 2, card_len, "Dwgs.User", 0.1) + line(card_w / 2, 3.4, card_w / 2, card_len, "Dwgs.User", 0.1)
    body += circ(-10.0, -7.6, 0.3, "F.SilkS")   # pin 1 side
    write(name, body, n); return name
m2_socket("M", (59, 66), 22, 42)
m2_socket("B", (12, 19), 30, 52)

# ---------------------------------------------------------------- Quectel LG290P (top view, module centred, KiCad y down; pin 1 top left)
def lg290p():
    name = "Quectel_LG290P"
    body = head(name, "Quectel LG290P GNSS module 12.2 x 16.0 LGA: 24 edge pads 1.5 x 0.8 at 1.1 mm (7 + 5 per side), 55 ground pads 1.0 mm at 1.4 mm (pins 25-79); hardware design figure 18", "GNSS LGA Quectel LG290P", -9.5, 9.5)
    rows = [1.0 + 1.1 * k for k in range(7)] + [10.6 + 1.1 * k for k in range(5)]
    n = 0
    for k, t in enumerate(rows):
        body += smd(k + 1, -5.05, t - 8.0, 1.5, 0.8); body += smd(24 - k, 5.05, t - 8.0, 1.5, 0.8); n += 2
    for r in range(11):
        for c in range(5): body += smd(25 + r * 5 + c, -2.8 + 1.4 * c, 1.0 + 1.4 * r - 8.0, 1.0, 1.0); n += 1
    body += rect(-6.1, -8.0, 6.1, 8.0, "F.Fab") + rect(-6.6, -8.5, 6.6, 8.5, "F.CrtYd", 0.05)
    body += line(-6.1, -8.0, 6.1, -8.0, "F.SilkS") + line(-6.1, 8.0, 6.1, 8.0, "F.SilkS") + line(-6.1, -8.0, -6.1, 8.0, "F.SilkS") + line(6.1, -8.0, 6.1, 8.0, "F.SilkS")
    body += circ(-7.0, -7.4, 0.3, "F.SilkS")
    write(name, body, n)
lg290p()

# ---------------------------------------------------------------- Ebyte E22-900M30S (top view, module centred; host pads reach 1.2 mm under the module edge and 2.0 mm outside it)
def e22():
    name = "Ebyte_E22-900M30S"
    body = head(name, "Ebyte E22-900M30S 1 W LoRa module 24.0 x 38.5 x 3.87, 22 stamp-hole pads at 2.54 mm (manual section 3.3); host pads 3.2 x 1.4; IPEX at the bottom left", "LoRa SX1262 Ebyte E22 stamp hole", -21.0, 21.0)
    n = 0
    tops = [2.61 + 2.54 * k for k in range(8)]; bots = [27.99 + 2.54 * j for j in range(3)]
    for k, t in enumerate(tops):
        body += smd(12 + k, -12.4, t - 19.25, 3.2, 1.4); body += smd(11 - k, 12.4, t - 19.25, 3.2, 1.4); n += 2
    for j, t in enumerate(bots):
        body += smd(20 + j, -12.4, t - 19.25, 3.2, 1.4); body += smd(3 - j, 12.4, t - 19.25, 3.2, 1.4); n += 2
    body += rect(-12.0, -19.25, 12.0, 19.25, "F.Fab") + rect(-14.2, -19.75, 14.2, 19.75, "F.CrtYd", 0.05)
    body += line(-12.0, -19.25, 12.0, -19.25, "F.SilkS") + line(-12.0, 19.25, 12.0, 19.25, "F.SilkS")
    body += rect(-11.0, 14.0, -6.5, 18.5, "F.Fab") + circ(13.5, 18.0, 0.3, "F.SilkS")   # IPEX pocket; pin 1 (bottom right) mark
    write(name, body, n)
e22()

# ---------------------------------------------------------------- Pulse H5007NL (pin 1 bottom left; pins 1-12 along the bottom row, 13-24 along the top row right to left)
def h5007():
    name = "Pulse_H5007NL"
    body = head(name, "Pulse H5007NL 1000BASE-T magnetics module, 17.53 x 12.20 x 5.51, 24 gull-wing pins at 1.27 mm; land 0.76 x 1.9 on 12.70 / 16.51 (HC500 page 1)", "magnetics 1000BASE-T Pulse H5007NL", -10.0, 10.0)
    n = 0
    for k in range(12):
        body += smd(1 + k, -6.985 + 1.27 * k, 7.30, 0.76, 1.9); body += smd(24 - k, -6.985 + 1.27 * k, -7.30, 0.76, 1.9); n += 2
    body += rect(-8.765, -6.1, 8.765, 6.1, "F.Fab") + rect(-9.3, -8.8, 9.3, 8.8, "F.CrtYd", 0.05)
    body += line(-8.765, -6.1, 8.765, -6.1, "F.SilkS") + line(-8.765, 6.1, 8.765, 6.1, "F.SilkS") + circ(-8.2, 9.0, 0.3, "F.SilkS")
    write(name, body, n)
h5007()

# ---------------------------------------------------------------- NiceRF SA868 (top view, module centred, KiCad y down): 35.6 x 19.0, 18 castellations 1.8 wide (datasheet V1.3 section 8;
#     pin 1 top left, 1-7 along the top at 4.45 mm, 8-11 down the right side (2.66 from the top, 4.45, 4.45, 4.6), 12-18 along the bottom right to left)
def sa868():
    name = "NiceRF_SA868"
    body = head(name, "NiceRF SA868 VHF walkie-talkie module 35.6 x 19.0 x 3.2, 18 castellated pads 1.8 mm (V1.3 section 8); host pads 1.6 x 2.6 reaching 1.4 mm outside the edge", "SA868 VHF module NiceRF castellated", -11.5, 11.5)
    n = 0
    xs = [-13.35 + 4.45 * k for k in range(7)]
    for k, x in enumerate(xs): body += smd(1 + k, x, -9.5 - 0.1, 1.6, 2.6); n += 1                       # top row, pin 1 left
    for k, y in enumerate((-9.5 + 2.66, -9.5 + 2.66 + 4.45, -9.5 + 2.66 + 8.9, 9.5 - 2.54)): body += smd(8 + k, 17.8 + 0.1, y, 2.6, 1.6); n += 1   # right side
    for k, x in enumerate(reversed(xs)): body += smd(12 + k, x, 9.5 + 0.1, 1.6, 2.6); n += 1              # bottom row, pin 12 right
    body += rect(-17.8, -9.5, 17.8, 9.5, "F.Fab") + rect(-18.6, -11.2, 19.6, 11.2, "F.CrtYd", 0.05)
    body += line(-17.8, -9.5, -17.8, 9.5, "F.SilkS") + line(-17.8, 9.5, 17.8, 9.5, "F.SilkS") + circ(-15.5, -12.0, 0.3, "F.SilkS")
    write(name, body, n)
sa868()

# ---------------------------------------------------------------- 128-pin QFP with exposed pad: the KiCad footprint plus pad 129 at the centre (paste in four windows)
def qfp_ep(src, name, ep):
    path = os.path.join(KLIB, "Package_QFP.pretty", src + ".kicad_mod")
    if not os.path.exists(path): raise SystemExit("KiCad footprint missing: " + path)
    s = open(path).read().rstrip()
    assert s.endswith(")")
    s = s.replace('(footprint "%s"' % src, '(footprint "%s"' % name, 1).replace('"%s"' % src, '"%s"' % name)
    s = s[:-1]
    s += '\t(pad "129" smd rect (at 0 0) (size %.2f %.2f) (layers "F.Cu" "F.Mask"))\n' % (ep, ep)
    q = ep * 0.42
    for sx in (-1, 1):
        for sy in (-1, 1): s += '\t(pad "" smd rect (at %.3f %.3f) (size %.2f %.2f) (layers "F.Paste"))\n' % (sx * ep / 4, sy * ep / 4, q, q)
    open(os.path.join(OUTDIR, name + ".kicad_mod"), "w").write(s + ")\n"); WRITTEN[name] = 128 + 1 + 4
qfp_ep("LQFP-128_14x14mm_P0.4mm", "LQFP-128_14x14mm_P0.4mm_EP6.0", 6.0)
qfp_ep("TQFP-128_14x14mm_P0.4mm", "TQFP-128_14x14mm_P0.4mm_EP10.0", 10.0)

# ---------------------------------------------------------------- TI RKS0020A (TMUXHS4212) and RSE0010A (TS3USB221A), both drawn from the
#     manufacturer's own LAND PATTERN EXAMPLE, not from a library part of a similar size. The first draft of the I/O HA fabric named
#     Package_DFN_QFN:VQFN-20-1EP_2.5x4.5mm_P0.5mm_EP1.0x3.0mm, which does not exist, and UQFN-10_1.4x1.8mm_P0.4mm, which exists and is
#     the wrong package (the RSE body is 1.5 x 2.0 at 0.5 mm pitch). A footprint key is a claim about the part's package and nobody
#     checks it: both are generated here from the drawings so the claim is the drawing.
def rks0020a():
    # SLASEP7A drawing 4222490/B: body 2.5 x 4.5, 0.5 mm pitch, exposed thermal pad 1.0 x 3.0, land pattern 20X (0.6) x (0.24),
    # 16X (0.5), overall (2.3) x (4.3), three 0.2 mm vias in the pad at y 0 and +-1.25. Pin 1 top left, counter-clockwise seen
    # from the top: 1 and 20 on the top short side, 2 to 9 down the left, 10 and 11 on the bottom short side, 12 to 19 up the right.
    name = "Texas_RKS0020A_VQFN-20_2.5x4.5mm"
    body = head(name, "TI RKS0020A VQFN-20 2.5 x 4.5 mm, 0.5 mm pitch, exposed pad 1.0 x 3.0 (pad 21); land pattern of SLASEP7A drawing 4222490/B", "VQFN-20 RKS TMUXHS4212 Texas", -3.2, 3.2)
    n = 0
    body += smd(1, -0.25, -1.85, 0.24, 0.6) + smd(20, 0.25, -1.85, 0.24, 0.6); n += 2
    body += smd(10, -0.25, 1.85, 0.24, 0.6) + smd(11, 0.25, 1.85, 0.24, 0.6); n += 2
    for k in range(8):
        body += smd(2 + k, -0.85, -1.75 + 0.5 * k, 0.6, 0.24); n += 1
        body += smd(12 + k, 0.85, 1.75 - 0.5 * k, 0.6, 0.24); n += 1
    body += '\t(pad "21" smd rect (at 0 0) (size 1.00 3.00) (layers "F.Cu" "F.Mask"))\n'; n += 1
    for y in (-1.05, 0.0, 1.05):                      # paste in three windows, about 64 percent of the pad
        body += '\t(pad "" smd rect (at 0 %.3f) (size 0.80 0.80) (layers "F.Paste"))\n' % y; n += 1
    body += rect(-1.25, -2.25, 1.25, 2.25, "F.Fab") + rect(-1.55, -2.55, 1.55, 2.55, "F.CrtYd", 0.05)
    body += line(-1.25, -2.25, 1.25, -2.25, "F.SilkS") + line(-1.25, 2.25, 1.25, 2.25, "F.SilkS") + circ(-1.45, -2.45, 0.15, "F.SilkS")
    write(name, body, n)
rks0020a()

def rse0010a():
    # SCDS277C drawing 4220307/A: body 1.5 x 2.0, 0.5 mm pitch, no thermal pad. Land 8X (0.55) long on the sides with the four outer
    # pads (1, 4, 6, 9) 0.25 wide and the four inner ones (2, 3, 7, 8) 0.2 wide, pins 5 and 10 0.3 x 0.6 on the short sides, overall
    # (1.35) x (1.8). Pin 1 top left, 2 to 4 down the left, 5 bottom centre, 6 to 9 up the right, 10 top centre.
    name = "Texas_RSE0010A_UQFN-10_1.5x2mm"
    body = head(name, "TI RSE0010A UQFN-10 1.5 x 2.0 mm, 0.5 mm pitch, no thermal pad; land pattern of SCDS277C drawing 4220307/A", "UQFN-10 RSE TS3USB221A Texas", -1.9, 1.9)
    n = 0
    for k in range(4):
        w = 0.25 if k in (0, 3) else 0.2
        body += smd(1 + k, -0.4, -0.75 + 0.5 * k, 0.55, w); n += 1
        body += smd(6 + k, 0.4, 0.75 - 0.5 * k, 0.55, w); n += 1
    body += smd(5, 0.0, 0.6, 0.3, 0.6) + smd(10, 0.0, -0.6, 0.3, 0.6); n += 2
    body += rect(-0.75, -1.0, 0.75, 1.0, "F.Fab") + rect(-1.05, -1.3, 1.05, 1.3, "F.CrtYd", 0.05)
    body += line(-0.75, -1.0, 0.75, -1.0, "F.SilkS") + line(-0.75, 1.0, 0.75, 1.0, "F.SilkS") + circ(-0.95, -1.2, 0.12, "F.SilkS")
    write(name, body, n)
rse0010a()

# ---------------------------------------------------------------- self-test
try:
    import pcbnew
    for name, npads in WRITTEN.items():
        fp = pcbnew.FootprintLoad(OUTDIR, name)
        if fp is None: raise SystemExit("self-test: pcbnew refuses %s" % name)
        got = len(list(fp.Pads()))
        if got != npads: raise SystemExit("self-test: %s has %d pads, expected %d" % (name, got, npads))
    print("gen_footprints_b16: %d footprints written and loaded: %s" % (len(WRITTEN), ", ".join(sorted(WRITTEN))))
except ImportError:
    print("gen_footprints_b16: %d footprints written (no pcbnew here, self-test skipped): %s" % (len(WRITTEN), ", ".join(sorted(WRITTEN))))
