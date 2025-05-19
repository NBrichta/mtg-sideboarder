#!/bin/bash

cd "$(dirname "$0")"  # Navigate to script's directory

ENV_NAME="sideboarder_env"

if conda info --envs | grep -q "$ENV_NAME"; then
  echo "Conda environment '$ENV_NAME' already exists."
else
  echo "Creating new Conda environment: $ENV_NAME"
  conda create -y -n $ENV_NAME python=3.10
fi

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate $ENV_NAME

pip install --upgrade pip
pip install -r requirements.txt

streamlit run sideboarder.py

