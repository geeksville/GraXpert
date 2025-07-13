#!/usr/bin/env bash
set -e

export USER=`whoami`

# the devcontainer mount of vscode/.local/share implicity makes the owner root (which is bad)
echo "Fixing permissions"
sudo chown -R $USER ~/.local

echo "Installing python requirements"
pip3 install --user -r requirements.txt

echo "Installing onnxruntime-rocm for AMD GPU support"
pip3 install --user onnxruntime-rocm -f https://repo.radeon.com/rocm/manylinux/rocm-rel-6.4.1/