# -*- coding: utf-8 -*-
"""把 lxgw-wenkai-webfont 的分片 woff2 合并后按站点字符集 subset，产出自托管字体。"""
import io
import sys
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "fonts"
TGZ_URL = "https://registry.npmmirror.com/lxgw-wenkai-webfont/-/lxgw-wenkai-webfont-1.7.0.tgz"
CACHE = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / ".fontcache"


def charset() -> str:
    chars = set()
    for p in list((ROOT / "posts").glob("*.md")) + [ROOT / "about.md", ROOT / "projects.md", ROOT / "build.py"]:
        if p.exists():
            chars.update(p.read_text(encoding="utf-8"))
    for hi in range(0xB0, 0xD8):
        for lo in range(0xA1, 0xFF):
            try:
                chars.add(bytes([hi, lo]).decode("gb2312"))
            except UnicodeDecodeError:
                pass
    chars.update(chr(c) for c in range(0x20, 0x7F))
    chars.update("·—–…‘’“”「」『』《》〈〉〔〕％＋－／＝×÷℃≈≤≥←→↑↓§¶†‡•№")
    return "".join(sorted(chars))


def main() -> None:
    from fontTools import subset
    from fontTools.merge import Merger
    from fontTools.ttLib import TTFont

    CACHE.mkdir(parents=True, exist_ok=True)
    tgz = CACHE / "webfont.tgz"
    if not tgz.exists():
        print("downloading", TGZ_URL, flush=True)
        urllib.request.urlretrieve(TGZ_URL, tgz)
    print("extracting", flush=True)
    with tarfile.open(tgz) as tf:
        tf.extractall(CACHE / "pkg", filter="data")
    pkg = CACHE / "pkg" / "package"

    text = charset()
    (CACHE / "charset.txt").write_text(text, encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)

    for weight in ("regular", "bold"):
        parts = sorted(pkg.glob(f"files/lxgwwenkai-{weight}-subset-*.woff2"))
        print(weight, "parts:", len(parts), flush=True)
        merger = Merger()
        merged = merger.merge([str(p) for p in parts])
        opts = subset.Options()
        opts.flavor = "woff2"
        opts.layout_features = ["kern", "liga", "locl", "ccmp", "vert", "vrt2"]
        opts.name_IDs = ["*"]
        opts.notdef_outline = True
        sub = subset.Subsetter(options=opts)
        sub.populate(text=text)
        sub.subset(merged)
        dest = OUT / f"lxgw-wenkai-{weight}.woff2"
        merged.flavor = "woff2"
        merged.save(dest)
        print("wrote", dest, dest.stat().st_size, flush=True)

    (OUT / "fonts.css").write_text(
        """/* 自托管霞鹜文楷（GB2312 一级 + 站点字符子集） */
@font-face {
  font-family: "LXGW WenKai";
  src: url("lxgw-wenkai-regular.woff2") format("woff2");
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: "LXGW WenKai";
  src: url("lxgw-wenkai-bold.woff2") format("woff2");
  font-weight: 700;
  font-style: normal;
  font-display: swap;
}
""",
        encoding="utf-8",
    )
    print("done", flush=True)


if __name__ == "__main__":
    main()