import json
import pathlib
import subprocess
import sys

if '22.04' not in subprocess.run(['lsb_release', '-r'], check=True, stdout=subprocess.PIPE).stdout.decode():
    print('You are not using ubuntu 22.04.')
    sys.exit()

json_path = pathlib.Path(r"/etc/docker/daemon.json")

if not json_path.is_file():
    print('Run vastai install script first.')
    sys.exit()

with json_path.open('r', encoding='utf-8') as f:
    json_dict = json.load(f) or {}

if 'exec-opts' in json_dict:
    print('No need to fix')
    sys.exit()

json_dict['exec-opts'] = ["native.cgroupdriver=cgroupfs"]

with json_path.open('w', encoding='utf-8') as f:
    json.dump(json_dict, f, indent=4, sort_keys=True)

print(subprocess.run(['sudo', 'systemctl', 'restart', 'docker'], check=True, stdout=subprocess.PIPE).stdout.decode())

print('Complete. Run vastai install script again.')
