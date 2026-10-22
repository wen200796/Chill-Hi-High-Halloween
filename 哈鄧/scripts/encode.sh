#!/usr/bin/env bash
# Mux the silent master with the mix into the preview and final deliverables (哈鄧/output/).
set -euo pipefail
cd "$(dirname "$0")/../output"
ffmpeg -v error -y -i _build/master_video.mp4 -i _build/mix.wav -map 0:v -map 1:a \
  -vf "scale=540:960:flags=lanczos" -c:v libx264 -preset veryfast -crf 26 -pix_fmt yuv420p \
  -c:a aac -b:a 128k -ar 48000 -shortest -movflags +faststart harry_dumbledore_preview.mp4
ffmpeg -v error -y -i _build/master_video.mp4 -i _build/mix.wav -map 0:v -map 1:a \
  -c:v libx264 -profile:v high -level 4.2 -preset slow -crf 19 -maxrate 18M -bufsize 36M -pix_fmt yuv420p \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 -r 24 \
  -c:a aac -b:a 256k -ar 48000 -ac 2 -shortest -movflags +faststart harry_dumbledore_final.mp4
