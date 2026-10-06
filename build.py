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
SITE_TITLE = "zixuann 的记忆终端"
SITE_SUB = "正在同步生活、技术、灵感与未命名的片段"
SITE_DESC = "记录生活、技术、灵感与未命名的片段"
SITE_BIO = "记录生活、技术、灵感与未命名的片段"
ABOUT_FILE = ROOT / "about.md"
START_DATE = "2026-10-06"

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
def nav_html(active: str = "", home: str = "{{HOME}}", about: str = "{{ABOUT}}") -> str:
    def cls(name: str) -> str:
        return ' class="active"' if name == active else ""

    return f"""<header class="site-nav">
  <a class="brand" href="{home}"><span class="brand-mark"></span>{html.escape(SITE_NAME)}</a>
  <nav class="nav-links">
    <a href="{home}"{cls("home")}>主页</a>
    <a href="{home}"{cls("archive")}>归档</a>
    <a href="{about}"{cls("about")}>关于</a>
    <a href="{home}#posts">其他</a>
  </nav>
</header>"""


def hero_html(home: str = "{{HOME}}") -> str:
    return f"""
<div class="hero">
  <div class="hero-deco">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
  </div>
  <div class="hero-copy">
    <h1 class="hero-title">{html.escape(SITE_TITLE)}</h1>
    <p class="hero-sub">{html.escape(SITE_SUB)}</p>
  </div>
  <div class="hero-wave">
    <svg viewBox="0 0 1440 90" preserveAspectRatio="none" aria-hidden="true">
      <path fill="#ffffff" d="M0,48 C240,90 420,10 720,42 C1020,74 1200,18 1440,50 L1440,90 L0,90 Z"></path>
    </svg>
  </div>
</div>"""


def profile_html() -> str:
    return f"""<section class="card profile">
  <div class="profile-avatar">
    <img src="{{{{ASSETS}}}}/avatar.svg" alt="avatar">
  </div>
  <h2 class="profile-name">{html.escape(SITE_NAME)}</h2>
  <p class="profile-bio">{html.escape(SITE_BIO)}</p>
</section>"""


def stats_html(posts: list[dict]) -> str:
    total_words = sum(len(re.sub(r"\s", "", p["source"])) for p in posts)
    tags: set[str] = set()
    cats: set[str] = set()
    for p in posts:
        if p["tags"]:
            for t in re.split(r"[,，、/|]", p["tags"]):
                t = t.strip()
                if t:
                    tags.add(t)
        if p.get("category"):
            cats.add(p["category"])
        else:
            cats.add(p["tags"] or "随笔")
    days = 1
    try:
        start = datetime.strptime(START_DATE, "%Y-%m-%d")
        days = max(1, (datetime.now() - start).days + 1)
    except Exception:
        pass
    last = posts[0]["date"] if posts else START_DATE
    return f"""<section class="card">
  <h3 class="side-title">站点统计</h3>
  <div class="stat-row"><span>文章</span><b>{len(posts)}</b></div>
  <div class="stat-row"><span>分类</span><b>{len(cats)}</b></div>
  <div class="stat-row"><span>标签</span><b>{len(tags)}</b></div>
  <div class="stat-row"><span>总字数</span><b>{total_words}</b></div>
  <div class="stat-row"><span>运行天数</span><b>{days} 天</b></div>
  <div class="stat-row"><span>最后活动</span><b>{html.escape(last)}</b></div>
  <div class="side-note">这是一个还在慢慢同步的记忆终端。</div>
</section>"""


def page(title: str, body: str, active: str = "", *, hero: bool = True) -> str:
    page_title = SITE_NAME if title == SITE_NAME else f"{title} · {SITE_NAME}"
    hero_block = hero_html() if hero else ""
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
{nav_html(active=active)}
{hero_block}
{body}
<footer class="site-footer">© {datetime.now().year} {html.escape(SITE_NAME)} · 记忆终端</footer>
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
                "cover": meta.get("cover", ""),
                "html": md_to_html(body),
                "source": body,
            }
        )
    posts.sort(key=lambda p: p["date"] or "0000-00-00", reverse=True)
    return posts


def post_card_html(p: dict, prefix: str = "posts/") -> str:
    summary = p["summary"] or _first_text(p["source"])
    tags = ""
    if p["tags"]:
        tags = "".join(
            f"<span>#{html.escape(t.strip())}</span>"
            for t in re.split(r"[,，、/|]", p["tags"])
            if t.strip()
        )
        tags = f'<div class="post-tags">{tags}</div>'
    cover = ""
    if p["cover"]:
        cover = f'<div class="post-cover"><img src="{html.escape(p["cover"])}" alt=""></div>'
    else:
        cover = '<div class="post-cover"></div>'
    return f"""<article class="card post-card">
  <div>
    <h2 class="post-title"><a href="{prefix}{p['slug']}.html">{html.escape(p['title'])}</a></h2>
    <div class="post-meta"><span>📅 {html.escape(p['date'])}</span><span>✍️ {html.escape(p['tags'] or '随笔')}</span><span>📝 {len(re.sub(r'\\s', '', p['source']))} 字</span></div>
    <p class="post-summary">{html.escape(summary)}</p>
    {tags}
  </div>
  {cover}
</article>"""


def build() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "posts").mkdir(parents=True)
    shutil.copytree(ASSETS_DIR, DIST / "assets")

    posts = load_posts()
    cards = "\n".join(post_card_html(p) for p in posts) if posts else "<p>还没有文章。</p>"
    tagbar = """<div class="tagbar">
  <a class="tag-chip active" href="index.html">🏠 主页<b>{n}</b></a>
  <a class="tag-chip" href="index.html">📁 归档<b>{n}</b></a>
  <a class="tag-chip" href="index.html">🧠 记忆<b>1</b></a>
  <a class="tag-chip" href="index.html">🛠 技术<b>1</b></a>
  <a class="tag-chip" href="index.html">🎨 设计<b>1</b></a>
</div>""".replace("{n}", str(len(posts)))

    index_body = f"""
<div class="page">
  <aside class="left-col">{profile_html()}</aside>
  <section class="main-col" id="posts">
    {tagbar}
    {cards}
  </section>
  <aside class="side-col">{stats_html(posts)}</aside>
</div>
"""
    _write(
        DIST / "index.html",
        page(SITE_NAME, index_body, active="home"),
        assets_prefix=".",
        home="index.html",
        about="about.html",
    )

    about_src = ""
    if ABOUT_FILE.exists():
        meta, body = parse_frontmatter(ABOUT_FILE.read_text(encoding="utf-8"))
        about_src = md_to_html(body)
    else:
        about_src = "<p>这里是关于页。</p>"
    about_body = f"""
<div class="article-shell">
  <div class="about-card">
    <h1 style="margin-top:0">关于</h1>
    <div class="article-body">{about_src}</div>
  </div>
</div>
"""
    _write(
        DIST / "about.html",
        page("关于", about_body, active="about"),
        assets_prefix=".",
        home="index.html",
        about="about.html",
    )

    for p in posts:
        tags = f"<span>{html.escape(p['tags'])}</span>" if p["tags"] else ""
        body = f"""
<div class="article-shell">
  <article class="article-card">
    <header class="article-header">
      <h1>{html.escape(p['title'])}</h1>
      <div class="post-meta"><span>📅 {html.escape(p['date'])}</span>{tags}</div>
    </header>
    <div class="article-body">
{p['html']}
    </div>
  </article>
  {giscus_html()}
</div>
"""
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
