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

pip3 install --user cx_Freeze build

# Moved into requirements.txt to match historic user expectations (though it adds about about 500MB to exe size)
# without this added exe is already 500MB.
#echo "Installing onnxruntime-gpu for NVIDIA GPU support"
#pip install --user onnxruntime-gpu

# FIXME test onnxruntime-openvino to see how exe size is affected

# would add 4.5GB! to exe size, make optional for AMD GPU users
# echo "Installing onnxruntime-rocm for AMD GPU support"
# pip3 install --user onnxruntime-rocm 