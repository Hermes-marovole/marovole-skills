#!/bin/bash
# headless-screenshot.sh — 用 Chrome Headless 截取 HTML 对比表长图
# Usage: ./headless-screenshot.sh <input.html> [output.png] [width] [height]
# 默认: width=1300, height=1600（可根据内容调整）

INPUT="${1:?Usage: $0 <input.html> [output.png] [width] [height]}"
OUTPUT="${2:-screenshot.png}"
WIDTH="${3:-1300}"
HEIGHT="${4:-1600}"

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

if [ ! -x "$CHROME" ]; then
    echo "❌ Chrome not found at $CHROME"
    echo "   Adjust CHROME path or install Google Chrome"
    exit 1
fi

# Convert to absolute file URL
if [[ "$INPUT" != file://* ]]; then
    INPUT="file://$(realpath "$INPUT")"
fi

echo "📸 Screenshot: $INPUT → $OUTPUT (${WIDTH}x${HEIGHT})"

"$CHROME" \
    --headless \
    --screenshot="$OUTPUT" \
    --window-size="${WIDTH},${HEIGHT}" \
    --disable-gpu \
    --no-sandbox \
    "$INPUT" 2>&1 | grep -E "bytes written|ERROR" || true

if [ -f "$OUTPUT" ]; then
    FILE_INFO=$(file "$OUTPUT" 2>/dev/null | awk -F: '{print $2}')
    SIZE=$(ls -lh "$OUTPUT" | awk '{print $5}')
    echo "✅ Done: $OUTPUT ($SIZE, $FILE_INFO)"
else
    echo "❌ Screenshot failed"
    exit 1
fi
