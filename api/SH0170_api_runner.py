"""Automation loop from chapter 17: submit each workflow per frame.

Las funciones submit_frame y log_frame son las impresas en el capitulo,
completas: envian el workflow (formato API) a /prompt con los parametros de
cada frame, esperan el resultado y registran una traza con el hash del
workflow para reproducibilidad.
"""
import argparse
import hashlib
import json
import mimetypes
import os
import time
import urllib.request
import uuid
from pathlib import Path

DEFAULT_HOST = "http://127.0.0.1:8188"

# Nodos de guardado cuyo filename_prefix hay que reescribir por frame.
# SaveImage escribe PNG de 8 bits; SaveEXR (ComfyUI-HQ-Image-Save) escribe
# EXR en coma flotante y es el que exigen las capas de datos del capitulo 13.
SAVE_NODES = ("SaveImage", "SaveEXR", "SaveEXRFrames")

# Los distintos samplers nombran la semilla de forma diferente.
SEED_KNOBS = ("seed", "noise_seed")


def load_workflow(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def find_nodes(workflow: dict, class_type: str) -> list[str]:
    return [nid for nid, node in workflow.items()
            if node.get("class_type") == class_type]


def upload_image(path: Path, host: str = DEFAULT_HOST) -> str:
    """Sube el frame a input/ y devuelve el nombre que espera LoadImage.

    LoadImage resuelve nombres contra la carpeta input/ del servidor: no
    acepta rutas absolutas. Subir el archivo es ademas lo unico que
    funciona cuando ComfyUI corre en otra maquina.
    """
    boundary = uuid.uuid4().hex
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    body = b"".join([
        f"--{boundary}\r\n".encode(),
        f'Content-Disposition: form-data; name="image"; filename="{path.name}"\r\n'.encode(),
        f"Content-Type: {mime}\r\n\r\n".encode(),
        path.read_bytes(), b"\r\n",
        f"--{boundary}\r\n".encode(),
        b'Content-Disposition: form-data; name="overwrite"\r\n\r\ntrue\r\n',
        f"--{boundary}--\r\n".encode(),
    ])
    req = urllib.request.Request(
        host + "/upload/image", data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req) as response:
        return json.load(response)["name"]


def resolve_input(frame_in: str, host: str = DEFAULT_HOST) -> str:
    """Si frame_in es un archivo del disco lo sube; si no, lo trata como
    un nombre ya presente en la carpeta input/ del servidor."""
    candidate = Path(frame_in)
    if candidate.is_file():
        return upload_image(candidate, host)
    return frame_in


def submit_frame(workflow: dict, frame_in: str, frame_out: str, seed: int,
                 host: str = DEFAULT_HOST) -> str:
    wf = json.loads(json.dumps(workflow))  # deep copy
    # Modificar nodos: ruta de entrada, prefijo de salida y semilla
    image_name = resolve_input(frame_in, host)
    for nid in find_nodes(wf, "LoadImage"):
        wf[nid]["inputs"]["image"] = image_name
    for class_type in SAVE_NODES:
        for nid in find_nodes(wf, class_type):
            wf[nid]["inputs"]["filename_prefix"] = frame_out
    for node in wf.values():
        inputs = node.get("inputs", {})
        for knob in SEED_KNOBS:
            if knob in inputs:
                inputs[knob] = seed
    req = urllib.request.Request(
        host + "/prompt", data=json.dumps({"prompt": wf}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as response:
        return json.load(response)["prompt_id"]


def wait_for(prompt_id: str, host: str = DEFAULT_HOST,
             timeout_s: int = 600) -> dict:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        with urllib.request.urlopen(f"{host}/history/{prompt_id}") as response:
            history = json.load(response)
        if prompt_id in history:
            return history[prompt_id]
        time.sleep(2)
    raise TimeoutError(f"frame sin terminar tras {timeout_s}s")


def log_frame(frame: int, seed: int, workflow_hash: str, result: dict,
              log_path: str = "SH0170_frames.jsonl") -> None:
    entry = {"frame": frame, "seed": seed, "workflow_hash": workflow_hash,
             "status": "done" if result.get("status", {}).get("completed")
             else "error"}
    with open(log_path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ejecuta un workflow de capa auxiliar sobre un rango de frames")
    parser.add_argument("workflow", help="ruta al .api.json del workflow")
    parser.add_argument("--frames", default="1-1", help="rango, ej. 1001-1050")
    parser.add_argument("--pattern", default="SH0170.%04d.png",
                        help="patron del frame de entrada: nombre en input/ "
                             "o ruta del disco, que se sube automaticamente")
    parser.add_argument("--out-prefix", default="SH0170_layer")
    parser.add_argument("--seed", type=int, default=4923811)
    parser.add_argument("--host", default=DEFAULT_HOST)
    args = parser.parse_args()

    workflow = load_workflow(args.workflow)
    workflow_hash = hashlib.sha256(
        json.dumps(workflow, sort_keys=True).encode()).hexdigest()[:16]
    start, end = (int(x) for x in args.frames.split("-"))
    for frame in range(start, end + 1):
        frame_in = args.pattern % frame
        frame_out = f"{args.out_prefix}.{frame:04d}"
        prompt_id = submit_frame(workflow, frame_in, frame_out,
                                 args.seed, args.host)
        result = wait_for(prompt_id, args.host)
        log_frame(frame, args.seed, workflow_hash, result)
        print(f"frame {frame}: ok")


if __name__ == "__main__":
    main()
