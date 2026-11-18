#!/usr/bin/env bash
# Render a deck to one PNG per slide for visual review.
#   bash presentation/build/render_check.sh <deck.pptx> <outdir>
set -euo pipefail

if [ $# -ne 2 ]; then
  echo "usage: $0 <deck.pptx> <outdir>" >&2
  exit 2
fi
pptx="$1"
out="$2"
tmp="${TMPDIR:-/tmp}"
tmp="${tmp%/}"
work="$(mktemp -d "$tmp/render.XXXXXX")"
trap 'rm -rf "$work"' EXIT

mkdir -p "$out"
rm -f "$out"/*.png
soffice -env:UserInstallation="file://$tmp/lo" --headless \
  --convert-to pdf --outdir "$work" "$pptx" >/dev/null
pdf="$work/$(basename "${pptx%.*}").pdf"
pdftoppm -r 60 -png "$pdf" "$out/slide"
echo "$(ls "$out"/*.png | wc -l | tr -d ' ') PNGs in $out"
