from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

from . import templates
from .config import (
    ASSETS_DIR,
    DIST_DIR,
    PAGES_DIR,
    PREVIEW_DIR,
    ROOT,
    SITE_DESC,
    SITE_NAME,
    SITE_URL,
    START_DATE,
)
from .content import load_page, load_posts, site_stats


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def mirror(source: Path, destination: Path) -> None:
    if destination.resolve() in {ROOT.resolve(), source.resolve()}:
        raise ValueError(f"refusing to mirror into {destination}")
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def rss_date(value: str) -> str:
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d")
        return parsed.strftime("%a, %d %b %Y 00:00:00 +0800")
    except ValueError:
        return value


def build() -> int:
    posts = load_posts()
    stats = site_stats(posts)

    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)
    shutil.copytree(ASSETS_DIR, DIST_DIR / "assets")

    write(DIST_DIR / "index.html", templates.home_page(posts, stats))
    write(DIST_DIR / "archive.html", templates.archive_page(posts, stats))
    write(DIST_DIR / "categories.html", templates.categories_page(posts))
    write(DIST_DIR / "tags.html", templates.tags_page(posts))

    about_title, about_content = load_page(
        "about.md", "关于我"
    )
    write(
        DIST_DIR / "about.html",
        templates.static_page(
            about_title,
            "ABOUT / 屋主",
            "关于归舸：打瓦、写点代码，偶尔想东想西。",
            about_content,
            "about",
        ),
    )

    projects_title, projects_content = load_page(
        "projects.md", "项目与作品"
    )
    write(
        DIST_DIR / "projects.html",
        templates.static_page(
            projects_title,
            "PROJECTS / 折腾",
            "在做的项目和折腾过的东西，有进展就补上。",
            projects_content,
            "projects",
        ),
    )

    for post in posts:
        write(DIST_DIR / "posts" / f"{post.slug}.html", templates.article_page(post, posts))

    write(DIST_DIR / "404.html", templates.not_found_page())

    search_index = [
        {
            "title": post.title,
            "url": f"posts/{post.slug}.html",
            "summary": post.summary,
            "tags": list(post.tags),
            "category": post.category,
            "date": post.date,
        }
        for post in posts
    ]
    write(DIST_DIR / "search-index.json", json.dumps(search_index, ensure_ascii=False))

    items = "\n".join(
        f"""<item>
  <title>{xml_escape(post.title)}</title>
  <link>{SITE_URL}/{post.url}</link>
  <guid>{SITE_URL}/{post.url}</guid>
  <pubDate>{rss_date(post.date)}</pubDate>
  <description>{xml_escape(post.summary)}</description>
</item>"""
        for post in posts[:20]
    )
    write(
        DIST_DIR / "feed.xml",
        f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
<title>{xml_escape(SITE_NAME)}</title>
<link>{SITE_URL}</link>
<description>{xml_escape(SITE_DESC)}</description>
<language>zh-cn</language>
{items}
</channel></rss>
""",
    )

    urls = ["", "about.html", "archive.html", "categories.html", "tags.html", "projects.html"]
    urls += [post.url for post in posts]
    write(
        DIST_DIR / "sitemap.xml",
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(f"<url><loc>{SITE_URL}/{url}</loc></url>" for url in urls)
        + "\n</urlset>\n",
    )
    write(
        DIST_DIR / "robots.txt",
        f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n",
    )
    write(DIST_DIR / "CNAME", "zixuann.top\n")

    # GitHub Pages has two possible sources; keep both deploy outputs identical.
    mirror(DIST_DIR, PAGES_DIR)
    mirror(DIST_DIR, PREVIEW_DIR)

    print(f"构建完成：{len(posts)} 篇")
    print(f"发布目录：{DIST_DIR}")
    print(f"Pages 镜像：{PAGES_DIR}")
    print(f"本地预览：{PREVIEW_DIR / 'index.html'}")
    return len(posts)


def main() -> None:
    build()


if __name__ == "__main__":
    main()