from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "posts"
ASSETS_DIR = ROOT / "assets"
DIST_DIR = ROOT / "dist"
PAGES_DIR = ROOT / "docs"
PREVIEW_DIR = ROOT.parent / "preview"

SITE_NAME = "归舸"
SITE_TITLE = "归舸的大窝"
SITE_SUB = "打瓦、想东想西——慢慢记下来"
SITE_DESC = "记录生活、技术、灵感与没写完的想法。"
SITE_BIO = "16 岁，打无畏契约、偶尔想东想西。这里慢慢同步生活、技术和灵感。"
SITE_URL = "https://zixuann.top"
START_DATE = "2026-10-06"
AUTHOR = "GuiGe101"
COUNT_NS = "zixuann.top"
COUNT_API = "https://abacus.jasoncameron.dev"

NAV = (
    ("首页", "index.html", "home"),
    ("归档", "archive.html", "archive"),
    ("分类", "categories.html", "categories"),
    ("标签", "tags.html", "tags"),
    ("项目", "projects.html", "projects"),
    ("关于", "about.html", "about"),
)

WALINE_SERVER = "https://waline-gamma-ruddy.vercel.app"
GISCUS = {
    "repo": "GuiGe101/blog",
    "repo_id": "R_kgDOU-a8Mw",
    "category": "Announcements",
    "category_id": "DIC_kwDOU-a8M84DHMCl",
}