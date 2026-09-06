#!/bin/bash
# vast.ai onstart for the RENDER box (owner ruling 6 Sep 2026 11:30: everything on vast.ai, a datacenter GPU box for the renders). Image nvidia/cuda:12.4.1-runtime-ubuntu22.04
# or ubuntu:24.04 with the host driver; installs Blender 4.2 LTS (the VM's version), Pillow for the title strips, rsync; the render files (scene, STL set, KiCad
# 3D models, board GLBs) come from the runner by rsync after SETUP-DONE. Log /root/setup.log.
exec > /root/setup.log 2>&1; set -x
export DEBIAN_FRONTEND=noninteractive LANG=C.UTF-8
touch /root/.no_auto_tmux
apt-get update && apt-get install -y --no-install-recommends ca-certificates curl xz-utils rsync python3 python3-pil fonts-dejavu-core libxi6 libxxf86vm1 libxfixes3 libxrender1 libgl1 libglu1-mesa libsm6 libxkbcommon0 procps || { echo "SETUP-FAILED apt"; exit 1; }
mkdir -p /root/blender && cd /root && curl -fsSL -o blender.tar.xz https://download.blender.org/release/Blender4.2/blender-4.2.11-linux-x64.tar.xz || { echo "SETUP-FAILED download"; exit 1; }
tar -xJf blender.tar.xz --strip-components=1 -C /root/blender && rm blender.tar.xz
/root/blender/blender --version | head -1; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; nproc; free -g | head -2
echo SETUP-DONE
