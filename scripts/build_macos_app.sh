#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
APP_DIR="$PROJECT_ROOT/dist/Notion2PDF.app"
EXECUTABLE="$APP_DIR/Contents/MacOS/Notion2PDF"

if [[ ! -f "$EXECUTABLE" ]]; then
  echo "Missing $EXECUTABLE" >&2
  exit 1
fi

chmod +x "$EXECUTABLE"
plutil -lint "$APP_DIR/Contents/Info.plist"
echo "Built $APP_DIR"
