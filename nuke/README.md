Caps. 12-17 — capas auxiliares del shot SH0170 con los nombres exactos del
capitulo 17: depth (DepthAnything), normales (BAE), clean plate (inpainting)
y relight (img2img a denoise 0.5; el capitulo menciona tambien relighting
neural dedicado). Se automatizan por frames con `../api/SH0170_api_runner.py`.

Los cuatro guardan con **`SaveEXR`** y el knob **`tonemap` en `linear`**: son
datos de escena que vuelven a Nuke y no admiten el recorte a 0-1 del PNG de
ocho bits. Requieren el paquete `ComfyUI-HQ-Image-Save` instalado en el
servidor; sin el, el nodo de guardado aparece en rojo al cargar el workflow.
El porque esta en `../POLITICA.md` y desarrollado en el capitulo 13.

Los cuatro pasan la validacion de /prompt contra un ComfyUI real con
HQ-Image-Save instalado. No se han ejecutado E2E con sus modelos porque la
maquina de validacion solo pudo arrancar en modo CPU y el preprocesador de
profundidad requiere CUDA.
