import concurrent.futures
import ipaddress
import json
import shlex
import socket
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request

api_get_external_ipv4 = "https://checkip.amazonaws.com"
api_connect_to_tcp_port = "https://portchecker.neuruae.com/api/v1/query"
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
        print(f"get_external_ipv4: {api_get_external_ipv4} appears to be unavailable.")
        exit(1)

    if is_ipv4(response_html.strip()):
        return response_html.strip()
    else:
        print(f"get_external_ipv4: {api_get_external_ipv4} returned invalid ipv4 address.")
        exit(1)


def test_tcp_port(ip, port):
    def sock_accept(sock):
        try:
            con, addr = sock.accept()
            con.close()
        except socket.timeout:
            pass

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(3)

    try:
        sock.bind(('0.0.0.0', int(port)))
        sock.listen()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(sock_accept, sock)

            req = urllib.request.Request(api_connect_to_tcp_port, method='POST')
            req.add_header('Accept', 'application/json')
            req.add_header('Content-Type', 'application/json')
            req.add_header('Authorization', "0013ec80-3b13-481c-96bc-2d0cd9240e68")
            req.add_header('User-Agent', user_agent)
            data_dict = {"host": ip, "ports": [int(port)]}
            data = json.dumps(data_dict).encode()

            try:
                with urllib.request.urlopen(req, data=data, timeout=10) as response:
                    if response.code != 200:
                        print(f"test_tcp_port: {api_connect_to_tcp_port} returned unexpected code.")
                        exit(1)

                    response_dict = json.load(response)

                if 'true' in json.dumps(response_dict):
                    return True
                else:
                    return False
            except (urllib.error.URLError, urllib.error.HTTPError):
                print(f"test_tcp_port: {api_connect_to_tcp_port} appears to be unavailable.")
                exit(1)
            finally:
                sock.close()
    except OSError:
        print(f"Port {port} is already listening.")

        req = urllib.request.Request(api_connect_to_tcp_port, method='POST')
        req.add_header('Accept', 'application/json')
        req.add_header('Content-Type', 'application/json')
        req.add_header('Authorization', "0013ec80-3b13-481c-96bc-2d0cd9240e68")
        req.add_header('User-Agent', user_agent)
        data_dict = {"host": ip, "ports": [int(port)]}
        data = json.dumps(data_dict).encode()

        try:
            with urllib.request.urlopen(req, data=data, timeout=10) as response:
                if response.code != 200:
                    print(f"test_tcp_port: {api_connect_to_tcp_port} returned unexpected code.")
                    exit(1)

                response_dict = json.load(response)

            if 'true' in json.dumps(response_dict):
                return True
        except (urllib.error.URLError, urllib.error.HTTPError):
            print(f"test_tcp_port: {api_connect_to_tcp_port} appears to be unavailable.")
            exit(1)

        print("Alternative testing method should be used. This will add temporary iptables rule and revert iptables to original state after the test is complete.")
        answer = input("Enter Y if you agree to proceed :")

        if answer.strip().upper() != 'Y':
            exit(1)

        proc = subprocess.run(
            shlex.split(f"sudo iptables -t nat -I PREROUTING -p tcp --dport {port} -j REDIRECT --to-port 65535"),
            stdout=subprocess.DEVNULL)

        if proc.returncode != 0:
            print("Failed to add iptables rule.")
            exit(1)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(3)

        try:
            sock.bind(('0.0.0.0', 65535))
            sock.listen()
        except OSError:
            print("Alternative testing method requires that port 65535 is not in use.")
            subprocess.run(
                    shlex.split(f"sudo iptables -t nat -D PREROUTING -p tcp --dport {port} -j REDIRECT --to-port 65535"),
                    stdout=subprocess.DEVNULL)
            exit(1)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(sock_accept, sock)

            req = urllib.request.Request(api_connect_to_tcp_port, method='POST')
            req.add_header('Accept', 'application/json')
            req.add_header('Content-Type', 'application/json')
            req.add_header('Authorization', "0013ec80-3b13-481c-96bc-2d0cd9240e68")
            req.add_header('User-Agent', user_agent)
            data_dict = {"host": ip, "ports": [int(port)]}
            data = json.dumps(data_dict).encode()

            try:
                with urllib.request.urlopen(req, data=data, timeout=10) as response:
                    if response.code != 200:
                        print(f"test_tcp_port: {api_connect_to_tcp_port} returned unexpected code.")
                        exit(1)

                    response_dict = json.load(response)

                if 'true' in json.dumps(response_dict):
                    return True
                else:
                    return False
            except (urllib.error.URLError, urllib.error.HTTPError):
                print(f"test_tcp_port: {api_connect_to_tcp_port} appears to be unavailable.")
                exit(1)
            finally:
                sock.close()
                subprocess.run(
                    shlex.split(f"sudo iptables -t nat -D PREROUTING -p tcp --dport {port} -j REDIRECT --to-port 65535"),
                    stdout=subprocess.DEVNULL)


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

external_ipv4 = get_external_ipv4()
print(f"Your public ipv4 address is {external_ipv4}")

is_closed = False

for port in range(start, end + 1):
    if test_tcp_port(external_ipv4, port):
        print(f"Port {port} is OPEN.")
    else:
        is_closed = True
        print(f"Port {port} is CLOSED.")
        break
    time.sleep(0.5)

if not is_closed:
    print("Now, you can safely run following command if this machine is idle:")
    print(f"sudo bash -c 'echo \"{start}-{end}\" > /var/lib/vastai_kaalia/host_port_range'")
else:
    print("CLOSED usually indicates that either port forwarding is configured incorrectly when using a router, or this machine's firewall is blocking access to the port.")
