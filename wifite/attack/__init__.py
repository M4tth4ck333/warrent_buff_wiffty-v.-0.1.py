# attack/__init__.py

# Evil Twin Attack importieren
from .evil_twin.manager import EvilTwinAttack

# Andere Attack-Klassen, z.B. WPS, WPA, WEP, PMKID,
# die du später ergänzen kannst:
# from .wps import WpsAttack
# from .wpa import WpaAttack
# from .wep import WepAttack
# from .pmkid import PmkidAttack

__all__ = [
    "EvilTwinAttack",
    # "WpsAttack",
    # "WpaAttack",
    # "WepAttack",
    # "PmkidAttack",
]
