"""Modal deployment for the Laya Nepali clothing decision service.

Deploy:
    modal secret create laya-api-key LAYA_API_KEY=<strong value>
    modal deploy modal_app.py

The service keeps Bearer auth (LAYA_API_KEY) and exposes /health, /v1/systemone,
and /v1/message. Scale-to-zero GPU (T4); the Next.js client falls back to Gemini
when a cold start exceeds its 3 s timeout.
"""

import modal

APP_NAME = "laya-nepali-decision"
CHECKPOINT = "data/checkpoints/clothing_v1"

app = modal.App(APP_NAME)

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("curl")
    .pip_install(
        "torch",
        "fastapi>=0.110",
        "uvicorn[standard]>=0.27",
        "pydantic>=2.0",
        "transformers>=4.40",
        "laya==0.3.20",
    )
    .workdir("/app")
    .env(
        {
            "PYTHONPATH": "/app/src",
            "PYTHONUNBUFFERED": "1",
            "HF_HUB_DISABLE_SYMLINKS": "1",
            "LAYA_MODEL_PATH": f"/app/{CHECKPOINT}",
            "LAYA_DOMAIN": "clothing",
            "LAYA_DEVICE": "cuda",
        }
    )
    .add_local_dir("src", remote_path="/app/src", copy=True)
    .add_local_dir(
        CHECKPOINT,
        remote_path=f"/app/{CHECKPOINT}",
        ignore=["checkpoint_latest", "checkpoint_latest/**"],
        copy=True,
    )
)


@app.function(
    image=image,
    gpu="T4",
    secrets=[modal.Secret.from_name("laya-api-key")],
    scaledown_window=300,
    timeout=600,
    startup_timeout=900,
    max_containers=2,
)
@modal.asgi_app()
def web():
    from layanep.serve import create_app

    return create_app(
        model_path=f"/app/{CHECKPOINT}",
        device="cuda",
        domain="clothing",
    )
