#!/bin/bash

PATTERN="nvidia/cuda|nvidia/opencl|ubuntu|pytorch/pytorch|atinoda/text-generation-webui|ai-dock/stable-diffusion-webui|ai-dock/comfyui|ai-dock/linux-desktop|nvidia/pytorch|onerahmet/openai-whisper-asr-webservice|ashleykza/kohya|runpod/kasm-desktop|selkies-project/nvidia-glx-desktop|tensorflow/tensorflow|opentensorfdn/bittensor|dizcza/docker-hashcat|koboldai/koboldai|rapidsai/rapidsai-cloud-ml|rocm/rocm-terminal|rocm/pytorch"


sudo docker rmi $(sudo docker image ls | grep -Ev "$PATTERN" | awk 'NR>1 {print $3}')
sudo docker builder prune -f
