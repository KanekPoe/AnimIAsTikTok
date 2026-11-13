# Estado del proyecto — Newton Bien Loco (13 nov 2026)

Nota de traspaso entre sesiones. Léela entera antes de seguir. Reglas fijas en `CLAUDE.md`;
errores que no deben repetirse en `docs/LECCIONES.md`.

## Cómo trabajar con el creador

- Habla español de México, directo. Cuando dice **"no codifiques" / "aún no codifiques"**: solo
  platicar y proponer, no tocar código.
- **No ejecutar producción masiva de videos hasta que dé la orden explícita.** Va "lento":
  primero se platica cada punto.
- El creador no puede abrir archivos de la nube: todo lo que deba ver se le manda con
  `SendUserFile` (imágenes, videos, documentos).
- Nunca pedir claves en el chat. La clave de Gemini la inyecta el proxy del entorno
  (encabezado `x-goog-api-key`).
- Registro de contenido y gasto: `docs/registro_contenido.xlsx` (hojas Contenido, Ideas,
  Resumen, Gasto). Mantenerlo al día.

## Publicado

| # | Video | Estado |
|---|---|---|
| 5 | Venus (`episodes/nbl05_venus.py`) | Publicado, audio limpio |
| 8 | Pulpo, sangre azul (`episodes/nbl08_pulpo_sangre.py`) | Publicado con el audio viejo (chik-chik); promoción en TikTok rechazada por "sangre"/groserías |

Los episodios 1–4, 6 y 7 se renderizaron con el audio dañado: se rehacen cuando el creador
escriba su guion (la caché `v2` y `audio_qc` los dejan limpios solos). `nbl01_manzana` quedó
truncado a 3 s.

## Personajes

- **Newton**: rig en `assets/art/newton/rig/<pose>/` (base, boca_abierta). Poses:
  explicando_pluma, senalando, asustado, pensando, manzana_pensando. Lentes de sol (sin parpadeo).
- **9 colegas aprobados** (Darwin, Tesla, Curie, Turing (con laptop), Gödel, Ada, Hipatia,
  Anning, Franklin). Rig en `assets/art/colegas/<nombre>/rig/<pose>/{base,boca_abierta,ojos_cerrados}.png`,
  poses: presentando, explicando, senalando, asustado, pensando. Revisado cara por cara.
  Se generan con `pipeline/rig_colegas.py` (5 imágenes por colega).
- No se agregan más colegas por ahora (el creador dijo que no a Galileo, Pasteur, etc.).
- Tesla solo trae el rayito en la mano en la pose "presentando" (las otras poses no). Pendiente si el creador lo quiere.

## Guiones

- **120 guiones base** en `guiones/NNN_slug.md` (una por idea del Excel), escritos por agentes
  Haiku con `guiones/GUIA.md`; los 120 pasan `python3 pipeline/validar_guion.py guiones/`.
  Índice: `guiones/INDICE.md`. Versión para leer (solo lo que se dice): se genera desde los .md.
- Estado: **esperan la edición del creador**. Cuando regrese uno editado: verificar CON FUENTES
  cada dato de "Datos que hay que verificar" (los de confianza media/baja primero), respetar sus
  modismos y avisarle de cualquier imprecisión.
- Ya corregidos en revisión: #100 (Vitruvio sí cuenta lo de salir desnudo), #91 (aguja gruesa
  sin punta; primera persona), #30 (hemocianina: menos eficiente, no "espesa").
- **Decisiones pendientes del creador**: #80 núcleo = "grano de pimienta" en vez de "canica";
  #84 "unos 75,000 años (a la velocidad de la Voyager)" en vez de "miles de años".
- El Excel (hoja Ideas) marca las 120 como "Guion base".

## Imágenes

- Tope mensual de imágenes: 150 (`IMAGEGEN_MAX_PER_MONTH` en `pipeline/imagegen.py`);
  usadas en noviembre 2026: 96. Registro en `assets/art/ledger.json`.
- **71 objetos nuevos** para los guiones ya generados (`assets/art/objetos/`), hechos con
  `pipeline/objetos_lote.py guiones/objetos_lote1.json` (hojas de ~6 con nombre automático;
  objetos verdes van en fondo magenta: `cutout.py` lo detecta solo).
- Pendiente de decisión: `iman_barra` salió de herradura; para #112 conviene uno de barra (1 imagen).
- Gasto Google: límite mensual de 300 MXN puesto por el creador (cuenta uso bruto aunque lo
  cubran créditos); hay ~1.27K MXN de créditos.

## Siguiente (aún sin orden de ejecutar)

Plan acordado: producir los 120 con una sesión multiagente de Haiku sobre un pipeline robusto.
Falta, antes de la orden:
1. **Motor con colegas**: `pipeline/nbl.py` solo sabe poner a Newton; hay que soportar un
   colega en escena (posición, su rig, parpadeo).
2. **Voces de los colegas**: elegir voz de Gemini TTS para cada uno (Newton = "Puck").
3. **Convertidor** guion `.md` → episodio `episodes/nblNNN_*.py` (números a palabras para la voz,
   cifras en subtítulos), con posiciones por "ranuras" con nombre y sin encimar objetos.
4. QA visual automática (zonas seguras, encimados, duración) además de `audio_qc`.
5. Lote piloto de ~10 videos, luego lotes de 20–30.

## Videos y almacenamiento

- Los videos van en `output/` (fuera de git a propósito: ~10 MB cada uno). Esta máquina es
  temporal: mandar cada video al creador al terminarlo.
- El creador va a conectar **Google Drive** (conector de claude.ai) para guardar ahí los videos
  aprobados. Al iniciar la sesión nueva: comprobar que el conector está activo y **probar subir
  un video de ~10 MB** antes de prometer nada; si no aguanta, proponer otra vía.

## Pendientes menores

- Un agente dejó un archivo vacío `/fix.py` en la raíz del contenedor viejo (fuera del repo);
  desaparece con el contenedor.
- `output/ep01_control_mundial/` (proyecto viejo de robots) ocupaba 5.8 GB de fotogramas en el
  contenedor viejo; no está en git.
