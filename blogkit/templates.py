from __future__ import annotations

import html
from datetime import date

from .config import (
    AUTHOR,
    COUNT_NS,
    GISCUS,
    NAV,
    SITE_BIO,
    SITE_DESC,
    SITE_NAME,
    SITE_SUB,
    SITE_TITLE,
    SITE_URL,
    START_DATE,
    WALINE_SERVER,
)
from .content import Post, SiteStats, by_category, by_tag, by_year, related_posts

e = html.escape


def icon(name: str) -> str:
    icons = {
        "search": '<circle cx="11" cy="11" r="6.5"/><path d="m16 16 4.5 4.5"/>',
        "menu": '<path d="M4 8h16M4 16h16"/>',
        "close": '<path d="m6 6 12 12M18 6 6 18"/>',
        "sun": (
            '<circle cx="12" cy="12" r="4"/>'
            '<path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2'
            'M5.3 5.3l1.4 1.4M17.3 17.3l1.4 1.4M18.7 5.3l-1.4 1.4M6.7 17.3l-1.4 1.4"/>'
        ),
        "moon": '<path d="M20 14.2A8.3 8.3 0 0 1 9.8 4 8.5 8.5 0 1 0 20 14.2Z"/>',
        "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
        "up-right": '<path d="M7 17 17 7M8 7h9v9"/>',
    }
    return (
        '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true" fill="none" '
        f'stroke="currentColor" stroke-width="1.7" stroke-linecap="round" '
        f'stroke-linejoin="round">{icons[name]}</svg>'
    )


def nav_links(prefix: str, active: str) -> str:
    links = []
    for label, href, key in NAV:
        current = ' class="is-active" aria-current="page"' if key == active else ""
        links.append(f'<a href="{prefix}{href}"{current}>{label}</a>')
    return "".join(links)


def shell(
    title: str,
    body: str,
    *,
    prefix: str = "",
    active: str = "",
    description: str = "",
    canonical: str = "",
    og_image: str = "",
    page_key: str = "",
    body_class: str = "",
) -> str:
    page_title = SITE_TITLE if title == SITE_TITLE else f"{title} · {SITE_NAME}"
    description = description or SITE_DESC
    canonical_url = f"{SITE_URL}/{canonical.lstrip('/')}" if canonical else f"{SITE_URL}/"
    og_path = og_image or "assets/valorant/hero-jett.jpg"
    og_url = og_path if og_path.startswith("http") else f"{SITE_URL}/{og_path.lstrip('../')}"
    year = date.today().year
    page_attr = f' data-page-key="{e(page_key)}"' if page_key else ""

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(page_title)}</title>
<meta name="description" content="{e(description)}">
<meta name="author" content="{AUTHOR}">
<meta name="theme-color" content="#f1ede4">
<link rel="canonical" href="{e(canonical_url)}">
<meta property="og:title" content="{e(page_title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{e(canonical_url)}">
<meta property="og:image" content="{e(og_url)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" title="{e(SITE_NAME)}" href="{prefix}feed.xml">
<link rel="icon" href="{prefix}assets/avatar.jpg" type="image/jpeg">
<link rel="preload" href="{prefix}assets/fonts/lxgw-wenkai-regular.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{prefix}assets/fonts/fonts.css">
<link rel="stylesheet" href="{prefix}assets/style.css">
<script>
document.documentElement.classList.add('js');
try {{ if (localStorage.getItem('theme') === 'dark') document.documentElement.classList.add('dark'); }} catch (e) {{}}
if (!matchMedia('(prefers-reduced-motion: reduce)').matches) {{
  document.documentElement.classList.add('motion-ready');
  setTimeout(function () {{
    if (!document.documentElement.classList.contains('motion-loaded')) {{
      document.documentElement.classList.remove('motion-ready');
    }}
  }}, 3500);
}}
</script>
<script type="speculationrules">
{{"prerender":[{{"where":{{"href_matches":"/*"}},"eagerness":"moderate"}}]}}
</script>
</head>
<body class="{body_class}" data-count-ns="{COUNT_NS}"{page_attr}>
<a class="skip-link" href="#main">跳到正文</a>
<div class="progress" id="progress" aria-hidden="true"></div>
<header class="site-header" id="site-header">
  <a class="brand" href="{prefix}index.html" aria-label="{e(SITE_NAME)}首页">
    <img src="{prefix}assets/avatar.jpg" alt="" width="40" height="40">
    <span class="brand-copy"><strong>{e(SITE_NAME)}</strong><small>GUI_GE / FIELD NOTES</small></span>
  </a>
  <nav class="desktop-nav" aria-label="主导航">{nav_links(prefix, active)}</nav>
  <div class="header-actions">
    <button class="header-button search-trigger" id="search-open" type="button" aria-label="搜索文章" aria-haspopup="dialog">
      {icon("search")}<span>搜索</span><kbd>Ctrl K</kbd>
    </button>
    <button class="icon-button theme-toggle" id="theme-toggle" type="button" aria-label="切换明暗主题">
      <span class="theme-icon sun">{icon("sun")}</span>
      <span class="theme-icon moon">{icon("moon")}</span>
    </button>
    <button class="icon-button menu-toggle" id="menu-toggle" type="button" aria-label="打开菜单" aria-expanded="false" aria-controls="mobile-nav">
      <span class="menu-open">{icon("menu")}</span><span class="menu-close">{icon("close")}</span>
    </button>
  </div>
