FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy packaging specs first for Docker caching
COPY pyproject.toml README.md ./

# Install core runtime dependencies (CPU-first default, CUDA compatible)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir \
    "fastapi>=0.110" \
    "uvicorn[standard]>=0.27" \
    "pydantic>=2.0" \
    "transformers>=4.40" \
    "laya==0.3.20"

# Copy source code and checkpoint
COPY src/ src/
COPY data/checkpoints/ data/checkpoints/

# Install layanep package
RUN pip install --no-cache-dir -e .

ENV PYTHONUNBUFFERED=1
ENV HF_HUB_DISABLE_SYMLINKS=1
ENV LAYA_MODEL_PATH=data/checkpoints/clothing_v1
ENV LAYA_DOMAIN=clothing
ENV LAYA_DEVICE=cpu
ENV LAYA_HOST=0.0.0.0
ENV LAYA_PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "layanep.serve", "--model-path", "data/checkpoints/clothing_v1", "--domain", "clothing", "--host", "0.0.0.0", "--port", "8000"]
