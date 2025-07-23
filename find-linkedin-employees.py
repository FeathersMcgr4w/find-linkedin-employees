#!/usr/bin/env python3

import requests
import re
import sys
import signal
import time
import random
import os
from pwn import *

# ctro+c (Interrupt)
def exit_handler(sig, frame):
    print("\n\n[!] Exiting...\n")
    sys.exit(1)

signal.signal(signal.SIGINT, exit_handler)

# banner
def banner():
    print(r"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~  ____  _               ____             _                     ~
~ / ___|| |__   ___ _ __|  _ \  ___  _ __| | __                 ~
~ \___ \| '_ \ / _ \ '__| | | |/ _ \| '__| |/ /     /\   /\     ~
~  ___) | | | |  __/ |  | |_| | (_) | |  |   <     /  \ /  \    ~
~ |____/|_| |_|\___|_|  |____/ \___/|_|  |_|\_\   /    .    \   ~
~ | | | | ___ | |_ __ ___   ___  ___             /___________\  ~
~ | |_| |/ _ \| | '_ ` _ \ / _ \/ __|           --------------- ~
~ |  _  | (_) | | | | | | |  __/\__ \               _     _     ~
~ |_| |_|\___/|_|_| |_| |_|\___||___/            '-(_)---(_)-'  ~
~                                                               ~
~ Author: FeathersMcgr4w                                        ~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """)

if len(sys.argv) != 2:
    banner()
    log.failure("Use: python3 %s your-domain.com" % sys.argv[0])
    sys.exit(1)

# verify valid domain (argument)
domain = sys.argv[1]
domain_pattern = re.compile(
    r'^(?!-)[A-Za-z0-9-]{1,63}(?<!-)\.[A-Za-z]{2,6}(\.[A-Za-z]{2,6})?$'
)

if not domain_pattern.match(domain):
    log.failure(f"The argument entered -> '{domain}' does not appear to be a valid domain.")
    log.failure("Use: python3 %s your-domain.com" % sys.argv[0])
    sys.exit(1)

# load credentials
def load_credentials(filepath):
    credentials = {}
    try:
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and ":" in line:
                    key, value = line.split(":", 1)
                    credentials[key.strip()] = value.strip()
    except FileNotFoundError:
        log.failure(f"Credentials file not found at: {filepath}")
        sys.exit(1)
    return credentials

credentials_path = os.path.join(os.path.dirname(__file__), "../credentials/your_api_credentials.txt")
creds = load_credentials(credentials_path)

# Google Custom Search API configuration
API_KEY = creds.get("googleApi")
SEARCH_ENGINE_ID = creds.get("googleId")

if not API_KEY or not SEARCH_ENGINE_ID:
    log.failure("Missing 'googleApi' or 'googleId' in credentials file.")
    sys.exit(1)

# keywords for search
keywords = [
    "software engineer", "software developer", "Sysadmin DevOps", "Desarrollador",
    "Team Manager", "Project Manager", "Chief Executive Officer CEO",
    "Chief information security officer CISO", "Chief Information Officer CIO",
    "Soporte IT", "Director de TI", "Gerente",
    "Analista de Ciberseguridad", "Cybersecurity",
    "Ejecutivo de cuentas", "Tesoreria",
    "Presidente", "Founder", "Recursos Humanos", "Atención al cliente"
]

linkedin_results = []

# filter duplicate results from URLs
def remove_duplicates(results):
    seen = set()
    unique_results = []
    for result in results:
        url = result["url"]
        if url not in seen:
            seen.add(url)
            unique_results.append(result)
    return unique_results

# random time
def random_delay():
    return round(random.uniform(2, 5))

for keyword in keywords:
    query = f'"{keyword}" "{domain}" "linkedin"'
    params = {
        "key": API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": query,
    }

    try:
        response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)

        if response.status_code == 200:
            data = response.json()

            if "items" in data:
                for item in data["items"]:
                    title = item.get("title", "Sin título")
                    link = item.get("link", "Sin enlace")
                    if "linkedin.com" in link:
                        linkedin_results.append({
                            "title": title,
                            "url": link,
                            "keyword": keyword
                        })

        elif response.status_code == 429:
            log.failure("Error 429: Too Many Requests.")
            log.failure("API quota may have been exceeded. Free plan allows 100 requests per day.")
            sys.exit(1)

        else:
            log.failure(f"Error in API request: {response.status_code}")
            log.failure(f"Response: {response.text}")

    except requests.exceptions.RequestException as e:
        log.failure(f"Exception in API request: {e}")
        continue

    delay = random_delay()
    log.info(f"Searching for '{keyword}'. Gathering information, please wait...")
    time.sleep(delay)

linkedin_results = remove_duplicates(linkedin_results)

# save results
output_file = "linkedin_employees.txt"
with open(output_file, "w") as file:
    for result in linkedin_results:
        file.write(f"{result['keyword']}: {result['title']} - {result['url']}\n")

log.success(f"{len(linkedin_results)} LinkedIn profiles found.")
log.info(f"Results saved in 'your_domain.com/linkedin/{output_file}'. Blessed Hacking!")