</header>
<nav class="mobile-nav" id="mobile-nav" aria-label="移动端导航" hidden>
  {nav_links(prefix, active)}
  <a href="{prefix}feed.xml" class="mobile-nav-extra">RSS 订阅 {icon("up-right")}</a>
</nav>
{body}
<footer class="site-footer">
  <div class="footer-top">
    <div>
      <a class="footer-brand" href="{prefix}index.html">{e(SITE_NAME)}的大窝</a>
      <p>{e(SITE_SUB)}</p>
    </div>
    <nav class="footer-links" aria-label="页脚导航">
      <a href="{prefix}archive.html">归档</a>
      <a href="{prefix}projects.html">项目</a>
      <a href="{prefix}about.html">关于</a>
      <a href="{prefix}feed.xml">RSS</a>
    </nav>
  </div>
  <div class="footer-bottom">
    <span>© {year} {e(SITE_NAME)} · 本站内容未经许可请勿转载</span>
    <span class="footer-stats">
      <span>访客 <b data-stat="uv">—</b></span>
      <span>浏览 <b data-stat="pv">—</b></span>
    </span>
  </div>
  <div class="footer-mega" aria-hidden="true">{e(SITE_NAME)}的大窝</div>
</footer>
<div class="search-shell" id="search-modal" hidden>
  <button class="search-backdrop" type="button" data-search-close aria-label="关闭搜索"></button>
  <section class="command" role="dialog" aria-modal="true" aria-labelledby="search-title">
    <header class="command-head">
      <div><span class="command-kicker">SEARCH / 全站检索</span><h2 id="search-title">找一段记录</h2></div>
      <button class="icon-button" type="button" data-search-close aria-label="关闭搜索">{icon("close")}</button>
    </header>
    <label class="sr-only" for="search-input">搜索标题、摘要、标签</label>
    <input id="search-input" type="search" placeholder="标题、摘要、标签…" autocomplete="off" spellcheck="false">
    <div class="search-results" id="search-results" role="listbox" aria-label="搜索结果"></div>
    <footer class="command-foot"><span>↑ ↓ 选择</span><span>Enter 打开</span><span>Esc 关闭</span></footer>
  </section>
