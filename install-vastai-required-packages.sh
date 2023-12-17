#!/bin/bash

# 이 스크립트는 ubuntu 22 minimized 버전으로 설치한 경우에 vastai 데몬이 요구하는 패키지를 설치합니다.
# This script will install the packages required by the vastai daemon if you have installed a minimized version of ubuntu 22.

sudo apt update
sudo apt install -y curl dmidecode hdparm lshw