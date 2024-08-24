import sys
import threading
import logging
from config.config import parse_args, config
from utils.logging_utils import setup_logging
from utils.banner import print_colored_banner
from utils.proxy_utils import set_os_proxy, unset_os_proxy
from proxy.proxy import Proxy

def print_version():
    print("POKUX v0.10.1\nA simple and fast anti-censorship tool written in Python.")

def main():
    parse_args()
    setup_logging()
    print_colored_banner()

    if config.version:
        print_version()
        sys.exit(0)

    proxy = Proxy(config)

    if config.system_proxy:
        set_os_proxy(config.port)

    proxy_thread = threading.Thread(target=proxy.start)
    proxy_thread.start()

    try:
        while proxy_thread.is_alive():
            proxy_thread.join(1)
    except KeyboardInterrupt:
        logging.info("[SIGNAL] Ctrl+C pressed, shutting down.")
        proxy.stop()
        if config.system_proxy:
            unset_os_proxy()
        sys.exit(0)
    finally:
        proxy.stop()
        if config.system_proxy:
            unset_os_proxy()

if __name__ == "__main__":
    main()
