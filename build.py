# -*- coding: utf-8 -*-
"""zixuann 记忆终端 · 完整静态博客构建器"""
from __future__ import annotations

import html
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape as xesc

ROOT = Path(__file__).parent.resolve()
POSTS_DIR = ROOT / "posts"
ASSETS_DIR = ROOT / "assets"
DIST = ROOT / "dist"
# 预览输出到会话工作目录（index.html 可直接浏览器打开）
SESSION_CWD = Path(r"E:\AI\MIMO DESKTOP\XiangMu\.mimo-sessions\2026\10\06\new-chat")
PREVIEW_DIR = SESSION_CWD if SESSION_CWD.exists() else Path.cwd()
if PREVIEW_DIR.resolve() == ROOT.resolve():
    PREVIEW_DIR = DIST

SITE_NAME = "归舸"
SITE_TITLE = "归舸的记忆终端"
SITE_SUB = "打瓦、想东想西——慢慢记下来"
SITE_DESC = "记录生活、技术、灵感与未命名的片段。技术、生活、思考三条主线。"
SITE_BIO = "16 岁，在写代码、打无畏契约、偶尔想东想西。这里慢慢同步生活、技术和灵感。"
SITE_URL = "https://zixuann.top"
START_DATE = "2026-10-06"
AUTHOR = "归舸"

GISCUS = {
    "repo": "GuiGe101/blog",
    "repo_id": "R_kgDOU-a8Mw",
    "category": "Announcements",
    "category_id": "DIC_kwDOU-a8M84DHMCl",
}

NAV = [
    ("主页", "index.html"),
    ("归档", "archive.html"),
    ("分类", "categories.html"),
    ("标签", "tags.html"),
    ("项目", "projects.html"),
    ("关于", "about.html"),
]


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
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img loading="lazy" alt="\1" src="\2">', text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    return text


