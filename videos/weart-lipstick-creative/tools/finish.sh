#!/bin/sh
# Rendered picture + assets/audio/mix.wav with one gain to about -14 LUFS (measured mix: -26.3 LUFS). Video stream copied.
cd "$(dirname "$0")/.."
ffmpeg -y -v error -i renders/raw.mp4 -i assets/audio/mix.wav -map 0:v -map 1:a -c:v copy -af volume=13.6dB,alimiter=limit=0.78:level=false -c:a aac -b:a 192k -shortest -movflags +faststart renders/weart-lipstick-creative.mp4
