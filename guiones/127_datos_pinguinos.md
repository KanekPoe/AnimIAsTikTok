---
n: 127
slug: datos_pinguinos
categoria: Animales
idea: Datos sorprendentes de los pingüinos
colega: darwin
badge: DATO ANIMAL
cta: ¿Cuál de estos datos te voló más la cabeza? 👇
estado: base
prioridad: creador
---

## Guion

1. [gancho] NEWTON (senalando) | fondo: estudio
   DICE: Los pingüinos estornudan sal y no tienen huesos huecos como otras aves. Wacha qué locura.
   PANTALLA: objetos/pinguino_nadando · texto "ESTORNUDAN SAL"
2. [dato] NEWTON (voz) | fondo: oceano
   DICE: Sus huesos son sólidos y pesados. Eso funciona como lastre para sumergirse sin flotar como corcho.
   PANTALLA: objetos/hueso_pinguino · texto "HUESOS SÓLIDOS"
3. [dato] NEWTON (voz) | fondo: oceano
   DICE: Pueden beber agua de mar porque una glándula sobre sus ojos filtra la sal y la saca por el pico.
   PANTALLA: objetos/sal_cristales · texto "FILTRO NATURAL"
4. [dato] COLEGA:darwin (explicando) | fondo: estudio
   DICE: Y su esmoquin es camuflaje: espalda negra para esconderse desde arriba y panza blanca desde abajo.
   PANTALLA: objetos/pinguino_nadando
5. [dato] NEWTON (voz) | fondo: oceano
   DICE: El pingüino emperador bucea a más de 500 metros y aguanta la respiración por más de 20 minutos.
   PANTALLA: texto "500 m · 20 min"
6. [giro] NEWTON (asustado) | fondo: estudio
   DICE: Una vez al año pasan por una muda catastrófica: cambian todas sus plumas a la vez y ayunan por semanas.
   PANTALLA: texto "MUDA CATASTRÓFICA"
7. [cierre] NEWTON (explicando_pluma) | fondo: estudio
   DICE: ¿Sabías que hasta hay pingüinos en el ecuador? ¿Qué otro animal te gustaría ver aquí?
   PANTALLA: objetos/tierra · texto "¿EN EL ECUADOR?"

## Datos que hay que verificar

- Los pingüinos tienen huesos densos y sólidos (osteosclerosis) en lugar de neumáticos para reducir la flotabilidad. Fuente sugerida: Smithsonian Ocean / artículos de anatomía aviar. Confianza: alta.
- La glándula supraorbital filtra el exceso de cloruro de sodio de la sangre y lo excreta en solución salina por las fosas nasales/pico. Fuente sugerida: National Geographic / estudios de fisiología marina. Confianza: alta.
- El pingüino emperador (Aptenodytes forsteri) puede sumergirse a más de 500 metros (récords superiores a 530 m) y permanecer sumergido más de 20 minutos. Fuente sugerida: British Antarctic Survey / Woods Hole Oceanographic Institution. Confianza: alta.
- La muda catastrófica ocurre una vez al año y dura entre 2 y 4 semanas, periodo en el que pierden impermeabilidad y ayunan en tierra. Fuente sugerida: Penguins International / Audubon. Confianza: alta.
- El pingüino de las Galápagos (Spheniscus mendiculus) habita en la línea ecuatorial. Fuente sugerida: UICN / Galápagos Conservancy. Confianza: alta.

## Imágenes nuevas

- objetos/pinguino_nadando: a cute cartoon penguin swimming underwater with flippers spread
- objetos/hueso_pinguino: a solid dense cartoon bird bone cross-section without air pockets

## Notas

- Guion del creador (13 nov 2026, escrito con otro LLM usando guiones/BRIEF_LLM.md). Llegó como n: 48; se renumeró a 127 (el 48 ya existe) y entra como prioridad del creador.
- Cambio de rigor: "pierden todas sus plumas de golpe" -> "cambian todas sus plumas a la vez" (las plumas nuevas empujan a las viejas durante 2–4 semanas; no se quedan pelones de golpe).
- Darwin tiene 1 línea.
