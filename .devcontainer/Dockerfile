# Run inside a recent debian based image with python3, pip3, git and sudo installed
FROM mcr.microsoft.com/devcontainers/python:3-bookworm

# We use 'user' as the name to match what the zhephyr-build image already created
ARG USERNAME=vscode

## Setup a user with sudo support
USER root

RUN apt update
RUN apt install -y libgl1-mesa-glx 

# extra packages needed for debugging native crashes in python
# RUN apt install -y python3-venv python3-dbg python3-tk-dbg

# Default user for devcontainer
USER vscode

