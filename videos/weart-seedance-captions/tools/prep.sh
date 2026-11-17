#!/bin/sh
# H.264 copy of her video for HyperFrames, with the account name in the WeArt menu blurred (14.25-15.62 s).
# Audio is copied untouched.
cd "$(dirname "$0")/.."
ffmpeg -y -v error -i assets/video/source.mov -filter_complex \
  "[0:v]split[a][b];[b]crop=900:70:180:232,boxblur=16:4[bl];[a][bl]overlay=180:232:enable='between(t,14.25,15.62)',format=yuv420p[v]" \
  -map "[v]" -map 0:a -c:v libx264 -crf 16 -preset medium -c:a copy -movflags +faststart assets/video/clip.mp4
