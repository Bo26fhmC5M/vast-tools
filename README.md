# vast-tools
Yet another useful tools for vastai hosts.

# Fix for nvml error when using Ubuntu 22
Hosts often make mistakes when applying nvml fixes manually. This fix automatically resolves nvml error without any worries.
```
wget -O fix-nvml-error.py https://raw.githubusercontent.com/Bo26fhmC5M/vast-tools/main/fix-nvml-error.py
sudo python3 fix-nvml-error.py
```

# How to install the packages required by vastai when using Ubuntu 22 minimized
If you install a minimized version of Ubuntu 22, mainboard name, disk name, and disk speed may be displayed incorrectly in the vastai dashboard due to missing packages.
```
wget -O install-vastai-required-packages.sh https://raw.githubusercontent.com/Bo26fhmC5M/vast-tools/main/install-vastai-required-packages.sh
sudo bash install-vastai-required-packages.sh
```

# How to disable automatic update
Automatic updates often cause errors such as Driver/library version mismatch. To prevent this, turn off automatic update.
```
wget -O setup-auto-update.sh https://raw.githubusercontent.com/Bo26fhmC5M/vast-tools/main/setup-auto-update.sh
sudo bash setup-auto-update.sh disable
```

# How to free up vastai storage while preserving popular images
If you want to free up the storage used by vastai, but are reluctant to remove all your images, this may be your best option.
```
wget -O clean-vastai-storage.sh https://raw.githubusercontent.com/Bo26fhmC5M/vast-tools/main/clean-vastai-storage.sh
sudo bash clean-vastai-storage.sh
```
