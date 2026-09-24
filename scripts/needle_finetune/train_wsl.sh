#!/usr/bin/env bash
# Fine-tune Needle 3 on Guardian data (LoRA on the frozen 20-layer base), export a .cact,
# and copy it to OUT_DIR (the Windows repo's models/ by default). Run inside WSL after setup_wsl.sh:
#   bash scripts/needle_finetune/train_wsl.sh guardian_train.jsonl [epochs] [out_dir]
set -e
DATA=${1:?path to training jsonl}
EPOCHS=${2:-3}
BATCH=${BATCH:-4}
OUT_DIR=${3:-/mnt/d/dell_pc/guardian_node/models}
export NEEDLE_TELEMETRY=0
export XLA_PYTHON_CLIENT_PREALLOCATE=false  # share the GPU with Windows
cd ~/needle-train && . .venv/bin/activate
cp "$DATA" data.jsonl
needle finetune data.jsonl --epochs "$EPOCHS" --batch-size "$BATCH" --val-split 0.1 --out guardian_lora.safetensors
needle build --lora guardian_lora.safetensors --out guardian_needle.cact
ls -lh guardian_needle.cact
mkdir -p "$OUT_DIR" && cp guardian_needle.cact guardian_lora.safetensors "$OUT_DIR"/ && echo "copied to $OUT_DIR"
