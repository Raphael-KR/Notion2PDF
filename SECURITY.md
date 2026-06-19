# Security Policy

Notion2PDF runs locally and converts user-provided Notion pages or HTML files
into HTML/PDF artifacts. Treat inputs and outputs as potentially sensitive.

## Sensitive Data

- Do not commit generated PDFs, generated HTML, logs, or Notion JSON dumps if
  they may contain private page content.
- Do not commit `NOTION_TOKEN`, `ntn` credentials, signed Notion file URLs, or
  copied environment files.
- When sharing bug reports, remove personal page URLs, workspace names,
  access tokens, and private document content.

## Supported Versions

This project is developed against the current `main` branch. Security fixes are
published there first.

## Reporting a Vulnerability

Please open a GitHub issue with a minimal reproduction that avoids private
content. If the issue requires sensitive details, describe the impact and ask
for a private contact path first.

## Dependency Notes

WeasyPrint and its native rendering dependencies are installed locally through
Homebrew and the project virtual environment. Keep Homebrew packages and Python
dependencies updated when processing untrusted HTML.
