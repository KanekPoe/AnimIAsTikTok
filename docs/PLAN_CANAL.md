# Plan del canal de datos curiosos científicos

Canal nuevo (TikTok + YouTube Shorts), presentado por los robots. Un video diario al inicio;
3 por semana cuando haya público. Rigor como marca: **cada dato con fuente verificada**.

## Restricciones de partida

- **Sin GPU**: todo se renderiza en la nube (CPU, EEVEE por software). Hoy: ~10 s por
  cuadro a 1080p. Un video de 105 s tardó ~8.5 h.
- **Voces gratuitas**: Piper, voz `carlfm`, con tono y efecto distinto por robot.
- **Sesión en la nube efímera**: lo que no esté en el repo se pierde cuando la sesión se
  cierra. Los videos se entregan apenas terminan.
- **Límite de 2 h por proceso en segundo plano**: el render va por tandas.

## Presupuesto de tiempo por video

| Ajuste | Efecto |
|---|---|
| Duración 20–40 s (no 105) | ~3× menos cuadros |
| 24 fps en vez de 30 | 20 % menos cuadros |
| Sets simples y reutilizables, menos luces | ~30 % menos por cuadro |
| Lo complejo (diagramas, datos, mapas) en 2D, no en 3D | Casi gratis |

Meta: **un video de 30 s en ~1.5 h de render**. Siete por semana ≈ 10–11 h de render,
repartidas en tandas.

## Tubería (de idea a video)

1. **Banco de ideas**: lista con categoría, formato y estado (idea → verificado →
   guion → aprobado → render → entregado → publicado).
2. **Verificación (obligatoria)**:
   - Al menos 2 fuentes serias e independientes, de preferencia primarias (agencia
     científica, estudio revisado por pares, universidad, enciclopedia de referencia).
   - Anotar la cifra exacta, la fuente y el enlace. Redondear con honestidad y decir "se
     estima" cuando sea una estimación.
   - Si las fuentes no coinciden o no se encuentran, **el dato no entra**.
   - Preferir datos que se puedan visualizar.
3. **Guion** (un archivo por video): formato, set, robots, frases, gags, cifra en pantalla
   y fuentes. 20–40 s; gancho en el segundo 0; 1–2 robots por video.
4. **Aprobación**: los 7 guiones de la semana, en texto, de una vez.
5. **Voces + línea de tiempo**: Piper con control automático de ritmo.
6. **Escena**: set de la biblioteca, objeto protagonista y animación del formato.
7. **Render** por tandas; cuadros de prueba antes del render completo.
8. **Composición**: subtítulos, la cifra en grande, "Fuente: …" en pantalla, pregunta
   para comentarios, contador o etiqueta del formato.
9. **Control de calidad automático**: duración, zonas seguras, volumen (-14 LUFS), sin
   cuadros faltantes, texto dentro de pantalla.
10. **Entrega**: el video, la descripción con fuentes y el comentario fijado.
11. **Tu revisión y publicación**: escuchar el audio (yo no puedo), activar la etiqueta
    de contenido IA, programar la publicación.
12. **Métricas**: me pasas las capturas y las registro.

## Formatos (plantillas)

| Formato | Estructura (≈30 s) |
|---|---|
| **¿Verdad o mito?** | Afirmación (0–3 s) → robots votan → revelación con la fuente → por qué |
| **Escala** | "Si X fuera del tamaño de Y…" → animación de comparación → cifra final |
| **Dato rápido** | Dato imposible (0–2 s) → visualización → explicación → remate |
| **Mito desmentido** | Lo que todos creen → "pero el estudio dice…" → la cifra real |

## Calendario semanal

| Día | Formato / tema |
|---|---|
| Lunes | ¿Verdad o mito? |
| Martes | Escala |
| Miércoles | Animales |
| Jueves | Cuerpo humano |
| Viernes | Espacio |
| Sábado | Física cotidiana |
| Domingo | Mito desmentido o pregunta de la audiencia |

## Biblioteca de escenarios (se construye una vez)

Espacio · Laboratorio · Cuerpo humano · Naturaleza · Ciudad · Estudio de los robots.
Más una biblioteca de objetos: planetas, átomo, ADN, célula, gota, termómetro, regla de
escala, signos de verdadero/falso, etc. Lo que sea difícil en 3D (animales complejos,
mapas, diagramas) va como gráfico 2D en pantalla o en el holograma.

## Flujo semanal (fase diaria)

| Cuándo | Qué | Quién |
|---|---|---|
| Lunes | Propongo 7–10 datos con sus fuentes | Claude |
| Lunes | Eliges 7 | Tú |
| Lunes–martes | Guiones de los 7, en texto | Claude → tú apruebas |
| Martes–sábado | Voces, cuadros de prueba, render por tandas; cada video se entrega al terminar | Claude |
| Al recibir cada video | Escuchar, revisar y programar | Tú |
| Domingo | Capturas de métricas; ajuste para la semana siguiente | Tú → Claude |

**Colchón**: lanzar con **7–10 videos listos**, para que un día malo no rompa la racha
diaria.

## Fase de arranque (una sola vez, antes de publicar)

1. **Cuentas nuevas** (tú):
   - Correo o cuenta de Google dedicada al canal y verificación en dos pasos.
   - Mismo nombre y usuario en TikTok y YouTube.
   - TikTok como cuenta de creador, no de empresa (las de empresa limitan la música).
   - YouTube como cuenta de marca.
   - Foto de perfil con los robots, bio y banner.
2. **Tubería** (yo):
   - Plantillas de los 4 formatos.
   - Biblioteca de sets y objetos.
   - Fuente en pantalla.
   - Control de calidad automático.
   - Ajustes de velocidad (24 fps, sets livianos).
3. **Entorno de la nube** (yo, con tu aprobación): que cada sesión nueva arranque con
   Blender, Piper, las voces y las fuentes instalados.
4. **Piloto**: 3 videos de prueba para medir el tiempo real y ajustar.
5. **Colchón** de 7–10 videos y lanzamiento.

## Reglas de rigor

- Ningún dato sin 2 fuentes; las cifras con su incertidumbre.
- La fuente principal va en pantalla y todas en la descripción.
- Política de correcciones: si un dato resulta mal, comentario fijado con la corrección
  y se registra.
- Contenido marcado como generado con IA en ambas plataformas.
- Los robots son caricaturas; nunca sugerir patrocinio ni representación oficial.

## Métricas (revisión semanal)

- Retención a 3 s (meta orientativa ≥ 65–70 %).
- Tiempo promedio de visualización y % que lo ve completo.
- Me gusta, comentarios y guardados por cada 1000 vistas.
- Qué formato y tema funcionan mejor.
- Una sola cosa cambia por semana.

## Pendientes de decidir

- Nombre y usuario del canal.
- Si los robots conservan los nombres y la estética de las marcas de IA (Claude, ChatGPT,
  Gemini…) o pasan a ser personajes propios. En un canal de ciencia, los personajes
  propios evitan problemas de marca y no dependen de cómo cambien esas empresas.