</div>
<script src="{prefix}assets/app.js" defer></script>
</body>
</html>
"""


def hero(posts: list[Post], stats: SiteStats) -> str:
    latest = posts[0] if posts else None
    latest_link = (
        f'<a class="button button-primary" href="posts/{e(latest.slug)}.html">'
        f'读最新一篇 {icon("arrow")}</a>'
        if latest
        else ""
    )
    return f"""
<section class="home-hero" aria-labelledby="home-title">
  <div class="hero-canvas" aria-hidden="true">
    <div class="hero-stage-card"><img src="assets/valorant/hero-a2.jpg" alt="" fetchpriority="high"><span class="stage-label">SUNSET / ALLEY — FIELD NOTES</span></div>
    <div class="hero-grade"></div>
    <div class="hero-gridlines"></div>
    <div class="hero-wordmark">归舸</div>
    <div class="hero-scan"></div>
    <span class="hero-tick tl"></span><span class="hero-tick tr"></span>
    <span class="hero-tick bl"></span><span class="hero-tick br"></span>
    <div class="hero-hud">
      <span class="hud-rec"><i></i>REC</span>
      <span>ZIXUANN.TOP</span>
      <span class="hud-time" data-clock>--:--:--</span>
      <span class="hud-frame">SCENE 01 / 05</span>
    </div>
  </div>
  <div class="hero-grid">
    <div class="hero-copy">
      <p class="eyebrow"><span>PERSONAL FIELD NOTES</span><span>EST. 2026</span></p>
      <h1 id="home-title" class="hero-title">
        <span class="sr-only">归舸的大窝</span>
        <span class="hero-title-visual" aria-hidden="true" data-split>归舸的<span class="hero-title-accent">大窝</span></span>
      </h1>
      <p class="hero-deck">{e(SITE_SUB)}。<br>技术、游戏、生活，和还没想明白的事，都先放在这里。</p>
      <div class="hero-actions">
        {latest_link}
        <a class="text-link" href="about.html">先认识一下 {icon("up-right")}</a>
      </div>
      <dl class="hero-figures">
        <div><dt>记录</dt><dd data-count="{stats.posts}">{stats.posts:02d}</dd></div>
        <div><dt>分类</dt><dd data-count="{stats.categories}">{stats.categories:02d}</dd></div>
        <div><dt>始于</dt><dd>2026.10</dd></div>
      </dl>
    </div>
    <figure class="hero-portrait">
      <span class="portrait-ring" aria-hidden="true"></span>
      <div class="portrait-frame">
        <img src="assets/avatar.jpg" alt="归舸的头像" width="640" height="640">
        <span class="portrait-stamp">GUI_GE</span>
      </div>
      <figcaption>
        <span><b>{e(SITE_NAME)}</b> / 16</span>
        <span>VALORANT · CODE · NOTES</span>
      </figcaption>
      <span class="portrait-note" aria-hidden="true">慢慢记</span>
    </figure>
  </div>
  <a class="scroll-cue" href="#journal"><span>往下翻</span><i></i></a>
</section>"""


def lead_story(post: Post) -> str:
    badge = '<span class="label-accent">精选</span>' if post.featured else ""
    return f"""
<article class="lead-story">
  <a class="lead-media" data-tilt href="posts/{e(post.slug)}.html" aria-label="阅读 {e(post.title)}">
    <img src="{e(post.cover)}" alt="" width="1200" height="760" decoding="async">
    <span class="lead-number">NO. {post.date[5:7]}.{post.date[8:10] if len(post.date) > 9 else ""}</span>
  </a>
  <div class="lead-copy">
    <p class="eyebrow">{badge}<span>{e(post.category)}</span><span>{e(post.date)}</span></p>
    <h2><a href="posts/{e(post.slug)}.html">{e(post.title)}</a></h2>
    <p>{e(post.summary)}</p>
    <div class="lead-foot">
      <span>{post.minutes} 分钟 · {post.words} 字</span>
      <a class="round-link" href="posts/{e(post.slug)}.html" aria-label="阅读全文">{icon("arrow")}</a>
    </div>
  </div>
