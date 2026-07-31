"""Chapter 10: talking to the ComfyUI server from Python.

Funciones completas del capitulo 10. El libro imprime los fragmentos que
explican cada decision; aqui estan reunidas y ejecutables.
"""
import asyncio
import json
import os
import uuid

import requests
import websockets

SERVER_URL = os.environ.get("COMFY_URL", "http://127.0.0.1:8188")


def send_workflow(workflow: dict, server_url: str = SERVER_URL) -> tuple[str, str]:
    """Encola un workflow en formato API y devuelve (prompt_id, client_id)."""
    client_id = str(uuid.uuid4())
    payload = {"prompt": workflow, "client_id": client_id}
    response = requests.post(f"{server_url}/prompt", json=payload)
    response.raise_for_status()
    return response.json()["prompt_id"], client_id


def upload_image(filepath: str, server_url: str = SERVER_URL) -> str:
    """Sube un archivo a input/ y devuelve el nombre que espera LoadImage.

    LoadImage resuelve el nombre recibido contra la carpeta input/ del
    servidor: no acepta rutas absolutas del sistema de archivos.
    """
    with open(filepath, "rb") as handle:
        files = {"image": (os.path.basename(filepath), handle,
                           "application/octet-stream")}
        response = requests.post(f"{server_url}/upload/image", files=files,
                                 data={"overwrite": "true"})
    response.raise_for_status()
    return response.json()["name"]


def get_output_files(prompt_id: str, server_url: str = SERVER_URL) -> list[str]:
    """Nombres de archivo producidos por una ejecucion ya terminada."""
    response = requests.get(f"{server_url}/history/{prompt_id}")
    response.raise_for_status()
    history = response.json()
    if prompt_id not in history:
        return []
    outputs = []
    for node_output in history[prompt_id].get("outputs", {}).values():
        for key in ("images", "gifs", "files"):
            for item in node_output.get(key, []):
                if isinstance(item, dict) and "filename" in item:
                    outputs.append(item["filename"])
    return outputs


def validate_workflow_nodes(workflow: dict,
                            server_url: str = SERVER_URL) -> list[str]:
    """Devuelve los class_types del workflow no disponibles en el servidor."""
    response = requests.get(f"{server_url}/object_info")
    response.raise_for_status()
    available = set(response.json().keys())

    missing = []
    for node_data in workflow.values():
        class_type = node_data.get("class_type")
        if class_type and class_type not in available:
            missing.append(class_type)
    return missing


def find_positive_encoder_ids(workflow: dict) -> set:
    """IDs de los nodos conectados a la entrada 'positive' de algun sampler.

    Un workflow real tiene dos CLIPTextEncode, el positivo y el negativo.
    Escribir el prompt en los dos deja el condicionamiento negativo
    saboteado sin que la ejecucion falle.
    """
    ids = set()
    for node in workflow.values():
        link = node.get("inputs", {}).get("positive")
        if isinstance(link, list) and len(link) == 2:
            ids.add(str(link[0]))
    return ids


def patch_workflow(workflow: dict, image_name: str, prompt_text: str,
                   seed: int) -> dict:
    """Inyecta imagen, prompt positivo y semilla en una copia del workflow."""
    patched = json.loads(json.dumps(workflow))
    positive_ids = find_positive_encoder_ids(patched)

    for node_id, node in patched.items():
        class_type = node.get("class_type")
        inputs = node.setdefault("inputs", {})

        if class_type == "LoadImage":
            inputs["image"] = image_name
        elif class_type == "CLIPTextEncode" and str(node_id) in positive_ids:
            inputs["text"] = prompt_text

        # Los distintos samplers nombran la semilla de forma diferente.
        if "seed" in inputs:
            inputs["seed"] = seed
        elif "noise_seed" in inputs:
            inputs["noise_seed"] = seed

    return patched


async def wait_for_completion(prompt_id: str, client_id: str,
                              server_url: str = SERVER_URL) -> None:
    """Espera por WebSocket hasta que el prompt termine o falle."""
    ws_url = server_url.replace("http://", "ws://").replace("https://", "wss://")
    ws_url = f"{ws_url}/ws?clientId={client_id}"

    async with websockets.connect(ws_url) as websocket:
        async for raw in websocket:
            # El servidor mezcla en el mismo canal mensajes de texto en JSON
            # y fotogramas binarios de previsualizacion. Los binarios llegan
            # como bytes y hay que descartarlos antes de parsear.
            if not isinstance(raw, str):
                continue
            message = json.loads(raw)
            data = message.get("data", {})

            if data.get("prompt_id") and data["prompt_id"] != prompt_id:
                continue

            message_type = message.get("type")
            if message_type == "progress":
                print(f"  sampling {data['value']}/{data['max']}")
            elif message_type == "executing" and data.get("node") is None:
                return
            elif message_type == "execution_error":
                raise RuntimeError(data.get("exception_message", "error desconocido"))


async def process_batch(workflow_path: str, frames: list[dict],
                        server_url: str = SERVER_URL) -> list[dict]:
    """Recorre una lista de frames aplicando el mismo workflow a cada uno."""
    with open(workflow_path, encoding="utf-8") as handle:
        base_workflow = json.load(handle)

    missing = validate_workflow_nodes(base_workflow, server_url)
    if missing:
        raise RuntimeError(f"Nodos no disponibles en el servidor: {missing}")

    results = []
    for frame in frames:
        uploaded = upload_image(frame["plate_path"], server_url)
        workflow = patch_workflow(base_workflow, uploaded, frame["prompt"],
                                  frame["seed"])

        prompt_id, client_id = send_workflow(workflow, server_url)
        await wait_for_completion(prompt_id, client_id, server_url)

        files = get_output_files(prompt_id, server_url)
        results.append({"frame": frame["frame_number"], "outputs": files})
        print(f"frame {frame['frame_number']}: {files}")

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Comprueba que el servidor responde y valida un workflow")
    parser.add_argument("workflow", help="ruta al .api.json")
    parser.add_argument("--host", default=SERVER_URL)
    args = parser.parse_args()

    with open(args.workflow, encoding="utf-8") as handle:
        wf = json.load(handle)
    missing_nodes = validate_workflow_nodes(wf, args.host)
    print("Nodos que faltan:", missing_nodes or "ninguno")
