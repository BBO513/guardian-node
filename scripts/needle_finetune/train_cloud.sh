#!/usr/bin/env bash
# Fine-tune Needle 3 for Guardian on any Linux machine with an NVIDIA GPU
# (cloud GPU box, Colab/Kaggle terminal, RunPod, etc.). Self-contained: sets up its own venv.
#
#   git clone -b clean-rewrite-investor-ready https://github.com/BBO513/guardian-node.git
#   cd guardian-node
#   bash scripts/needle_finetune/train_cloud.sh [epochs] [batch]
#
# Then download out/guardian_needle.cact and copy it to the Pi's ~/guardian-node/models/.
# Check it with: python scripts/needle_router_eval.py --mode router --weights models/guardian_needle.cact
set -e
EPOCHS=${1:-3}
BATCH=${2:-16}      # 16 needs ~9 GB of GPU memory; use 4 on 8-12 GB cards
cd "$(dirname "$0")/../.."
export NEEDLE_TELEMETRY=0
export XLA_PYTHON_CLIENT_PREALLOCATE=false

if [ ! -d .needle-train ]; then
  python3 -m venv .needle-train || { pip install -q uv && uv venv -q --python 3.12 .needle-train; }
fi
. .needle-train/bin/activate
pip install -q --upgrade pip
pip install -q "cactus-needle[train]==3.0.4" "jax[cuda12]" pyyaml
python -c "import jax; d=jax.devices(); print('jax devices:', d); assert d[0].platform=='gpu', 'no GPU visible'"

python scripts/needle_finetune/make_dataset.py --n "${N:-2000}" --out out_train.jsonl
mkdir -p out
needle finetune out_train.jsonl --epochs "$EPOCHS" --batch-size "$BATCH" --val-split 0.1 \
  --out out/guardian_lora.safetensors
needle build --lora out/guardian_lora.safetensors --out out/guardian_needle.cact
ls -lh out/
