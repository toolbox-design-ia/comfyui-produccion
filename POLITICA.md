# Por qué unos workflows guardan en PNG y otros en EXR

No es una inconsistencia: es la distinción que el capítulo 13 del libro
desarrolla, aplicada al material.

## Los que guardan en EXR (`SaveEXR`, `tonemap = linear`)

| Workflow | Capítulo |
| --- | --- |
| `nuke/SH0170_depth_v01` | 14, 17 |
| `nuke/SH0170_normals_v01` | 14, 17 |
| `nuke/SH0170_cleanplate_v01` | 15, 17 |
| `nuke/SH0170_relight_v01` | 15, 17 |
| `workflows/16_17_proyectos/16_plate_hero` | 16, 17 |

Todos alimentan el ida y vuelta con Nuke. Son datos de escena, no imágenes
de pantalla: un mapa de profundidad métrico, un campo de normales con
valores entre -1 y 1, una plate con altas luces por encima de 1.0. Guardar
eso en PNG de ocho bits recorta los valores fuera del rango 0-1 de forma
irreversible, que es exactamente el error que el capítulo 13 enseña a
evitar. Dejarlos en PNG habría desmentido al libro con el archivo delante.

El knob `tonemap` va en `linear` en los cinco, declarado explícitamente y no
heredado del valor por defecto. Ese valor por defecto es `sRGB`, y con él el
nodo aplica una conversión de curva antes de escribir que deshace justo lo que
se buscaba. Medido sobre la misma imagen guardada de las dos formas: cambia el
100 % de los píxeles, con una diferencia media de 0,22 sobre un rango de 0 a 1,
y un gris medio de 0,314 sale como 0,080. El archivo sigue siendo un EXR válido
en coma flotante de 32 bits, así que el error no se manifiesta hasta mucho más
abajo en el pipeline.

**Requisito:** estos cinco workflows necesitan el paquete
[`ComfyUI-HQ-Image-Save`](https://github.com/spacepxl/ComfyUI-HQ-Image-Save),
que aporta el nodo `SaveEXR`. Sin él, el nodo de guardado aparece en rojo al
cargar el workflow. Se instala desde el Manager o clonándolo en
`custom_nodes/`, como cualquier otro custom node.

## Los que guardan en PNG (`SaveImage`)

Los doce restantes: `03_txt2img_basico`, los cuatro de `05_modelos/`, los
dos de `06_control/`, los tres de `07_loras/` y los dos de `08_upscaling/`.

Son ejercicios demostrativos. Enseñan la interfaz, comparan modelos, ilustran
un mecanismo de control o una estrategia de escalado, y su resultado se mira
en pantalla. Ahí el PNG de ocho bits es el formato correcto: meter EXR sería
ruido, obligaría a instalar una dependencia que el ejercicio no necesita y
haría más difícil comprobar el resultado de un vistazo.

Si alguno de esos grafos se lleva a producción —un inpainting que va a comp,
un upscale de una plate real— el cambio es de un nodo: sustituir `SaveImage`
por `SaveEXR` y poner `tonemap` en `linear`. Los cinco de arriba sirven de
plantilla de cómo queda.
