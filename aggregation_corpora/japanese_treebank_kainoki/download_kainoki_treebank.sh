#!/usr/bin/env bash

set -euo pipefail

BASE_URL="https://oncoj.orinst.ox.ac.uk/cgi-bin"
OVERVIEW_URL="${BASE_URL}/overview.sh?db=Kainoki&mode=download"
OUT_DIR="${1:-.}"
DELAY_SECONDS="${DELAY_SECONDS:-1.5}"
RATE_LIMIT="${RATE_LIMIT:-150k}"
RETRIES="${RETRIES:-3}"
MAX_FILES="${MAX_FILES:-0}"

mkdir -p "$OUT_DIR"

if ! command -v curl >/dev/null 2>&1; then
  echo "Error: curl is required but not installed." >&2
  exit 1
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

OVERVIEW_HTML="$TMP_DIR/overview.html"
FILES_LIST="$TMP_DIR/files.txt"

# One request to get the full file list from the download overview page.
curl --fail --silent --show-error --location \
  --retry "$RETRIES" --retry-delay 2 --retry-connrefused \
  --max-time 120 --user-agent "kainoki-downloader/1.0" \
  "$OVERVIEW_URL" > "$OVERVIEW_HTML"

# Extract unique file IDs from links like context.sh?file=<name>&db=Kainoki&mode=download.
# Filenames in this corpus are ASCII, so no URL decoding is needed.
grep -oE 'context\.sh\?file=[^&" ]+' "$OVERVIEW_HTML" \
  | sed 's/^context\.sh?file=//' \
  | sort -u > "$FILES_LIST"

TOTAL="$(wc -l < "$FILES_LIST" | tr -d ' ')"
if [ "$TOTAL" -eq 0 ]; then
  echo "Error: no file names were discovered from overview page." >&2
  exit 1
fi

echo "Discovered $TOTAL files. Output directory: $OUT_DIR"

downloaded=0
skipped=0
failed=0
index=0

while IFS= read -r file_id; do
  if [ "$MAX_FILES" -gt 0 ] && [ "$index" -ge "$MAX_FILES" ]; then
    break
  fi

  index=$((index + 1))
  out_path="$OUT_DIR/$file_id"

  if [ -s "$out_path" ]; then
    skipped=$((skipped + 1))
    printf '[%d/%d] skip  %s (already exists)\n' "$index" "$TOTAL" "$file_id"
    continue
  fi

  # Keep load low: sequential requests and a pause between each download.
  sleep "$DELAY_SECONDS"

  url="${BASE_URL}/context.sh?file=${file_id}&db=Kainoki&mode=download"
  tmp_out="$TMP_DIR/${file_id}.part"

  if curl --fail --silent --show-error --location --compressed \
      --retry "$RETRIES" --retry-delay 2 --retry-connrefused \
      --limit-rate "$RATE_LIMIT" --max-time 120 \
      --user-agent "kainoki-downloader/1.0" \
      "$url" > "$tmp_out"; then
    if [ -s "$tmp_out" ]; then
      mv "$tmp_out" "$out_path"
      downloaded=$((downloaded + 1))
      printf '[%d/%d] saved %s\n' "$index" "$TOTAL" "$file_id"
    else
      failed=$((failed + 1))
      printf '[%d/%d] fail  %s (empty response)\n' "$index" "$TOTAL" "$file_id" >&2
    fi
  else
    failed=$((failed + 1))
    printf '[%d/%d] fail  %s (request error)\n' "$index" "$TOTAL" "$file_id" >&2
  fi

done < "$FILES_LIST"

echo
echo "Done. downloaded=$downloaded skipped=$skipped failed=$failed total=$TOTAL"
if [ "$failed" -gt 0 ]; then
  exit 2
fi
