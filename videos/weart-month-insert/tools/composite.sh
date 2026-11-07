#!/bin/sh
# Overlay the motion band (1072x816) onto the white bottom zone (y=1104) of her video.
# Her audio: one gain (-4.6 dB) to reach about -14 LUFS, no other processing, no music.
cd "$(dirname "$0")/.."
ffmpeg -y -v error -i assets/video/source.mov -i renders/band.mp4 \
  -filter_complex "[1:v]format=yuv420p[b];[0:v][b]overlay=0:1104:eof_action=pass,format=yuv420p[v]" \
  -map "[v]" -map 0:a -c:v libx264 -crf 17 -preset medium -af volume=-4.6dB -c:a aac -b:a 192k -movflags +faststart \
  renders/weart-month-insert.mp4
