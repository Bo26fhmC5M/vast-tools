#!/bin/bash

# 이 스크립트는 vast.ai 템플릿 페이지의 인기있는 이미지를 제외하고 삭제하여 디스크 용량을 확보합니다.
# This script frees up disk space by deleting all but popular images from vast.ai template page.

PATTERN="nvidia/cuda|nvidia/opencl|ubuntu|pytorch/pytorch|atinoda/text-generation-webui|ghcr.io/ai-dock/stable-diffusion-webui|ghcr.io/ai-dock/comfyui|koboldai/koboldai|runpod/stable-diffusion|onerahmet/openai-whisper-asr-webservice|ashleykza/kohya|runpod/kasm-desktop|ghcr.io/selkies-project/nvidia-glx-desktop|tensorflow/tensorflow|opentensorfdn/bittensor"


sudo docker rmi $(sudo docker image ls | grep -Ev "$PATTERN" | awk 'NR>1 {print $3}')
sudo docker builder prune -f