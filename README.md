🧠🔓 Warrent Buff WiFFT[y] v0.1 – Wireless Attack Framework Reloaded

    ⚙️ Modular. 🧠 KI-gestützt. 🕵️ Evil Twin Ready.
    "If Buffett did Wi-Fi audits..." – by Jan

🚀 Überblick

Warrent Buff WiFFT[y] ist ein modernes, modulares Wireless-Audit-Framework für Pentester, Red Teams und Security-Forscher.
Es kombiniert klassische Angriffe (WEP/WPA/WPS), KI-gestützte Zielauswahl und Passwortgenerierung, Evil Twin Automation und ein flexibles Datenbank-Backend – alles steuerbar per CLI, bald auch per GUI.
💡 Features

    Klassische Wireless Attacks:

        WEP, WPA/WPA2, WPS (Aircrack-ng Suite, Reaver, Hashcat, Crunch)

    🧠 KI-Unterstützung (LLM/GPT):

        Dynamische Wortlisten aus SSID/BSSID/Vendor

        Smarte Zielauswahl (MAC → Hersteller → Angriffsmethode)

        Social Engineering Text-Injection für Evil Twin (zeit- & ortsabhängig)

    🕸️ Evil Twin Automation:

        Fake-AP mit hostapd, DHCP/DNS-Umleitung (dnsmasq), Captive Portal (Webserver)

        Vendor-spezifische Loginseiten (ASUS, TP-Link, FritzBox, etc.)

        Passwortvalidierung gegen echten AP, automatische Deauthentifizierung

    PMKID-Attacke:

        hcxdumptool + hashcat für clientlose WPA2/PMKID-Angriffe

    Zentrale SQLite-Datenbank:

        Speicherung von Zielen, Passwortversuchen, Cracks, AI-Entscheidungen

    Cracker-Wrapper-Modul:

        Einheitliche Schnittstelle für Hashcat, John, Pyrit, Crunch etc.

    Wortlisten-Generator:

        GPT-basierte Heuristik + Crunch-Regeln für gezielte Passwortlisten

    Docker & Singularity Support:

        Für portable, reproduzierbare Pentest-Umgebungen

    Zukunfts-Module:

        GUI (Tkinter, OpenGL), Bluetooth/BLE, Drohnen-Bridge, lokale GPT-Modelle

🗂️ Projektstruktur (modular & erweiterbar)


        warrent_buff_wiffty/
        ├── attack/
        │   ├── evil_twin/        # Hostapd, DNSMasq, Deauth, Validator, Webserver
        │   └── pmkid.py          # PMKID Capture & Hash Conversion
        ├── tools/
        │   ├── cracker_base.py   # Cracker-Wrapper
        │   └── hashcat.py / crunch.py / aircrack.py / ...
        ├── db/
        │   └── wifite.db         # SQLite-DB: Targets, Passwortversuche etc.
        ├── config/
        │   ├── setup.cfg         # Installations- & Modulkonfiguration
        │   └── hostapd.tpl / dnsmasq.tpl / ...
        ├── main/
        │   └── warrent_buff_wiffty-v.0.1.py   # CLI-Entry Point
        └── README.md
        
⚡ Installation & Setup
Systemvoraussetzungen (Debian/Ubuntu)

bash
sudo apt update
sudo apt install -y hashcat aircrack-ng crunch dnsmasq hostapd mdk4 reaver python3 python3-pip
pip3 install -r requirements.txt

Python Requirements (Ausschnitt)
    scapy
    colorama
    sqlite3
    (und weitere, siehe requirements.txt)
🚀 Schnellstart

bash
python3 main/warrent_buff_wiffty-v.0.1.py

Optionen:
    WPA-only, Evil Twin only, Wordlist-Gen, Datenbank-Analyse etc.
🧪 Coming Soon

    🌍 GUI mit Tkinter & OpenGL
    📡 Bluetooth/BLE-Scan- und Angriffsmodule
    🚀 Drohnen-Exfiltration Bridge (WLAN + SDR)
    🧬 Lokales GPT-Modell via ollama / llama.cpp

🛡️ Sicherheit & Legal

Achtung: Dieses Framework ist ausschließlich für den legalen Einsatz in eigenen Netzwerken oder mit
ausdrücklicher Erlaubnis des Netzwerkbetreibers gedacht!
Missbrauch ist strafbar.
👨‍💻 Autor & Credits

Jan Schröder aka buff-sec
Projektleitung: The PentState / Little Zucker Berg / TheBigPingTheory
⚖️ Lizenz

GPLv3 – Knowledge is Free. Share it.

Pull Requests, Feature-Ideen & Bug-Reports sind willkommen!
Stay safe. Hack smart.
