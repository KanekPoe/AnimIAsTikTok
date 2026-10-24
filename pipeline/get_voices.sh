#!/usr/bin/env bash
# Descarga las voces Piper en español a assets/voices/ (no se suben al repo).
# Requiere: pip install piper-tts
set -euo pipefail
cd "$(dirname "$0")/../assets" 2>/dev/null || { mkdir -p "$(dirname "$0")/../assets"; cd "$(dirname "$0")/../assets"; }
mkdir -p voices && cd voices
for v in es-mls_10246-low es-mls_9972-low es-carlfm-x-low; do
  [ -f "$v/$v.onnx" ] && continue
  curl -sSL -o "$v.tar.gz" "https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-$v.tar.gz"
  mkdir -p "$v" && tar xzf "$v.tar.gz" -C "$v" && rm "$v.tar.gz"
done
echo "Voces listas en $(pwd)"
