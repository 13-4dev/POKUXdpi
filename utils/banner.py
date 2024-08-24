import os
from colorama import init, Fore
from config.config import config

init(autoreset=True)

def print_colored_banner():
    if config.no_banner:
        return

    current_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(current_dir, 'assets', 'logo')


    try:
        with open(logo_path, 'r', encoding='utf-8') as logo_file:
            logo = logo_file.read()
    except FileNotFoundError:
        return

    print(Fore.CYAN + logo)
    
    config_details = [
        f"ADDR    : {config.addr}",
        f"PORT    : {config.port}",
        f"DNS     : {config.dns_addr}",
        f"DEBUG   : {config.debug}"
    ]
    
    max_length = max(len(line) for line in config_details)
    
    separator = "-" * max_length
    
    print(Fore.GREEN + separator)
    for detail in config_details:
        print(Fore.GREEN + detail)
    print(Fore.GREEN + separator)
