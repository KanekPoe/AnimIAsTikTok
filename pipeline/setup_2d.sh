#!/usr/bin/env bash
# Instala las herramientas del pipeline 2D/3D. Es idempotente: se puede correr varias veces.
# Uso (como root, desde la raíz del repo):  bash pipeline/setup_2d.sh
#
# Instala:
#   - Manim Community (diagramas y animación científica) + LaTeX mínimo para fórmulas
#   - skia-python y pycairo (dibujo vectorial rápido), python-lottie
#   - Blender 4.5 LTS en /opt (Grease Pencil v3) como `blender45`; Blender del sistema queda para el 3D
#   - Inkscape (SVG por línea de comandos) y Synfig CLI (animación vectorial)
#   - Íconos Phosphor (MIT) y emojis Twemoji (gráficos CC-BY 4.0) en assets/vendor
#   - Revideo (animación con código TypeScript, render sin pantalla) en tools/revideo
#   - Piper TTS y voces en español
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BLENDER_VERSION=4.5.16
export DEBIAN_FRONTEND=noninteractive

echo "== Paquetes del sistema"
apt-get update -qq
apt-get install -y -qq build-essential python3-dev pkg-config libcairo2-dev libpango1.0-dev \
  ffmpeg inkscape synfig texlive-latex-base texlive-latex-extra texlive-fonts-recommended \
  dvisvgm fonts-noto-color-emoji libegl1 libgl1-mesa-dri blender python3-numpy >/dev/null

echo "== Paquetes de Python"
# srt y lottie traen instaladores antiguos que fallan con el setuptools del sistema:
# se compilan en un entorno aislado (--use-pep517).
pip install --break-system-packages -q --use-pep517 srt lottie
pip install --break-system-packages -q manim skia-python pycairo piper-tts numpy pillow

echo "== Blender $BLENDER_VERSION LTS (Grease Pencil v3)"
if [ ! -x "/opt/blender-$BLENDER_VERSION/blender" ]; then
  curl -sSL "https://download.blender.org/release/Blender4.5/blender-$BLENDER_VERSION-linux-x64.tar.xz" \
    | tar xJ -C /opt
  mv "/opt/blender-$BLENDER_VERSION-linux-x64" "/opt/blender-$BLENDER_VERSION"
fi
ln -sf "/opt/blender-$BLENDER_VERSION/blender" /usr/local/bin/blender45

echo "== Íconos y emojis"
mkdir -p "$ROOT/assets/vendor"
(cd "$ROOT/assets/vendor" && [ -f package.json ] || echo '{"private": true}' > package.json)
(cd "$ROOT/assets/vendor" && npm install --silent @phosphor-icons/core@2 @twemoji/svg@15)

echo "== Revideo"
if [ -f "$ROOT/tools/revideo/package.json" ]; then
  (cd "$ROOT/tools/revideo" && PUPPETEER_SKIP_DOWNLOAD=1 npm install --silent)
fi

echo "== Voces"
bash "$ROOT/pipeline/get_voices.sh" || echo "[aviso] no se pudieron descargar las voces"

echo "Listo."
