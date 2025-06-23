#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ..model.attack import Attack
from ..util.color import Color
import subprocess
import os
import time

class AttackBluetooth(Attack):
    """
    Bluetooth-Sniffing-Angriff mit btmon, Ubertooth oder BlueZ.
    """

    def __init__(self, target, method="btmon", output_file=None):
        super().__init__(target)
        self.method = method.lower()
        self.output_file = output_file or f"{self.method}_{int(time.time())}.log"
        self.process = None

    def run(self):
        """
        Startet den Mitschnitt mit dem gewählten Tool.
        """
        if self.method == "btmon":
            return self._run_btmon()
        elif self.method == "ubertooth":
            return self._run_ubertooth()
        elif self.method == "bluez":
            return self._run_bluez()
        else:
            Color.pl(f"{R}! Unbekannte Bluetooth-Methode: {self.method}{W}")
            return False

    def _run_btmon(self):
        if not self._tool_exists("btmon"):
            Color.pl("{!} btmon ist nicht installiert!")
            return False
        try:
            self.process = subprocess.Popen(
                ["btmon", "-w", self.output_file],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            Color.pl(f"{G}+ Starte btmon Mitschnitt: {self.output_file}{W}")
            # Beispiel: 10 Sekunden mitschneiden
            time.sleep(10)
            self.process.terminate()
            self.process.wait()
            Color.pl(f"{G}+ Mitschnitt beendet: {self.output_file}{W}")
            return True
        except Exception as e:
            Color.pl(f"{R}! Fehler bei btmon: {e}{W}")
            return False

    def _run_ubertooth(self):
        if not self._tool_exists("ubertooth-btle"):
            Color.pl("{!} ubertooth-btle ist nicht installiert!")
            return False
        try:
            self.process = subprocess.Popen(
                ["ubertooth-btle", "-f", self.output_file],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            Color.pl(f"{G}+ Starte Ubertooth Mitschnitt: {self.output_file}{W}")
            time.sleep(10)
            self.process.terminate()
            self.process.wait()
            Color.pl(f"{G}+ Mitschnitt beendet: {self.output_file}{W}")
            return True
        except Exception as e:
            Color.pl(f"{R}! Fehler bei Ubertooth: {e}{W}")
            return False

    def _run_bluez(self):
        if not self._tool_exists("hcitool"):
            Color.pl("{!} hcitool ist nicht installiert!")
            return False
        try:
            Color.pl(f"{G}+ Starte BlueZ Scan...{W}")
            subprocess.run(["hcitool", "scan"], check=True)
            Color.pl(f"{G}+ BlueZ Scan abgeschlossen.{W}")
            return True
        except Exception as e:
            Color.pl(f"{R}! Fehler bei BlueZ: {e}{W}")
            return False

    @staticmethod
    def _tool_exists(tool):
        from shutil import which
        return which(tool) is not None
