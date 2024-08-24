import subprocess
import sys
import logging

def set_os_proxy(port):
    if sys.platform != "darwin":
        return

    try:
        network = subprocess.check_output(
            "sh -c \"networksetup -listnetworkserviceorder | grep `route -n get 0.0.0.0 | grep 'interface' | cut -d ':' -f2` -B 1 | head -n 1 | cut -d ' ' -f 2-\"",
            shell=True).decode().strip()

        subprocess.check_call(
            f"sh -c \"networksetup -setwebproxy '{network}' 127.0.0.1 {port}\"", shell=True)
        subprocess.check_call(
            f"sh -c \"networksetup -setsecurewebproxy '{network}' 127.0.0.1 {port}\"", shell=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error setting proxy: {e}")

def unset_os_proxy():
    if sys.platform != "darwin":
        return

    try:
        network = subprocess.check_output(
            "sh -c \"networksetup -listnetworkserviceorder | grep `route -n get 0.0.0.0 | grep 'interface' | cut -d ':' -f2` -B 1 | head -n 1 | cut -d ' ' -f 2-\"",
            shell=True).decode().strip()

        subprocess.check_call(
            f"sh -c \"networksetup -setwebproxystate '{network}' off\"", shell=True)
        subprocess.check_call(
            f"sh -c \"networksetup -setsecurewebproxystate '{network}' off\"", shell=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error unsetting proxy: {e}")
