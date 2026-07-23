# API de ComfyUI — capitulos 10, 11 y 17

`SH0170_api_runner.py` es el ciclo de automatizacion del capitulo 17:
envia un workflow por frame (`/prompt`), espera el resultado
(`/history`) y registra frame, semilla y hash del workflow en un JSONL
de trazas. Uso:

```
python SH0170_api_runner.py ../nuke/SH0170_depth_v01.api.json \
  --frames 1001-1010 --pattern 'SH0170.%04d.png' --out-prefix SH0170_depth
```

Cada workflow del repositorio tiene dos versiones: `.json` (formato de
la interfaz, para arrastrar al lienzo) y `.api.json` (formato de la
API, el que consume este script).
