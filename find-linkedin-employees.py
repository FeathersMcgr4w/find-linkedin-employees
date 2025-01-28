#!/bin/python3

import requests
import re
import sys
import signal
from pwn import *

# Google Custom Search API configuration
API_KEY = ""
SEARCH_ENGINE_ID = ""

def exit_handler(sig, frame):
    print("\n\n[!] Exiting...\n")
    sys.exit(1)

# Ctrl+C
signal.signal(signal.SIGINT, exit_handler)

if len(sys.argv) != 2:
    log.failure("Use: %s your-domain.com" % sys.argv[0])
    sys.exit(1)

# Validate that the argument is a valid domain
domain = sys.argv[1]
domain_pattern = re.compile(
    r'^(?!-)[A-Za-z0-9-]{1,63}(?<!-)\.[A-Za-z]{2,6}(\.[A-Za-z]{2,6})?$'
)

if not domain_pattern.match(domain):
    log.failure(f"The argumnet entered -> '{domain}' does not appear to be a valid domain.")
    log.failure("Use: %s your-domain.com" % sys.argv[0])
    sys.exit(1)

# Key words for search
keywords = [
    "software engineer", "software developer", "Sysadmin DevOps", "Desarrollador",
    "Team Manager", "Project Manager", "Chief Executive Officer CEO",
    "Chief information security officer CISO", "Chief Information Officer CIO",
    "Soporte IT", "Operaciones IT", "Director de TI", "Jefe Operativo", "Gerente",
    "Supervisor", "Analista de Datos", "Analista de Ciberseguridad", "Cybersecurity",
    "Tecnico", "Ejecutivo de cuentas", "Coordinadora Cuentas", "Tesoreria", "Contador",
    "Administrador de Sistemas", "Administrador de Redes", "Soporte Sistemas tecnico",
    "Presidente", "Co-Founder Founder", "Recursos Humanos", "Abogado", "Atención al cliente"
]

linkedin_results = []

# Iterate over keywords
for keyword in keywords:
    query = f'"{keyword}" "{domain}" "linkedin"'
    params = {
        "key": API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": query,
    }

    print(f"[*] Searching for '{keyword}'...")
    response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)

    if response.status_code != 200:
        log.failure(f"API Error: {response.status_code} - {response.text}")
        continue

    data = response.json()

    # Process results
    if "items" in data:
        for item in data["items"]:
            title = item.get("title", "Sin título")
            link = item.get("link", "Sin enlace")
            if "linkedin.com" in link:
                linkedin_results.append({"title": title, "url": link, "keyword": keyword})
                print(f"[+] {title} - {link}")

# Save results in a txt file
output_file = "linkedin_employees.txt"
with open(output_file, "w") as file:
    for result in linkedin_results:
        file.write(f"{result['keyword']}: {result['title']} - {result['url']}\n")

print(f"\n\n[*] Results saved in '{output_file}'. Bye!")
