"""Chapter 11: batch processing of a plate sequence.

Script completo del capitulo 11. El workflow actua como plantilla
parametrica: los campos que cambian frame a frame llevan un centinela
(__PLATE__, __MASK__, __SEED__, __PREFIX__) que este script sustituye
antes de cada envio.
"""
import argparse
import copy
import csv
import hashlib
import json
import time
from pathlib import Path

import requests

COMFY_URL = "http://127.0.0.1:8188"
BASE_SEED = 42


def make_seed(shot: str, frame: int) -> int:
    """Semilla determinista derivada del plano y del numero de frame."""
    digest = hashlib.sha256(f"{shot}_{frame:04d}".encode()).digest()
    return int.from_bytes(digest[:4], "big")


def workflow_version(workflow: dict) -> str:
    """Hash corto del workflow, para la traza de auditoria."""
    canonical = json.dumps(workflow, sort_keys=True).encode()
    return hashlib.sha256(canonical).hexdigest()[:8]


def upload_image(path: Path, host: str = COMFY_URL) -> str:
    """Sube el archivo a input/ y devuelve el nombre que espera LoadImage.

    LoadImage resuelve nombres contra la carpeta input/ del servidor. Pasarle
    una ruta absoluta produce un error de archivo no encontrado aunque la
    ruta exista en la maquina que lanza el script.
    """
    with open(path, "rb") as handle:
        files = {"image": (path.name, handle, "application/octet-stream")}
        response = requests.post(f"{host}/upload/image", files=files,
                                 data={"overwrite": "true"})
    response.raise_for_status()
    return response.json()["name"]


def submit_frame(workflow_template: dict, plate_path: Path, mask_path: Path,
                 output_prefix: str, seed: int, host: str = COMFY_URL) -> str:
    """Instancia la plantilla para un frame y la encola en el servidor."""
    workflow = copy.deepcopy(workflow_template)
    plate_name = upload_image(plate_path, host)
    mask_name = upload_image(mask_path, host) if mask_path else ""

    for node in workflow.values():
        inputs = node.get("inputs", {})
        for knob, value in inputs.items():
            if value == "__PLATE__":
                inputs[knob] = plate_name
            elif value == "__MASK__":
                inputs[knob] = mask_name
            elif value == "__SEED__":
                inputs[knob] = seed
            elif value == "__PREFIX__":
                inputs[knob] = output_prefix

    response = requests.post(f"{host}/prompt", json={"prompt": workflow})
    response.raise_for_status()
    return response.json()["prompt_id"]


def wait_for(prompt_id: str, host: str = COMFY_URL,
             timeout_s: int = 600) -> dict:
    """Espera a que el frame termine. Nunca sin limite: un servidor caido
    convierte un bucle infinito en un batch colgado que nadie vigila."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        response = requests.get(f"{host}/history/{prompt_id}")
        if response.ok and prompt_id in response.json():
            return response.json()[prompt_id]
        time.sleep(2)
    raise TimeoutError(f"frame sin terminar tras {timeout_s}s: {prompt_id}")


def frame_failed(result: dict) -> bool:
    status = result.get("status", {})
    if status.get("status_str") == "error":
        return True
    return not status.get("completed", False)


def read_shot_list(path: Path) -> list[dict]:
    """Lee la shot list: CSV con columnas shot, frame, plate, mask."""
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Procesa una secuencia de plates con un workflow plantilla")
    parser.add_argument("workflow", help="ruta al .api.json con los centinelas")
    parser.add_argument("shotlist", help="CSV con shot, frame, plate, mask")
    parser.add_argument("--host", default=COMFY_URL)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--log", default="batch_log.jsonl")
    args = parser.parse_args()

    with open(args.workflow, encoding="utf-8") as handle:
        template = json.load(handle)
    version = workflow_version(template)

    failed = []
    for row in read_shot_list(Path(args.shotlist)):
        shot = row["shot"]
        frame = int(row["frame"])
        seed = make_seed(shot, frame)
        prefix = f"{shot}_denoise_v001.{frame:04d}"

        for attempt in range(1, args.retries + 1):
            try:
                prompt_id = submit_frame(
                    template, Path(row["plate"]),
                    Path(row["mask"]) if row.get("mask") else None,
                    prefix, seed, args.host)
                result = wait_for(prompt_id, args.host)
                status = "error" if frame_failed(result) else "ok"
            except Exception as error:              # noqa: BLE001
                prompt_id, status = "", f"error: {error}"

            entry = {"shot": shot, "frame": frame, "seed": seed,
                     "prompt_id": prompt_id, "workflow_version": version,
                     "attempt": attempt, "status": status,
                     "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")}
            with open(args.log, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(entry) + "\n")

            if status == "ok":
                print(f"{shot} {frame}: ok")
                break
            print(f"{shot} {frame}: intento {attempt} fallido ({status})")
            # Ritmo de envio: encolar en rafaga no acelera nada y satura la red.
            time.sleep(1)
        else:
            failed.append((shot, frame))

    print(f"\nFrames fallidos: {failed or 'ninguno'}")


if __name__ == "__main__":
    main()
