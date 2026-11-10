# Herramientas del pipeline 2D

Todo se instala con `bash pipeline/setup_2d.sh` (como root, desde la raíz del repo).
Velocidades medidas en la nube sin GPU, a 1080x1920.

| Herramienta | Para qué | Velocidad medida | Licencia |
|---|---|---|---|
| **Manim Community 0.22** (`manim`) | Diagramas científicos, escalas, órbitas, gráficas, fórmulas (LaTeX) | 105 cuadros en ~2.5 s | MIT |
| **Blender 4.5 LTS – Grease Pencil v3** (`blender45`) | Personajes 2D animados (Newton, Manzanita), mezcla 2D/3D | ~0.8 s por cuadro (Workbench) | GPL |
| **skia-python 144** / **pycairo 1.29** | Dibujo vectorial rápido: textos, tarjetas, gráficos | — | BSD / LGPL-MPL |
| **Pillow + ffmpeg** | Composición, subtítulos, exportación | — | HPND / LGPL |
| **Revideo 0.11** (`tools/revideo`) | Animación con código TypeScript, render sin pantalla | 1.5 s de video en segundos | MIT |
| **Inkscape 1.2** (CLI) | Convertir SVG a PNG, preparar dibujos | — | GPL |
| **Synfig 1.5** (CLI) | Animación vectorial (render sin pantalla) | — | GPL |
| **python-lottie 0.7** | Animaciones Lottie | — | AGPL |
| **Phosphor Icons 2** (`assets/vendor`) | 1512 íconos × 6 estilos | — | MIT |
| **Twemoji 15** (`assets/vendor`) | 3723 emojis en SVG | — | Gráficos CC-BY 4.0 (dar crédito) |
| **Blender 4.0** (`blender`) | El 3D del episodio 1 | ~10 s por cuadro (EEVEE) | GPL |

## Notas de uso

- **Grease Pencil**: crear trazos con `drawing.add_strokes([n])` (API v3). Poner
  `layer.use_lights = False`, motor Workbench con `shading.light = "FLAT"`,
  `color_type = "MATERIAL"` y `view_transform = "Standard"` para colores planos.
  Los colores de material son lineales: convertir desde hex sRGB.
- **Manim**: para video vertical, `config.pixel_width=1080`, `pixel_height=1920`,
  `frame_width=9`, `frame_height=16`.
- **Revideo**: `cd tools/revideo && node render.mjs src/project.tsx salida.mp4`. Usa el
  Chromium de `/opt/pw-browsers` (variable `CHROME_PATH` para cambiarlo).
- **Twemoji**: poner el crédito "Emojis: Twemoji (CC-BY 4.0)" en la descripción cuando se
  usen.

## Alternativas evaluadas y no instaladas

| Herramienta | Por qué no |
|---|---|
| After Effects, Illustrator, Photoshop, Toon Boom | De pago, necesitan pantalla, no corren en Linux |
| OpenToonz, Krita, Glaxnimate, Friction | Son de interfaz gráfica; útiles en tu PC para dibujar, no para render automático |
| Motion Canvas | Renderiza desde su editor; el núcleo casi no se mantiene. Revideo es su sucesor sin pantalla |
| Remotion | Gratis para individuos, pero de pago para empresas de más de 3 personas; Revideo cubre lo mismo con MIT |
| OpenMoji | Licencia CC-BY-SA (obliga a compartir igual); Twemoji es más simple |

## Fuentes

- Manim: https://docs.manim.community/en/stable/installation/linux.html · https://pypi.org/project/manim/
- Grease Pencil v3: https://developer.blender.org/docs/release_notes/4.3/grease_pencil_migration/ ·
  https://developer.blender.org/docs/release_notes/4.5/grease_pencil/
- Revideo y Motion Canvas: https://rendercomp.com/blog/remotion-vs-revideo-comparison/ ·
  https://img.ly/blog/remotion-alternatives/
- Licencia de Remotion: https://www.remotion.dev/docs/license/faq
- Alternativas a After Effects: https://www.xda-developers.com/best-open-source-2d-animation-software-ditch-after-effects/