</article>"""


def latest_list(posts: list[Post]) -> str:
    items = "".join(
        f"""<li>
  <a href="posts/{e(post.slug)}.html">
    <span class="latest-index">{index:02d}</span>
    <span class="latest-copy">
      <small>{e(post.date)} · {e(post.category)}</small>
      <strong>{e(post.title)}</strong>
    </span>
    {icon("up-right")}
  </a>
</li>"""
        for index, post in enumerate(posts, start=1)
    )
    return f'<ol class="latest-list">{items}</ol>'


def journal_item(post: Post, index: int) -> str:
    tags = "".join(f"<span>#{e(tag)}</span>" for tag in post.tags)
    return f"""
<article class="journal-item">
  <div class="journal-aside"><span>{index:02d}</span><time datetime="{e(post.date)}">{e(post.date[5:])}</time></div>
  <div class="journal-copy">
    <p class="journal-category">{e(post.category)} · {post.minutes} 分钟</p>
    <h3><a href="posts/{e(post.slug)}.html">{e(post.title)}</a></h3>
    <p class="journal-summary">{e(post.summary)}</p>
    <div class="tag-line">{tags}</div>
  </div>
  <a class="journal-thumb" href="posts/{e(post.slug)}.html" aria-label="阅读 {e(post.title)}">
    <img src="{e(post.cover)}" alt="" loading="lazy" decoding="async">
  </a>
</article>"""


def profile_card(prefix: str = "") -> str:
    return f"""
<section class="rail-card profile-card">
  <div class="profile-head">
    <img src="{prefix}assets/avatar.jpg" alt="归舸的头像" loading="lazy" width="72" height="72">
    <div><span class="rail-label">ABOUT</span><h2>{e(SITE_NAME)}</h2></div>
  </div>
  <p>{e(SITE_BIO)}</p>
  <div class="profile-links"><a href="{prefix}about.html">关于</a><a href="{prefix}projects.html">项目</a><a href="{prefix}feed.xml">RSS</a></div>
</section>"""


def stats_card(stats: SiteStats, prefix: str = "") -> str:
    return f"""
<section class="rail-card">
  <div class="rail-heading"><span class="rail-label">SITE INDEX</span><h2>这一站</h2></div>
  <dl class="stat-grid">
    <div><dt>文章</dt><dd>{stats.posts}</dd></div>
    <div><dt>分类</dt><dd>{stats.categories}</dd></div>
    <div><dt>标签</dt><dd>{stats.tags}</dd></div>
    <div><dt>字数</dt><dd>{stats.words}</dd></div>
    <div><dt>运行</dt><dd><span id="run-days" data-start="{START_DATE}">—</span></dd></div>
    <div><dt>更新</dt><dd>{e(stats.last_activity[5:] if stats.last_activity else "—")}</dd></div>
  </dl>
</section>"""


def tags_card(posts: list[Post], prefix: str = "") -> str:
    groups = by_tag(posts)
    chips = "".join(
        f'<a class="tag-chip" href="{prefix}tags.html#{e(tag)}">#{e(tag)}<sup>{len(items)}</sup></a>'
        for tag, items in list(groups.items())[:12]
    )
    return f'<section class="rail-card"><div class="rail-heading"><span class="rail-label">TAGS</span><h2>常用标签</h2></div><div class="tag-cloud">{chips}</div></section>'


def ticker() -> str:
    terms = ("记录", "技术", "游戏", "生活", "灵感", "未命名", "慢慢记")
    items = "".join(f"<span>{term}</span><i>·</i>" for term in terms)
    return (
        '<div class="motion-ticker" aria-hidden="true">'
        f'<div class="ticker-track">{items}{items}</div>'
        "</div>"
    )


def home_page(posts: list[Post], stats: SiteStats) -> str:
    if not posts:
        return shell(
            "还没有文章",
            '<div class="empty-state"><h1>还没有文章</h1><p>把第一篇 Markdown 放进 posts/ 就会出现在这里。</p></div>',
            active="home",
        )
    lead = posts[0]
    latest = posts[1:4]
    remaining = posts[1:]
    journal = "".join(journal_item(post, index) for index, post in enumerate(remaining, start=2))
    body = f"""
