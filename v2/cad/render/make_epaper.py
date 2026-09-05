#!/usr/bin/env python3
# The e-paper content of the concept renders: the QR code of https://meshsat.net (PANEL.md: the QR page is shown while TEST is held after a UI request)
# with the status lines of the mock. WeAct 3.7 is 416 x 240 pixels; the texture is drawn at 3x. Needs: pip install qrcode pillow
import qrcode
from PIL import Image, ImageDraw, ImageFont
q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2); q.add_data("https://meshsat.net"); q.make(fit=True)
qr = q.make_image(fill_color="black", back_color="white").convert("L")
W, H = 1248, 720
im = Image.new("L", (W, H), 245); d = ImageDraw.Draw(im)
def font(sz):
    for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        try: return ImageFont.truetype(f, sz)
        except Exception: pass
    return ImageFont.load_default()
side = H - 80; qr = qr.resize((side, side), Image.NEAREST); im.paste(qr, (40, 40))
x0 = side + 100
d.text((x0, 56), "MESHSAT", font=font(74), fill=0); d.text((x0, 150), "tesseract  node 2/3", font=font(38), fill=0)
d.line((x0, 215, W - 40, 215), fill=0, width=4)
for i, (k, v) in enumerate((("MESH", "7 peers   ch 3"), ("SAT", "RockBLOCK OK"), ("LTE", "4G  -87 dBm"), ("GPS", "11 sv  fix 3D"), ("BAT", "78 %  shore"))):
    d.text((x0, 240 + i * 70), "%-5s %s" % (k, v), font=font(40), fill=0)
d.text((x0, H - 96), "https://meshsat.net", font=font(38), fill=0)
im.convert("RGB").save("epaper.png"); print("epaper.png", im.size)
