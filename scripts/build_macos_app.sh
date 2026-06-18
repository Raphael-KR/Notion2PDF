#!/bin/zsh
set -euo pipefail

APP_DIR="dist/Notion2PDF.app"
EXECUTABLE="$APP_DIR/Contents/MacOS/Notion2PDF"

if [[ ! -f "$EXECUTABLE" ]]; then
  echo "Missing $EXECUTABLE" >&2
  exit 1
fi

chmod +x "$EXECUTABLE"
plutil -lint "$APP_DIR/Contents/Info.plist"
echo "Built $APP_DIR"
