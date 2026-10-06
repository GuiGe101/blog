# -*- coding: utf-8 -*-
"""个人博客构建脚本：posts/*.md -> dist/*.html"""
from __future__ import annotations

import html
import re
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
POSTS_DIR = ROOT / "posts"
ASSETS_DIR = ROOT / "assets"
DIST = ROOT / "dist"

SITE_NAME = "zixuann"
SITE_DESC = "记录一点想说的"
ABOUT_FILE = ROOT / "about.md"

# giscus 配置（部署后到 https://giscus.app 填你的 GitHub 仓库再替换）
GISCUS = {
    "repo": "GuiGe101/blog",
    "repo_id": "R_kgDOU-a8Mw",
    "category": "Announcements",
    "category_id": "DIC_kwDOU-a8M84DHMCl",
}


# ---------- Markdown ----------
def parse_frontmatter(text: str) -> tuple[dict, str]:
    meta: dict = {}
    body = text
    if text.startswith("---"):
        m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?", text, re.S)
        if m:
            for line in m.group(1).splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip("\"'")
            body = text[m.end():]
    return meta, body


def inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img alt="\1" src="\2">', text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    return text


def md_to_html(text: str) -> str:
    lines = text.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]

        # 代码块
        if line.strip().startswith("```"):
            lang = line.strip()[3:].strip()
            i += 1
            code_lines: list[str] = []
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1
            cls = f' class="lang-{html.escape(lang)}"' if lang else ""
            out.append(f"<pre><code{cls}>{html.escape(chr(10).join(code_lines))}</code></pre>")
            continue

        # 标题
        hm = re.match(r"^(#{1,6})\s+(.*)$", line)
        if hm:
            level = len(hm.group(1))
            out.append(f"<h{level}>{inline(hm.group(2).strip())}</h{level}>")
            i += 1
            continue

        # 引用
        if line.startswith(">"):
            quote_lines: list[str] = []
            while i < n and lines[i].startswith(">"):
                quote_lines.append(lines[i].lstrip("> ").rstrip())
                i += 1
            inner = "<br>".join(inline(x) for x in quote_lines if x.strip())
            out.append(f"<blockquote><p>{inner}</p></blockquote>")
            continue

        # 无序列表
        if re.match(r"^[-*+]\s+", line):
            items: list[str] = []
            while i < n and re.match(r"^[-*+]\s+", lines[i]):
                items.append(f"<li>{inline(re.sub(r'^[-*+]\s+', '', lines[i]))}</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue

        # 有序列表
        if re.match(r"^\d+\.\s+", line):
            items = []
            while i < n and re.match(r"^\d+\.\s+", lines[i]):
                items.append(f"<li>{inline(re.sub(r'^\d+\.\s+', '', lines[i]))}</li>")
                i += 1
            out.append("<ol>" + "".join(items) + "</ol>")
            continue

        # 空行
        if not line.strip():
            i += 1
            continue

        # 段落（合并连续非空行）
        para: list[str] = []
        while i < n and lines[i].strip() and not re.match(
            r"^(#{1,6}\s|>|[-*+]\s|\d+\.\s|```)", lines[i]
        ):
            para.append(lines[i].strip())
            i += 1
        out.append(f"<p>{inline(' '.join(para))}</p>")

    return "\n".join(out)


# ---------- 模板 ----------
def page(title: str, body: str, active: str = "") -> str:
    def nav_class(name: str) -> str:
        return ' class="active"' if name == active else ""

    page_title = SITE_NAME if title == SITE_NAME else f"{title} · {SITE_NAME}"
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(page_title)}</title>
<meta name="description" content="{html.escape(SITE_DESC)}">
<link rel="stylesheet" href="{{{{ASSETS}}}}/style.css">
</head>
<body>
<header class="site-header">
  <a class="site-title" href="{{{{HOME}}}}">{html.escape(SITE_NAME)}</a>
  <nav class="site-nav">
    <a href="{{{{HOME}}}}" {nav_class("home")}>首页</a>
    <a href="{{{{ABOUT}}}}" {nav_class("about")}>关于</a>
  </nav>
