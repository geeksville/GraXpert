#!/usr/bin/env bash
set -e

export USER=`whoami`

# the devcontainer mount of vscode/.local/share implicity makes the owner root (which is bad)
echo "Fixing permissions"
# Some containers might not have a .local directory at all, don't fail in that case
mkdir ~/.local | true
sudo chown -R $USER ~/.local

echo "Installing python requirements"
pip3 install --user -r requirements.txt

echo "Installing utilities for developers"
pip3 install --user python-appimage setuptools wheel cx_freeze==8.3.0

wget -O bin/linuxdeploy https://github.com/linuxdeploy/linuxdeploy/releases/download/1-alpha-20250213-2/linuxdeploy-x86_64.AppImage
chmod a+x bin/linuxdeploy 

echo "Installing onnxruntime-gpu for NVIDIA GPU support"
pip install --user onnxruntime-gpu

echo "Installing onnxruntime-rocm for AMD GPU support"
pip3 install --user onnxruntime-rocm -f https://repo.radeon.com/rocm/manylinux/rocm-rel-6.4.2/