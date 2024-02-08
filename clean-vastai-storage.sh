#!/bin/bash

PATTERN="nvidia/cuda|nvidia/opencl|ubuntu|pytorch/pytorch|atinoda/text-generation-webui|ghcr.io/ai-dock/stable-diffusion-webui|ghcr.io/ai-dock/comfyui|koboldai/koboldai|runpod/stable-diffusion|onerahmet/openai-whisper-asr-webservice|ashleykza/kohya|runpod/kasm-desktop|ghcr.io/selkies-project/nvidia-glx-desktop|tensorflow/tensorflow|opentensorfdn/bittensor"


sudo docker rmi $(sudo docker image ls | grep -Ev "$PATTERN" | awk 'NR>1 {print $3}')
sudo docker builder prune -f