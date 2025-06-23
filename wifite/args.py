#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
import importlib

from .util.color import Color

class Arguments:
    '''Hält Argumente für Wifite und lädt Tools dynamisch'''

    def __init__(self, configuration):
        self.config = configuration
        self.verbose = '-v' in sys.argv or '-hv' in sys.argv or '-vh' in sys.argv
        self.args = self._parse_arguments()
        self.loaded_tools = {}
        self._load_tools()

    def _verbose(self, msg):
        return Color.s(msg) if self.verbose else argparse.SUPPRESS

    def _parse_arguments(self):
        parser = argparse.ArgumentParser(
            usage=argparse.SUPPRESS,
            formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=80, width=130)
        )

        self._add_global_args(parser.add_argument_group(Color.s('{C}SETTINGS{W}')))
        self._add_wep_args(parser.add_argument_group(Color.s('{C}WEP{W}')))
        self._add_wpa_args(parser.add_argument_group(Color.s('{C}WPA{W}')))
        self._add_wps_args(parser.add_argument_group(Color.s('{C}WPS{W}')))
        self._add_pmkid_args(parser.add_argument_group(Color.s('{C}PMKID{W}')))
        self._add_eviltwin_args(parser.add_argument_group(Color.s('{C}EVIL TWIN{W}')))
        self._add_dns_args(parser.add_argument_group(Color.s('{C}DNS RECON{W}')))
        self._add_command_args(parser.add_argument_group(Color.s('{C}COMMANDS{W}')))

        return parser.parse_args()

    def _load_tools(self):
        # Beispiel für dynamischen Import eines DNS Recon Tools
        if getattr(self.args, 'use_dns_recon', False):
            try:
                mod = importlib.import_module('tools.dns_recon')
                self.loaded_tools['dns_recon'] = mod
            except ImportError:
                print(Color.s('{R}Fehler:{W} DNS Recon Modul konnte nicht geladen werden.'))
        # Weitere Tools können hier dynamisch geladen werden
        # z.B. if self.args.use_wep: self.loaded_tools['wep'] = importlib.import_module('tools.wep')

    def _add_global_args(self, group):
        group.add_argument('-v', '--verbose', action='count', default=0, dest='verbose',
                           help=Color.s('Zeigt mehr Optionen ({C}-h -v{W}). Druckt Befehle und Outputs. (default: {G}leise{W})'))

        group.add_argument('-i', action='store', dest='interface', metavar='[interface]', type=str,
                           help=Color.s('Wireless Interface, z.B. {C}wlan0mon{W} (default: {G}abfragen{W})'))

        group.add_argument('-c', '--channel', action='store', dest='channel', metavar='[channel]', type=int,
                           help=Color.s('Kanal zum Scannen (default: {G}alle 2GHz Kanäle{W})'))

        group.add_argument('-5', '--5ghz', action='store_true', dest='five_ghz',
                           help=self._verbose('5GHz Kanäle mit einbeziehen (default: {G}aus{W})'))

        group.add_argument('-mac', '--random-mac', action='store_true', dest='random_mac',
                           help=Color.s('MAC-Adresse der WLAN-Karte randomisieren (default: {G}aus{W})'))

        group.add_argument('-p', '--pillage', action='store', nargs='?', const=10, dest='scan_time', metavar='scan_time', type=int,
                           help=Color.s('{G}Pillage{W}: Greift alle Ziele nach {C}scan_time{W} Sekunden an'))

        group.add_argument('--kill', action='store_true', dest='kill_conflicting_processes',
                           help=Color.s('Prozesse beenden, die mit Airmon/Airodump in Konflikt stehen (default: {G}aus{W})'))

        group.add_argument('-b', '--bssid', action='store', dest='target_bssid', metavar='[bssid]', type=str,
                           help=self._verbose('BSSID des Access Points (z.B. {GR}AA:BB:CC:DD:EE:FF{W})'))

        group.add_argument('-e', '--essid', action='store', dest='target_essid', metavar='[essid]', type=str,
                           help=self._verbose('ESSID des Access Points (z.B. {GR}NETGEAR07{W})'))

        group.add_argument('-E', '--ignore-essid', action='store', dest='ignore_essid', metavar='[text]', type=str, default=None,
                           help=self._verbose('Ziele mit ESSIDs, die den Text enthalten, ignorieren'))

        group.add_argument('--clients-only', action='store_true', dest='clients_only',
                           help=Color.s('Nur Ziele mit verbundenen Clients anzeigen (default: {G}aus{W})'))

        group.add_argument('--showb', action='store_true', dest='show_bssids',
                           help=self._verbose('BSSIDs der Ziele während des Scans anzeigen'))

        group.add_argument('--nodeauths', '--no-deauths', '-nd', action='store_true', dest='no_deauth',
                           help=Color.s('Passivmodus: Keine Deauthentifizierungen senden (default: {G}aus{W})'))

        group.add_argument('--num-deauths', action='store', type=int, dest='num_deauths', metavar='[num]', default=self.config.num_deauths,
                           help=self._verbose('Anzahl Deauth-Pakete senden (Standard: {G}%d{W})' % self.config.num_deauths))

    def _add_eviltwin_args(self, group):
        # Platzhalter für Evil Twin Argumente
        pass

    def _add_wep_args(self, group):
        group.add_argument('--wep', action='store_true', dest='wep_filter', help=Color.s('Nur WEP-verschlüsselte Netzwerke anzeigen'))
        group.add_argument('--require-fakeauth', action='store_true', dest='require_fakeauth',
                           help=Color.s('Angriffe fehlschlagen lassen, wenn Fake-Auth fehlschlägt'))

        group.add_argument('--keep-ivs', action='store_true', dest='wep_keep_ivs',
                           help=Color.s('IVS-Dateien behalten und wiederverwenden'))

        group.add_argument('--pps', action='store', dest='wep_pps', metavar='[pps]', type=int,
                           help=self._verbose('Pakete pro Sekunde für Replay (Standard: %d)' % self.config.wep_pps))

        group.add_argument('--wept', action='store', dest='wep_timeout', metavar='[Sekunden]', type=int,
                           help=self._verbose('Warten bevor Angriff fehlschlägt (Standard: %d Sek.)' % self.config.wep_timeout))

        group.add_argument('--wepca', action='store', dest='wep_crack_at_ivs', metavar='[ivs]', type=int,
                           help=self._verbose('Ab wie vielen IVs starten (Standard: %d)' % self.config.wep_crack_at_ivs))

        group.add_argument('--weprs', action='store', dest='wep_restart_stale_ivs', metavar='[Sekunden]', type=int,
                           help=self._verbose('Aireplay neu starten wenn keine neuen IVs (Standard: %d Sek.)' % self.config.wep_restart_stale_ivs))

        group.add_argument('--weprc', action='store', dest='wep_restart_aircrack', metavar='[Sekunden]', type=int,
                           help=self._verbose('Aircrack nach dieser Zeit neu starten (Standard: %d Sek.)' % self.config.wep_restart_aircrack))

        group.add_argument('--arpreplay', action='store_true', dest='wep_attack_replay',
                           help=self._verbose('ARP Replay WEP Angriff verwenden (Standard: an)'))

        group.add_argument('--fragment', action='store_true', dest='wep_attack_fragment',
                           help=self._verbose('Fragmentation WEP Angriff verwenden (Standard: an)'))

        group.add_argument('--chopchop', action='store_true', dest='wep_attack_chopchop',
                           help=self._verbose('Chop-Chop WEP Angriff verwenden (Standard: an)'))

        group.add_argument('--caffelatte', action='store_true', dest='wep_attack_caffe',
                           help=self._verbose('Caffe-Latte WEP Angriff verwenden (Standard: an)'))

        group.add_argument('--p0841', action='store_true', dest='wep_attack_p0841',
                           help=self._verbose('p0841 WEP Angriff verwenden (Standard: an)'))

        group.add_argument('--hirte', action='store_true', dest='wep_attack_hirte',
                           help=self._verbose('Hirte WEP Angriff verwenden (Standard: an)'))

    def _add_wpa_args(self, group):
        group.add_argument('--wpa', action='store_true', dest='wpa_filter',
                           help=Color.s('Nur WPA-verschlüsselte Netzwerke anzeigen (inkl. WPS)'))

        group.add_argument('--hs-dir', action='store', dest='wpa_handshake_dir', metavar='[Verzeichnis]', type=str,
                           help=self._verbose('Verzeichnis für Handshake-Dateien (Standard: %s)' % self.config.wpa_handshake_dir))

        group.add_argument('--new-hs', action='store_true', dest='ignore_old_handshakes',
                           help=Color.s('Nur neue Handshakes erfassen, alte ignorieren'))

        group.add_argument('--dict', action='store', dest='wordlist', metavar='[Datei]', type=str,
                           help=Color.s('Passwort-Wortliste zum Knacken (Standard: %s)' % self.config.wordlist))

        group.add_argument('--wpadt', action='store', dest='wpa_deauth_timeout', metavar='[Sekunden]', type=int,
                           help=self._verbose('Pause zwischen Deauth-Paketen (Standard: %d Sek.)' % self.config.wpa_deauth_timeout))

        group.add_argument('--wpat', action='store', dest='wpa_attack_timeout', metavar='[Sekunden]', type=int,
                           help=self._verbose('Zeit bis WPA Angriff fehlschlägt (Standard: %d Sek.)' % self.config.wpa_attack_timeout))

    def _add_wps_args(self, group):
        group.add_argument('--wps', action='store_true', dest='wps_filter', help=Color.s('Nur WPS-fähige Netzwerke anzeigen'))
        group.add_argument('--no-wps', action='store_true', dest='no_wps',
                           help=self._verbose('Nie WPS PIN & Pixie-Dust Angriffe verwenden'))

        group.add_argument('--wps-only', action='store_true', dest='wps_only',
                           help=Color.s('Nur WPS PIN & Pixie-Dust Angriffe nutzen'))

        group.add_argument('--pixie', action='store_true', dest='wps_pixie',
                           help=self._verbose('Nur WPS Pixie-Dust Angriff (kein PIN Angriff)'))

        group.add_argument('--no-pixie', action='store_true', dest='wps_no_pixie',
                           help=self._verbose('Nie WPS Pixie-Dust Angriff verwenden'))

        group.add_argument('--bully', action='store_true', dest='use_bully',
                           help=Color.s('Bully Programm für WPS PIN & Pixie-Dust Angriffe verwenden'))

        group.add_argument('--ignore-locks', action='store_true', dest='wps_ignore_lock',
                           help=Color.s('WPS PIN Angriff nicht stoppen, wenn AP gesperrt'))

        group.add_argument('--wps-time', action='store', dest='wps_pixie_timeout', metavar='[Sekunden]', type=int,
                           help=self._verbose('Maximale Wartezeit PixieDust Angriff (Standard: %d Sek.)' % self.config.wps_pixie_timeout))

        group.add_argument('--wps-fails', action='store', dest='wps_fail_threshold', metavar='[Anzahl]', type=int,
                           help=self._verbose('Maximale WPSFail/NoAssoc Fehler vor Abbruch (Standard: %d)' % self.config.wps_fail_threshold))

        group.add_argument('--wps-timeouts', action='store', dest='wps_timeout_threshold', metavar='[Anzahl]', type=int,
                           help=self._verbose('Maximale Timeouts vor Abbruch (Standard: %d)' % self.config.wps_timeout_threshold))

    def _add_pmkid_args(self, group):
        group.add_argument('--pmkid', action='store_true', dest='use_pmkid_only',
                           help=Color.s('Nur PMKID Captures verwenden, andere Angriffe vermeiden'))

        group.add_argument('--pmkid-timeout', action='store', dest='pmkid_timeout', metavar='[Sekunden]', type=int,
                           help=Color.s('Wartezeit auf PMKID Capture (Standard: %d Sekunden)' % self.config.pmkid_timeout))

    def _add_dns_args(self, group):
        group.add_argument('--dns-recon', action='store_true', dest='use_dns_recon',
                           help=self._verbose('DNS Recon Scans aktivieren (Subdomain-Bruteforce, Zone Transfer, etc.)'))
        group.add_argument('--dns-wordlist', action='store', dest='dns_wordlist', metavar='[Datei]', type=str,
                           help=self._verbose('Wortliste für DNS Bruteforce (Standard: interne Liste)'))
        group.add_argument('--dns-zone-transfer', action='store_true', dest='dns_zone_transfer',
                           help=self._verbose('DNS Zone Transfer (AXFR) versuchen'))

    def _add_command_args(self, group):
        group.add_argument('--cracked', action='store_true', dest='cracked',
                           help=Color.s('Zeigt bereits geknackte Access Points'))
        group.add_argument('--check', action='store', nargs='?', const='<all>', dest='check_handshake',
                           metavar='Datei', help=Color.s('Prüft .cap Dateien auf WPA Handshakes'))
        group.add_argument('--crack', action='store_true', dest='crack_handshake',
                           help=Color.s('Zeigt Befehle zum Knacken eines Handshakes'))

if __name__ == '__main__':
    from .config import Configuration
    Configuration.initialize(False)
    a = Arguments(Configuration)
    args = a.args
    for key, value in sorted(args.__dict__.items()):
        Color.pl('{C}%s: {G}%s{W}' % (key.ljust(21), value))
