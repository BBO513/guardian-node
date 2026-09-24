#!/usr/bin/env bash
# One-time training env for Needle LoRA fine-tuning (WSL Ubuntu + NVIDIA GPU).
set -e
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
mkdir -p ~/needle-train && cd ~/needle-train
[ -d .venv ] || uv venv -q --python 3.12 .venv
. .venv/bin/activate
uv pip install -q "cactus-needle[train]==3.0.4" "jax[cuda12]"
python -c "import jax; print('jax', jax.__version__, jax.devices())"
