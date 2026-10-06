# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path

src = Path(r"D:\Edge\zixuann.top.png")
out = Path(r"E:\AI\MIMO\Blog\assets\domain-cert.png")
im = Image.open(src).convert("RGB")
w, h = im.size

def runs_in(y0, y1, x0=200, x1=1180, thr=100, merge_gap=12):
    gray = im.convert("L")
    cols = []
    for x in range(x0, x1):
        has = any(gray.getpixel((x, y)) < thr for y in range(y0, y1))
        cols.append((x, has))
    runs, start = [], None
    for x, has in cols:
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
            merged.append((r[0], r[1]))
    return merged

# locate name fields
print("body CN", runs_in(455, 515, 250, 900))
print("body EN L1", runs_in(520, 580, 250, 1180))
print("body EN L2", runs_in(560, 620, 50, 400))
print("holder", runs_in(710, 760, 250, 900))
print("registrant", runs_in(765, 815, 250, 900))
