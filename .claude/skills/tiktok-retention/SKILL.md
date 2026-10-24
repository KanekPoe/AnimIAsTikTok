---
name: tiktok-retention
description: Reglas de edición para maximizar la retención en videos de TikTok de este proyecto (animaciones en Blender donde los robots LLM responden una pregunta). Úsala al planear una escena nueva, escribir el guion/gancho, decidir duración, orden de los robots, ritmo de cortes, subtítulos, audio o el cierre de un video; y al revisar un video renderizado antes de publicarlo.
---

# Retención en TikTok — guía del proyecto

Formato del canal: **"Le preguntamos lo mismo a 6 IAs"**. Robots de `blender/build_models.py`
(Claude, ChatGPT, Gemini, DeepSeek, Grok, Mistral) responden una pregunta del usuario en una
misma sala. Vertical 1080x1920, 30 fps.

> Nota sobre la evidencia: casi todos los números vienen de blogs de agencias/herramientas,
> no de TikTok. Úsalos como referencia, no como ley. Lo único oficial: guía de TikTok Ads
> (9:16 a pantalla completa ≈ +25 % de visualización a 6 s; texto corto superpuesto).
> La fuente de verdad final es la gráfica de retención del propio canal.

## Principios (consenso de fuentes)

1. **Los primeros 1–3 s deciden todo.** Empezar en plena acción: sin intro, sin logo, sin
   "hola". Gancho escrito en pantalla desde el cuadro 0. Meta orientativa: ≥65–70 % sigue
   viendo al segundo 3.
2. **Duración 21–34 s** para máxima tasa de finalización. Más largo solo si la retención se
   sostiene (gana en tiempo total visto, pierde en % completado).
3. **Cambio visual cada 1–3 s**: corte, zoom, movimiento de cámara, reacción o nueva línea de
   subtítulo. Nunca una toma estática > 3 s.
4. **Texto siempre en pantalla + sonido diseñado.** TikTok se ve mayormente con sonido, pero
   los subtítulos sostienen a quien lo ve en silencio.
5. **Zona segura (1080x1920)**: evitar arriba ~250 px, derecha ~175 px y todo debajo de
   ~1450 px. Texto importante en el **tercio medio, un poco arriba del centro**.
6. **Loop abierto**: prometer algo al inicio ("la última…") y guardar lo más fuerte para el
   final. Formatos de lista rinden mejor con el mejor elemento al último.
7. **Final en loop**: el último cuadro debe conectar con el primero para provocar re-vista.
   Nunca terminar en un cuadro muerto/negro.

## Plantilla de escena (~33 s)

| Tiempo | Bloque | Contenido |
|---|---|---|
| 0–2 s | Gancho | Acción inmediata (p. ej. objeto cae + SFX fuerte, los 6 robots giran a la vez). Texto grande con la tensión de la pregunta + loop abierto. |
| 2–29 s | 6 turnos × ~4.5 s | Cada turno = 3–4 planos: entrada del robot → primer plano hablando (boca LED animada) → gag visual en la pantalla del fondo que ilustre SU respuesta → reacción de otro robot. |
| 29–33 s | Cierre | Los 6 en fila con etiqueta de 1–2 palabras cada uno + pregunta para comentarios ("¿A cuál le darías…? 👇"). Último cuadro = primer cuadro del gancho (loop). |

Reglas de contenido:
- **Orden**: de la respuesta más tranquila a la más impactante; la más fuerte al final.
- **Gancho honesto**: el loop abierto debe cumplirse con las respuestas reales. Nunca
  inventar ni exagerar lo que dijo un modelo; resumir fielmente sus respuestas.
- **Texto por turno**: 2–3 frases cortas máximo; resumir, no leer la respuesta completa.
- **Contador de progreso** "n/6" en esquina segura (heurística propia, no dato de fuentes).
- **Misma sala y estructura** en cada pregunta → formato de serie reconocible.

## Subtítulos

- Grandes, palabra por palabra (o 2–3 palabras), en el tercio medio.
- Palabra clave resaltada con el color del robot que habla:
  Claude `#D97757`, ChatGPT `#10A37F`, Gemini `#4285F4`→`#9B72CB`, DeepSeek `#4D6BFE`,
  Grok `#FFFFFF`, Mistral `#FA500F`.
- Contorno/sombra oscura para legibilidad sobre cualquier fondo.

## Audio

- Voz robótica distinta por modelo, boca LED (`<n>_mouth`, escala Z) sincronizada.
- SFX en cada evento: golpe/mazo en el gancho, whoosh en cada corte, beeps en reacciones.
- Exportar además una **versión sin música** para poder usar un audio en tendencia en la app.

## Checklist antes de publicar

- [ ] ¿El cuadro 0 ya tiene acción y texto? ¿Se entiende el tema en < 2 s?
- [ ] ¿Duración ≤ ~35 s?
- [ ] ¿Ninguna toma estática > 3 s?
- [ ] ¿Todo el texto dentro de la zona segura? (revisar un fotograma con superposición)
- [ ] ¿Se entiende sin sonido? ¿Y con sonido suena vivo?
- [ ] ¿La respuesta más fuerte va al final y cumple lo prometido en el gancho?
- [ ] ¿El final enlaza con el inicio (loop) y tiene pregunta para comentarios?

## Después de publicar

Revisar en TikTok Studio la gráfica de retención:
- Caída en 0–3 s → cambiar el gancho.
- Caída a mitad → acortar turnos o meter más cambios visuales.
- Probar dos versiones con distinto gancho y comparar.

## Fuentes

- TikTok Ads – Auction Ads Creative Tips (oficial): https://ads.tiktok.com/business/library/Auction_Ads_Creative_Tips.pdf
- OpusClip – duración y retención: https://www.opus.pro/blog/tiktok-length-format-retention-data
- SocialBu – duración ideal: https://socialbu.com/blog/ideal-lenghth-of-tiktok-videos
- Flowshorts – duración: https://flowshorts.app/blog/how-long-can-tiktok-be
- Greedier Social Media – benchmarks 2026: https://greediersocialmedia.co.uk/tiktok-views-retention/
- Sozee – edición para retención: https://www.sozee.ai/resources/edit-tiktok-trend-videos-retention/
- Dynamoi – regla de 3 s: https://dynamoi.com/learn/tiktok-music-promotion/what-is-the-3-second-rule-on-tiktok
- PostPlanify – zonas seguras: https://postplanify.com/tools/tiktok-safe-zone-checker
- SamAutomation – subtítulos: https://samautomation.work/blog/tiktok-captions-engagement-strategy/
- Socialk.it – retención y storytelling: https://socialk.it/en/blog/tiktok-retention-watch-time-guide , https://socialk.it/en/blog/tiktok-storytelling-guide
- Smartly – buenas prácticas creativas: https://www.smartly.io/blog/top-5-tiktok-creative-best-practices
