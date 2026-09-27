# Prepared maker questions (stream PWR, 26 September 2026): TEXT ONLY, NOTHING SENT

Prepared under the rule that the session never contacts outside parties. The owner or the ordering session sends them
if and when it chooses. Each closes a row that `v2/docs/feasibility/POWER-THERMAL.md` carries as T or R. No figure
from the kit, the design or the project is disclosed beyond the part numbers and the product being a prototype.

## 1. AsiaRF (sales@asiarf.com), AW7915-AED

Subject: AW7915-AED power figures and operating temperature

Hello,

We are designing a prototype that uses the AW7915-AED (M.2 A/E-key, MT7915DAN) as a mesh-point link on a PCIe Gen 2
x1 lane, with Linux and the mainline mt76 driver. Could you help with four figures that the datasheet and the product
page do not give?

1. Power consumption with the interface up and associated but idle (beacons only, no traffic), at 3.3 V.
2. Power consumption with W_DISABLE1# asserted (held low), and whether the card acts on that pin with the mt76
   driver at all: does it disable both the 2.4 GHz and the 5 GHz radios?
3. The conditions behind "average is 4 - 8 W" (traffic type, band, transmit power) and behind "maximum 9 W".
4. The operating temperature: the product page says -10 to +70 C, and the 2023 datasheet v1.0 says 0 to +70 C.
   Which applies to cards shipped today, and is a wider-temperature grade available?

Thank you.

## 2. Xenarc Technologies, 709GNK

Subject: 709GNK typical power consumption

Hello,

The 709GNK specification gives "Power Consumption: <= 10W". Could you tell us the typical input power at 12 V and at
14.4 V with an HDMI signal present, at full backlight, at about half backlight and at the lowest dimmer setting? Is
the touch controller's USB power included in that figure?

Thank you.

## 3. Lime Microsystems, LimeSDR Mini v2.4

Subject: LimeSDR Mini v2.4 receive-only power

Hello,

The v2.4 documentation gives a maximum of 4.5 W (the USB 3.0 limit) and says consumption depends on configuration.
Could you share a typical figure for receive only (one channel, about 2 MS/s and about 10 MS/s) and for the FPGA idle
with the transceiver powered down? Is there an industrial or extended-temperature build, since the documented range
is 0 to +70 C for both operation and storage?

Thank you.
