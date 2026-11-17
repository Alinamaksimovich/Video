#!/bin/sh
# Rendered picture + her original audio with one gain (-6.0 dB -> about -14 LUFS). Video stream copied.
cd "$(dirname "$0")/.."
ffmpeg -y -v error -i renders/weart-tutorial2-captions.mp4 -i assets/video/source.mov -map 0:v -map 1:a \
  -c:v copy -af volume=-6.0dB -c:a aac -b:a 192k -shortest -movflags +faststart renders/weart-tutorial2-captions-final.mp4
