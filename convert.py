#!/usr/bin/env python3
"""Convert static HTML to a print-ready PDF with WeasyPrint."""

from __future__ import annotations

import argparse
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_STYLESHEET = PROJECT_ROOT / "styles" / "print.css"
PRESET_STYLESHEETS = {
    "print": PROJECT_ROOT / "styles" / "print.css",
    "notion": PROJECT_ROOT / "styles" / "notion.css",
}
FONTCONFIG_CACHE = PROJECT_ROOT / "tmp" / "fontconfig"

# Fontconfig tries to write under the user's home directory by default. Keeping
# the cache in the project avoids permission noise in sandboxed/local runs.
FONTCONFIG_CACHE.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("XDG_CACHE_HOME", str(PROJECT_ROOT / "tmp"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a static HTML file or inline HTML string to PDF."
    )
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "input",
        nargs="?",
        help="Path to the source HTML file.",
    )
    input_group.add_argument(
        "--html-string",
        help="Inline HTML string to render. Useful for generated static HTML.",
    )
    parser.add_argument("output", help="Path where the PDF will be written.")
    parser.add_argument(
        "--preset",
        choices=sorted(PRESET_STYLESHEETS),
        default="print",
        help="Stylesheet preset to use. Defaults to print.",
    )
    parser.add_argument(
        "--stylesheet",
        help="Custom CSS path. Overrides --preset when provided.",
    )
    return parser.parse_args()


def convert_html_to_pdf(
    output_path: Path,
    stylesheet_path: Path,
    input_path: Path | None = None,
    html_string: str | None = None,
) -> None:
    from weasyprint import CSS, HTML

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if html_string is not None:
        html = HTML(string=html_string, base_url=str(PROJECT_ROOT))
    else:
        assert input_path is not None
        html = HTML(filename=str(input_path), base_url=str(input_path.parent))

    html.write_pdf(
        target=str(output_path),
        stylesheets=[CSS(filename=str(stylesheet_path))],
    )


def main() -> None:
    args = parse_args()
    if args.stylesheet:
        stylesheet_path = Path(args.stylesheet).expanduser().resolve()
    else:
        stylesheet_path = PRESET_STYLESHEETS[args.preset].resolve()
    output_path = Path(args.output).expanduser().resolve()
    input_path = Path(args.input).expanduser().resolve() if args.input else None

    convert_html_to_pdf(
        output_path=output_path,
        stylesheet_path=stylesheet_path,
        input_path=input_path,
        html_string=args.html_string,
    )
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
