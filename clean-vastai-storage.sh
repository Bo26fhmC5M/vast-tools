#!/bin/bash

# �� ��ũ��Ʈ�� vast.ai ���ø� �������� �α��ִ� �̹����� �����ϰ� �����Ͽ� ��ũ �뷮�� Ȯ���մϴ�.
# This script frees up disk space by deleting all but popular images from vast.ai template page.

sudo docker rmi $(sudo docker image ls | grep -Ev "nvidia/cuda|nvidia/opencl|ubuntu|pytorch/pytorch|atinoda/text-generation-webui|ghcr.io/ai-dock/stable-diffusion-webui|koboldai/koboldai|runpod/stable-diffusion|ashleykza/kohya|opentensorfdn/bittensor|tensorflow/tensorflow" | awk 'NR>1 {print $3}')
sudo docker builder prune -f