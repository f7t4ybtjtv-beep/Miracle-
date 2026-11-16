#!/bin/bash
# Usage: go.sh <epic.png> <W> <H> <out.mp4> [audio.mp3] [seconds]
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
E=$1; W=$2; H=$3; OUT=$4; A=${5:-fatiha/audio/fond-remaster.mp3}; T=${6:-59.2}
FO=$(python3 -c "print(max(0,$T-3.5))")
python3 -I "$HERE/render.py" "$E" "$W" "$H" "$T" - fatiha/media/planets/moon.webp \
 | ffmpeg -v error -y -f rawvideo -pix_fmt rgb24 -s ${W}x${H} -r 30 -i - -t "$T" -i "$A" \
  -map 0:v -map 1:a:0 -c:v libx264 -preset slow -crf 18 -profile:v high -pix_fmt yuv420p -tune film \
  -af "afade=t=in:st=0:d=0.8,afade=t=out:st=$FO:d=3.5" -c:a aac -b:a 192k -shortest -movflags +faststart -map_metadata -1 "$OUT"
ffmpeg -v error -y -sseof -0.1 -i "$OUT" -frames:v 1 -q:v 3 "${OUT%.mp4}-poster.jpg"
echo "done $OUT"