<div class="hero-stage">
  {hero(posts, stats)}
</div>
<main id="main" class="home-main">
  {ticker()}
  <section class="lead-layout">
    {lead_story(lead)}
    <aside class="latest-panel">
      <div class="section-heading"><div><span class="section-kicker">RECENT</span><h2>最近写的</h2></div></div>
      {latest_list(latest)}
    </aside>
  </section>
  <section class="journal-section" id="journal">
    <div class="section-heading wide">
      <div><span class="section-kicker">JOURNAL</span><h2>日志</h2></div>
      <a class="text-link" href="archive.html">全部归档 {icon("arrow")}</a>
    </div>
    <div class="journal-layout">
      <div class="journal-list">{journal}</div>
      <aside class="home-rail">
        {profile_card()}
        {stats_card(stats)}
        {tags_card(posts)}
      </aside>
    </div>
  </section>
</main>"""
    return shell(
        SITE_TITLE,
        body,
        active="home",
        description=SITE_DESC,
        canonical="",
    )


def collection_head(kicker: str, title: str, description: str, meta: str = "") -> str:
    return f"""
<header class="collection-head">
  <p class="eyebrow"><span>{e(kicker)}</span><span>{e(meta)}</span></p>
  <h1><span class="sr-only">{e(title)}</span><span aria-hidden="true" data-split>{e(title)}</span></h1>
  <p>{e(description)}</p>
</header>"""


def archive_page(posts: list[Post], stats: SiteStats) -> str:
    sections = []
    for year, items in by_year(posts).items():
        rows = "".join(
            f"""<li>
  <time datetime="{e(post.date)}">{e(post.date[5:])}</time>
  <a href="posts/{e(post.slug)}.html">{e(post.title)}</a>
  <span>{e(post.category)}</span>
</li>"""
            for post in items
        )
        sections.append(
            f'<section class="archive-year"><h2>{e(year)}<sup>{len(items):02d}</sup></h2><ol>{rows}</ol></section>'
        )
    body = f"""
<main id="main" class="page-wrap">
  {collection_head("ARCHIVE / 索引", "全部记录", "按时间往回翻。长文、短记和没头没尾的想法都在这里。", f"{stats.posts:02d} ENTRIES")}
  <div class="archive-list">{''.join(sections)}</div>
</main>"""
    return shell("归档", body, active="archive", canonical="archive.html", description="归舸的大窝全部文章归档。")


def categories_page(posts: list[Post]) -> str:
    groups = by_category(posts)
    chips = "".join(
        f'<a class="tag-chip" href="#{e(name)}">{e(name)}<sup>{len(items)}</sup></a>'
        for name, items in groups.items()
    )
    sections = "".join(
        f"""<section class="taxonomy-group" id="{e(name)}">
  <header><span class="section-kicker">CATEGORY</span><h2>{e(name)}<sup>{len(items):02d}</sup></h2></header>
  <ol class="entry-list">{''.join(f'<li><time>{e(post.date)}</time><a href="posts/{e(post.slug)}.html">{e(post.title)}</a></li>' for post in items)}</ol>
</section>"""
        for name, items in groups.items()
    )
    body = f"""
<main id="main" class="page-wrap">
  {collection_head("CATEGORIES", "分类", "按主题找一个方向。", f"{len(groups):02d} GROUPS")}
  <div class="taxonomy-chips">{chips}</div>
  <div class="taxonomy-list">{sections}</div>
