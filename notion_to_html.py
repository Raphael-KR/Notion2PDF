#!/usr/bin/env python3
"""Render a Notion page to static HTML using the official Notion API."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


NOTION_VERSION = "2022-06-28"
PROJECT_ROOT = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch a Notion page and render it as static HTML."
    )
    parser.add_argument("page", help="Notion page URL or page ID.")
    parser.add_argument("output", help="Path where the HTML file will be written.")
    parser.add_argument(
        "--client",
        choices=["ntn", "api"],
        default="ntn",
        help="Use Notion CLI auth (ntn) or direct API token auth. Defaults to ntn.",
    )
    parser.add_argument(
        "--ntn-path",
        default=shutil.which("ntn") or "ntn",
        help="Path to the ntn executable. Defaults to the ntn found on PATH.",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("NOTION_TOKEN"),
        help="Notion API token for --client api. Defaults to NOTION_TOKEN.",
    )
    return parser.parse_args()


def extract_page_id(value: str) -> str:
    compact = value.replace("-", "")
    match = re.search(r"([0-9a-fA-F]{32})", compact)
    if not match:
        raise ValueError("Could not find a 32-character Notion page ID.")
    raw = match.group(1).lower()
    return f"{raw[:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:]}"


class DirectNotionClient:
    def __init__(self, token: str) -> None:
        self.token = token

    def request(self, method: str, path: str, body: dict[str, Any] | None = None) -> Any:
        data = json.dumps(body).encode("utf-8") if body else None
        request = urllib.request.Request(
            f"https://api.notion.com/v1{path}",
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "Notion-Version": NOTION_VERSION,
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Notion API error {error.code}: {detail}") from error

    def page(self, page_id: str) -> dict[str, Any]:
        return self.request("GET", f"/pages/{page_id}")

    def block_children(self, block_id: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        cursor: str | None = None
        while True:
            query = f"?start_cursor={urllib.parse.quote(cursor)}" if cursor else ""
            payload = self.request("GET", f"/blocks/{block_id}/children{query}")
            results.extend(payload.get("results", []))
            cursor = payload.get("next_cursor")
            if not payload.get("has_more") or not cursor:
                return results


class NtnNotionClient:
    def __init__(self, ntn_path: str) -> None:
        self.ntn_path = ntn_path

    def request(self, method: str, path: str, body: dict[str, Any] | None = None) -> Any:
        if method != "GET" or body is not None:
            raise ValueError("The ntn client currently supports GET requests only.")

        command = [self.ntn_path, "api", path.removeprefix("/")]
        process = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )
        if process.returncode != 0:
            raise RuntimeError(process.stderr.strip() or process.stdout.strip())
        return json.loads(process.stdout)

    def page(self, page_id: str) -> dict[str, Any]:
        return self.request("GET", f"/v1/pages/{page_id}")

    def block_children(self, block_id: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        cursor: str | None = None
        while True:
            command = [
                self.ntn_path,
                "api",
                f"v1/blocks/{block_id}/children",
                "page_size==100",
            ]
            if cursor:
                command.append(f"start_cursor=={cursor}")

            process = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
            )
            if process.returncode != 0:
                raise RuntimeError(process.stderr.strip() or process.stdout.strip())

            payload = json.loads(process.stdout)
            results.extend(payload.get("results", []))
            cursor = payload.get("next_cursor")
            if not payload.get("has_more") or not cursor:
                return results


def rich_text(items: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for item in items:
        text = item.get("plain_text", "")
        escaped = html.escape(text)
        href = item.get("href")
        annotations = item.get("annotations", {})

        if annotations.get("code"):
            escaped = f"<code>{escaped}</code>"
        if annotations.get("bold"):
            escaped = f"<strong>{escaped}</strong>"
        if annotations.get("italic"):
            escaped = f"<em>{escaped}</em>"
        if annotations.get("strikethrough"):
            escaped = f"<s>{escaped}</s>"
        if annotations.get("underline"):
            escaped = f"<u>{escaped}</u>"
        color = annotations.get("color")
        if color and color != "default":
            escaped = f'<span class="notion-color-{html.escape(color, quote=True)}">{escaped}</span>'
        if href:
            escaped = f'<a href="{html.escape(href, quote=True)}">{escaped}</a>'
        parts.append(escaped)
    return "".join(parts)


def page_title(page: dict[str, Any]) -> str:
    for prop in page.get("properties", {}).values():
        if prop.get("type") == "title":
            title = rich_text(prop.get("title", []))
            if title:
                return re.sub(r"<[^>]+>", "", title)
    return "Notion Page"


def render_list(items: list[str], ordered: bool = False) -> str:
    tag = "ol" if ordered else "ul"
    return f"<{tag}>\n" + "\n".join(items) + f"\n</{tag}>"


def block_value(block: dict[str, Any]) -> dict[str, Any]:
    return block.get(block.get("type"), {}) or {}


def block_classes(block: dict[str, Any], *extra: str) -> str:
    value = block_value(block)
    classes = ["notion-block", f"notion-{block.get('type', 'unknown')}"]
    classes.extend(name for name in extra if name)
    color = value.get("color")
    if color and color != "default":
        classes.append(f"notion-color-{color}")
    return " ".join(html.escape(name, quote=True) for name in classes)


def data_attrs(block: dict[str, Any]) -> str:
    block_id = html.escape(block.get("id", ""), quote=True)
    return f'data-notion-id="{block_id}"' if block_id else ""


def plain_rich_text(value: dict[str, Any]) -> str:
    return "".join(part.get("plain_text", "") for part in value.get("rich_text", []) or [])


def collect_headings(blocks: list[dict[str, Any]]) -> list[tuple[int, str, str]]:
    headings: list[tuple[int, str, str]] = []
    heading_levels = {
        "heading_1": 1,
        "heading_2": 2,
        "heading_3": 3,
        "heading_4": 4,
    }
    for block in blocks:
        block_type = block.get("type")
        if block_type in heading_levels:
            text = plain_rich_text(block_value(block))
            if text:
                headings.append((heading_levels[block_type], text, block.get("id", "")))
        headings.extend(collect_headings(block.get("children", [])))
    return headings


def render_toc(headings: list[tuple[int, str, str]]) -> str:
    tree: list[dict[str, Any]] = []
    stack: list[tuple[int, list[dict[str, Any]]]] = [(0, tree)]

    for level, content, heading_id in headings:
        if not heading_id:
            continue
        while len(stack) > 1 and level <= stack[-1][0]:
            stack.pop()
        node = {
            "level": level,
            "content": content,
            "heading_id": heading_id,
            "children": [],
        }
        stack[-1][1].append(node)
        stack.append((level, node["children"]))

    def render_nodes(nodes: list[dict[str, Any]], root: bool = False) -> str:
        if not nodes:
            return ""
        list_class = "toc-list toc-root" if root else "toc-list"
        items: list[str] = []
        for node in nodes:
            level = node["level"]
            heading_id = html.escape(node["heading_id"], quote=True)
            content = html.escape(node["content"])
            children = render_nodes(node["children"])
            items.append(
                f'<li class="toc-level-{level}"><a href="#{heading_id}">{content}</a>{children}</li>'
            )
        return f'<ul class="{list_class}">' + "\n".join(items) + "</ul>"

    return render_nodes(tree, root=True)


def hydrate_children(client: Any, blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for block in blocks:
        if block.get("has_children") and "children" not in block:
            block["children"] = client.block_children(block["id"])
        if block.get("children"):
            hydrate_children(client, block["children"])
    return blocks


def render_blocks(
    client: Any,
    blocks: list[dict[str, Any]],
    headings: list[tuple[int, str, str]] | None = None,
) -> str:
    html_blocks: list[str] = []
    pending_bullets: list[str] = []
    pending_numbers: list[str] = []
    headings = headings or collect_headings(blocks)

    def flush_lists() -> None:
        nonlocal pending_bullets, pending_numbers
        if pending_bullets:
            html_blocks.append(render_list(pending_bullets))
            pending_bullets = []
        if pending_numbers:
            html_blocks.append(render_list(pending_numbers, ordered=True))
            pending_numbers = []

    for block in blocks:
        block_type = block.get("type")
        value = block_value(block)

        if block_type == "bulleted_list_item":
            content = rich_text(value.get("rich_text", []))
            children = render_child_blocks(client, block, headings)
            pending_bullets.append(
                f'<li class="{block_classes(block)}" {data_attrs(block)}>{content}{children}</li>'
            )
            continue
        if block_type == "numbered_list_item":
            content = rich_text(value.get("rich_text", []))
            children = render_child_blocks(client, block, headings)
            pending_numbers.append(
                f'<li class="{block_classes(block)}" {data_attrs(block)}>{content}{children}</li>'
            )
            continue

        flush_lists()

        if block_type == "paragraph":
            content = rich_text(value.get("rich_text", []))
            empty_class = " notion-empty" if not content else ""
            html_blocks.append(
                f'<p class="{block_classes(block)}{empty_class}" {data_attrs(block)}>{content}</p>'
            )
        elif block_type in {"heading_1", "heading_2", "heading_3", "heading_4"}:
            level = {"heading_1": 1, "heading_2": 2, "heading_3": 3, "heading_4": 4}[block_type]
            content = rich_text(value.get("rich_text", []))
            heading_id = html.escape(block.get("id", ""), quote=True)
            html_blocks.append(
                f'<h{level} id="{heading_id}" class="{block_classes(block)}">{content}</h{level}>'
            )
        elif block_type == "table_of_contents":
            toc = render_toc(headings)
            if toc:
                html_blocks.append(
                    f'<nav class="{block_classes(block, "toc")}" {data_attrs(block)}>{toc}</nav>'
                )
        elif block_type == "to_do":
            checked = "done" if value.get("checked") else ""
            html_blocks.append(
                f'<ul class="checklist"><li class="{block_classes(block, checked)}" {data_attrs(block)}>{rich_text(value.get("rich_text", []))}</li></ul>'
            )
        elif block_type == "callout":
            icon_value = value.get("icon") or {}
            icon = icon_value.get("emoji", "")
            content = rich_text(value.get("rich_text", []))
            children = render_child_blocks(client, block, headings)
            if icon:
                callout_body = (
                    f'<div class="callout-main"><span class="callout-icon">{html.escape(icon)}</span>'
                    f'<div class="callout-content">{content}{children}</div></div>'
                )
            else:
                callout_body = f'<div class="callout-content">{content}{children}</div>'
            html_blocks.append(
                f'<section class="{block_classes(block, "callout")}" {data_attrs(block)}>{callout_body}</section>'
            )
        elif block_type == "quote":
            html_blocks.append(
                f'<blockquote class="{block_classes(block)}" {data_attrs(block)}>{rich_text(value.get("rich_text", []))}</blockquote>'
            )
        elif block_type == "code":
            code = html.escape("".join(part.get("plain_text", "") for part in value.get("rich_text", [])))
            language = html.escape(value.get("language", "text"))
            html_blocks.append(
                f'<pre class="{block_classes(block)}" {data_attrs(block)}><code class="language-{language}">{code}</code></pre>'
            )
        elif block_type == "divider":
            html_blocks.append(f'<hr class="{block_classes(block)}" {data_attrs(block)}>')
        elif block_type == "child_page":
            title = html.escape(value.get("title", "Untitled"))
            html_blocks.append(
                f'<p class="{block_classes(block, "child-page")}" {data_attrs(block)}>↳ {title}</p>'
            )
        elif block_type == "table":
            html_blocks.append(render_table(client, block))
        elif block_type == "column_list":
            children = render_child_blocks(client, block, headings)
            html_blocks.append(
                f'<div class="{block_classes(block, "column-list")}" {data_attrs(block)}>{children}</div>'
            )
        elif block_type == "column":
            children = render_child_blocks(client, block, headings)
            html_blocks.append(
                f'<div class="{block_classes(block, "column")}" {data_attrs(block)}>{children}</div>'
            )
        elif block.get("has_children"):
            html_blocks.append(render_child_blocks(client, block, headings))

    flush_lists()
    return "\n".join(html_blocks)


def render_child_blocks(
    client: Any,
    block: dict[str, Any],
    headings: list[tuple[int, str, str]] | None = None,
) -> str:
    if not block.get("has_children"):
        return ""
    child_blocks = block.get("children")
    if child_blocks is None:
        child_blocks = client.block_children(block["id"])
    children = render_blocks(client, child_blocks, headings)
    return f"\n<div class=\"children\">{children}</div>" if children else ""


def render_table(client: Any, block: dict[str, Any]) -> str:
    table = block_value(block)
    rows = block.get("children")
    if rows is None:
        rows = client.block_children(block["id"])
    rendered_rows: list[str] = []
    for row_index, row in enumerate(rows):
        cells = row.get("table_row", {}).get("cells", [])
        cell_tag = "th" if table.get("has_column_header") and row_index == 0 else "td"
        rendered_cells = "".join(
            f"<{cell_tag}>{rich_text(cell)}</{cell_tag}>" for cell in cells
        )
        rendered_rows.append(f'<tr class="{block_classes(row)}" {data_attrs(row)}>{rendered_cells}</tr>')
    if table.get("has_column_header") and rendered_rows:
        return (
            f'<table class="{block_classes(block)}" {data_attrs(block)}>\n<thead>\n'
            + rendered_rows[0]
            + "\n</thead>\n<tbody>\n"
            + "\n".join(rendered_rows[1:])
            + "\n</tbody>\n</table>"
        )
    return (
        f'<table class="{block_classes(block)}" {data_attrs(block)}>\n<tbody>\n'
        + "\n".join(rendered_rows)
        + "\n</tbody>\n</table>"
    )


def render_document(title: str, body: str, page_id: str | None = None) -> str:
    page_attr = f' data-notion-page-id="{html.escape(page_id, quote=True)}"' if page_id else ""
    return f"""<!doctype html>
<html lang="ko">
  <head>
    <meta charset="utf-8">
    <title>{html.escape(title)}</title>
  </head>
  <body{page_attr}>
    <h1>{html.escape(title)}</h1>
{body}
  </body>
</html>
"""


def main() -> None:
    args = parse_args()
    page_id = extract_page_id(args.page)
    if args.client == "api":
        if not args.token:
            raise SystemExit("Set NOTION_TOKEN or pass --token when using --client api.")
        client: Any = DirectNotionClient(args.token)
    else:
        client = NtnNotionClient(args.ntn_path)

    page = client.page(page_id)
    blocks = hydrate_children(client, client.block_children(page_id))
    title = page_title(page)

    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        render_document(title, render_blocks(client, blocks), page_id),
        encoding="utf-8",
    )
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
