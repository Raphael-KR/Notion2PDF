#!/usr/bin/env python3
"""Convert a Notion page URL directly to PDF via static HTML."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from convert import PROJECT_ROOT, PRESET_STYLESHEETS, convert_html_to_pdf
from notion_to_html import (
    DirectNotionClient,
    NtnNotionClient,
    extract_page_id,
    hydrate_children,
    page_title,
    render_blocks,
    render_document,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a Notion page URL or page ID directly to PDF."
    )
    parser.add_argument("page", help="Notion page URL or page ID.")
    parser.add_argument("output", nargs="?", help="Path where the PDF will be written.")
    parser.add_argument(
        "--title-only",
        action="store_true",
        help="Print the Notion page title and exit without writing a PDF.",
    )
    parser.add_argument(
        "--html-output",
        help="Optional path to keep the intermediate HTML file.",
    )
    parser.add_argument(
        "--preset",
        choices=sorted(PRESET_STYLESHEETS),
        default="notion",
        help="Stylesheet preset to use. Defaults to notion.",
    )
    parser.add_argument(
        "--stylesheet",
        help="Custom CSS path. Overrides --preset when provided.",
    )
    parser.add_argument(
        "--client",
        choices=["ntn", "api"],
        default="ntn",
        help="Use Notion CLI auth (ntn) or direct API token auth. Defaults to ntn.",
    )
    parser.add_argument(
        "--ntn-path",
        default="ntn",
        help="Path to the ntn executable. Defaults to ntn on PATH.",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("NOTION_TOKEN"),
        help="Notion API token for --client api. Defaults to NOTION_TOKEN.",
    )
    return parser.parse_args()


def build_client(args: argparse.Namespace) -> DirectNotionClient | NtnNotionClient:
    if args.client == "api":
        if not args.token:
            raise SystemExit("Set NOTION_TOKEN or pass --token when using --client api.")
        return DirectNotionClient(args.token)
    return NtnNotionClient(args.ntn_path)


def main() -> None:
    args = parse_args()
    if not args.title_only and not args.output:
        raise SystemExit("output is required unless --title-only is used.")

    page_id = extract_page_id(args.page)
    client = build_client(args)

    page = client.page(page_id)
    title = page_title(page)
    if args.title_only:
        print(title)
        return

    blocks = hydrate_children(client, client.block_children(page_id))
    html_text = render_document(title, render_blocks(client, blocks), page_id)

    if args.html_output:
        html_path = Path(args.html_output).expanduser().resolve()
    else:
        html_path = PROJECT_ROOT / "tmp" / "notion" / f"{page_id}.html"

    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html_text, encoding="utf-8")

    stylesheet_path = (
        Path(args.stylesheet).expanduser().resolve()
        if args.stylesheet
        else PRESET_STYLESHEETS[args.preset].resolve()
    )
    assert args.output is not None
    output_path = Path(args.output).expanduser().resolve()
    convert_html_to_pdf(
        input_path=html_path,
        output_path=output_path,
        stylesheet_path=stylesheet_path,
    )
    print(f"Wrote {output_path}")
    if args.html_output:
        print(f"Wrote {html_path}")


if __name__ == "__main__":
    main()
