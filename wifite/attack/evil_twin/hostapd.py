# attack/evil_twin/hostapd.py

import subprocess
import os

class HostapdManager:
    def __init__(self, ssid, iface):
        self.ssid = ssid
        self.iface = iface
        self.proc = None
        self.conf_path = "/tmp/hostapd.conf"

    def start(self):
        print(f"[*] Erstelle hostapd.conf für SSID '{self.ssid}' auf {self.iface}")
        with open(self.conf_path, "w") as f:
            f.write(f"""
interface={self.iface}
driver=nl80211
ssid={self.ssid}
hw_mode=g
channel=6
""")
        print("[*] Starte hostapd ...")
        self.proc = subprocess.Popen(["hostapd", self.conf_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def stop(self):
        if self.proc:
            print("[*] Stoppe hostapd ...")
            self.proc.terminate()
            self.proc.wait()
            self.proc = None
        if os.path.exists(self.conf_path):
            os.remove(self.conf_path)
