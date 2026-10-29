#!/bin/zsh
# Full render: frames 1..360 -> build/frames/0001.png .. 0360.png (frame f = time (f-1)/30 s).
# Usage: ./render_all.sh [start] [end]
set -euo pipefail
cd "$(dirname "$0")"
S=${1:-1}; E=${2:-360}
mkdir -p build/frames
start=$(date +%s)
blender -b clawd.blend -P gpu.py -o "//build/frames/####" -F PNG -s $S -e $E -a 2>&1 | tee -a build/render_log.txt | grep --line-buffered -E "^Fra:.*Time|Saved:|Error"
echo "rendered $S..$E in $(( $(date +%s) - start )) s" | tee -a build/render_log.txt
