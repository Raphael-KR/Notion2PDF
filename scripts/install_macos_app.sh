#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCE="$PROJECT_ROOT/dist/Notion2PDF.app"
DESTINATION="/Applications/Notion2PDF.app"

if [[ ! -x "$PROJECT_ROOT/.venv/bin/python" ]]; then
  echo "Set up the project .venv before installing." >&2
  exit 1
fi

"$SCRIPT_DIR/build_macos_app.sh"
if [[ -e "$DESTINATION" ]]; then
  BACKUP="$PROJECT_ROOT/tmp/app-backups/$(date +%Y%m%d-%H%M%S)-$$/Notion2PDF.app"
  mkdir -p "$(dirname "$BACKUP")"
  /usr/bin/ditto "$DESTINATION" "$BACKUP"
  echo "Previous app preserved: $BACKUP"
fi
/usr/bin/ditto "$SOURCE" "$DESTINATION"
/usr/bin/plutil -replace Notion2PDFProjectRoot -string "$PROJECT_ROOT" "$DESTINATION/Contents/Info.plist"
/usr/bin/plutil -lint "$DESTINATION/Contents/Info.plist"
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$DESTINATION"
"$DESTINATION/Contents/MacOS/Notion2PDF" --version
echo "Installed and registered: $DESTINATION"
