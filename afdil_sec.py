import json
import socket
import ssl
import sys
import urllib.parse
import urllib.request

RED, GREEN, CYAN, YELLOW, RESET = (
    "\033[91m",
    "\033[92m",
    "\033[96m",
    "\033[93m",
    "\033[0m",
)


def deep_port_scan(host):
    """Deep Port Scanner for Infrastructure"""
    if not host:
        print(f"{RED}[-] Target Host Missing!{RESET}")
        return
    host = host.replace("https://", "").replace("http://", "").split("/")[0]

    ports = [80, 443, 8080, 8443, 22, 53, 3306, 8000]
    print(f"{CYAN}\n[=== AFDIL Port Scan Target: {host} ===]{RESET}")

    try:
        ip = socket.gethostbyname(host)
        print(f"{YELLOW}[i] Target Resolved IP: {ip}{RESET}")
    except Exception as e:
        print(f"{RED}[-] IP Resolution Failed: {e}{RESET}")
        return

    for p in ports:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.5)
            res = s.connect_ex((ip, p))
            s.close()
            if res == 0:
                print(f"{GREEN}[+] Port {p:<5} --> OPEN{RESET}")
            else:
                print(f"{RED}[-] Port {p:<5} --> CLOSED{RESET}")
        except Exception:
            pass


def check_ssl_details(hostname):
    """SSL/TLS Inspection"""
    if not hostname:
        print(f"{RED}[-] Target Hostname Missing for SSL Check!{RESET}")
        return
    hostname = (
        hostname.replace("https://", "").replace("http://", "").split("/")[0]
    )
    print(f"{CYAN}\n[=== AFDIL SSL Inspection: {hostname} ===]{RESET}")

    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=3) as sock:
            with context.wrap_socket(
                sock, server_hostname=hostname
            ) as ssock:
                cert = ssock.getpeercert()
                version = ssock.version()
                cipher = ssock.cipher()
                print(f"{GREEN}[✓] Protocol: {version}{RESET}")
                print(f"{GREEN}[✓] Cipher: {cipher[0]}{RESET}")
                issuer = dict(x[0] for x in cert.get("issuer", []))
                print(
                    f"{GREEN}[✓] Issuer: {issuer.get('organizationName', 'Unknown')}{RESET}"
                )
    except Exception as e:
        print(f"{RED}[-] SSL Audit Failed: {e}{RESET}")


def extended_route_check(url):
    """Deep Route Discovery with Fake-200 Filter"""
    if not url:
        print(f"{RED}[-] Target URL Missing for Route Check!{RESET}")
        return
    if not url.startswith("http"):
        url = "https://" + url

    endpoints = [
        "robots.txt",
        "sitemap.xml",
        "admin",
        "login",
        "api",
        ".env",
        ".git/HEAD",
    ]
    print(f"{CYAN}\n[=== AFDIL Route Audit: {url} ===]{RESET}")

    for ep in endpoints:
        target = f"{url.rstrip('/')}/{ep}"
        try:
            req = urllib.request.Request(
                target,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AFDIL-Sec/4.1"
                },
            )
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                content_type = resp.headers.get("Content-Type", "").lower()
                body = resp.read(500).decode("utf-8", errors="ignore")

                if "text/html" in content_type and (
                    "<html" in body or "<doctype" in body.lower()
                ):
                    if ep in [".env", ".git/HEAD"]:
                        print(
                            f"{YELLOW}[!] Fake 200 OK (SPA HTML Page): {target}{RESET}"
                        )
                    else:
                        print(f"{GREEN}[+] Web Page Available: {target}{RESET}")
                else:
                    print(
                        f"{GREEN}[+] Real Resource Found ({content_type}): {target}{RESET}"
                    )

        except urllib.error.HTTPError as e:
            print(f"{RED}[-] Status {e.code}: {target}{RESET}")
        except Exception:
            pass


def parse_and_run_afdil(script_text):
    """Simple & Flexible Command Parser"""
    for line in script_text.split("\n"):
        clean = line.strip()
        if not clean or clean.startswith("#") or clean.startswith("//"):
            continue

        # Extract values inside quotes or after '='
        val = None
        if '"' in clean:
            val = clean.split('"')[1]
        elif "=" in clean:
            val = clean.split("=")[1].strip()

        if "deep_scan" in clean:
            deep_port_scan(val)
        elif "check_ssl" in clean or "check ssl" in clean:
            check_ssl_details(val)
        elif "deep_routes" in clean:
            extended_route_check(val)


if __name__ == "__main__":
    print(f"{CYAN}⚡ AFDIL-Sec Engine v4.1 (Fixed & Activated){RESET}")
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], "r") as f:
                parse_and_run_afdil(f.read())
        except FileNotFoundError:
            print(f"{RED}[-] File not found.{RESET}")
    else:
        print(f"{CYAN}[i] Usage: python afdil_sec.py <script.afsec>{RESET}")