def md_to_html(text: str) -> str:
    lines = text.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
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
        hm = re.match(r"^(#{1,6})\s+(.*)$", line)
        if hm:
            level = len(hm.group(1))
            title = hm.group(2).strip()
            hid = re.sub(r"[^\w一-鿿-]+", "-", title).strip("-").lower() or f"h{level}"
            out.append(f'<h{level} id="{hid}">{inline(title)}</h{level}>')
            i += 1
            continue
        if line.startswith(">"):
            quote: list[str] = []
            while i < n and lines[i].startswith(">"):
                quote.append(lines[i].lstrip("> ").rstrip())
                i += 1
            inner = "<br>".join(inline(x) for x in quote if x.strip())
            out.append(f"<blockquote><p>{inner}</p></blockquote>")
            continue
        if re.match(r"^[-*+]\s+", line):
            items: list[str] = []
            while i < n and re.match(r"^[-*+]\s+", lines[i]):
                items.append(f"<li>{inline(re.sub(r'^[-*+]\s+', '', lines[i]))}</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue
        if re.match(r"^\d+\.\s+", line):
            items = []
            while i < n and re.match(r"^\d+\.\s+", lines[i]):
                items.append(f"<li>{inline(re.sub(r'^\d+\.\s+', '', lines[i]))}</li>")
                i += 1
            out.append("<ol>" + "".join(items) + "</ol>")
            continue
        if not line.strip():
            i += 1
            continue
        para: list[str] = []
        while i < n and lines[i].strip() and not re.match(
            r"^(#{1,6}\s|>|[-*+]\s|\d+\.\s|```)", lines[i]
        ):
            para.append(lines[i].strip())
            i += 1
        out.append(f"<p>{inline(' '.join(para))}</p>")
    return "\n".join(out)


def extract_toc(html_text: str) -> str:
    heads = re.findall(r'<h([23]) id="([^"]+)">([^<]+)</h\1>', html_text)
    if not heads:
        return ""
    items = []
    for level, hid, title in heads:
        cls = "toc-h3" if level == "3" else "toc-h2"
        items.append(f'<a class="{cls}" href="#{hid}">{html.escape(title)}</a>')
    return f'<nav class="toc"><div class="toc-title">目录</div>{"".join(items)}</nav>'


def word_count(md: str) -> int:
    return len(re.sub(r"\s", "", md))


def reading_minutes(words: int) -> int:
    return max(1, round(words / 400))


def split_tags(tags: str) -> list[str]:
    return [t.strip() for t in re.split(r"[,，、/|]", tags or "") if t.strip()]


# ---------- 片段 ----------
def icon(name: str) -> str:
    icons = {
        "search": (
            '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">'
            '<circle cx="11" cy="11" r="6.5" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '<path d="M16 16l4.5 4.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>'
            "</svg>"
        ),
        "theme": (
            '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">'
            '<circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '<path d="M12 3v2.2M12 18.8V21M3 12h2.2M18.8 12H21M5.6 5.6l1.6 1.6M16.8 16.8l1.6 1.6M18.4 5.6l-1.6 1.6M7.2 16.8l-1.6 1.6" '
            'fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>'
            "</svg>"
        ),
        "menu": (
            '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">'
            '<path d="M5 8h14M5 12h14M5 16h14" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>'
            "</svg>"
        ),
    }
    return icons[name]


def nav_html(prefix: str = "", active: str = "主页") -> str:
    links = []
    for name, href in NAV:
        cls = ' class="active"' if name == active else ""
        links.append(f'<a href="{prefix}{href}"{cls}>{name}</a>')
    return f"""<header class="site-nav">
  <a class="brand" href="{prefix}index.html"><span class="brand-mark"><img src="{prefix}assets/avatar.jpg" alt=""></span>{html.escape(SITE_NAME)}</a>
  <nav class="nav-links">{''.join(links)}</nav>
  <div class="nav-actions">
    <button class="icon-btn" id="search-open" title="搜索" aria-label="搜索">{icon('search')}</button>
    <button class="icon-btn" id="theme-toggle" title="明暗切换" aria-label="明暗切换">{icon('theme')}</button>
    <button class="icon-btn menu-btn" id="menu-toggle" title="菜单" aria-label="菜单">{icon('menu')}</button>
  </div>
</header>
<div class="mobile-nav" id="mobile-nav">{''.join(links)}</div>"""


def hero_html(post_count: int = 0) -> str:
    return f"""
<div class="hero">
  <div class="hero-shade"></div>
  <div class="hero-copy">
    <p class="hero-kicker">MEMORY TERMINAL</p>
    <h1 class="hero-title">{html.escape(SITE_TITLE)}</h1>
    <p class="hero-sub">{html.escape(SITE_SUB)}</p>
    <div class="hero-stats">
      <span>访问 <b id="stat-site-pv-hero">…</b></span>
      <span>文章 <b>{post_count}</b></span>
      <span>自 {START_DATE}</span>
    </div>
  </div>
  <div class="hero-wave">
    <svg viewBox="0 0 1440 90" preserveAspectRatio="none" aria-hidden="true">
      <path fill="var(--paper)" d="M0,48 C240,90 420,10 720,42 C1020,74 1200,18 1440,50 L1440,90 L0,90 Z"></path>
    </svg>
  </div>
</div>"""


def profile_card(prefix: str = "") -> str:
    return f"""<section class="card profile">
  <div class="profile-avatar"><img src="{prefix}assets/avatar.jpg" alt="avatar" loading="lazy"></div>
  <h2 class="profile-name">{html.escape(SITE_NAME)}</h2>
  <p class="profile-bio">{html.escape(SITE_BIO)}</p>
  <div class="profile-links">
    <a href="{prefix}about.html">关于</a>
    <a href="{prefix}projects.html">项目</a>
    <a href="{prefix}feed.xml">RSS</a>
  </div>
</section>"""


def stats_card(posts: list[dict], prefix: str = "") -> str:
    words = sum(p["words"] for p in posts)
    tags: set[str] = set()
    cats: set[str] = set()
    for p in posts:
        tags.update(p["tag_list"])
        cats.add(p["category"] or "随笔")
    days = 1
    try:
        days = max(1, (datetime.now() - datetime.strptime(START_DATE, "%Y-%m-%d")).days + 1)
    except Exception:
        pass
    rows = [
        ("文章", str(len(posts))),
        ("分类", str(len(cats))),
        ("标签", str(len(tags))),
        ("总字数", f"{words}"),
        ("运行天数", f"{days} 天"),
        ("最后活动", html.escape(posts[0]["date"] if posts else START_DATE)),
    ]
    body = "".join(f'<div class="stat-row"><span>{k}</span><b>{v}</b></div>' for k, v in rows)
    return f"""<section class="card">
  <h3 class="side-title">站点统计</h3>
  {body}
  <div class="side-note">访问统计由 Abacus 提供，刷新页面数字会跳。</div>
</section>"""


def categories_card(posts: list[dict], prefix: str = "") -> str:
    from collections import Counter

    c = Counter(p["category"] or "随笔" for p in posts)
    chips = "".join(
        f'<a class="tag-chip" href="{prefix}categories.html#{html.escape(k)}">{html.escape(k)}<b>{v}</b></a>'
        for k, v in c.most_common()
    )
    return f'<section class="card"><h3 class="side-title">分类</h3><div class="tagbar">{chips}</div></section>'


def tags_card(posts: list[dict], prefix: str = "") -> str:
    from collections import Counter

    c = Counter(t for p in posts for t in p["tag_list"])
    chips = "".join(
        f'<a class="tag-chip" href="{prefix}tags.html#{html.escape(k)}">#{html.escape(k)}<b>{v}</b></a>'
        for k, v in c.most_common(16)
    )
    return f'<section class="card"><h3 class="side-title">标签</h3><div class="tagbar">{chips}</div></section>'


def toc_and_meta(p: dict) -> str:
    toc = extract_toc(p["html"])
    return toc


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
    async></script>
</section>"""


def page(
    title: str,
    body: str,
    *,
    prefix: str = "",
    active: str = "主页",
    desc: str = "",
    hero: bool = True,
    hero_count: int = 0,
    og_image: str = "",
) -> str:
    page_title = SITE_NAME if title == SITE_NAME else f"{title} · {SITE_NAME}"
    desc = desc or SITE_DESC
    og = og_image or f"{prefix}assets/valorant/hero-jett.jpg"
    hero_block = hero_html(post_count=hero_count) if hero else ""
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(page_title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="author" content="{AUTHOR}">
<link rel="canonical" href="{SITE_URL}/{title if title != SITE_NAME else ''}">
<meta property="og:title" content="{html.escape(page_title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE_URL}/">
<meta property="og:image" content="{og}">
<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" title="{html.escape(SITE_NAME)}" href="{prefix}feed.xml">
<link rel="icon" href="{prefix}assets/avatar.jpg" type="image/jpeg">
<link rel="stylesheet" href="{prefix}assets/style.css">
<script>
  (function () {{
    try {{
      var t = localStorage.getItem('theme');
      if (t === 'dark' || (!t && window.matchMedia('(prefers-color-scheme: dark)').matches)) {{
        document.documentElement.classList.add('dark');
      }}
    }} catch (e) {{}}
  }})();
</script>
</head>
<body>
<div class="progress" id="progress"></div>
{nav_html(prefix=prefix, active=active)}
{hero_block}
{body}
<footer class="site-footer">
  <div>© {datetime.now().year} {html.escape(SITE_NAME)} · 记忆终端</div>
  <div class="footer-meta">
    <a href="{prefix}feed.xml">RSS</a>
    <a href="{prefix}sitemap.xml">Sitemap</a>
    <span>访客 <b id="stat-site-uv">…</b></span>
    <span>访问 <b id="stat-site-pv">…</b></span>
  </div>
</footer>
<div class="search-modal" id="search-modal" hidden>
  <div class="search-box">
    <input id="search-input" type="search" placeholder="搜索标题、摘要、标签…" autocomplete="off">
    <div id="search-results"></div>
  </div>
</div>
<script src="{prefix}assets/app.js"></script>
<script>
(function () {{
  var NS = "zixuann.top";
  var API = "https://abacus.jasoncameron.dev";
  function set(id, v) {{
    var n = document.getElementById(id);
    if (n && v != null) n.textContent = v;
  }}
  function jsonp(url) {{
    return new Promise(function (resolve) {{
      var name = "abacus_cb_" + Date.now() + "_" + Math.floor(Math.random() * 10000);
      window[name] = function (data) {{ resolve(data); cleanup(); }};
      var s = document.createElement("script");
      s.src = url + (url.indexOf("?") >= 0 ? "&" : "?") + "callback=" + name;
      s.onerror = function () {{ resolve(null); cleanup(); }};
      function cleanup() {{
        try {{ delete window[name]; }} catch (e) {{ window[name] = undefined; }}
        if (s.parentNode) s.parentNode.removeChild(s);
      }}
      document.head.appendChild(s);
    }});
  }}
  function hit(key) {{ return jsonp(API + "/hit/" + NS + "/" + key); }}
  function get(key) {{ return jsonp(API + "/get/" + NS + "/" + key); }}

  var pageEl = document.getElementById("stat-page-pv");
  if (pageEl) {{
    var pageKey = pageEl.getAttribute("data-key") || location.pathname.replace(/\\W+/g, "-");
    hit("page-" + pageKey).then(function (d) {{ if (d) set("stat-page-pv", d.value); }});
  }}

  hit("site-pv").then(function (d) {{
    if (!d) return;
    set("stat-site-pv", d.value);
    set("stat-site-pv-hero", d.value);
  }});

  var uvSeenKey = "zixuann-uv-seen";
  var seen = false;
  try {{ seen = localStorage.getItem(uvSeenKey) === "1"; }} catch (e) {{}}
  var uvCall = seen ? get("site-uv") : hit("site-uv");
  if (!seen) {{ try {{ localStorage.setItem(uvSeenKey, "1"); }} catch (e) {{}} }}
  uvCall.then(function (d) {{ if (d) set("stat-site-uv", d.value); }});
}})();
</script>
</body>
</html>
"""


# ---------- 内容 ----------
def load_posts() -> list[dict]:
    posts: list[dict] = []
    if not POSTS_DIR.exists():
        return posts
    for path in POSTS_DIR.glob("*.md"):
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        words = word_count(body)
        tag_list = split_tags(meta.get("tags", ""))
        posts.append(
            {
                "slug": path.stem,
                "title": meta.get("title", path.stem),
                "date": meta.get("date", ""),
                "summary": meta.get("summary", ""),
                "tags": meta.get("tags", ""),
                "tag_list": tag_list,
                "category": meta.get("category", tag_list[0] if tag_list else "随笔"),
                "cover": meta.get("cover", "assets/valorant/cover-sage.jpg"),
                "featured": meta.get("featured", "").lower() in {"1", "true", "yes", "y"},
                "series": meta.get("series", ""),
                "series_order": int(meta.get("series_order", "0") or 0),
                "html": md_to_html(body),
                "source": body,
                "words": words,
                "minutes": reading_minutes(words),
            }
        )
    posts.sort(key=lambda p: (p["date"] or "0000-00-00", p["slug"]), reverse=True)
    return posts


def post_card(p: dict, prefix: str = "posts/") -> str:
    tags = "".join(f"<span>#{html.escape(t)}</span>" for t in p["tag_list"])
    featured = '<span class="badge">精选</span>' if p["featured"] else ""
    series = f'<span class="badge series">{html.escape(p["series"])}</span>' if p["series"] else ""
    return f"""<article class="card post-card">
  <div>
    <div class="badges">{featured}{series}</div>
    <h2 class="post-title"><a href="{prefix}{p['slug']}.html">{html.escape(p['title'])}</a></h2>
    <div class="post-meta">
      <span>{html.escape(p['date'])}</span>
      <span>{html.escape(p['category'])}</span>
      <span>{p['minutes']} 分钟</span>
      <span>{p['words']} 字</span>
    </div>
    <p class="post-summary">{html.escape(p['summary'])}</p>
    <div class="post-tags">{tags}</div>
  </div>
  <a class="post-cover" href="{prefix}{p['slug']}.html">
    <img src="{p['cover']}" alt="" loading="lazy">
  </a>
</article>"""


def build() -> None:
    posts = load_posts()
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "posts").mkdir(parents=True)
    shutil.copytree(ASSETS_DIR, DIST / "assets")

    # 搜索索引
    index = [
        {
            "title": p["title"],
            "url": f"/posts/{p['slug']}.html",
            "summary": p["summary"],
            "tags": p["tag_list"],
            "category": p["category"],
            "date": p["date"],
        }
        for p in posts
    ]
    (DIST / "search-index.json").write_text(
        json.dumps(index, ensure_ascii=False), encoding="utf-8"
    )

    # 首页
    featured = [p for p in posts if p["featured"]]
    rest = [p for p in posts if not p["featured"]]
    feat_html = ""
    if featured:
        items = "".join(post_card(p) for p in featured)
        feat_html = f'<h2 class="section-title">精选</h2>{items}'
    stream = "".join(post_card(p) for p in rest) or "<p>暂无更多文章。</p>"
    index_body = f"""
<div class="page">
  <aside class="left-col">{profile_card()}<div class="stack">{categories_card(posts)}</div></aside>
  <section class="main-col" id="posts">
    {feat_html}
    <h2 class="section-title">最新</h2>
    {stream}
  </section>
  <aside class="side-col">
    {stats_card(posts)}
    {tags_card(posts)}
  </aside>
</div>"""
    _write(
        DIST / "index.html",
        page(SITE_NAME, index_body, active="主页", hero_count=len(posts)),
        prefix="",
    )

    # 归档
    by_year: dict[str, list[dict]] = {}
    for p in posts:
        y = (p["date"] or "0000")[:4]
        by_year.setdefault(y, []).append(p)
    arch = []
    for y in sorted(by_year.keys(), reverse=True):
        lis = "".join(
            f'<li><span>{html.escape(p["date"])}</span><a href="posts/{p["slug"]}.html">{html.escape(p["title"])}</a></li>'
            for p in by_year[y]
        )
        arch.append(f'<h2 class="section-title">{y}</h2><ul class="arch-list">{lis}</ul>')
    _write(
        DIST / "archive.html",
        page("归档", f'<div class="page single">{"".join(arch)}</div>', active="归档", hero=False),
        prefix="",
    )

    # 分类
    from collections import defaultdict

    by_cat: dict[str, list[dict]] = defaultdict(list)
    for p in posts:
        by_cat[p["category"] or "随笔"].append(p)
    cat_html = []
    for cat, items in sorted(by_cat.items(), key=lambda kv: -len(kv[1])):
        lis = "".join(
            f'<li><span>{html.escape(p["date"])}</span><a href="posts/{p["slug"]}.html">{html.escape(p["title"])}</a></li>'
            for p in items
        )
        cat_html.append(f'<h2 class="section-title" id="{html.escape(cat)}">{html.escape(cat)} <small>{len(items)}</small></h2><ul class="arch-list">{lis}</ul>')
    _write(
        DIST / "categories.html",
        page("分类", f'<div class="page single">{"".join(cat_html)}</div>', active="分类", hero=False),
        prefix="",
    )

    # 标签
    by_tag: dict[str, list[dict]] = defaultdict(list)
    for p in posts:
        for t in p["tag_list"]:
            by_tag[t].append(p)
    tag_cloud = "".join(
        f'<a class="tag-chip" href="#{html.escape(t)}">#{html.escape(t)}<b>{len(v)}</b></a>'
        for t, v in sorted(by_tag.items(), key=lambda kv: -len(kv[1]))
    )
    tag_html = [f'<div class="tagbar">{tag_cloud}</div>']
    for t, items in sorted(by_tag.items(), key=lambda kv: -len(kv[1])):
        lis = "".join(
            f'<li><span>{html.escape(p["date"])}</span><a href="posts/{p["slug"]}.html">{html.escape(p["title"])}</a></li>'
            for p in items
        )
        tag_html.append(f'<h2 class="section-title" id="{html.escape(t)}">#{html.escape(t)}</h2><ul class="arch-list">{lis}</ul>')
    _write(
        DIST / "tags.html",
        page("标签", f'<div class="page single">{"".join(tag_html)}</div>', active="标签", hero=False),
        prefix="",
    )

    # 静态页
    for name, fname, active in [
        ("关于", "about", "关于"),
        ("项目", "projects", "项目"),
    ]:
        md_path = ROOT / f"{fname}.md"
        if md_path.exists():
            meta, body = parse_frontmatter(md_path.read_text(encoding="utf-8"))
            content = md_to_html(body)
            title = meta.get("title", name)
        else:
            content = "<p>内容准备中。</p>"
            title = name
        _write(
            DIST / f"{fname}.html",
            page(
                title,
                f'<div class="page single"><div class="card pad">{content}</div></div>',
                active=active,
                hero=False,
            ),
            prefix="",
        )

    # 404
    _write(
        DIST / "404.html",
        page(
            "页面不存在",
            """<div class="page single"><div class="card pad center">
  <h1>404</h1><p>你走进了未命名的片段。</p>
  <p><a class="btn" href="index.html">回首页</a></p>
</div></div>""",
            active="",
            hero=False,
        ),
        prefix="",
    )

    # 文章页
    # 系列导航
    series_map: dict[str, list[dict]] = defaultdict(list)
    for p in posts:
        if p["series"]:
            series_map[p["series"]].append(p)
    for s in series_map.values():
        s.sort(key=lambda x: x["series_order"])

    for p in posts:
        toc = extract_toc(p["html"])
        tags = "".join(f'<a class="tag-chip" href="../tags.html#{html.escape(t)}">#{html.escape(t)}</a>' for t in p["tag_list"])
        # 相关
        related = [
            x
            for x in posts
            if x["slug"] != p["slug"]
            and (x["category"] == p["category"] or set(x["tag_list"]) & set(p["tag_list"]))
        ][:3]
        rel_html = "".join(
            f'<li><a href="{x["slug"]}.html">{html.escape(x["title"])}</a></li>' for x in related
        )
        # 系列
        ser_html = ""
        if p["series"] and p["series"] in series_map:
            sibs = series_map[p["series"]]
            idx = next(i for i, x in enumerate(sibs) if x["slug"] == p["slug"])
            prev = sibs[idx - 1] if idx > 0 else None
            nxt = sibs[idx + 1] if idx + 1 < len(sibs) else None
            ser_html = '<nav class="series-nav">'
            if prev:
                ser_html += f'<a href="{prev["slug"]}.html">← 上一篇：{html.escape(prev["title"])}</a>'
            else:
                ser_html += "<span></span>"
            ser_html += f'<b>{html.escape(p["series"])} · {idx + 1}/{len(sibs)}</b>'
            if nxt:
                ser_html += f'<a href="{nxt["slug"]}.html">下一篇：{html.escape(nxt["title"])} →</a>'
            else:
                ser_html += "<span></span>"
            ser_html += "</nav>"

        body = f"""
<div class="page article-page">
  <aside class="left-col">{profile_card(prefix="../")}</aside>
  <article class="article-shell">
    <div class="article-card">
      <header class="article-header">
        <div class="badges">
          <span class="badge">{html.escape(p['category'])}</span>
          {f'<span class="badge series">{html.escape(p["series"])}</span>' if p["series"] else ''}
        </div>
        <h1>{html.escape(p['title'])}</h1>
        <div class="post-meta">
          <span>{html.escape(p['date'])}</span>
          <span>{p['minutes']} 分钟</span>
          <span>{p['words']} 字</span>
          <span>阅读 <b id="stat-page-pv" data-key="{html.escape(p["slug"])}">…</b></span>
        </div>
      </header>
      {ser_html}
      <div class="article-body">{p['html']}</div>
      <div class="article-foot">
        <div class="post-tags">{tags}</div>
        <p class="copyright">© {datetime.now().year} {html.escape(SITE_NAME)} · 转载请注明出处</p>
      </div>
    </div>
    {f'<section class="card pad"><h3 class="side-title">相关文章</h3><ul class="arch-list">{rel_html}</ul></section>' if rel_html else ''}
    {giscus_html()}
  </article>
  <aside class="side-col">{toc}</aside>
</div>"""
        _write(
            DIST / "posts" / f"{p['slug']}.html",
            page(p["title"], body, prefix="../", active="主页", desc=p["summary"], hero=False),
            prefix="../",
        )

    # RSS
    items = []
    for p in posts[:20]:
        items.append(
            f"""<item>
  <title>{xesc(p['title'])}</title>
  <link>{SITE_URL}/posts/{p['slug']}.html</link>
  <guid>{SITE_URL}/posts/{p['slug']}.html</guid>
  <pubDate>{p['date']}</pubDate>
  <description>{xesc(p['summary'])}</description>
</item>"""
        )
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
<title>{xesc(SITE_NAME)}</title>
<link>{SITE_URL}</link>
<description>{xesc(SITE_DESC)}</description>
<language>zh-cn</language>
{''.join(items)}
</channel></rss>
"""
    (DIST / "feed.xml").write_text(feed, encoding="utf-8")

    # sitemap
    urls = ["", "about.html", "archive.html", "categories.html", "tags.html", "projects.html"]
    urls += [f"posts/{p['slug']}.html" for p in posts]
    sm = ["<?xml version=\"1.0\" encoding=\"UTF-8\"?>", '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append(f"<url><loc>{SITE_URL}/{u}</loc></url>")
    sm.append("</urlset>")
    (DIST / "sitemap.xml").write_text("\n".join(sm), encoding="utf-8")

    # robots
    (DIST / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8"
    )

    # 自定义域名
    (DIST / "CNAME").write_text("zixuann.top\n", encoding="utf-8")

    # 预览副本到会话目录（勿写回源码根目录）
    if PREVIEW_DIR.resolve() != ROOT.resolve():
        for item in DIST.iterdir():
            dest = PREVIEW_DIR / item.name
            if item.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)

    print(f"构建完成：{len(posts)} 篇 → {DIST}")
    print(f"预览入口：{PREVIEW_DIR / 'index.html'}")


def _write(path: Path, html_text: str, *, prefix: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # page() 已经直接写好 prefix 路径
    path.write_text(html_text, encoding="utf-8")


if __name__ == "__main__":
    build()
