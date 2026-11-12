# Newton Bien Loco — instrucciones para Claude

Canal de datos curiosos científicos (TikTok / YouTube Shorts) presentado por Newton en 2D.
Motor: `pipeline/nbl.py` (episodios en `episodes/nbl*.py`). Plan: `docs/PLAN_CANAL.md`.

## Antes de tocar audio o renderizar

1. **Lee `docs/LECCIONES.md`.** Contiene errores reales que ya pasaron y no deben repetirse.
2. Si cambiaste algo de audio (voz, efectos, mezcla): `python3 tests/test_audio.py` debe pasar.
3. El control `pipeline/audio_qc.py` corre solo al generar voces y antes de exportar; si bloquea
   un render, **arregla la causa**, no lo desactives ni subas los umbrales para que pase.

## Reglas del canal

- Rigor: cada dato con fuente verificada; nada de exagerar (ver `.claude/skills/tiktok-retention`).
- Máximo 3 efectos de sonido de acento por video (`MAX_ACCENTS`).
- Si el video se va a promocionar: nada de sangre explícita ni groserías fuertes.
- Guiones del creador: respetar su estilo y modismos; solo corregir imprecisiones y avisarle.
- Gasto: imágenes con tope mensual (`pipeline/imagegen.py`, registro en `assets/art/ledger.json`).
