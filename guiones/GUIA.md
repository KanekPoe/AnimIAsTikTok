# Guía para escribir guiones base — Newton Bien Loco

Canal de datos científicos curiosos (TikTok / YouTube Shorts) para público mexicano. Lo presenta
**Newton**, una caricatura en 2D con lentes de sol, a veces con un **colega** científico.
Un guion *base* es un borrador: el creador lo edita con su estilo y después se revisan los datos
con cuidado. Aun así debe ser correcto y no exagerar.

Cada guion es un archivo `guiones/NNN_slug.md` (NNN = número de la idea con 3 dígitos, slug en
minúsculas sin acentos, con guiones bajos; p. ej. `047_cielo_azul.md`). Se comprueba con:

    python3 pipeline/validar_guion.py guiones/047_cielo_azul.md

Si el validador marca errores, corrígelos hasta que diga OK.

---

## Reglas de contenido

1. **Gancho en la línea 1** (0–3 s): un dato sorprendente o una pregunta con tensión. Nada de
   "hola", "hoy les traigo" ni presentaciones.
2. **Duración 30–45 s**: entre **70 y 120 palabras** en total sumando todas las líneas `DICE`.
   Excepción solo si el creador lo pide (tops, listas): `duracion: larga` en el encabezado permite
   hasta 165 palabras (~50 s).
   **6 a 10 líneas**, cada una de **máximo 25 palabras**.
3. **Lo más fuerte justo después del gancho**; el giro o la imagen más loca, cerca del final.
4. **Cierre**: la última línea es una pregunta para comentarios o un gancho a otro video. Si
   puede conectar con el inicio (loop), mejor.
5. **Rigor**: cada número o afirmación va en "Datos que hay que verificar". Si hay matiz de
   rigor en la idea, **respétalo en el texto** (p. ej. "se cree", "unos", "según un estudio").
   No inventes cifras: si no estás seguro, usa una aproximación honesta ("miles", "cientos") y
   márcala con confianza baja. Prohibido exagerar para que suene más impactante.
6. **Lenguaje**: español de México, coloquial y divertido, frases cortas que se puedan decir
   en voz alta. Modismos del creador (úsalos con medida, 1–3 por guion): *neta, wacha, tons,
   símon, nel, o nel, machín, re-, pasado de lanza, qué onda, ¿a poco?, está cañón*.
   **Prohibido**: groserías fuertes (pedo, cabrón, verga, chingar, pinche, mierda, culero,
   wey/güey), sangre explícita o violencia gráfica (los videos se promocionan y TikTok los
   rechaza).
7. **Visual cada 1–3 s**: cada línea dice qué se ve en pantalla. Prefiere objetos que ya
   existen (lista abajo). Máximo **4 objetos nuevos** y **1 fondo nuevo** por guion; cada uno
   se declara en "Imágenes nuevas" con una descripción breve **en inglés** para el generador
   de imágenes (solo el objeto, estilo caricatura).
8. **Números**: escríbelos con cifras (`243 días`, `464 °C`); luego se convierten a palabras
   para la voz.

## Personajes

**NEWTON** — poses: `explicando_pluma`, `senalando`, `asustado`, `pensando`, `manzana_pensando`.

**Colegas** (opcional, máximo 1 por guion y **máximo 2 líneas suyas**). Se usan cuando el tema
es de su área, como invitado que aporta un dato o una reacción:

| colega | área | rasgo |
|---|---|---|
| `darwin` | animales, evolución | tortuga de Galápagos en el hombro |
| `tesla` | electricidad, magnetismo | pelo electrizado con chispas |
| `curie` | química, radiactividad | matraz que brilla |
| `turing` | computación, códigos | laptop con código verde |
| `godel` | matemáticas, escalas, números grandes | abrigo enorme, pizarrón con ∞ |
| `ada` | programación, máquinas | tira de tarjetas perforadas |
| `hipatia` | astronomía, espacio | astrolabio |
| `anning` | fósiles, dinosaurios, geología | sombrero de copa, martillo y amonita |
| `franklin` | ADN, células, cuerpo humano | placa de rayos X (Foto 51) |

Poses de colegas: `presentando`, `explicando`, `senalando`, `asustado`, `pensando`.
Si no hay colega, pon `colega: ninguno`. **Nunca** pongas a un colega a decir algo falso de su
propia vida.

## Fondos disponibles

`estudio`, `jardin`, `espacio`, `oceano` (arrecife tropical), `mar_antartico` (mar helado bajo el agua), `laboratorio`, `paris`, `venus_superficie`.
Newton y los colegas solo aparecen de cuerpo entero en `estudio` (o en un fondo nuevo que lo
permita). En los demás fondos la línea es "voz en off" con objetos en pantalla: escribe
`NEWTON (voz)`.

