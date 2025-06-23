# attack/evil_twin/iptables.py

import subprocess

class IptablesManager:
    def __init__(self, iface):
        self.iface = iface

    def setup(self):
        print("[*] Setze iptables Regeln für Redirects ...")
        # Beispiel: redirect Port 80 auf 10.0.0.1 (AP IP)
        subprocess.run(["iptables", "-t", "nat", "-A", "PREROUTING", "-i", self.iface,
                        "-p", "tcp", "--dport", "80", "-j", "DNAT", "--to-destination", "10.0.0.1"], check=False)

        subprocess.run(["iptables", "-t", "nat", "-A", "POSTROUTING", "-o", self.iface,
                        "-j", "MASQUERADE"], check=False)

        # IP forwarding einschalten
        subprocess.run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)

    def cleanup(self):
        print("[*] Lösche iptables Regeln ...")
        subprocess.run(["iptables", "-t", "nat", "-F"], check=False)
        subprocess.run(["iptables", "-F"], check=False)
        subprocess.run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
