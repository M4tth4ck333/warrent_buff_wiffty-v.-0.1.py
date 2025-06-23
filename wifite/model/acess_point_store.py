# access_point_store.py

from typing import Dict, Set, Tuple, Any

class AccessPointStore(dict):
    """
    Dict-basierter Speicher für bekannte Access Points.
    Jeder Schlüssel ist ein Tupel (ESSID, BSSID).
    Der Wert ist ein Dict mit:
      - passwords: Set[str]
      - pmks: Dict[str, str]
      - meta: Dict[str, Any]
    """

    def add_ap(self, essid: str, bssid: str) -> None:
        """Fügt einen neuen AP-Eintrag hinzu, falls noch nicht vorhanden."""
        key = (essid, bssid)
        if key not in self:
            self[key] = {
                "passwords": set(),
                "pmks": {},
                "meta": {}
            }

    def add_password(self, essid: str, bssid: str, password: str) -> None:
        """Fügt ein Passwort zum AP hinzu."""
        self.add_ap(essid, bssid)
        self[(essid, bssid)]["passwords"].add(password)

    def add_pmk(self, essid: str, bssid: str, password: str, pmk: str) -> None:
        """Fügt eine PMK für ein Passwort zum AP hinzu."""
        self.add_ap(essid, bssid)
        self[(essid, bssid)]["pmks"][password] = pmk

    def get_pmks(self, essid: str, bssid: str) -> Dict[str, str]:
        """Gibt alle PMKs für den AP zurück."""
        return self.get((essid, bssid), {}).get("pmks", {})

    def get_passwords(self, essid: str, bssid: str) -> Set[str]:
        """Gibt alle gespeicherten Passwörter für den AP zurück."""
        return self.get((essid, bssid), {}).get("passwords", set())

    def set_meta(self, essid: str, bssid: str, key: str, value: Any) -> None:
        """Setzt einen Metadaten-Eintrag für den AP."""
        self.add_ap(essid, bssid)
        self[(essid, bssid)]["meta"][key] = value

    def get_meta(self, essid: str, bssid: str) -> Dict[str, Any]:
        """Gibt alle Metadaten des AP zurück."""
        return self.get((essid, bssid), {}).get("meta", {})

    def export_hashcat(self, essid: str, bssid: str) -> str:
        """
        Exportiert alle PMKs im Hashcat-ähnlichen Format (z.B. als einfache Textzeilen).
        Format: ESSID:BSSID:password:pmk
        """
        pmks = self.get_pmks(essid, bssid)
        lines = [f"{essid}:{bssid}:{pwd}:{pmk}" for pwd, pmk in pmks.items()]
        return "\n".join(lines)

# ---------------------------
# Optionaler Wrapper für Visualyzer
# (Platzhalter, auskommentiert)
# ---------------------------

# import visualyzer
#
# class VisualyzerWrapper:
#     """
#     Wrapper-Klasse zur Integration von Visualyzer mit AccessPointStore.
#     """
#     def __init__(self, ap_store: AccessPointStore):
#         self.ap_store = ap_store
#         self.viz = visualyzer.Visualyzer()
#
#     def update_visualization(self) -> None:
#         """
#         Aktualisiert die Visualisierung basierend auf den AP-Daten.
#         """
#         for (essid, bssid), data in self.ap_store.items():
#             self.viz.add_access_point(essid, bssid, data)
#         self.viz.render()
#
#     def clear(self) -> None:
#         self.viz.clear()