</header>
<main>
{body}
</main>
<footer class="site-footer">© {datetime.now().year} {html.escape(SITE_NAME)}</footer>
</body>
</html>
"""


def giscus_html() -> str:
    return f"""
<section class="echo">
  <h2 class="echo-title">回声</h2>
  <p class="echo-note">欢迎留言、点赞。登录 GitHub 账号即可参与。</p>
  <script src="https://giscus.app/client.js"
    data-repo="{GISCUS['repo']}"
    data-repo-id="{GISCUS['repo_id']}"
    data-category="{GISCUS['category']}"
    data-category-id="{GISCUS['category_id']}"
    data-mapping="pathname"
    data-strict="0"
    data-reactions-enabled="1"
    data-emit-metadata="0"
    data-input-position="bottom"
    data-theme="preferred_color_scheme"
    data-lang="zh-CN"
    crossorigin="anonymous"
    async>
  </script>
</section>
"""


def load_posts() -> list[dict]:
    posts: list[dict] = []
    for path in sorted(POSTS_DIR.glob("*.md"), reverse=True):
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        posts.append(
            {
                "slug": path.stem,
                "title": meta.get("title", path.stem),
                "date": meta.get("date", ""),
                "summary": meta.get("summary", ""),
                "tags": meta.get("tags", ""),
                "html": md_to_html(body),
                "source": body,
            }
        )
    # 按日期倒序，无日期的靠后
    posts.sort(key=lambda p: p["date"] or "0000-00-00", reverse=True)
    return posts


def build() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "posts").mkdir(parents=True)
    shutil.copytree(ASSETS_DIR, DIST / "assets")

    posts = load_posts()

    # 首页
    items = []
    for p in posts:
        summary = p["summary"] or _first_text(p["source"])
        items.append(
            f"""<li class="post-item">
  <h2><a href="posts/{p['slug']}.html">{html.escape(p['title'])}</a></h2>
  <div class="post-meta">{html.escape(p['date'])}</div>
  <p class="post-summary">{html.escape(summary)}</p>
</li>"""
        )
    index_body = '<ul class="post-list">' + "\n".join(items) + "</ul>" if items else "<p>还没有文章。</p>"
    _write(
        DIST / "index.html",
        page(SITE_NAME, index_body, active="home"),
        assets_prefix=".",
        home="index.html",
        about="about.html",
    )

    # 关于
    about_body = ""
    if ABOUT_FILE.exists():
        meta, body = parse_frontmatter(ABOUT_FILE.read_text(encoding="utf-8"))
        about_body = f'<div class="about-body">{md_to_html(body)}</div>'
    else:
        about_body = '<div class="about-body"><p>这里是关于页。</p></div>'
    _write(
        DIST / "about.html",
        page("关于", about_body, active="about"),
        assets_prefix=".",
        home="index.html",
        about="about.html",
    )

    # 文章
    for p in posts:
        tags = f"<span>{html.escape(p['tags'])}</span>" if p["tags"] else ""
        body = f"""<article>
<header class="article-header">
  <h1>{html.escape(p['title'])}</h1>
  <div class="post-meta">{html.escape(p['date'])} {tags}</div>
</header>
<div class="article-body">
{p['html']}
</div>
{giscus_html()}
</article>"""
        _write(
            DIST / "posts" / f"{p['slug']}.html",
            page(p["title"], body, active="home"),
            assets_prefix="..",
            home="../index.html",
            about="../about.html",
        )

    print(f"构建完成：{len(posts)} 篇文章 -> {DIST}")


def _first_text(md: str, limit: int = 80) -> str:
    for line in md.splitlines():
        s = re.sub(r"[#>*`\[\]!]", "", line).strip()
        if s:
            return s[:limit] + ("…" if len(s) > limit else "")
    return ""


def _write(path: Path, html_text: str, *, assets_prefix: str, home: str, about: str) -> None:
    html_text = (
        html_text.replace("{{ASSETS}}", f"{assets_prefix}/assets")
        .replace("{{HOME}}", home)
        .replace("{{ABOUT}}", about)
    )
    path.write_text(html_text, encoding="utf-8")


if __name__ == "__main__":
    build()