## Objetos que ya existen (`objetos/<nombre>`)

bacteria_bacilo bacteria_cadena bacteria_coco bacteria_espiral bacteria_racimo bacterias_grupo
brazo_venas cable_cobre calendario cancha_futbol celula_humana cerebro cerebro_colores
cerebro_oscuro clavo_oxidado copo_nieve elefante estatua_libertad_cobre estatua_libertad_verde
flecha_giro flecha_orbita fuego gota_azul gota_roja gota_roja_oscura gota_transparente
grano_pimienta libros_parados libros_pila_3 libros_pila_4 libros_pila_5 luna lupa manzana_1
manzana_mordida molecula_co2 pelota_playa persona_nadando plomo_derretido prisma pulpo
pulpo_corazones pulpo_saludando reloj_arena sol telescopio termometro_caliente termometro_frio
tierra torre_eiffel venus

En `PANTALLA` también puedes poner textos: `texto "464 °C"` (dato grande) o `sello "MITO"`
(sello que cae con golpe; **máximo 1 sello por guion**).

---

## Formato exacto (copia esta estructura)

```markdown
---
n: 47
slug: cielo_azul
categoria: Física cotidiana
idea: ¿Por qué el cielo es azul?
colega: ninguno
badge: DATO CURIOSO
cta: ¿Qué otra pregunta "obvia" quieres que te explique? 👇
estado: base
---

## Guion

1. [gancho] NEWTON (senalando) | fondo: estudio
   DICE: Si la luz del Sol es blanca… ¿por qué el cielo es azul? Neta, ¿alguna vez te lo preguntaste?
   PANTALLA: texto "¿AZUL?"
2. [dato] NEWTON (voz) | fondo: espacio
   DICE: La luz blanca trae todos los colores juntos, como un arcoíris escondido.
   PANTALLA: objetos/sol · objetos/prisma
3. [dato] NEWTON (voz) | fondo: espacio
   DICE: Cuando entra al aire, choca con moléculas diminutas que rebotan la luz azul para todos lados.
   PANTALLA: objetos/tierra · objetos/rayos_luz_colores
4. [dato] NEWTON (voz) | fondo: jardin
   DICE: El azul se dispersa unas 5 veces más que el rojo. Tons, mires a donde mires, te llega azul.
   PANTALLA: texto "AZUL × 5"
5. [giro] NEWTON (asustado) | fondo: estudio
   DICE: ¿Y el violeta? Se dispersa todavía más… pero tus ojos son más sensibles al azul.
   PANTALLA: texto "¿Y EL VIOLETA?"
6. [dato] NEWTON (pensando) | fondo: estudio
   DICE: Y al atardecer la luz cruza mucho más aire: el azul se queda en el camino y llega el rojo.
   PANTALLA: objetos/atardecer
7. [cierre] NEWTON (explicando_pluma) | fondo: estudio
   DICE: ¿Y en Marte de qué color crees que son los atardeceres? Te leo en los comentarios.
   PANTALLA: texto "¿MARTE?"

## Datos que hay que verificar

- La luz azul se dispersa unas 5.5 veces más que la roja (dispersión de Rayleigh, ∝ 1/λ⁴). Fuente sugerida: NASA SpacePlace. Confianza: alta.
- El violeta se dispersa más, pero el ojo es más sensible al azul y el Sol emite menos violeta. Fuente sugerida: NOAA / libros de óptica. Confianza: alta.

## Imágenes nuevas

- objetos/rayos_luz_colores: colorful rays of light (red, green, blue) bouncing off tiny air molecules
- objetos/atardecer: a small orange and red sunset over a hill

## Notas

- Conecta con la idea 2 (atardeceres azules en Marte) para el siguiente video.
```

Campos:
- `[etiqueta]`: `gancho` (solo la línea 1), `dato`, `giro`, `cierre` (solo la última).
- `QUIÉN`: `NEWTON (pose)`, `NEWTON (voz)` o `COLEGA:<nombre> (pose)`, p. ej. `COLEGA:darwin (senalando)`.
- `badge`: 1–3 palabras en mayúsculas (DATO ESPACIAL, DATO ANIMAL, ¿VERDAD O MITO?, etc.).
- `cta`: texto corto que aparece en pantalla al final, con 👇.
- `portada` (opcional): el primer cuadro es la miniatura del perfil. Por defecto el gancho abre en el
  primer fondo del guion que no es el estudio, con el primer objeto; para elegirlo a mano:
  `portada: espacio objetos/agujero_negro`. `portada: estudio` deja el gancho en la oficina.