</main>"""
    return shell("分类", body, active="categories", canonical="categories.html", description="按分类浏览归舸的大窝文章。")


def tags_page(posts: list[Post]) -> str:
    groups = by_tag(posts)
    chips = "".join(
        f'<a class="tag-chip" href="#{e(tag)}">#{e(tag)}<sup>{len(items)}</sup></a>'
        for tag, items in groups.items()
    )
    sections = "".join(
        f"""<section class="taxonomy-group" id="{e(tag)}">
  <header><span class="section-kicker">TAG</span><h2>#{e(tag)}<sup>{len(items):02d}</sup></h2></header>
  <ol class="entry-list">{''.join(f'<li><time>{e(post.date)}</time><a href="posts/{e(post.slug)}.html">{e(post.title)}</a></li>' for post in items)}</ol>
</section>"""
        for tag, items in groups.items()
    )
    body = f"""
<main id="main" class="page-wrap">
  {collection_head("TAGS", "标签", "细一点的关键词，偶尔比分类更准确。", f"{len(groups):02d} TAGS")}
  <div class="taxonomy-chips">{chips}</div>
  <div class="taxonomy-list">{sections}</div>
</main>"""
    return shell("标签", body, active="tags", canonical="tags.html", description="按标签浏览归舸的大窝文章。")


def static_page(title: str, kicker: str, description: str, content: str, active: str) -> str:
    body = f"""
<main id="main" class="page-wrap">
  {collection_head(kicker, title, description)}
  <article class="prose page-prose">{content}</article>
</main>"""
    return shell(title, body, active=active, canonical=f"{active}.html", description=description)


def comments() -> str:
    if not WALINE_SERVER:
        return f"""
<section class="comments">
  <div class="section-heading"><div><span class="section-kicker">ECHO</span><h2>回声</h2></div></div>
  <p class="comments-note">欢迎留言、点赞。登录 GitHub 账号即可参与。</p>
  <script src="https://giscus.app/client.js" data-repo="{GISCUS['repo']}" data-repo-id="{GISCUS['repo_id']}" data-category="{GISCUS['category']}" data-category-id="{GISCUS['category_id']}" data-mapping="pathname" data-strict="0" data-reactions-enabled="1" data-emit-metadata="0" data-input-position="bottom" data-theme="preferred_color_scheme" data-lang="zh-CN" crossorigin="anonymous" async></script>
  <p class="comments-fallback" data-comments-fallback hidden>评论服务暂时连不上，稍后刷新再试。</p>
</section>"""
    return f"""
<section class="comments">
  <div class="section-heading"><div><span class="section-kicker">ECHO</span><h2>回声</h2></div></div>
  <p class="comments-note">欢迎留言。昵称和邮箱就能发，邮箱不会公开。</p>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@waline/client@v3/dist/waline.css">
  <div id="waline" class="comments-widget"></div>
  <p class="comments-fallback" data-comments-fallback hidden>评论服务暂时连不上，稍后刷新再试。</p>
  <script type="module">
    import {{ init }} from 'https://cdn.jsdelivr.net/npm/@waline/client@v3/dist/waline.js';
    init({{ el: '#waline', serverURL: '{WALINE_SERVER.rstrip("/")}', lang: 'zh-CN', requiredMeta: ['nick', 'mail'], meta: ['nick', 'mail', 'link'], placeholder: '随便聊聊。', dark: 'html.dark' }});
  </script>
</section>"""


def toc_html(post: Post, mobile: bool = False) -> str:
    if not post.headings:
        return ""
    links = "".join(
        f'<a class="toc-level-{heading.level}" href="#{heading.anchor}">{e(heading.title)}</a>'
        for heading in post.headings
    )
    if mobile:
        return f'<details class="toc-mobile"><summary>本文目录 <span>{len(post.headings):02d}</span></summary><nav>{links}</nav></details>'
    return f'<nav class="toc-nav" aria-label="本文目录">{links}</nav>'


def article_page(post: Post, posts: list[Post]) -> str:
    tags = "".join(
        f'<a href="../tags.html#{e(tag)}">#{e(tag)}</a>' for tag in post.tags
    )
    related = related_posts(post, posts)
    related_html = "".join(
        f"""<a class="related-item" href="{e(item.slug)}.html">
  <span>{e(item.category)} · {e(item.date)}</span>
  <strong>{e(item.title)}</strong>
  {icon("up-right")}
