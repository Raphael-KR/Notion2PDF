#!/usr/bin/env python3
"""Dump a Notion page and its block tree to JSON using ntn auth."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from notion_to_html import NtnNotionClient, extract_page_id


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dump Notion page JSON via ntn.")
    parser.add_argument("page", help="Notion page URL or page ID.")
    parser.add_argument("output", help="Path where the JSON dump will be written.")
    parser.add_argument("--ntn-path", default="ntn", help="Path to ntn executable.")
    return parser.parse_args()


def fetch_block_tree(client: NtnNotionClient, block_id: str) -> list[dict[str, Any]]:
    blocks = client.block_children(block_id)
    for block in blocks:
        if block.get("has_children"):
            block["children"] = fetch_block_tree(client, block["id"])
    return blocks


def main() -> None:
    args = parse_args()
    page_id = extract_page_id(args.page)
    client = NtnNotionClient(args.ntn_path)

    payload = {
        "page_id": page_id,
        "page": client.page(page_id),
        "blocks": fetch_block_tree(client, page_id),
    }

    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
