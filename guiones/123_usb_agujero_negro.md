---
n: 123
slug: usb_agujero_negro
categoria: Grandes preguntas
idea: Top 6 de medios para guardar información (agujeros negros USB)
colega: turing
badge: TOP 6
cta: ¿Cabe el GTA 6 en el número 1? 👇
estado: base
duracion: larga
prioridad: creador
---

## Guion

1. [gancho] NEWTON (senalando) | fondo: estudio
   DICE: ¡Pum! Top 6 para guardar información. Y el número 1… está pasado de lanza, acá de aliens.
   PANTALLA: texto "TOP 6"
2. [dato] NEWTON (voz) | fondo: laboratorio
   DICE: Número 6: la tarjeta perforada: hoyitos, como 80 letras.
   PANTALLA: objetos/tarjeta_perforada · texto "#6"
3. [dato] NEWTON (voz) | fondo: laboratorio
   DICE: Número 5: la hoja de papel, unas 3 mil letras. Un libro: unas 200 páginas.
   PANTALLA: objetos/hoja_papel · texto "#5"
4. [dato] COLEGA:turing (explicando) | fondo: estudio
   DICE: Número 4: tu USB de un tera: más de un millón de libros.
   PANTALLA: objetos/memoria_usb · texto "#4"
5. [dato] COLEGA:turing (senalando) | fondo: estudio
   DICE: Número 3: la cinta magnética. No te lo crees, yo tampoco, pero sigue viva en centros de datos.
   PANTALLA: objetos/cinta_magnetica · texto "#3"
6. [dato] NEWTON (voz) | fondo: laboratorio
   DICE: Un cartucho: 40 terabytes, 40 de tus USBs.
   PANTALLA: objetos/cinta_magnetica · texto "= 40 USBs"
7. [dato] NEWTON (voz) | fondo: laboratorio
   DICE: Número 2: ya es investigación, casi ciencia ficción. Cristal 5D: un láser graba dentro del vidrio.
   PANTALLA: objetos/cristal_5d · texto "#2"
8. [dato] NEWTON (voz) | fondo: laboratorio
   DICE: 360 terabytes por disco, por miles de millones de años. Eso sí: no se borra.
   PANTALLA: objetos/cristal_5d · texto "360 TB"
9. [giro] NEWTON (voz) | fondo: espacio
   DICE: Y ahora sí, lo mero chido. Número 1: un agujero negro de 2 cm: un 3 con 59 ceros de libros.
   PANTALLA: objetos/agujero_negro · texto "#1"
10. [cierre] NEWTON (asustado) | fondo: estudio
   DICE: Pero pesaría como la Tierra, y sacar los datos… quién sabe. ¿Crees que ahí quepa el GTA 6?
   PANTALLA: objetos/tierra

## Datos que hay que verificar


- El cristal 5D es de una sola escritura (no se puede borrar ni reescribir). Fuente: Universidad de Southampton; Microsoft Project Silica (misma idea). Confianza: alta.
- La cinta magnética se usa hoy para archivo en centros de datos (nube, bancos, ciencia). Fuente: lto.org. Confianza: alta.
- Orden del top: por cuánto cabe en cada objeto (no por antigüedad). La tarjeta perforada guardaba menos que una hoja de papel, por eso va en el 6; la cinta guarda más que una USB, por eso va arriba de ella.
- Tarjeta perforada IBM de 80 columnas: 80 caracteres (un renglón, ~80 bytes). Fuente: IBM, "The IBM punched card" (ibm.com/history/punched-card). Confianza: alta.
- Hoja de papel: unos 2,000–3,000 caracteres por página escrita (~3 KB). Estimación común; confianza: media (depende de la letra).
- Libro de 200 páginas (dato del creador; los libros comunes van de ~200 a 300 páginas) × 3,000 letras ≈ 600,000 caracteres ≈ 0.6 MB. 1 TB ≈ 1.7 millones de libros ("más de un millón"); 40 TB ≈ 67 millones ("unos 60 millones"). Cálculo propio. Confianza: media (orden de magnitud).
- Cinta LTO-10: cartuchos de 30 TB y 40 TB nativos (40 TB a la venta desde enero de 2026). Fuente: lto.org/lto-10; Tom's Hardware. Confianza: alta.
- Cristal 5D (Universidad de Southampton): datos grabados con láser de femtosegundos en cuarzo fundido; capacidad proyectada de 360 TB por disco; estabilidad estimada de 13,800 millones de años a 190 °C (extrapolación de los autores). Sigue en etapa de investigación; lo demostrado fueron archivos pequeños. Se llama "5D" (3 dimensiones de posición + tamaño + orientación de la nanoestructura), no "4D". Fuente: Universidad de Southampton (2013, 2016); The Register (2016). Confianza: alta (que lo dicen); media (que la capacidad y la duración se alcancen).
- Agujero negro de 1 cm de radio (2 cm de diámetro): ≈ 1.7×10⁶⁶ bits = 2.1×10⁶⁵ bytes ≈ 3.5×10⁵⁹ libros de 0.6 MB ("un 3 con 59 ceros") (cálculo de Bekenstein–Hawking, ver versión anterior en el registro). Masa ≈ 6.7×10²⁴ kg ≈ 1.1 Tierras. Confianza: alta (teoría).

## Imágenes nuevas

- objetos/tarjeta_perforada: a beige IBM-style computer punched card with rows of small rectangular holes and a cut corner
- objetos/hoja_papel: a single sheet of paper with lines of handwritten text
- objetos/cinta_magnetica: a modern black data tape cartridge (LTO style), square with a small label
- objetos/cristal_5d: a small round transparent glass disc with tiny glowing blue data dots inside

## Notas

- Versión 3 (13 nov 2026): borrador del creador ("¡Pum! Top 6…"), pulido respetando su estilo. Cambios: "otro pedo" -> "está pasado de lanza, acá de aliens" (frase del creador, versión 4); "millones y millones de años" -> "miles de millones" (lo que dicen los investigadores); "un millón de libros" -> "más de un millón" (con libros de 200 páginas salen 1.7 millones).
- Cierre del creador: "¿Crees que ahí quepa el GTA 6?" (versión 4).
- duracion: larga (~55 s) porque es un top; si se quiere de 45 s, quitar las líneas 6 y 8 y juntar datos.
