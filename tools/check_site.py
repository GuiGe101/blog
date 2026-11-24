from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
PAGES = ROOT / "docs"


def local_links(html: str) -> list[str]:
    links = re.findall(r'(?:href|src)=["\']([^"\']+)["\']', html)
    return [
        link
        for link in links
        if not re.match(r"^(?:https?:|mailto:|data:|#)", link)
    ]


def verify_site(site: Path) -> list[str]:
    errors: list[str] = []
    html_files = sorted(site.rglob("*.html"))
    if not html_files:
        return [f"{site}: no HTML files"]

    for page in html_files:
        relative = page.relative_to(site)
        html = page.read_text(encoding="utf-8")
        if len(re.findall(r"<h1[\s>]", html)) != 1:
            errors.append(f"{relative}: expected exactly one h1")
        if not re.search(r'<meta name="description" content="[^"]+"', html):
            errors.append(f"{relative}: missing meta description")
        if 'rel="canonical"' not in html:
            errors.append(f"{relative}: missing canonical URL")
        if 'property="og:image"' not in html:
            errors.append(f"{relative}: missing og:image")
        if re.search(r"<img(?![^>]*\balt=)[^>]*>", html):
            errors.append(f"{relative}: image without alt attribute")
        for link in local_links(html):
            clean = link.split("#", 1)[0].split("?", 1)[0]
            if clean and not (page.parent / clean).resolve().exists():
                errors.append(f"{relative}: broken local reference {link}")

    for required in ("index.html", "archive.html", "categories.html", "tags.html", "projects.html", "about.html", "404.html", "feed.xml", "sitemap.xml", "search-index.json", "CNAME"):
        if not (site / required).exists():
            errors.append(f"{site}: missing {required}")

    try:
        index = json.loads((site / "search-index.json").read_text(encoding="utf-8"))
        if not isinstance(index, list):
            errors.append(f"{site}: search index is not a list")
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"{site}: invalid search index ({error})")

    for feed in ("feed.xml", "sitemap.xml"):
        try:
            ET.parse(site / feed)
        except (OSError, ET.ParseError) as error:
            errors.append(f"{site}: invalid {feed} ({error})")

    return errors


def main() -> int:
    errors = verify_site(DIST)
    if PAGES.exists():
        errors.extend(verify_site(PAGES))
        dist_files = {
            path.relative_to(DIST): path.read_bytes()
            for path in DIST.rglob("*")
            if path.is_file()
        }
        docs_files = {
            path.relative_to(PAGES): path.read_bytes()
            for path in PAGES.rglob("*")
            if path.is_file()
        }
        if dist_files != docs_files:
            errors.append("docs/ mirror differs from dist/")

    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors))
        return 1

    pages = len(list(DIST.rglob("*.html")))
    print(f"OK: {pages} pages, local links, feeds and Pages mirror verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())