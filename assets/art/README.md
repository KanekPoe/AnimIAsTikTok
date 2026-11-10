# Arte del canal (Newton Bien Loco)

Ilustraciones generadas por el autor del canal; recortadas con `pipeline/cutout.py`
(fondo verde → transparencia, sin borde blanco, sin halo verde).

| Carpeta | Contenido |
|---|---|
| `raw/` | Originales tal como se generaron |
| `newton/` | 4 poses de cuerpo completo (`pose_*`) y 6 caras (`cara_*`). `cara_ojos_cerrados_serio` se espejó para mirar al mismo lado que las demás |
| `objetos/` | 9 manzanas (una mordida), telescopio, prisma con arcoíris, 4 grupos de libros |
| `fondos/` | **Estudio en vertical (1080x1920, con piso)**; jardín con manzano, estudio y espacio en horizontal (1116x663) y la escena completa del manzano (2000x1116) |

Pendiente: fondos en vertical 1080x1920 (los actuales pierden nitidez al ampliarse ~3x),
variantes de boca de cada pose para hablar, y Manzanita.

## Escala de Newton en el estudio vertical

Horizonte ≈ y 435; el escritorio (75 cm) mide ~225 px con las patas en y≈920. Para que Newton
(175 cm) quede en proporción con los pies en `feet_y`:
`altura = 525 * (feet_y - 435) / (920 - 435)` (≈1466 px con los pies en y=1790).
