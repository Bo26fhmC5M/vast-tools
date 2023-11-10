#!/bin/bash

# setup-auto-update.sh enable
# setup-auto-update.sh disable

if [ "${1,,}" == "enable" ]
then
	sudo sed -i  's/APT::Periodic::Update-Package-Lists "0";/APT::Periodic::Update-Package-Lists "1";/' /etc/apt/apt.conf.d/20auto-upgrades
	sudo sed -i  's/APT::Periodic::Unattended-Upgrade "0";/APT::Periodic::Unattended-Upgrade "1";/' /etc/apt/apt.conf.d/20auto-upgrades
fi

if [ "${1,,}" == "disable" ]
then
	sudo sed -i  's/APT::Periodic::Update-Package-Lists "1";/APT::Periodic::Update-Package-Lists "0";/' /etc/apt/apt.conf.d/20auto-upgrades
	sudo sed -i  's/APT::Periodic::Unattended-Upgrade "1";/APT::Periodic::Unattended-Upgrade "0";/' /etc/apt/apt.conf.d/20auto-upgrades
fi