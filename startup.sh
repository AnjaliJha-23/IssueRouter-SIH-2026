#!/bin/bash
set -e

# ==============================================================================
# Azure App Service Linux Startup Script for IssueRouter
# ==============================================================================

echo "[startup] Initializing IssueRouter on Azure App Service..."

# 1. Directory resolution
if [ -d "/home/site/wwwroot/backend" ]; then
    cd /home/site/wwwroot/backend
    export PYTHONPATH="/home/site/wwwroot/backend:$PYTHONPATH"
elif [ -d "backend" ]; then
    cd backend
    export PYTHONPATH="$(pwd):$PYTHONPATH"
else
    export PYTHONPATH="$(pwd):$PYTHONPATH"
fi

# 2. Port configuration (Azure App Service sets $PORT, default 8000)
APP_PORT="${PORT:-8000}"

# 3. Model cache and PyTorch CPU threads configuration for Azure App Service
# Persist Hugging Face and torch cache to /home/site/models if persistent storage enabled
if [ -d "/home/site" ]; then
    export HF_HOME="${HF_HOME:-/home/site/models/huggingface}"
    export TRANSFORMERS_CACHE="${TRANSFORMERS_CACHE:-/home/site/models/transformers}"
    export TORCH_HOME="${TORCH_HOME:-/home/site/models/torch}"
    mkdir -p "$HF_HOME" "$TRANSFORMERS_CACHE" "$TORCH_HOME" 2>/dev/null || true
fi

# App Service S1 has 1 vCPU (100 ACU). Constrain PyTorch threadpool to avoid thread thrashing
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-1}"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}"
export VECLIB_MAXIMUM_THREADS="${VECLIB_MAXIMUM_THREADS:-1}"
export NUMEXPR_NUM_THREADS="${NUMEXPR_NUM_THREADS:-1}"

# S1 memory constraint: 1.75 GB RAM total.
# Worker count MUST strictly remain 1: every worker holds its own copy of the
# in-process models (sentence-transformers, spaCy) and, when
# CLASSIFIER_BACKEND=transformers, ~1.6 GB of BART weights on top.
WORKER_COUNT=1

echo "[startup] Launching Gunicorn with ${WORKER_COUNT} Uvicorn worker on port ${APP_PORT}..."
exec gunicorn \
    -w ${WORKER_COUNT} \
    -k uvicorn.workers.UvicornWorker \
    --bind "0.0.0.0:${APP_PORT}" \
    --timeout 600 \
    --access-logfile - \
    --error-logfile - \
    main:app
