import concurrent.futures
import configparser
import ipaddress
import json
import pathlib
import random
import re
import socket
import subprocess
import time
import urllib.error
import urllib.request

api_get_external_ipv4 = "https://checkip.amazonaws.com"
api_connect_to_tcp_port = "https://check-host.net/check-tcp?host={ip}:{port}&max_nodes=3"
api_get_port_check_result = "https://check-host.net/check-result/{request_id}"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"


def print_info(msg):
    print(f"\\033[34m{msg}\\033[0m")

def print_warn(msg):
    print(f"\\033[33m{msg}\\033[0m")

def print_error(msg):
    print(f"\\033[31m{msg}\\033[0m")

def is_ipv4(text):
    try:
        ipaddress.IPv4Network(text)
        return True
    except ValueError:
        return False

def get_external_ipv4():
    try:
        with urllib.request.urlopen(api_get_external_ipv4, timeout=10) as response:
            response_html = response.read().decode(response.headers.get_content_charset())
    except (urllib.error.URLError, urllib.error.HTTPError, TypeError):
        print_error(f"get_external_ipv4: {api_get_external_ipv4} appears to be unavailable.")
        exit(1)

    if is_ipv4(response_html.strip()):
        return response_html.strip()
    else:
        print_error(f"get_external_ipv4: {api_get_external_ipv4} returned invalid ipv4 address.")
        exit(1)

def test_tcp_port(ip, port):
    def sock_accept(sock):
        con, addr = sock.accept()
        con.close()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(10)
        try:
            sock.bind(('0.0.0.0', int(port)))
        except OSError:
            print(f"Port {port} is already listening.")
            return False
        sock.listen()

        future = executor.submit(sock_accept, sock)

        req = urllib.request.Request(api_connect_to_tcp_port.format(ip=ip, port=port))
        req.add_header('Accept', 'application/json')
        req.add_header('User-Agent', user_agent)

        try:
            response = urllib.request.urlopen(req, timeout=10)
            json_dict = json.load(response)
            response.close()
            
            if 'request_id' not in json_dict:
                print_error(f"test_tcp_port: {api_connect_to_tcp_port} returned invalid json.")
                sock.close()
                exit(1)
        except (urllib.error.URLError, urllib.error.HTTPError):
            print_error(f"test_tcp_port: {api_connect_to_tcp_port} appears to be unavailable.")
            sock.close()
            exit(1)

        try:
            future.result(timeout=10)
            return True
        except (concurrent.futures.TimeoutError, socket.timeout):
            return False
        finally:
            sock.close()

def test_tcp_port_without_listen(ip, port):
    req = urllib.request.Request(api_connect_to_tcp_port.format(ip=ip, port=port))
    req.add_header('Accept', 'application/json')
    req.add_header('User-Agent', user_agent)

    try:
        response = urllib.request.urlopen(req, timeout=10)
        json_dict = json.load(response)
        response.close()

        if 'request_id' in json_dict:
            request_id = json_dict['request_id']
        else:
            print_error(f"test_tcp_port_without_listen: {api_connect_to_tcp_port} returned invalid json.")
            exit(1)
    except (urllib.error.URLError, urllib.error.HTTPError):
        print_error(f"test_tcp_port_without_listen: {api_connect_to_tcp_port} appears to be unavailable.")
        exit(1)

    time.sleep(3)

    req = urllib.request.Request(api_get_port_check_result.format(request_id=request_id))
    req.add_header('Accept', 'application/json')
    req.add_header('User-Agent', user_agent)

    try:
        response = urllib.request.urlopen(req, timeout=10)
        json_dict = json.load(response)
        response.close()
    except (urllib.error.URLError, urllib.error.HTTPError):
        print_error(f"test_tcp_port_without_listen: {api_connect_to_tcp_port} appears to be unavailable.")
        exit(1)

    if "\"time\"" in json.dumps(json_dict):
        return True
    else:
        return False


start = input("Enter start port: ")
if not start.isdigit() or not (0 <= int(start) <= 65535):
    print("Invalid start port.")
    exit(1)

end = input("Enter end port: ")
if not end.isdigit() or not (0 <= int(end) <= 65535):
    print("Invalid end port.")
    exit(1)

start = int(start)
end = int(end)

if start >= end:
    print("End port must be larger than start port.")
    exit(1)

picked = random.randint(start, end)

external_ipv4 = get_external_ipv4()
print(f"Your public ipv4 address is {external_ipv4}")

is_closed = False

for port in [start, picked, end]:
    # Try without listening (vast daemon port)
    if test_tcp_port_without_listen(external_ipv4, port):
        print(f"Port {port} is already listening.")
        print(f"Port {port} is OPEN.")
    else:
        if test_tcp_port(external_ipv4, port):
            print(f"Port {port} is OPEN.")
        else:
            is_closed = True
            print(f"Port {port} is CLOSED.")
            break
    time.sleep(3)

if not is_closed:
    print("Now, you can safely run following command if this machine is idle:")
    print(f"sudo bash -c 'echo \"{start}-{end}\" > /var/lib/vastai_kaalia/host_port_range'")
else:
    print("CLOSED usually indicates that either port forwarding is configured incorrectly when using a router, or this machine's firewall is blocking access to the port.")
    print("Exception : If docker is mapping specific port but your client isn't actually using that port, then the port cannot be tested, and the port can only be tested after the client deletes the instance.")
