# The dockerfile for building our release reference image
# FIXME try to find a slim version similar to 3.9.13-slim-buster
FROM python:3.12-slim-bookworm

# FIXME change source after merging per https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#labelling-container-images
LABEL org.opencontainers.image.source=https://github.com/geeksville/GraXpert
LABEL org.opencontainers.image.description="A container for running GraXpert, an astrophotography image processing tool"
LABEL org.opencontainers.image.licenses=GPL-3.0
# FIXME have github CI docker push ghcr.io/geeksville/graxpert:latest

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN apt update
RUN apt install -y libgl1-mesa-glx wget sudo tk

# Create a non-root user if one doesn't exist, and give it sudo rights
RUN if ! id -u ${USERNAME} > /dev/null 2>&1; then \
        groupadd --gid ${USER_GID} ${USERNAME} && \
        useradd --uid ${USER_UID} --gid ${USER_GID} --create-home --shell /bin/bash ${USERNAME} && \
        echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME}-nopasswd; \
    fi

# create working directory and 
WORKDIR /app

# The app will store prefs (and very large models) in this volume, which we'd prefer to be persistent
VOLUME /home/$USERNAME/.local/share/GraXpert
VOLUME ["/data"]

# Ensure /app and our prefs dir is owned by the non-root user
RUN chown -R $USERNAME:$USERNAME /app /home/$USERNAME/.local

# [Optional] Set the default user. Omit if you want to keep the default as root.
USER $USERNAME

# Copy in all needed project files
# FIXME: don't copy unneeded files
COPY . .

# install pip dependencies
RUN pip3 install --no-cache-dir --user -r requirements.txt

# Install AMD ROCm GPU support
RUN pip3 install --no-cache-dir --user onnxruntime-gpu
RUN pip3 install --no-cache-dir --user onnxruntime-rocm -f https://repo.radeon.com/rocm/manylinux/rocm-rel-6.4.1/

# Launch the app with this as the current working directory
WORKDIR /data

# Run the app (for the time being we only allow the CLI - not the GUI)
ENV PYTHONPATH=/app
ENTRYPOINT [ "python", "-m", "graxpert.main", "--cli", "--help"]
CMD []