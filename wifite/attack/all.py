#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .wep import AttackWEP
from .wpa import AttackWPA
from .wpa3 import AttackWPA3
from .wps import AttackWPS
from .pmkid import AttackPMKID
from .hci import AttackHCI
from ..config import Configuration
from ..util.color import Color
import logging

class AttackAll:
    SUPPORTED_ATTACKS = [
        ('WEP', AttackWEP),
        ('WPA3', AttackWPA3),
        ('WPA', AttackWPA),
        ('WPS', AttackWPS),
        ('PMKID', AttackPMKID),
        ('HCI', AttackHCI),
        # Weitere Angriffsklassen können hier ergänzt werden
    ]

    @classmethod
    def attack_multiple(cls, targets):
        """
        Führt Angriffe auf alle angegebenen Ziele aus.
        Gibt die Anzahl der angegriffenen Ziele zurück.
        """
        if any(getattr(t, 'wps', False) for t in targets) and not AttackWPS.can_attack_wps():
            Color.pl('{!} {O}Hinweis: WPS-Angriffe sind nicht möglich (reaver/bully fehlen)')

        attacked_targets = 0
        targets_remaining = len(targets)
        for index, target in enumerate(targets, start=1):
            attacked_targets += 1
            targets_remaining -= 1

            bssid = getattr(target, 'bssid', 'unbekannt')
            essid = getattr(target, 'essid', '{O}ESSID unbekannt{W}') if getattr(target, 'essid_known', False) else '{O}ESSID unbekannt{W}'

            Color.pl('\n{+} ({G}%d{W}/{G}%d{W}) Starte Angriff auf {C}%s{W} ({C}%s{W})' % (index, len(targets), bssid, essid))

            should_continue = cls.attack_single(target, targets_remaining)
            if not should_continue:
                break

        return attacked_targets

    @classmethod
    def attack_single(cls, target, targets_remaining):
        """
        Führt alle passenden Angriffe auf ein Ziel aus.
        Gibt True zurück, wenn mit weiteren Zielen fortgefahren werden soll.
        """
        attacks = cls._resolve_attacks(target)

        if not attacks:
            Color.pl('{!} {R}Fehler: {O}Kein passender Angriff verfügbar')
            return True

        while attacks:
            attack = attacks.pop(0)
            try:
                result = attack.run()
                if result:
                    break  # Erfolg: keine weiteren Angriffe auf dieses Ziel
            except KeyboardInterrupt:
                Color.pl('\n{!} {O}Unterbrochen{W}\n')
                answer = cls.user_wants_to_continue(targets_remaining, len(attacks))
                if answer is True:
                    continue
                elif answer is None:
                    return True
                else:
                    return False
            except Exception as e:
                logging.exception(f"Fehler bei Angriff auf {getattr(target, 'bssid', 'unbekannt')}: {e}")
                Color.pexception(e)
                continue

        if getattr(attack, 'success', False):
            try:
                attack.crack_result.save()
            except Exception as e:
                logging.error(f"Fehler beim Speichern des Angriffsresultats: {e}")

        return True

    @classmethod
    def _resolve_attacks(cls, target):
        """
        Ermittelt und instanziiert alle passenden Angriffsobjekte für das Ziel.
        """
        attacks = []

        encryption = getattr(target, 'encryption', '').upper()
        wps_enabled = getattr(target, 'wps', False)
        hci_enabled = getattr(target, 'hci', False)

        # EvilTwin als Beispiel für weitere Angriffsarten
        if getattr(Configuration, 'use_eviltwin', False):
            # TODO: EvilTwin-Angriff implementieren
            pass

        # WPA3
        if 'WPA3' in encryption:
            attacks.append(AttackWPA3(target))

        # WPA2/WPA
        elif 'WPA' in encryption:
            # WPS (sofern nicht nur PMKID gewünscht)
            if not Configuration.use_pmkid_only and wps_enabled and AttackWPS.can_attack_wps():
                if Configuration.wps_pixie:
                    attacks.append(AttackWPS(target, pixie_dust=True))
                if Configuration.wps_pin:
                    attacks.append(AttackWPS(target, pixie_dust=False))
            if not Configuration.wps_only:
                attacks.append(AttackPMKID(target))
                if not Configuration.use_pmkid_only:
                    attacks.append(AttackWPA(target))

        # WEP
        elif 'WEP' in encryption:
            attacks.append(AttackWEP(target))

        # Bluetooth (HCI)
        if hci_enabled:
            attacks.append(AttackHCI(target))

        return attacks

    @classmethod
    def user_wants_to_continue(cls, targets_remaining, attacks_remaining=0):
        """
        Fragt den Nutzer, ob weitere Angriffe/Targets bearbeitet werden sollen.
        """
        if attacks_remaining == 0 and targets_remaining == 0:
            return  # Keine Ziele oder Angriffe mehr

        prompt_list = []
        if attacks_remaining > 0:
            prompt_list.append(Color.s('{C}%d{W} Angriff(e)' % attacks_remaining))
        if targets_remaining > 0:
            prompt_list.append(Color.s('{C}%d{W} Ziel(e)' % targets_remaining))
        prompt = ' und '.join(prompt_list) + ' verbleiben'
        Color.pl('{+} %s' % prompt)

        prompt = '{+} Möchtest du'
        options = '('

        if attacks_remaining > 0:
            prompt += ' {G}weiter{W} angreifen,'
            options += '{G}w{W}{D}, {W}'

        if targets_remaining > 0:
            prompt += ' {O}zum nächsten Ziel springen,'
            options += '{O}s{W}{D}, {W}'

        options += '{R}e{W})'
        prompt += ' oder {R}beenden{W} %s? {C}' % options

        from ..util.input import raw_input
        answer = raw_input(Color.s(prompt)).lower()

        if answer.startswith('s'):
            return None  # Skip
        elif answer.startswith('e'):
            return False  # Exit
        else:
            return True  # Continue
