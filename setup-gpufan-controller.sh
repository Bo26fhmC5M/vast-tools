#!/bin/bash

# setup-gpufan-controller.sh install
# setup-gpufan-controller.sh uninstall

BASEDIR="$(dirname "$0")"


if [[ "${1,,}" == "install" ]]; then
sudo curl -o /usr/local/sbin/set_fan_curve https://github.com/jjziets/GPU_FAN_OC_Manager/raw/main/set_fan_curve
sudo chmod +x /usr/local/sbin/set_fan_curve

sudo curl -o /usr/local/sbin/set_fan_speed https://github.com/jjziets/GPU_FAN_OC_Manager/raw/main/set_fan_speed
sudo chmod +x /usr/local/sbin/set_fan_speed

sudo tee /etc/systemd/system/gpufan-controller.service << 'EOF' > /dev/null
[Unit]
Description=GPU Fan Controller

[Service]
ExecStart=/usr/local/sbin/set_fan_curve 90
Restart=on-failure
RestartSec=5s
ExecStop=/bin/bash -c "/bin/kill -2 $MAINPID && /usr/local/sbin/set_fan_speed auto"

[Install]
WantedBy=multi-user.target
EOF

echo "$FILE_GPUFAN_CONTROLLER_SERVICE" | sudo tee /etc/systemd/system/gpufan-controller.service > /dev/null

sudo systemctl enable gpufan-controller.service
sudo systemctl start gpufan-controller.service
sudo systemctl status gpufan-controller.service
fi

if [[ "${1,,}" == "uninstall" ]]; then
sudo systemctl stop gpufan-controller.service
sudo systemctl disable gpufan-controller.service
sudo rm -f /etc/systemd/system/gpufan-controller.service

sudo rm -f /usr/local/sbin/set_fan_curve
sudo rm -f /usr/local/sbin/set_fan_speed
fi