import json
import os
import pathlib
import subprocess
import sys

supported_ubuntu_versions = ['22.04', '24.04']
docker_json_path = pathlib.Path(r"/etc/docker/daemon.json")


def main():
    # Check root privileges
    if os.geteuid() != 0:
        print("You need root privileges to run the script.")
        sys.exit(1)

    # Check ubuntu version
    proc = subprocess.run(['lsb_release', '-r'], check=True, stdout=subprocess.PIPE)

    if not any(e in proc.stdout.decode() for e in supported_ubuntu_versions):
        print(f"Your ubuntu version is not supported. The following versions are supported: {supported_ubuntu_versions}")
        sys.exit(1)

    # Check docker config
    if not docker_json_path.is_file():
        print("Please run vastai install script first.")
        sys.exit(1)

    proc = subprocess.run(['docker', 'info'], check=True, stdout=subprocess.PIPE)

    if "Cgroup Driver: cgroupfs".casefold() in proc.stdout.decode().casefold():
        print("Fix for nvml error is already applied.")
        sys.exit()

    subprocess.run(['chattr', '-i', str(docker_json_path)], check=False)

    with docker_json_path.open('r', encoding='utf-8') as f:
        docker_json_dict = json.load(f) or {}

    docker_json_dict['exec-opts'] = ["native.cgroupdriver=cgroupfs"]

    with docker_json_path.open('w', encoding='utf-8') as f:
        json.dump(docker_json_dict, f, indent=2, sort_keys=False)

    print("The docker configuration file has been updated.")
    print()

    # Restart the docker service
    answer = input("""A restart of the docker service is required for the changes to take effect.
Do you want to restart the docker service? [Y/N] """)

    if answer.strip().lower() == 'y':
        proc = subprocess.run(['systemctl', 'restart', 'docker'], check=True)

        if proc.returncode == 0:
            print("The Docker service has restarted.")
        else:
            print("""The restart of the docker service failed.
Make sure you don't have permissions or that the docker service exists.""")
            sys.exit(1)
    else:
        print("You must manually restart the docker service for the changes to take effect.")

    print()

    # Make the docker config immutable
    answer = input("""You can give the docker configuration file the immutable attribute to prevent fix for nvml error from being removed later.
When immutable is set, the docker configuration file cannot be modified or deleted.
Do you want to make your docker configuration file immutable? [Y/N] """)

    if answer.strip().lower() == 'y':
        proc = subprocess.run(['chattr', '+i', str(docker_json_path)], check=True)

        if proc.returncode == 0:
            print(f"""The docker configuration file is now immutable. To undo the changes, type the following command:
chattr -i {str(docker_json_path)}""")
        else:
            print("""Changing an attribute in the docker configuration file failed."
Make sure you don't have permissions.""")
            sys.exit(1)

    print()
    print("Complete. Please run vastai install script again.")


if __name__ == '__main__':
    main()
