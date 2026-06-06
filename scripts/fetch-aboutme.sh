#!/usr/bin/env bash
# Fetch the GitHub profile README into assets/_aboutme.md for the landing-page about-me block.
# Soft-fail: if the fetch fails and a prior assets/_aboutme.md exists, keep it;
# otherwise write a minimal placeholder so `quarto render` still succeeds.

URL="https://raw.githubusercontent.com/betopark97/betopark97/main/README.md"
OUT="assets/_aboutme.md"
TMP="$(mktemp)"

mkdir -p "$(dirname "$OUT")"

if curl -fsSL --max-time 10 "$URL" -o "$TMP" && [ -s "$TMP" ]; then
  mv "$TMP" "$OUT"
  echo "fetch-aboutme: pulled $URL -> $OUT"
else
  rm -f "$TMP"
  if [ -f "$OUT" ]; then
    echo "fetch-aboutme: fetch failed; reusing existing $OUT" >&2
  else
    printf '# Hi\n\n*(profile README unavailable)*\n' > "$OUT"
    echo "fetch-aboutme: fetch failed and no cached $OUT; wrote placeholder" >&2
  fi
fi
