# ComfyUI en producción — Material del libro

Repositorio companion del libro **«ComfyUI en producción»**
(Henry Ramírez Reyes, colección IA APLICADA A LA POSTPRODUCCIÓN, Studio35).

Aquí viven los workflows `.json` de cada capítulo, los scripts de la API
y la lista de modelos con sus enlaces de descarga. El Anexo A del libro
explica, paso a paso, cómo descargar este repositorio, cómo cargar un
workflow en ComfyUI y dónde colocar cada modelo.

## Cómo usar este repositorio

1. Descarga el repositorio: botón verde **Code → Download ZIP** (no hace
   falta cuenta de GitHub) y descomprime el archivo.
2. Arrastra el `.json` del capítulo al lienzo de ComfyUI (o menú
   **Workflow → Open**).
3. Si aparecen nodos en rojo: **Manager → Install missing custom nodes**
   (Anexo B del libro).
4. Los modelos que usa cada workflow están en `models/MODELOS.md` con su
   enlace de descarga y la carpeta exacta donde colocarlos.
5. Para los scripts de `api/`: `pip install -r requirements.txt`.

## Árbol de carpetas

```
comfyui-produccion/
├── workflows/               Grafos por capítulo, en formato interfaz (.json) y API (.api.json)
│   ├── 03_interfaz/
│   ├── 05_modelos/
│   ├── 06_control/
│   ├── 07_loras/
│   ├── 08_upscaling/
│   └── 16_17_proyectos/
├── nuke/                    Capas auxiliares del shot SH0170: depth, normales, clean plate y relight
├── api/                     Scripts de Python de los capítulos 10, 11 y 17
├── ejemplos/                Imágenes de entrada para reproducir los ejercicios
├── models/                  MODELOS.md: qué modelo usa cada workflow y dónde colocarlo
├── POLITICA.md              Por qué unos workflows guardan en PNG y otros en EXR
├── requirements.txt
├── README.md
└── LICENSE
```

Cada carpeta lleva su propio `README.md` con el detalle de sus archivos.

## Correspondencia capítulo → material

| Capítulo | Carpeta | Archivos | Salida |
| --- | --- | --- | --- |
| 3. La interfaz y el grafo | `workflows/03_interfaz/` | `03_txt2img_basico` | PNG |
| 5. Los modelos de 2026 | `workflows/05_modelos/` | `05_sd15_txt2img`, `05_sdxl_txt2img`, `05_flux_dev_txt2img`, `05_flux_schnell_txt2img` | PNG |
| 6. Control de la imagen | `workflows/06_control/` | `06_img2img`, `06_controlnet_canny` | PNG |
| 7. LoRAs, inpainting y outpainting | `workflows/07_loras/` | `07_lora_estilo`, `07_inpainting`, `07_outpainting` | PNG |
| 8. Upscaling a fondo | `workflows/08_upscaling/` | `08_upscale_esrgan`, `08_hires_fix` | PNG |
| 10. La API de ComfyUI | `api/` | `comfy_api.py` | — |
| 11. Batch y pipeline | `api/` | `batch_runner.py` | — |
| 12-17. Integración con Nuke | `nuke/` | `SH0170_depth_v01`, `SH0170_normals_v01`, `SH0170_cleanplate_v01`, `SH0170_relight_v01` | **EXR** |
| 16. Proyecto: del concept a la plate | `workflows/16_17_proyectos/` | `16_plate_hero` | **EXR** |
| 17. Proyecto: un shot completo en Nuke | `api/`, `nuke/` | `SH0170_api_runner.py` + los cuatro workflows de `nuke/` | **EXR** |

Los capítulos 1, 2, 4, 9, 13, 14 y 15 no traen workflow propio: exponen
conceptos, procedimientos de instalación o criterios de composición que se
aplican sobre los grafos de los demás capítulos.

## Dos políticas de guardado, y por qué

Los cinco workflows que alimentan el ida y vuelta con Nuke —las cuatro capas
del shot SH0170 y la plate hero del capítulo 16— guardan con **`SaveEXR`** y
el knob **`tonemap` en `linear`**. Son datos de escena: profundidad, normales,
altas luces por encima de 1.0. Guardarlos en PNG de ocho bits recorta esos
valores de forma irreversible, que es justo el error que el capítulo 13 enseña
a evitar.

Los doce restantes son ejercicios demostrativos —aprender la interfaz,
comparar modelos, ilustrar un control— y guardan con **`SaveImage`** en PNG,
que ahí es el formato correcto y no obliga a instalar nada extra.

El razonamiento completo, con la tabla de cuál es cuál, está en
[`POLITICA.md`](POLITICA.md).

> **Dependencia de los workflows en EXR.** `SaveEXR` viene del paquete
> [`ComfyUI-HQ-Image-Save`](https://github.com/spacepxl/ComfyUI-HQ-Image-Save).
> Sin él instalado, esos cinco workflows cargan con el nodo de guardado en
> rojo. Es el mismo procedimiento que el Anexo B describe para cualquier
> custom node que falte.

**Estado de pruebas.** Los 17 workflows están validados grafo a grafo contra
ComfyUI 0.21.1 (nodos, tipos y modelos presentes), y tres se ejecutaron de
principio a fin como prueba de humo (SD 1.5 txt2img, upscale Real-ESRGAN y
depth). Cada workflow existe en formato interfaz (`.json`) y API
(`.api.json`).

Los cinco workflows convertidos a `SaveEXR` se validaron además **contra un
ComfyUI real** con `ComfyUI-HQ-Image-Save` instalado: los cinco pasan la
validación de `/prompt` sin un solo error de nodo, y las ocho entradas
obligatorias de `SaveEXR` coinciden en nombre, orden, tipo y dominio con las
que declara el servidor. Aparte, `SaveEXR` se ejecutó de principio a fin con
`tonemap` en `linear` y en `sRGB`: ambos escriben un OpenEXR válido en coma
flotante de 32 bits, y la diferencia entre los dos afecta al 100 % de los
píxeles (media 0,22 sobre un rango de 0 a 1). Esa medición es la que sostiene
la advertencia del capítulo 13.

No se han ejecutado de extremo a extremo los cuatro workflows de `nuke/` con
sus modelos: la validación se hizo en modo CPU y `DepthAnythingPreprocessor`
requiere CUDA. Es una limitación del entorno de prueba, no de los workflows.

## Licencia

MIT para los workflows y el código. El texto del libro tiene todos los
derechos reservados.
