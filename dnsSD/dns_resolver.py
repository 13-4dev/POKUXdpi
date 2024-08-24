import re
import dns
import dns.message
import dns.query
import dns.resolver
import requests
import socket
import logging
import base64
from config.config import config

class DNSResolver:
    def __init__(self):
        self.host = config.dns_addr
        self.port = config.dns_port
        self.enable_doh = config.enable_doh

    def lookup(self, domain, use_system_dns):
        ip_regex = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9][0-9]?)$"
        if re.match(ip_regex, domain):
            return domain

        if use_system_dns:
            logging.debug("[DNS] Resolving with system dns")
            return self.system_lookup(domain)

        if self.enable_doh:
            logging.debug(f"[DNS] {domain} resolving with dns over https")
            return self.doh_lookup(domain)

        logging.debug(f"[DNS] {domain} resolving with custom dns")
        return self.custom_lookup(domain)

    def custom_lookup(self, domain):
        try:
            resolver = dns.resolver.Resolver(configure=False)
            resolver.nameservers = [self.host]
            answer = resolver.resolve(domain, 'A')
            return answer[0].address
        except dns.resolver.NXDOMAIN:
            logging.error("[DNS] NXDOMAIN for domain: %s", domain)
            return None
        except Exception as e:
            logging.error(f"[DNS] Error resolving {domain} with custom DNS: {e}")
            return None

    def system_lookup(self, domain):
        try:
            return socket.gethostbyname(domain)
        except socket.gaierror as e:
            logging.error("[DNS] System DNS lookup failed for domain: %s, error: %s", domain, e)
            return None

    def doh_lookup(self, domain):
        url = f"https://{self.host}/dns-query?dns="
        message = dns.message.make_query(domain, dns.rdatatype.A)
        try:
            query_data = base64.urlsafe_b64encode(message.to_wire()).decode()
            headers = {"Accept": "application/dns-message"}
            response = requests.get(url + query_data, headers=headers)
            if response.status_code == 200:
                return dns.message.from_wire(response.content).answer[0][0].address
            else:
                logging.error(f"[DNS] DOH lookup failed with status code {response.status_code}")
        except Exception as e:
            logging.error(f"[DNS] DOH lookup failed for domain: {domain}, error: {e}")
        return None
