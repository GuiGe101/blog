# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path

src = Path(r"D:\Edge\zixuann.top.png")
out = Path(r"E:\AI\MIMO\Blog\assets\domain-cert.png")
im = Image.open(src).convert("RGB")

# from dark-run scan
boxes = [
    (548, 470, 675, 515),   # 舒梓轩 Chinese body
    (1018, 518, 1095, 565),  # 舒梓 English L1
    (78, 550, 128, 600),     # 轩 English L2
    (418, 700, 510, 750),    # 舒梓轩 holder line (y700-740)
    (418, 740, 575, 790),    # shu zi xuan registrant (y740-780)
]

for i, box in enumerate(boxes):
    region = im.crop(box).filter(ImageFilter.GaussianBlur(radius=16))
    im.paste(region, box)
    ImageDraw.Draw(im).rectangle(box, fill=(25, 25, 25))
    print("masked", i, box)

im.save(out, "PNG")

# pixel verification: sample mask centers — should be near-black
px = im.load()
for i, box in enumerate(boxes):
    cx, cy = (box[0] + box[2]) // 2, (box[1] + box[3]) // 2
    print("sample", i, "center", px[cx, cy])

# save a fresh check strip of the name areas only
strip = im.crop((100, 450, 1100, 800))
strip.save(out.parent / "_check_names.png")
print("saved", out, out.stat().st_size)
