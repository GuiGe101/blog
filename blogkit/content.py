from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from .config import POSTS_DIR, ROOT
from .markdown import (
    Heading,
    MarkdownRenderer,
    parse_frontmatter,
    reading_minutes,
    split_tags,
    word_count,
)


@dataclass(frozen=True)
class Post:
    slug: str
    title: str
    date: str
    summary: str
    tags: tuple[str, ...]
    category: str
    cover: str
    featured: bool
    series: str
    series_order: int
    body: str
    html: str
    headings: tuple[Heading, ...]
    words: int
    minutes: int

    @property
    def year(self) -> str:
        return (self.date or "0000")[:4]

    @property
    def url(self) -> str:
        return f"posts/{self.slug}.html"


@dataclass(frozen=True)
class SiteStats:
    posts: int
    categories: int
    tags: int
    words: int
    last_activity: str


def load_posts() -> list[Post]:
    posts: list[Post] = []
    if not POSTS_DIR.exists():
        return posts

    for path in POSTS_DIR.glob("*.md"):
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        tags = tuple(split_tags(meta.get("tags", "")))
        rendered = MarkdownRenderer(image_prefix="../").render(body)
        words = word_count(body)
        posts.append(
            Post(
                slug=path.stem,
                title=meta.get("title", path.stem),
                date=meta.get("date", ""),
                summary=meta.get("summary", ""),
                tags=tags,
                category=meta.get("category", tags[0] if tags else "随笔"),
                cover=meta.get("cover", "assets/valorant/cover-sage.jpg"),
                featured=meta.get("featured", "").lower() in {"1", "true", "yes", "y"},
                series=meta.get("series", ""),
                series_order=int(meta.get("series_order", "0") or 0),
                body=body,
                html=rendered.html,
                headings=tuple(rendered.headings),
                words=words,
                minutes=int(meta.get("minutes", "") or 0) or reading_minutes(words),
            )
        )

    posts.sort(key=lambda post: (post.date, post.slug), reverse=True)
    return posts


def load_page(markdown_name: str, fallback_title: str) -> tuple[str, str]:
    path = ROOT / markdown_name
    if not path.exists():
        return fallback_title, "<p>内容准备中。</p>"
    meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    rendered = MarkdownRenderer().render(body)
    return meta.get("title", fallback_title), rendered.html


def site_stats(posts: list[Post]) -> SiteStats:
    return SiteStats(
        posts=len(posts),
        categories=len({post.category for post in posts}),
        tags=len({tag for post in posts for tag in post.tags}),
        words=sum(post.words for post in posts),
        last_activity=posts[0].date if posts else "",
    )


def by_year(posts: list[Post]) -> dict[str, list[Post]]:
    grouped: dict[str, list[Post]] = defaultdict(list)
    for post in posts:
        grouped[post.year].append(post)
    return dict(sorted(grouped.items(), reverse=True))


def by_category(posts: list[Post]) -> dict[str, list[Post]]:
    grouped: dict[str, list[Post]] = defaultdict(list)
    for post in posts:
        grouped[post.category].append(post)
    return dict(sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])))


def by_tag(posts: list[Post]) -> dict[str, list[Post]]:
    grouped: dict[str, list[Post]] = defaultdict(list)
    for post in posts:
        for tag in post.tags:
            grouped[tag].append(post)
    return dict(sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])))


def related_posts(post: Post, posts: list[Post], limit: int = 3) -> list[Post]:
    def score(candidate: Post) -> tuple[int, str]:
        shared_tags = len(set(candidate.tags) & set(post.tags))
        same_category = 1 if candidate.category == post.category else 0
        return (shared_tags * 2 + same_category, candidate.date)

    candidates = [candidate for candidate in posts if candidate.slug != post.slug]
    return sorted(candidates, key=score, reverse=True)[:limit]