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

## Nota sobre EXR

Los workflows de este repositorio guardan con `SaveImage`, que escribe PNG
de ocho bits. Para las capas de datos que los capítulos 13, 14 y 17
describen —depth y normales en coma flotante— hay que sustituir ese nodo
por `SaveEXR` del paquete `ComfyUI-HQ-Image-Save`, con el knob `tonemap`
en `linear`. Los scripts de esta carpeta ya reescriben el
`filename_prefix` de ambos nodos, así que el cambio no exige tocar el
código.
