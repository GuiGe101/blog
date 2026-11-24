from __future__ import annotations

import html
import re
from dataclasses import dataclass, field

CJK = r"\u3400-\u4dbf\u4e00-\u9fff\u3000-\u303f\uff00-\uffef"
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
ORDERED_RE = re.compile(r"^\d+\.\s+")
UNORDERED_RE = re.compile(r"^[-*+]\s+")
RULE_RE = re.compile(r"^(?:-{3,}|\*{3,}|_{3,})\s*$")
TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?[\s:|-]+\|?\s*$")


@dataclass(frozen=True)
class Heading:
    level: int
    anchor: str
    title: str


@dataclass
class RenderedMarkdown:
    html: str
    headings: list[Heading] = field(default_factory=list)


def split_tags(tags: str) -> list[str]:
    return [tag.strip() for tag in re.split(r"[,，、/|]", tags or "") if tag.strip()]


def word_count(markdown: str) -> int:
    return len(re.sub(r"\s", "", markdown))


def reading_minutes(words: int) -> int:
    return max(1, round(words / 400))


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    meta: dict[str, str] = {}
    body = text
    if text.startswith("---"):
        match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?", text, re.S)
        if match:
            for line in match.group(1).splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    meta[key.strip()] = value.strip().strip("\"'")
            body = text[match.end() :]
    return meta, body


