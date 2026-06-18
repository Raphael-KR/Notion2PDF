# Notion2PDF

Notion 페이지와 정적 HTML/CSS를 인쇄 품질 PDF로 변환하는 로컬 CLI/App 도구입니다. WeasyPrint를 사용해 A4 PDF를 만들고, Notion API JSON의 블록 색상, 목차, 다단, 표, 체크리스트 같은 구조를 가능한 한 HTML에 보존한 뒤 PDF로 렌더링합니다.

## 설치

macOS Apple Silicon 기준입니다. Python 패키지는 반드시 프로젝트 로컬 venv에만 설치합니다.

```bash
brew install pango gdk-pixbuf libffi poppler
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 샘플 PDF 생성

```bash
source .venv/bin/activate
python convert.py templates/sample.html output/sample.pdf
```

Notion 페이지처럼 원본에 없는 머리말, 꼬리말, 페이지 번호, 변환 메타 문구를 넣지 않아야 하는 문서는 Notion 프리셋을 사용합니다.

```bash
source .venv/bin/activate
python convert.py templates/sample.html output/sample-notion.pdf --preset notion
```

Notion CLI(`ntn`)에 로그인되어 있다면, Notion 페이지를 HTML로 먼저 변환할 수 있습니다.

```bash
ntn login
source .venv/bin/activate
python notion_to_html.py "https://app.notion.com/p/..." templates/notion-page.html
python convert.py templates/notion-page.html output/notion-page.pdf --preset notion
```

Notion 링크를 바로 PDF로 변환할 수도 있습니다.

```bash
source .venv/bin/activate
python notion_to_pdf.py "https://app.notion.com/p/..." output/notion-page.pdf
```

중간 HTML을 함께 보관하려면:

```bash
python notion_to_pdf.py "https://app.notion.com/p/..." output/notion-page.pdf --html-output templates/notion-page.html
```

## macOS 앱

Notion 링크를 PDF로 변환하는 얇은 macOS 앱 번들이 포함되어 있습니다.

```bash
chmod +x scripts/build_macos_app.sh
./scripts/build_macos_app.sh
open dist/Notion2PDF.app
```

앱을 더블클릭하면 Notion 링크와 PDF 저장 위치를 묻습니다. 내부적으로는 `ntn` 인증과 `notion_to_pdf.py`를 사용합니다.
첫 화면에서 중간 HTML 저장 여부를 선택할 수 있습니다. 저장을 켜면 PDF와 같은 폴더에 같은 파일명 `.html`로 함께 저장됩니다.
PDF 저장 대화상자의 기본 파일명은 Notion 페이지 제목을 자동으로 사용합니다.
실패하면 `tmp/macos-app-YYYYMMDD-HHMMSS.log`와 `tmp/macos-app.latest.log`를 확인하세요.

CI처럼 `ntn` keychain 로그인 대신 API 토큰을 직접 써야 하는 환경에서는 `--client api`를 사용할 수 있습니다.

```bash
export NOTION_TOKEN="secret_xxx"
python notion_to_html.py "https://app.notion.com/p/..." templates/notion-page.html --client api
```

inline HTML 문자열도 변환할 수 있습니다.

```bash
source .venv/bin/activate
python convert.py --html-string '<h1>안녕하세요</h1><p>정적 HTML 문자열입니다.</p>' output/inline.pdf
```

## 프로젝트 구조

```text
.
├── convert.py
├── dist/
│   └── Notion2PDF.app
├── notion_to_html.py
├── notion_to_pdf.py
├── requirements.txt
├── README.md
├── styles/
│   ├── print.css
│   └── notion.css
├── templates/
│   └── sample.html
├── fonts/
│   ├── Pretendard-Regular.woff2
│   └── Pretendard-Bold.woff2
└── output/
    └── sample.pdf
```

## CSS 핵심

- `@page size: A4`와 margin box로 머리말과 꼬리말을 출력합니다.
- `counter(page) " / " counter(pages)`로 하단 중앙에 페이지 번호를 표시합니다.
- `thead { display: table-header-group; }`로 페이지가 넘어간 표의 헤더 행을 반복합니다.
- `.page-break { break-before: page; }`와 `.avoid-break { break-inside: avoid; }`로 페이지 나눔을 제어합니다.
- `@font-face`로 `fonts/` 안의 Pretendard 파일을 불러와 한글 폰트를 PDF에 임베딩합니다.
- `styles/notion.css`는 같은 본문 스타일을 쓰되 원본에 없는 header/footer/page number를 만들지 않습니다.

## 트러블슈팅

### 한글이 네모로 보이거나 깨질 때

```bash
ls -l fonts/Pretendard-Regular.woff2 fonts/Pretendard-Bold.woff2
```

폰트 파일이 없으면 다시 내려받고, `styles/print.css`의 `@font-face` 경로가 맞는지 확인합니다.

### Fontconfig cache 경고가 보일 때

`convert.py`는 기본적으로 `tmp/fontconfig` 아래에 Fontconfig 캐시를 만들도록 `XDG_CACHE_HOME`을 설정합니다. 직접 WeasyPrint를 호출하는 스크립트에서는 아래처럼 프로젝트 내부 캐시 경로를 먼저 지정하세요.

```bash
export XDG_CACHE_HOME="$PWD/tmp"
```

### pango 또는 gobject 관련 오류가 날 때

```bash
brew install pango gdk-pixbuf libffi
brew --prefix
```

Apple Silicon Homebrew의 기본 경로는 보통 `/opt/homebrew`입니다. 터미널을 새로 열거나 셸 설정에 Homebrew PATH가 반영되어 있는지 확인하세요.

### PDF 검증 도구가 없을 때

```bash
brew install poppler
pdfinfo output/sample.pdf
pdftoppm -png output/sample.pdf tmp/pdfs/sample
```

`pdfinfo`와 `pdftoppm`은 PDF 페이지 수와 렌더링 결과를 점검할 때 사용합니다.

### JavaScript로 만든 내용이 PDF에 안 나올 때

WeasyPrint는 JavaScript를 실행하지 않습니다. 변환 전에 데이터를 HTML에 반영하거나, 차트와 동적 요소를 정적 PNG/SVG로 저장해 포함하세요.
