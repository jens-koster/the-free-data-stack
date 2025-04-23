#!/bin/bash

pyenv global 3.8.10

# Remove existing .venv if it exists
if [ -d ".venv" ]; then
  echo "Removing existing .venv..."
  rm -rf .venv
fi

# Create a new virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Get full Python version (e.g., 3.10.12)
PYTHON_VERSION=$(python --version | awk '{print $2}')

echo "Using Python version: $PYTHON_VERSION"

# Install dependencies
echo "Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -r ./spark/requirements.txt

# Install Jupyter kernel with full version in display name
echo "Installing Jupyter kernel..."
python -m ipykernel install --user --name=.venv --display-name "TFDS $PYTHON_VERSION"

echo "✅ Setup complete with Python $PYTHON_VERSION"