def plain_text(fragment: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", fragment)).strip()


def slugify(title: str) -> str:
    slug = re.sub(r"[^\w\u3400-\u9fff\u3000-\u303f-]+", "-", title, flags=re.UNICODE)
    return slug.strip("-").lower() or "section"


def join_soft_lines(lines: list[str]) -> str:
    text = " ".join(line.strip() for line in lines)
    return re.sub(rf"(?<=[{CJK}]) +(?=[{CJK}])", "", text)


class MarkdownRenderer:
    def __init__(self, image_prefix: str = "") -> None:
        self.image_prefix = image_prefix

    def render(self, source: str) -> RenderedMarkdown:
        lines = source.replace("\r\n", "\n").split("\n")
        blocks: list[str] = []
        headings: list[Heading] = []
        used_anchors: dict[str, int] = {}
        i = 0

        while i < len(lines):
            line = lines[i]

            if line.strip().startswith("```"):
                language = line.strip()[3:].strip()
                i += 1
                code: list[str] = []
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    code.append(lines[i])
                    i += 1
                i += 1
                class_attr = f' class="language-{html.escape(language)}"' if language else ""
                blocks.append(
                    '<div class="code-block"><pre><code'
                    f"{class_attr}>{html.escape(chr(10).join(code))}</code></pre>"
                    '<button class="code-copy" type="button" aria-label="复制代码">复制</button></div>'
                )
                continue

            heading = HEADING_RE.match(line)
            if heading:
                level = len(heading.group(1))
                title_html = self.inline(heading.group(2).strip())
                title = plain_text(title_html)
                base = slugify(title)
                count = used_anchors.get(base, 0)
                used_anchors[base] = count + 1
                anchor = base if count == 0 else f"{base}-{count + 1}"
                if level in (2, 3):
                    headings.append(Heading(level, anchor, title))
                link = (
                    f'<a class="heading-link" href="#{anchor}" '
                    f'aria-label="链接到 {html.escape(title, quote=True)}">#</a>'
                )
                blocks.append(f'<h{level} id="{anchor}">{title_html}{link}</h{level}>')
                i += 1
                continue

            if self._is_table(lines, i):
                table, i = self._render_table(lines, i)
                blocks.append(table)
                continue

            if line.startswith(">"):
                quote_lines: list[str] = []
                while i < len(lines) and lines[i].startswith(">"):
                    quote_lines.append(lines[i].lstrip(">").strip())
                    i += 1
                quote = join_soft_lines(quote_lines)
                blocks.append(f"<blockquote><p>{self.inline(quote)}</p></blockquote>")
                continue

            if UNORDERED_RE.match(line) or ORDERED_RE.match(line):
                ordered = bool(ORDERED_RE.match(line))
                item_re = ORDERED_RE if ordered else UNORDERED_RE
                items: list[str] = []
                while i < len(lines) and item_re.match(lines[i]):
                    item = item_re.sub("", lines[i], count=1)
                    items.append(f"<li>{self.inline(item)}</li>")
                    i += 1
                tag = "ol" if ordered else "ul"
                blocks.append(f"<{tag}>{''.join(items)}</{tag}>")
                continue

            if RULE_RE.match(line):
                blocks.append('<hr class="section-rule">')
                i += 1
                continue

            if not line.strip():
                i += 1
                continue

            paragraph: list[str] = []
            while i < len(lines) and lines[i].strip():
                if paragraph and self._starts_block(lines, i):
                    break
                paragraph.append(lines[i])
                i += 1
            blocks.append(f"<p>{self.inline(join_soft_lines(paragraph))}</p>")

        return RenderedMarkdown("\n".join(blocks), headings)

    def inline(self, text: str) -> str:
        code_tokens: list[str] = []

        def protect_code(match: re.Match[str]) -> str:
            code_tokens.append(f"<code>{match.group(1)}</code>")
            return f"\x00CODE{len(code_tokens) - 1}\x00"

        text = html.escape(text, quote=False)
        text = re.sub(r"`([^`]+)`", protect_code, text)

        def image(match: re.Match[str]) -> str:
            alt, src = match.groups()
            if not re.match(r"^(?:[a-z][a-z0-9+.-]*:|//|/|#)", src, re.I):
                src = self.image_prefix + src
            return (
                f'<img loading="lazy" decoding="async" alt="{alt}" '
                f'src="{html.escape(src, quote=True)}">'
            )

        text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", image, text)
        text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
        text = re.sub(
            r"&lt;(https?://[^&<\s]+)&gt;",
            r'<a href="\1" rel="noopener">\1</a>',
            text,
        )
        text = re.sub(r"~~([^~]+)~~", r"<del>\1</del>", text)
        text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
        text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)

        for index, code in enumerate(code_tokens):
            text = text.replace(f"\x00CODE{index}\x00", code)
        return text

    def _starts_block(self, lines: list[str], index: int) -> bool:
        line = lines[index]
        return bool(
            HEADING_RE.match(line)
            or line.strip().startswith("```")
            or line.startswith(">")
            or UNORDERED_RE.match(line)
            or ORDERED_RE.match(line)
            or RULE_RE.match(line)
            or self._is_table(lines, index)
        )

    def _is_table(self, lines: list[str], index: int) -> bool:
        if index + 1 >= len(lines) or "|" not in lines[index]:
            return False
        separator = lines[index + 1].strip()
        return bool(
            "|" in separator
            and TABLE_SEPARATOR_RE.match(separator)
            and "-" in separator
        )

    def _render_table(self, lines: list[str], index: int) -> tuple[str, int]:
        headers = self._table_cells(lines[index])
        separators = self._table_cells(lines[index + 1])
        aligns: list[str] = []
        for separator in separators:
            left, right = separator.startswith(":"), separator.endswith(":")
            aligns.append("center" if left and right else "right" if right else "left")

        rows: list[str] = []
        i = index + 2
        while i < len(lines) and "|" in lines[i] and lines[i].strip():
            cells = self._table_cells(lines[i])
            values = []
            for column, cell in enumerate(cells):
                align = aligns[column] if column < len(aligns) else "left"
                values.append(f'<td class="align-{align}">{self.inline(cell)}</td>')
            rows.append(f"<tr>{''.join(values)}</tr>")
            i += 1

        head = "".join(
            f'<th scope="col" class="align-{aligns[column] if column < len(aligns) else "left"}">'
            f"{self.inline(cell)}</th>"
            for column, cell in enumerate(headers)
        )
        return (
            '<div class="table-wrap"><table><thead><tr>'
            f"{head}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>",
            i,
        )

    @staticmethod
    def _table_cells(line: str) -> list[str]:
        return [cell.strip() for cell in line.strip().strip("|").split("|")]