</a>"""
        for item in related
    )
    series_nav = ""
    series_posts = [item for item in posts if post.series and item.series == post.series]
    if len(series_posts) > 1:
        series_posts.sort(key=lambda item: item.series_order)
        index = [item.slug for item in series_posts].index(post.slug)
        previous = series_posts[index - 1] if index > 0 else None
        following = series_posts[index + 1] if index + 1 < len(series_posts) else None
        prev_html = f'<a href="{e(previous.slug)}.html">← {e(previous.title)}</a>' if previous else "<span></span>"
        next_html = f'<a href="{e(following.slug)}.html">{e(following.title)} →</a>' if following else "<span></span>"
        series_nav = (
            f'<nav class="series-nav"><span class="series-name">{e(post.series)} '
            f'{index + 1}/{len(series_posts)}</span>{prev_html}{next_html}</nav>'
        )

    body = f"""
<main id="main" class="article-layout">
  <aside class="article-rail">
    <a class="back-link" href="../archive.html">{icon("arrow")} 返回归档</a>
    <div class="rail-heading"><span class="rail-label">ON THIS PAGE</span><h2>目录</h2></div>
    {toc_html(post)}
    <div class="article-facts">
      <span>{post.words} 字</span><span>{post.minutes} 分钟</span>
      <span>阅读 <b data-page-views>—</b></span>
    </div>
  </aside>
  <article class="article">
    <header class="article-header">
      <p class="eyebrow"><span>{e(post.category)}</span><span>{e(post.date)}</span></p>
      <h1><span class="sr-only">{e(post.title)}</span><span aria-hidden="true" data-split>{e(post.title)}</span></h1>
      <p class="article-deck">{e(post.summary)}</p>
      <div class="article-meta"><span>{e(post.date)}</span><span>{post.words} 字</span><span>{post.minutes} 分钟</span></div>
    </header>
    {toc_html(post, mobile=True)}
    <figure class="article-cover" data-tilt><img src="../{e(post.cover)}" alt="{e(post.title)}" width="1200" height="700" decoding="async"><span class="cover-number" aria-hidden="true">{e(post.date[5:].replace("-", "."))}</span></figure>
    {series_nav}
    <div class="prose article-prose">{post.html}</div>
    <div class="article-end" aria-hidden="true"><span>✦</span></div>
    <footer class="article-footer">
      <div class="tag-line">{tags}</div>
      <p>© {date.today().year} {e(SITE_NAME)} · 转载请注明出处</p>
    </footer>
    <section class="related">
      <div class="section-heading"><div><span class="section-kicker">KEEP READING</span><h2>接着看</h2></div></div>
      <div class="related-grid">{related_html}</div>
    </section>
    {comments()}
  </article>
</main>"""
    return shell(
        post.title,
        body,
        prefix="../",
        active="",
        description=post.summary,
        canonical=post.url,
        og_image=post.cover,
        page_key=post.slug,
        body_class="is-article",
    )


def not_found_page() -> str:
    body = """
<main id="main" class="not-found">
  <p class="eyebrow"><span>404</span><span>OFF THE MAP</span></p>
  <h1><span class="sr-only">这页不在地图上</span><span aria-hidden="true" data-split>这页<br>不在地图上</span></h1>
  <p>链接可能旧了，也可能是我自己写错了。回首页，或者去归档里翻翻。</p>
  <div class="not-found-actions">
    <a class="button button-primary" href="index.html">回首页</a>
    <a class="text-link" href="archive.html">去看归档</a>
  </div>
</main>"""
    return shell("页面不存在", body, active="", canonical="404.html", description="页面不存在。")