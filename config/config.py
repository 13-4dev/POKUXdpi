import argparse
import logging
import re
import sys

class Config:
    def __init__(self):
        self.addr = "127.0.0.1"
        self.port = 8080
        self.dns_addr = "8.8.8.8"
        self.dns_port = 53
        self.enable_doh = False
        self.debug = False
        self.no_banner = False
        self.system_proxy = True
        self.timeout = 0
        self.allowed_pattern = []
        self.window_size = 0
        self.version = False

config = Config()

def parse_args():
    parser = argparse.ArgumentParser(description="POKUXs")
    parser.add_argument("--addr", default="127.0.0.1", help="listen address")
    parser.add_argument("--port", type=int, default=8080, help="port")
    parser.add_argument("--dns-addr", default="8.8.8.8", help="dns address")
    parser.add_argument("--dns-port", type=int, default=53, help="port number for dns")
    parser.add_argument("--enable-doh", action="store_true", help="enable 'dns-over-https'")
    parser.add_argument("--debug", action="store_true", help="enable debug output")
    parser.add_argument("--no-banner", action="store_true", help="disable banner")
    parser.add_argument("--system-proxy", action="store_true", help="enable system-wide proxy")
    parser.add_argument("--timeout", type=int, default=0, help="timeout in milliseconds; no timeout when not given")
    parser.add_argument("--window-size", type=int, default=0, help="chunk size, in number of bytes, for fragmented client hello")
    parser.add_argument("--version", action="store_true", help="print POKUXs version")
    parser.add_argument("--pattern", action="append", help="bypass DPI only on packets matching this regex pattern; can be given multiple times")

    args = parser.parse_args()

    config.addr = args.addr
    config.port = args.port
    config.dns_addr = args.dns_addr
    config.dns_port = args.dns_port
    config.enable_doh = args.enable_doh
    config.debug = args.debug
    config.no_banner = args.no_banner
    config.system_proxy = args.system_proxy
    config.timeout = args.timeout
    config.window_size = args.window_size
    config.version = args.version

    if args.pattern:
        try:
            config.allowed_pattern = [re.compile(p) for p in args.pattern]
        except re.error as e:
            logging.error(f"Invalid regex pattern: {e}")
            sys.exit(1)
