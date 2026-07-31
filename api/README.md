# API de ComfyUI — capítulos 10, 11 y 17

Los tres scripts usan el formato API de los workflows (`.api.json`), no el
formato de la interfaz (`.json`). Cada workflow del repositorio existe en
las dos versiones: `.json` para arrastrar al lienzo y `.api.json` para
consumir desde código.

Instala las dependencias con `pip install -r ../requirements.txt`.

| Archivo | Capítulo | Qué contiene |
| --- | --- | --- |
| `comfy_api.py` | 10 | Funciones de la API: `send_workflow`, `upload_image`, `get_output_files`, `validate_workflow_nodes`, `patch_workflow`, `wait_for_completion` (WebSocket) y `process_batch` |
| `batch_runner.py` | 11 | Procesador de secuencias: plantilla con centinelas, semilla determinista por frame, reintentos y traza JSONL |
| `SH0170_api_runner.py` | 17 | Ciclo del shot: un workflow por frame, espera con timeout y registro de frame, semilla y hash del workflow |

## Uso

Validar que un servidor tiene los nodos que el workflow necesita:

```
python comfy_api.py ../workflows/06_control/06_controlnet_canny.api.json
```

Procesar una secuencia a partir de una shot list en CSV con columnas
`shot,frame,plate,mask`:

```
python batch_runner.py plantilla.api.json shotlist.csv
```

Generar una capa auxiliar del shot SH0170 sobre un rango de frames:

```
python SH0170_api_runner.py ../nuke/SH0170_depth_v01.api.json \
  --frames 1001-1010 --pattern 'SH0170.%04d.png' --out-prefix SH0170_depth
```

`--pattern` acepta tanto un nombre ya presente en la carpeta `input/` del
servidor como una ruta del disco: en ese segundo caso el script sube el
archivo por `/upload/image` antes de encolar el frame.

## Nodos de guardado

Los scripts reescriben el `filename_prefix` tanto de `SaveImage` como de
`SaveEXR`, así que funcionan con los dos tipos de workflow sin cambios. Los
cuatro workflows de `../nuke/` y `16_plate_hero` usan `SaveEXR` con `tonemap`
en `linear`; los doce demostrativos usan `SaveImage`. El criterio está en
`../POLITICA.md`.

Con `filename_prefix` relativo, `SaveEXR` numera igual que `SaveImage`, con un
contador (`_00001_`). Con una ruta absoluta usa en cambio la numeración de
secuencia de producción (`nombre_v001.1001.exr`), gobernada por sus knobs
`version`, `start_frame` y `frame_pad`. Y a diferencia de `SaveImage`, se
niega a sobrescribir un archivo que ya existe.
