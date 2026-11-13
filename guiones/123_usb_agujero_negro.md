---
n: 123
slug: usb_agujero_negro
categoria: Grandes preguntas
idea: Top 6 para guardar información: de la tarjeta perforada al agujero negro
colega: turing
badge: TOP 6
cta: ¿Qué guardarías en el número 1? 👇
estado: base
prioridad: creador
---

## Guion

1. [gancho] NEWTON (senalando) | fondo: estudio
   DICE: Top 6 para guardar información… y el número 1 te vuela la cabeza.
   PANTALLA: texto "TOP 6"
2. [dato] NEWTON (voz) | fondo: laboratorio
   DICE: Número 6: la tarjeta perforada. Un cartón con hoyitos: un renglón, 80 letras.
   PANTALLA: objetos/tarjeta_perforada · texto "#6"
3. [dato] NEWTON (voz) | fondo: laboratorio
   DICE: Número 5: una hoja de papel. Unas 3 mil letras.
   PANTALLA: objetos/hoja_papel · texto "#5"
4. [dato] COLEGA:turing (explicando) | fondo: estudio
   DICE: Número 4: tu USB de un terabyte: como un millón de libros.
   PANTALLA: objetos/memoria_usb · texto "#4"
5. [dato] COLEGA:turing (senalando) | fondo: estudio
   DICE: Número 3: la cinta magnética. Sigue viva: un cartucho guarda 40 terabytes.
   PANTALLA: objetos/cinta_magnetica · texto "#3"
6. [dato] NEWTON (voz) | fondo: laboratorio
   DICE: Número 2: el cristal 5D. Láser dentro de vidrio: 360 terabytes por disco… por miles de millones de años.
   PANTALLA: objetos/cristal_5d · texto "#2"
7. [giro] NEWTON (voz) | fondo: espacio
   DICE: Y el número 1: un agujero negro. Uno de 2 cm guardaría un número de libros con 59 ceros.
   PANTALLA: objetos/agujero_negro · texto "#1"
8. [giro] NEWTON (asustado) | fondo: estudio
   DICE: El detalle: pesaría como toda la Tierra. No te cabe en la mochila.
   PANTALLA: objetos/tierra
9. [cierre] NEWTON (explicando_pluma) | fondo: estudio
   DICE: ¿Qué guardarías tú en el número 1? Te leo.
   PANTALLA: texto "¿QUÉ GUARDARÍAS?"

## Datos que hay que verificar

- Orden del top: por cuánto cabe en cada objeto (no por antigüedad). La tarjeta perforada guardaba menos que una hoja de papel, por eso va en el 6; la cinta guarda más que una USB, por eso va arriba de ella.
- Tarjeta perforada IBM de 80 columnas: 80 caracteres (un renglón, ~80 bytes). Fuente: IBM, "The IBM punched card" (ibm.com/history/punched-card). Confianza: alta.
- Hoja de papel: unos 2,000–3,000 caracteres por página escrita (~3 KB). Estimación común; confianza: media (depende de la letra).
- Libro ≈ 1 MB de texto (≈300 páginas × 3 KB): 1 TB ≈ un millón de libros. Cálculo propio, orden de magnitud. Confianza: media.
- Cinta LTO-10: cartuchos de 30 TB y 40 TB nativos (40 TB a la venta desde enero de 2026). Fuente: lto.org/lto-10; Tom's Hardware. Confianza: alta.
- Cristal 5D (Universidad de Southampton): datos grabados con láser de femtosegundos en cuarzo fundido; capacidad proyectada de 360 TB por disco; estabilidad estimada de 13,800 millones de años a 190 °C (extrapolación de los autores). Sigue en etapa de investigación; lo demostrado fueron archivos pequeños. Se llama "5D" (3 dimensiones de posición + tamaño + orientación de la nanoestructura), no "4D". Fuente: Universidad de Southampton (2013, 2016); The Register (2016). Confianza: alta (que lo dicen); media (que la capacidad y la duración se alcancen).
- Agujero negro de 1 cm de radio (2 cm de diámetro): ≈ 1.7×10⁶⁶ bits = 2.1×10⁶⁵ bytes ≈ 2×10⁵⁹ libros de 1 MB (cálculo de Bekenstein–Hawking, ver versión anterior en el registro). Masa ≈ 6.7×10²⁴ kg ≈ 1.1 Tierras. Confianza: alta (teoría).

## Imágenes nuevas

- objetos/tarjeta_perforada: a beige IBM-style computer punched card with rows of small rectangular holes and a cut corner
- objetos/hoja_papel: a single sheet of paper with lines of handwritten text
- objetos/cinta_magnetica: a modern black data tape cartridge (LTO style), square with a small label
- objetos/cristal_5d: a small round transparent glass disc with tiny glowing blue data dots inside

## Notas

- Versión 2 a pedido del creador (13 nov 2026): de "USB de agujero negro" a un top 6 (papel, tarjetas perforadas, cintas, USB, cristal, agujero negro).
- El creador dijo "cristal 4D": el nombre real es cristal 5D (memoria 5D en vidrio).
- El orden va por capacidad; el del creador era histórico. Si prefiere el histórico, el papel va primero y se aclara que la tarjeta guardaba menos.
