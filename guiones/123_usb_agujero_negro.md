---
n: 123
slug: usb_agujero_negro
categoria: Grandes preguntas
idea: USBs de agujeros negros: la memoria más grande posible
colega: turing
badge: DATO ESPACIAL
cta: ¿Qué guardarías en una USB de agujero negro? 👇
estado: base
---

## Guion

1. [gancho] NEWTON (senalando) | fondo: estudio
   DICE: ¿Y si tu próxima USB fuera un agujero negro? Sería la memoria más brutal del universo.
   PANTALLA: objetos/agujero_negro · texto "¿USB?"
2. [dato] NEWTON (voz) | fondo: espacio
   DICE: Bekenstein y Hawking descubrieron algo loquísimo: un agujero negro guarda información… en su superficie.
   PANTALLA: objetos/agujero_negro
3. [dato] COLEGA:turing (explicando) | fondo: estudio
   DICE: Uno del tamaño de una USB, de unos 2 cm, guardaría un uno con 66 ceros de bits.
   PANTALLA: texto "10⁶⁶ BITS"
4. [dato] COLEGA:turing (senalando) | fondo: estudio
   DICE: Tu USB de un terabyte tiene unos 8 billones. Le gana por un uno con 53 ceros.
   PANTALLA: objetos/memoria_usb · texto "× 10⁵³"
5. [giro] NEWTON (asustado) | fondo: estudio
   DICE: El detalle: así de chiquito pesaría lo mismo que toda la Tierra. No te cabe en la mochila.
   PANTALLA: objetos/tierra
6. [dato] NEWTON (pensando) | fondo: estudio
   DICE: Y sacar los datos tampoco es fácil: si la información se puede recuperar todavía se discute.
   PANTALLA: texto "¿Y LOS DATOS?"
7. [cierre] NEWTON (explicando_pluma) | fondo: estudio
   DICE: Nadie la va a fabricar, pero marca el límite: nada de ese tamaño puede guardar más. ¿Qué guardarías tú?
   PANTALLA: texto "EL LÍMITE"

## Datos que hay que verificar

- La entropía (información) de un agujero negro es proporcional al área de su horizonte, no a su volumen: S = k·A / (4·ℓp²). Bekenstein (1972–1973) y Hawking (1974–1975). Fuente sugerida: Bekenstein, Phys. Rev. D 7, 2333 (1973); Hawking, Commun. Math. Phys. 43 (1975). Confianza: alta.
- Cálculo propio: horizonte de radio 1 cm → A = 4π(0.01 m)² = 1.26×10⁻³ m²; bits = A / (4·ℓp²·ln 2) con ℓp = 1.616×10⁻³⁵ m → ≈ 1.7×10⁶⁶ bits. Confianza: alta (verificar la cuenta).
- 1 TB = 8×10¹² bits; 1.7×10⁶⁶ / 8×10¹² ≈ 2×10⁵³. Confianza: alta.
- Masa para un horizonte de 1 cm: M = r·c² / (2G) ≈ 6.7×10²⁴ kg ≈ 1.1 masas terrestres (el radio de Schwarzschild de la Tierra es ~9 mm). Fuente sugerida: cualquier libro de relatividad; NASA. Confianza: alta.
- La "paradoja de la información" (si la información que cae se recupera con la radiación de Hawking) sigue abierta, aunque hay avances desde 2019 (curva de Page, "islas"). Fuente sugerida: Quanta Magazine (2020) sobre la paradoja de la información. Confianza: alta (que se discute).
- Límite holográfico / cota de Bekenstein: ninguna región con esa superficie puede contener más información que un agujero negro del mismo tamaño. Fuente sugerida: Bousso, Rev. Mod. Phys. 74 (2002). Confianza: alta.

## Imágenes nuevas

- objetos/memoria_usb: a cartoon USB flash drive, blue plastic body with a silver metal connector

## Notas

- Idea del creador (13 nov 2026). Interpretación: "la memoria USB definitiva" = cuánta información cabe en un agujero negro (límite holográfico). Si el creador pensaba en otra cosa, ajustar.
- Turing (computación) da las cifras de bits. "Un uno con 66 ceros" se dice así para la voz; en pantalla, 10⁶⁶.
