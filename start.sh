#!/bin/bash

ENV_NAME="sideboarder_env"

# Check if Conda environment exists
if conda info --envs | grep -q "$ENV_NAME"; then
  echo "Conda environment '$ENV_NAME' already exists."
else
  echo "Creating new Conda environment: $ENV_NAME"
  conda create -y -n $ENV_NAME python=3.10
fi

# Activate the Conda environment
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate $ENV_NAME

# Install requirements via pip inside conda env
pip install --upgrade pip
pip install -r requirements.txt

# Run the Streamlit app
streamlit run sideboarder.py
