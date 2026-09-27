# A07: two computed consequences, with every assumption named (standard AWG tables at 20 C; contact resistances TBD)
AWG26 = 0.1339   # ohm/m, annealed copper, 20 C
AWG12 = 0.00521  # ohm/m
L = 0.350        # m, ASSEMBLY.md:53 and :60
R10 = 0.002      # board P shunt, gen_sch_p.py:152
main = R10 + AWG12 * L                   # P GND -> R10 -> PACK_N -> W_N 12 AWG -> XT60 -> E GND (XT60 contact omitted: TBD)
for rc in (0.0, 0.010, 0.020):           # total XH contact resistance in the SMBus GND wire, TBD (JST catalogue not read)
    byp = AWG26 * L + rc
    f = main / (main + byp)
    print("contacts %.0f mohm: main %.2f mohm, bypass %.1f mohm, share around the shunt %.1f %%, at 18 A %.2f A in the 26 AWG GND wire"
          % (rc * 1e3, main * 1e3, byp * 1e3, 100 * f, 18 * f))
# D2 USBLC6-2SC6: VBUS pin on VCC_F, fed from PACK_P through R7 1k (gen_sch_p.py:116, :171); VBR min 6 V at 1 mA (DS4260 Rev 7 Table 2)
for vpack in (12.0, 14.4, 16.8):
    for vcl in (6.0, 7.0):
        i = (vpack - vcl) / 1000.0
        print("PACK_P %.1f V, clamp %.1f V: %.1f mA, R7 %.0f mW (0603), D2 %.0f mW, drain %.0f mW" % (vpack, vcl, i * 1e3, i * i * 1000 * 1e3, i * vcl * 1e3, i * vpack * 1e3))
