# -*- coding: utf-8 -*-
from pathlib import Path
import re

p = Path(r"E:\AI\MIMO\Blog\posts\2026-10-18-recap-clean.md")
t = p.read_text(encoding="utf-8")
t = t.replace(
    "1. **构建脚本里的站点标题**（`SITE_TITLE`）—— 头图大标题、浏览器标签、分享卡片都吃这个",
    "1. **构建脚本里的站点标题**（`SITE_TITLE`）。头图大标题、浏览器标签、分享卡片都吃这个",
)
t = t.replace(
    "4. 文章页、关于页的头像 —— 路径前缀不同（`../assets`），别 404",
    "4. 文章页、关于页的头像：路径前缀不同（`../assets`），别 404",
)
t = t.replace("- `dist/` —— 本地构建产物，给预览用", "- `dist/` 本地构建产物，给预览用")
t = t.replace("- `docs/` —— GitHub Pages 吃的目录", "- `docs/` GitHub Pages 吃的目录")
t = t.replace(
    "不影响 GitHub 发布——推的是 `docs/`，不是预览目录。",
    "不影响 GitHub 发布，推的是 `docs/`，不是预览目录。",
)
p.write_text(t, encoding="utf-8")
print("dash", t.count("——"))
for i, ln in enumerate(t.splitlines(), 1):
    if "——" in ln or re.search(r"不是[^。]{1,25}(而是|，是)", ln):
        print(i, ln[:100])
print("ok")
