# Modelos usados por los workflows

Cada entrada: archivo, carpeta destino dentro de `ComfyUI/models/` y fuente
de descarga (la URL de la FUENTE, no de una copia perecedera). El Anexo A
del libro explica la descarga desde Hugging Face paso a paso.

| Archivo | Carpeta | Fuente |
| --- | --- | --- |
| `sd_xl_base_1.0.safetensors` | `checkpoints/` | huggingface.co/stabilityai/stable-diffusion-xl-base-1.0 |
| `RealVisXL_V5.0_fp16.safetensors` | `checkpoints/` | huggingface.co/SG161222/RealVisXL_V5.0 |
| `v1-5-pruned-emaonly.safetensors` | `checkpoints/` | huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5 |
| `flux1-dev-fp8.safetensors` | `checkpoints/` | huggingface.co/Comfy-Org/flux1-dev (fp8, licencia no comercial) |
| `flux1-schnell-fp8.safetensors` | `checkpoints/` | huggingface.co/Comfy-Org/flux1-schnell (Apache-2.0) |
| `controlnet-canny-sdxl-1.0-fp16.safetensors` | `controlnet/` | huggingface.co/diffusers/controlnet-canny-sdxl-1.0 |
| `canopus-pencil-art-sdxl.safetensors` | `loras/` | huggingface.co/prithivMLmods/Canopus-Pencil-Art-LoRA |
| `RealESRGAN_x4plus.pth` | `upscale_models/` | github.com/xinntao/Real-ESRGAN/releases (v0.1.0) |

Los preprocesadores de depth y normales (capitulo 17) descargan su modelo
automaticamente en el primer uso (paquete comfyui_controlnet_aux).

Revisa la licencia de cada modelo antes de uso comercial; el capitulo 5
trata las diferencias (FLUX.1 dev vs schnell, por ejemplo).
