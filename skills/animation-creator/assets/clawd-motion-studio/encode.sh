#!/bin/zsh
# Encode build/frames/0001..0360.png + audio/soundtrack.wav -> out/clawd_no_after_effects.mp4
# H.264 High CRF 17, 30 fps, soft vignette, AAC 320k, +faststart (prompt pack page 4).
set -e
cd "$(dirname "$0")"
mkdir -p out
ffmpeg -y -framerate 30 -start_number 1 -i build/frames/%04d.png -i audio/soundtrack.wav \
  -frames:v 360 -vf "vignette=angle=PI/5:mode=forward,format=yuv420p" \
  -c:v libx264 -profile:v high -crf 17 -preset slow -r 30 \
  -c:a aac -b:a 320k -ar 48000 -t 12 -movflags +faststart out/clawd_no_after_effects.mp4
ffmpeg -y -loglevel error -i out/clawd_no_after_effects.mp4 -vf "select=eq(n\,359)" -frames:v 1 out/poster.png
echo done
