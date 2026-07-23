"""Automation loop from chapter 17: submit each workflow per frame.

Las funciones submit_frame y log_frame son las impresas en el capitulo,
completas: envian el workflow (formato API) a /prompt con los parametros de
cada frame, esperan el resultado y registran una traza con el hash del
workflow para reproducibilidad.
"""
import argparse
import hashlib
import json
import time
import urllib.request

DEFAULT_HOST = "http://127.0.0.1:8188"


def load_workflow(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def find_nodes(workflow: dict, class_type: str) -> list[str]:
    return [nid for nid, node in workflow.items()
            if node["class_type"] == class_type]


def submit_frame(workflow: dict, frame_in: str, frame_out: str, seed: int,
                 host: str = DEFAULT_HOST) -> str:
    wf = json.loads(json.dumps(workflow))  # deep copy
    # Modificar nodos: ruta de entrada, prefijo de salida y semilla
    for nid in find_nodes(wf, "LoadImage"):
        wf[nid]["inputs"]["image"] = frame_in
    for nid in find_nodes(wf, "SaveImage"):
        wf[nid]["inputs"]["filename_prefix"] = frame_out
    for nid, node in wf.items():
        if "seed" in node["inputs"]:
            node["inputs"]["seed"] = seed
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
                        help="patron del nombre de frame de entrada")
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
