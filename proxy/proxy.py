import contextlib
import logging
import socket
import threading
import time
from dnsSD.dns_resolver import DNSResolver

BUFFER_SIZE = 1024

class Proxy:
    def __init__(self, config):
        self.addr = config.addr
        self.port = config.port
        self.timeout = config.timeout
        self.resolver = DNSResolver()
        self.window_size = config.window_size
        self.allowed_pattern = config.allowed_pattern
        self.running = True

    def start(self):
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            sock.bind((self.addr, self.port))
            sock.listen(5)
            logging.info(f"[PROXY] Listening on {self.addr}:{self.port}")

            while self.running:
                conn, addr = sock.accept()
                logging.info(f"[PROXY] Accepted connection from {addr}")
                threading.Thread(target=self.handle_connection, args=(conn, addr)).start()

    def handle_connection(self, conn, addr):
        try:
            pkt = self.read_http_packet(conn)
            if pkt is None:
                conn.close()
                return

            domain = pkt['domain']
            matched = self.pattern_matches(domain.encode())
            use_system_dns = not matched

            ip = self.resolver.lookup(domain, use_system_dns)
            if ip is None:
                conn.sendall(f"{pkt['version']} 502 Bad Gateway\r\n\r\n".encode())
                conn.close()
                return

            if pkt['method'] == "CONNECT":
                logging.debug(f"[PROXY] Start HTTPS for {domain}")
                self.handle_https(conn, matched, pkt, ip)
            else:
                logging.debug(f"[PROXY] Handling HTTP for {domain}")
                self.handle_http(conn, pkt, ip)
        except Exception as e:
            logging.error(f"[PROXY] Connection error from {addr}: {e}")
        finally:
            conn.close()

    def pattern_matches(self, data):
        if not self.allowed_pattern:
            return True
        return any(pat.match(data) for pat in self.allowed_pattern)

    def read_http_packet(self, conn):
        try:
            request = conn.recv(BUFFER_SIZE).decode()
            request = "\n".join([line.strip() for line in request.splitlines()])
            method, path, version = request.splitlines()[0].split()
            domain, port = (request.split("Host: ")[1].split()[0]).split(":") if ":" in request else (request.split("Host: ")[1], None)
            logging.debug(f"[PROXY] Request from {conn.getpeername()}\n\n{request}")
            return {"method": method, "domain": domain, "port": port or "80", "version": version, "path": path, "raw": request}
        except Exception as e:
            logging.error(f"[PROXY] Failed to parse request: {e}")
            return None

    def handle_http(self, conn, pkt, ip):
        try:
            rconn = socket.create_connection((ip, int(pkt['port'])))
            rconn.sendall(pkt['raw'].encode())

            logging.debug(f"[HTTP] Forwarding HTTP request to {pkt['domain']}:{pkt['port']}")

            while True:
                data = rconn.recv(BUFFER_SIZE)
                if not data:
                    break
                conn.sendall(data)
        except Exception as e:
            logging.error(f"[PROXY] HTTP connection error: {e}")
        finally:
            conn.close()

    def handle_https(self, conn, matched, pkt, ip):
        try:
            rconn = socket.create_connection((ip, 443))
            conn.sendall(f"{pkt['version']} 200 Connection Established\r\n\r\n".encode())
            logging.debug(f"[HTTPS] Sent 200 Connection Established to {conn.getpeername()}")

            if matched and self.window_size > 0:
                logging.debug(f"[HTTPS] Client sent hello {len(pkt['raw'])} bytes")
                logging.debug(f"[HTTPS] Writing chunked client hello to {pkt['domain']}")
                logging.debug(f"[HTTPS] window-size: {self.window_size}")
                logging.debug(f"[HTTPS] Using legacy fragmentation.")
                self.bypass_dpi(conn, rconn)
            else:
                logging.debug(f"[HTTPS] New connection to the server {pkt['domain']} {rconn.getpeername()}")
                threading.Thread(target=self.serve, args=(conn, rconn)).start()
                self.serve(rconn, conn)

        except Exception as e:
            logging.error(f"[HTTPS] Error handling HTTPS connection: {e}")
        finally:
            conn.close()

    def bypass_dpi(self, client_conn, server_conn):
        try:
            logging.debug("[HTTPS] Fragmenting ClientHello for DPI bypass")
            initial_data = client_conn.recv(BUFFER_SIZE)

            if len(initial_data) > self.window_size:
                first_part = initial_data[:self.window_size]
                remaining_part = initial_data[self.window_size:]
            else:
                first_part = initial_data
                remaining_part = b""

            server_conn.sendall(first_part)
            time.sleep(0.1)
            server_conn.sendall(remaining_part)

            threading.Thread(target=self.serve, args=(client_conn, server_conn)).start()
            self.serve(server_conn, client_conn)

        except Exception as e:
            logging.error(f"[DPI Bypass] Error during DPI bypass: {e}")

    def serve(self, src, dst):
        try:
            while True:
                data = src.recv(BUFFER_SIZE)
                if not data:
                    break
                dst.sendall(data)
        except socket.error as e:
            logging.error(f"[HTTPS] Serve error: {e}")
        except Exception as e:
            logging.error(f"[HTTPS] Unexpected serve error: {e}")

    def stop(self):
        self.running = False
        logging.info("[PROXY] Stopping proxy server...")
