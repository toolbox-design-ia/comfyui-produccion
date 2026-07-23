# ComfyUI en producción — Material del libro

Repositorio companion del libro **«ComfyUI en producción»**
(Henry Ramírez Reyes, colección IA APLICADA A LA POSTPRODUCCIÓN, Studio35).

Aquí viven los workflows `.json` de cada capítulo, los snippets de la API
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

## Correspondencia capítulo → material

| Capítulo | Carpeta |
| --- | --- |
| 3. La interfaz y el grafo | `workflows/03_interfaz/` |
| 5. Los modelos de 2026 | `workflows/05_modelos/` |
| 6. Control de la imagen | `workflows/06_control/` |
| 7. LoRAs, inpainting y outpainting | `workflows/07_loras/` |
| 8. Upscaling a fondo | `workflows/08_upscaling/` |
| 10. La API de ComfyUI | `api/` |
| 11. Batch y pipeline | `api/` |
| 12-15. Integración con Nuke | `nuke/` |
| 16-17. Proyectos finales | `workflows/16_17_proyectos/` |

Los workflows se publican junto con el libro; cada uno se prueba en una
instalación real de ComfyUI antes de subirlo.

## Licencia

MIT para los workflows y el código. El texto del libro tiene todos los
derechos reservados.
