#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
APP_DIR="$PROJECT_ROOT/dist/Notion2PDF.app"
EXECUTABLE="$APP_DIR/Contents/MacOS/Notion2PDF"
ICON_SOURCE="$PROJECT_ROOT/assets/Notion2PDF.png"
ICONSET="$PROJECT_ROOT/tmp/Notion2PDF.iconset"

if [[ ! -f "$EXECUTABLE" ]]; then
  echo "Missing $EXECUTABLE" >&2
  exit 1
fi

chmod +x "$EXECUTABLE"
if [[ ! -f "$ICON_SOURCE" ]]; then
  echo "Missing $ICON_SOURCE" >&2
  exit 1
fi

mkdir -p "$ICONSET" "$APP_DIR/Contents/Resources"
for size in 16 32 128 256 512; do
  sips -z "$size" "$size" "$ICON_SOURCE" --out "$ICONSET/icon_${size}x${size}.png" >/dev/null
  retina_size=$((size * 2))
  sips -z "$retina_size" "$retina_size" "$ICON_SOURCE" --out "$ICONSET/icon_${size}x${size}@2x.png" >/dev/null
done
iconutil -c icns "$ICONSET" -o "$APP_DIR/Contents/Resources/Notion2PDF.icns"
plutil -lint "$APP_DIR/Contents/Info.plist"
echo "Built $APP_DIR"
