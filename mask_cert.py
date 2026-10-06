# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path

src = Path(r"D:\Edge\zixuann.top.png")
out = Path(r"E:\AI\MIMO\Blog\assets\domain-cert.png")
orig = Image.open(src).convert("RGB")

# dump several candidate strips from ORIGINAL so we can see exact layout
strips = {
    "body_cn": (250, 455, 750, 525),
    "holder": (250, 695, 700, 755),
    "registrant": (250, 735, 750, 795),
}
strip_dir = Path(r"E:\AI\MIMO\Blog\assets\strips")
strip_dir.mkdir(exist_ok=True)
for name, box in strips.items():
    orig.crop(box).save(strip_dir / f"orig_{name}.png")
    print("saved", name, box)

# Also print dark-run boundaries with fine merge on body_cn line
gray = orig.convert("L")

def fine_runs(y0, y1, x0, x1, thr=110, merge_gap=6):
    runs, start = [], None
    for x in range(x0, x1):
        has = any(gray.getpixel((x, y)) < thr for y in range(y0, y1))
        if has and start is None:
            start = x
        elif not has and start is not None:
            runs.append((start, x - 1))
            start = None
    if start is not None:
        runs.append((start, x1 - 1))
    merged = []
    for r in runs:
        if merged and r[0] - merged[-1][1] <= merge_gap:
            merged[-1] = (merged[-1][0], r[1])
        else:
            merged.append(r)
    return merged

print("body_cn fine", fine_runs(465, 515, 250, 750, merge_gap=6))
print("holder fine", fine_runs(705, 745, 250, 700, merge_gap=6))
print("registrant fine", fine_runs(745, 785, 250, 750, merge_gap=6))
