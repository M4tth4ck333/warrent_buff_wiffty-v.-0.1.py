based on an idea from Sandman: Include "Evil Twin" attack in Wifite.
Descript by fluxion 
added by m4tth4ck
Evil Twin
=========
README: Evil Twin Attack Module for Wifite
Overview

The Evil Twin Attack Module for Wifite allows you to create a rogue Wi-Fi Access Point (AP),
that mimics a legitimate AP. The goal is to trick clients into connecting to the fake AP in order
to capture credentials, analyze network traffic, or perform targeted attacks.

How It Works
    Target Selection:
    Wifite scans for available Wi-Fi networks and lets you select the target AP (SSID & BSSID).
    Launching the Evil Twin Attack:
        A rogue AP is started with the same SSID and channel as the target (using hostapd).
        DHCP and DNS services are provided via dnsmasq.
        iptables redirects all HTTP/HTTPS traffic to a local web server.
    Captive Portal:
        Connected clients are presented with a fake login page (e.g., mimicking their router).
        Entered passwords are saved and validated against the real AP.
    Deauthentication:
        mdk4 or aireplay-ng is used to continuously disconnect clients from the real AP, pushing them to the Evil Twin.
    Cleanup:
        After the attack, all services and iptables rules are reset.
Modules and Components

Module	        Purpose
manager.py	    Controls the flow, loads configuration, coordinates the attack
hostapd.py	    Starts and configures the fake AP
dnsmasq.py	    DHCP and DNS server, redirects requests to captive portal
iptables.py	    Redirects traffic to the web server, optionally with sslstrip
webserver.py	  Serves fake login pages, stores credentials
validator.py	  Checks passwords against the real AP, ends attack on success
deauth.py	      Forces clients to disconnect from the real AP

Advanced Features
    Dynamic vendor matching (MAC → router type → login page)
    Multilingual captive portals
    Logging with timestamp, client MAC, and user agent
    Integration with Hashcat/Pyrit for password analysis
    Modular state manager (JSON/DB backend)
Requirements
    hostapd
    dnsmasq
    iptables
    mdk4 or aireplay-ng
    Python 3.x
    (optional) sslstrip, Pyrit, Hashcat
Usage
    Install all requirements
    Start Wifite and select the target AP
    Launch the Evil Twin attack
    Analyze captured passwords and logs
Security Notice
This tool is for testing and research purposes only. Use it only on networks you own or have explicit permission to test!
Further Development
    Improved user interface and workflow
    More router templates and languages
    Automated analysis and reporting
