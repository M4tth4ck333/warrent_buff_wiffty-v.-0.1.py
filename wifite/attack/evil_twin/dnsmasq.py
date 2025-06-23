# attack/evil_twin/dnsmasq.py

import subprocess
import os

class DnsmasqManager:
    def __init__(self, iface):
        self.iface = iface
        self.proc = None
        self.conf_path = "/tmp/dnsmasq.conf"

    def start(self):
        print(f"[*] Erstelle dnsmasq.conf auf Interface {self.iface}")
        with open(self.conf_path, "w") as f:
            f.write(f"""
interface={self.iface}
dhcp-range=10.0.0.10,10.0.0.250,12h
dhcp-option=3,10.0.0.1
dhcp-option=6,10.0.0.1
log-queries
log-dhcp
""")
        print("[*] Starte dnsmasq ...")
        self.proc = subprocess.Popen(["dnsmasq", "-C", self.conf_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def stop(self):
        if self.proc:
            print("[*] Stoppe dnsmasq ...")
            self.proc.terminate()
            self.proc.wait()
            self.proc = None
        if os.path.exists(self.conf_path):
            os.remove(self.conf_path)
