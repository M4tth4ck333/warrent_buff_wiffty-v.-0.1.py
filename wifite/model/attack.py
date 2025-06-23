#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Optional, Callable

class TargetNotFoundError(Exception):
    pass

class Attack:
    target_wait: int = 60

    def __init__(self, target):
        self.target = target

    def run(self):
        raise NotImplementedError('run() must be implemented by subclass')

    def wait_for_target(self, airodump, callback: Optional[Callable[[int], None]] = None):
        start_time = time.time()
        while True:
            targets = airodump.get_targets(apply_filter=False)
            if targets:
                for t in targets:
                    if t.bssid == self.target.bssid:
                        return t
            elapsed = int(time.time() - start_time)
            if elapsed > self.target_wait:
                raise TargetNotFoundError(f'Target did not appear after {self.target_wait} seconds')
            if callback:
                callback(elapsed)
            time.sleep(1)
