#!/bin/sh
# Rendered picture + her original audio with one gain (-5.6 dB -> about -14 LUFS). Video stream copied.
cd "$(dirname "$0")/.."
ffmpeg -y -v error -i renders/weart-seedance-captions.mp4 -i assets/video/source.mov -map 0:v -map 1:a \
  -c:v copy -af volume=-5.6dB -c:a aac -b:a 192k -shortest -movflags +faststart renders/weart-seedance-captions-final.mp4
