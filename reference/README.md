# Notion Export CSS Reference

`notion-export.css` is the CSS extracted from a Notion GUI HTML export of the
same sample page. Treat it as a visual reference, not as a stylesheet to import
directly.

## Workflow

1. Check `reference/notion-export.css` before adjusting Notion-like output.
2. Copy only the relevant values into `styles/notion.css`.
3. Translate Notion export class names to the renderer's class names.
4. Regenerate the sample HTML/PDF and compare visually.

## Class Mapping

| Notion export CSS | Notion2PDF renderer |
| --- | --- |
| `.block-color-*_background` | `.notion-color-*_background` |
| `.block-color-*` | `.notion-color-*` |
| `.table_of_contents-*` | `.toc`, `.toc-list`, `.toc-level-*` |
| `.column-list`, `.column` | `.column-list`, `.column` |
| `.callout` | `.callout`, `.callout-main`, `.callout-icon`, `.callout-content` |
| `.code`, `.code-wrap` | `pre.notion-code`, `pre.notion-code code` |
| `blockquote` | `blockquote` |
| `.simple-table` | `table`, `th`, `td` |
| `ul`, `ol`, `.bulleted-list`, `.numbered-list` | `ul:not(.toc-list):not(.checklist)`, `ol:not(.toc-list)` |
| `.to-do-list` | `.checklist` |

## Notes

- Do not import this file in production rendering. It contains export-specific
  selectors, browser-only rules, and fonts that are not bundled with Notion2PDF.
- Keep `styles/notion.css` as the source of truth for PDF output.
- Preserve the local font strategy in `styles/notion.css` so Korean text remains
  embedded correctly in generated PDFs.
