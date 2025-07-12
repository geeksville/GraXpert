# The dockerfile for building our release reference image
# FIXME try to find a slim version similar to 3.9.13-slim-buster
FROM python:3.12-bookworm 

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create the user
#RUN groupadd --gid $USER_GID $USERNAME \
#   && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    #
    # [Optional] Add sudo support. Omit if you don't need to install software after connecting.
#    && apt-get update \
#    && apt-get install -y sudo \
#    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
#    && chmod 0440 /etc/sudoers.d/$USERNAME

RUN apt update
RUN apt install -y libgl1-mesa-glx 

# create working directory and 
WORKDIR /app

# Ensure /app is owned by the non-root user
RUN chown $USERNAME:$USERNAME /app

# [Optional] Set the default user. Omit if you want to keep the default as root.
USER $USERNAME

# Copy in all needed project files
# FIXME: don't copy unneeded files
COPY . .

# install pip dependencies
RUN pip3 install --user -r requirements.txt

# Install AMD ROCm GPU support
RUN pip3 install --user onnxruntime-rocm -f https://repo.radeon.com/rocm/manylinux/rocm-rel-6.4.1/

# run the flask server  
CMD [ "bash" ]