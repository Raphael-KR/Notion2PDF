# Table and column layout correction

- Goal: keep short table labels readable and multi-column content inside the page body.
- Scope: Notion HTML table classification and the Notion print stylesheet.
- Completion: regenerate the requested document; inspect every page, table label wrapping, column boundaries, and text preservation.
- Exclusions: Notion source edits, GUI changes, publication, and blanket column-width overrides.
- Validation: existing document data, WeasyPrint layout bounds, extracted PDF text, and rendered page images.

## Rules

Keep automatic table layout. Add `label-value-table` only when every row has two cells, all body labels are nonempty and at most 12 characters without line breaks, and total body value length exceeds twice the total label length. Header content is excluded from length classification. This is a conservative heuristic, not recovery of Notion's original column widths. Give those first-column cells a 6em minimum; allow wrapping for longer labels.

Keep fixed table layout for multi-column blocks, with a 100% container, automatic cell widths, zero border spacing, and 7pt inner padding on each side of adjacent columns. Outer edges have no padding. Do not expand the container or hide overflow.

Prefer keeping each multi-column group on one page (`break-inside: avoid`), so short side-by-side comparisons are not split at a page boundary. Groups taller than a page still require renderer fragmentation.

Generated documents and private source snapshots remain in ignored output/tmp folders.

## Verification result (2026-10-19)

The requested page was fetched again through the configured ntn client and rendered with WeasyPrint 67.0. The result is 19 A4 pages. The first table's label column is 101 CSS pixels instead of approximately 60. The right column ends at the body boundary (725.67 CSS pixels), with zero horizontal overrun. The complete two-column comparison stays on page 5. Both two-column tables receive the label rule; the three-column table keeps automatic sizing.

All 19 final page images were inspected. Text boxes stay within the body bounds; no blank pages were detected. Source HTML is identical to the previous renderer apart from the new table class. PDF text was compared using both physical and reading-order extraction because multi-column tables can interleave text in one extraction mode. No HTML text segments were missing. Pretendard Regular, SemiBold and Bold are embedded.

Long code blocks continue across pages. Some bold paragraphs used as informal subheadings remain separated from their following code block at page boundaries; this is an existing pagination limitation outside the table/column correction. Exact Notion UI column widths and arbitrary documents with more than two layout columns are not covered by this document's validation.

Local evidence: `tmp/layout-fix-report.json`, `tmp/pdfs/layout-fixed/`, and `output/pdf/2026-ai-layout-fixed.pdf`. The installed app uses this project's Python/CSS files, so these changes apply on its next conversion without reinstalling the bundle.
