# Third-Party Notices

This project depends on third-party open-source software installed into the
local Python virtual environment from `requirements.txt`.

## WeasyPrint

- Project: WeasyPrint
- Repository: https://github.com/Kozea/WeasyPrint
- Package: https://pypi.org/project/weasyprint/
- License: BSD-3-Clause
- Used as: runtime Python dependency for HTML/CSS to PDF rendering

Notion2PDF does not vendor or modify WeasyPrint source code. It imports the
installed package through Python:

```python
from weasyprint import CSS, HTML
```

If this project is later distributed as a self-contained binary or app bundle
that includes WeasyPrint and its installed dependencies, include the full
license texts for those bundled packages in the distribution materials.
