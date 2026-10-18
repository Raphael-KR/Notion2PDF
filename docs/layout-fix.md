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

Long code blocks continue across pages. At this stage, some bold paragraphs used as informal subheadings remained separated from their following code block at page boundaries (addressed in the follow-up below). Exact Notion UI column widths and arbitrary documents with more than two layout columns are not covered by this document's validation.

Local evidence: `tmp/layout-fix-report.json`, `tmp/pdfs/layout-fixed/`, and `output/pdf/2026-ai-layout-fixed.pdf`. The installed app uses this project's Python/CSS files, so these changes apply on its next conversion without reinstalling the bundle.

## Paragraph-subheading pagination follow-up

- Goal: prevent informal subheadings from being stranded before their content.
- Scope: paragraph classification and the Notion stylesheet; reuse the same hydrated source snapshot for comparison.
- Completion: no separated subheading/content pairs in the requested document; inspect every regenerated page.
- Exclusions: source edits, heading/TOC promotion, keeping entire long code blocks together, Git publication, and GUI work.
- Validation: baseline/current page positions, text preservation, table/column bounds, and all rendered page images.

A paragraph whose trimmed text is 1-80 characters, contains no line break, and has bold annotations on every non-whitespace rich-text run receives `notion-subheading`. It remains a paragraph, preserving its content, appearance, and TOC semantics. Apply `break-after: avoid` and `break-inside: avoid` to keep it with the start of the next block, not with the entire block. Long, partly bold, multiline, and empty paragraphs are excluded. This is a conservative formatting heuristic, not a semantic claim about every bold paragraph.

### Follow-up verification (2026-10-19)

Used the same complete snapshot fetched for the table/column repair (source last edited at 2026-10-18T22:17:00Z), without fetching or modifying Notion again. Compared the current renderer with commit `91af6e7` using the same snapshot and WeasyPrint 67.0. Nineteen of 65 paragraphs receive the new class; 46 are excluded. HTML is byte-identical after removing that class, and all 382 nonempty source rich-text runs are preserved.

Checked 58 real-heading/informal-subheading and following-block pairs. The baseline has five separated pairs; the result has zero. These include a paragraph/link pair as well as paragraph/code pairs. The resulting PDF is 20 A4 pages (previously 19). All 20 rendered pages were visually inspected, including the table split with repeated header on pages 16-17 and the short final references page. No text overflow, missing HTML text segments, or blank pages were found. The first table still has a 101 CSS-pixel label column; both columns still fit on page 5 with the right edge at the body boundary. Pretendard Regular, SemiBold, and Bold remain embedded.

Long code blocks still split across pages intentionally. Keeping labels with their content can increase page count and leave whitespace near page ends. Arbitrary documents, empty spacer blocks between labels and content, and blocks taller than a page are not guaranteed by this document-specific verification.

Local evidence: `tmp/verify_pagination_fix.py`, `tmp/pagination-fix-report.json`, `tmp/pdfs/pagination-fixed/`, and `output/pdf/2026-ai-pagination-fixed.pdf`. The prior PDF is preserved for comparison. No Git publication or app reinstallation was performed for this follow-up.
