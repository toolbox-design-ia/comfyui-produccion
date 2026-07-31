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
│   ├── 03_interfaz/         03_txt2img_basico
│   ├── 05_modelos/          05_sd15, 05_sdxl, 05_flux_dev, 05_flux_schnell
│   ├── 06_control/          06_img2img, 06_controlnet_canny
│   ├── 07_loras/            07_lora_estilo, 07_inpainting, 07_outpainting
│   ├── 08_upscaling/        08_upscale_esrgan, 08_hires_fix
│   └── 16_17_proyectos/     16_plate_hero
├── nuke/                    Capas auxiliares del shot SH0170: depth, normals, cleanplate, relight
├── api/                     Scripts de Python de los capítulos 10, 11 y 17
├── ejemplos/                Imágenes de entrada para reproducir los ejercicios
├── models/                  MODELOS.md: qué modelo usa cada workflow y dónde colocarlo
├── requirements.txt
├── README.md
└── LICENSE
```

Cada carpeta lleva su propio `README.md` con el detalle de sus archivos.

## Correspondencia capítulo → material

| Capítulo | Carpeta | Archivos |
| --- | --- | --- |
| 3. La interfaz y el grafo | `workflows/03_interfaz/` | `03_txt2img_basico` |
| 5. Los modelos de 2026 | `workflows/05_modelos/` | `05_sd15_txt2img`, `05_sdxl_txt2img`, `05_flux_dev_txt2img`, `05_flux_schnell_txt2img` |
| 6. Control de la imagen | `workflows/06_control/` | `06_img2img`, `06_controlnet_canny` |
| 7. LoRAs, inpainting y outpainting | `workflows/07_loras/` | `07_lora_estilo`, `07_inpainting`, `07_outpainting` |
| 8. Upscaling a fondo | `workflows/08_upscaling/` | `08_upscale_esrgan`, `08_hires_fix` |
| 10. La API de ComfyUI | `api/` | `comfy_api.py` |
| 11. Batch y pipeline | `api/` | `batch_runner.py` |
| 12-17. Integración con Nuke | `nuke/` | `SH0170_depth_v01`, `SH0170_normals_v01`, `SH0170_cleanplate_v01`, `SH0170_relight_v01` |
| 16. Proyecto: del concept a la plate | `workflows/16_17_proyectos/` | `16_plate_hero` |
| 17. Proyecto: un shot completo en Nuke | `api/`, `nuke/` | `SH0170_api_runner.py` + los cuatro workflows de `nuke/` |

Los capítulos 1, 2, 4, 9, 13, 14 y 15 no traen workflow propio: exponen
conceptos, procedimientos de instalación o criterios de composición que se
aplican sobre los grafos de los demás capítulos.

**Estado de pruebas.** Los 17 workflows están validados grafo a grafo contra
ComfyUI 0.21.1 (nodos, tipos y modelos presentes), y tres se ejecutaron de
principio a fin como prueba de humo (SD 1.5 txt2img, upscale Real-ESRGAN y
depth). Cada workflow existe en formato interfaz (`.json`) y API
(`.api.json`).

**Salida en EXR.** Todos los workflows guardan con `SaveImage`, que escribe
PNG de ocho bits. Los capítulos 13, 14 y 17 exigen coma flotante para las
capas de datos y para el ida y vuelta con Nuke: para eso hay que sustituir
ese nodo por `SaveEXR` del paquete `ComfyUI-HQ-Image-Save` y poner su knob
`tonemap` en `linear`. Está explicado en `api/README.md` y desarrollado en
el capítulo 13.

## Licencia

MIT para los workflows y el código. El texto del libro tiene todos los
derechos reservados.
