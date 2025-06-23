import sqlite3
import os
from datetime import datetime

class DBConfiguration:
    def __init__(self, db_path="config.sqlite"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self._init_schema()

    def _init_schema(self):
        """Initialisiert das Datenbankschema, wenn nicht vorhanden."""
        c = self.conn.cursor()
        c.executescript("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT
            );

            CREATE TABLE IF NOT EXISTS tools (
                name TEXT PRIMARY KEY,
                path TEXT,
                version TEXT,
                enabled INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS wordlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                path TEXT,
                active INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS interfaces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                mac TEXT,
                monitor_mode INTEGER,
                active INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS attacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                status TEXT,
                target_bssid TEXT,
                essid TEXT,
                created_at DATETIME,
                log TEXT
            );
        """)
        self.conn.commit()

    # ────────────────────────────────────────────────
    # CONFIG
    def set_config(self, key, value):
        self.conn.execute("REPLACE INTO config (key, value) VALUES (?, ?)", (key, str(value)))
        self.conn.commit()

    def get_config(self, key, default=None):
        cur = self.conn.execute("SELECT value FROM config WHERE key = ?", (key,))
        row = cur.fetchone()
        return row[0] if row else default

    # ────────────────────────────────────────────────
    # TOOLS
    def add_tool(self, name, path, version="unknown"):
        self.conn.execute("REPLACE INTO tools (name, path, version) VALUES (?, ?, ?)", (name, path, version))
        self.conn.commit()

    def get_tool_path(self, name):
        cur = self.conn.execute("SELECT path FROM tools WHERE name = ?", (name,))
        row = cur.fetchone()
        return row[0] if row else None

    def tool_exists(self, name):
        return self.get_tool_path(name) is not None

    # ────────────────────────────────────────────────
    # WORDLISTS
    def add_wordlist(self, name, path, active=False):
        self.conn.execute("INSERT INTO wordlists (name, path, active) VALUES (?, ?, ?)", (name, path, int(active)))
        self.conn.commit()

    def set_active_wordlist(self, path):
        self.conn.execute("UPDATE wordlists SET active = 0")
        self.conn.execute("UPDATE wordlists SET active = 1 WHERE path = ?", (path,))
        self.conn.commit()

    def get_active_wordlist(self):
        cur = self.conn.execute("SELECT path FROM wordlists WHERE active = 1")
        row = cur.fetchone()
        return row[0] if row else None

    def list_wordlists(self):
        return [(row[0], row[1]) for row in self.conn.execute("SELECT name, path FROM wordlists")]

    # ────────────────────────────────────────────────
    # INTERFACES
    def add_interface(self, name, mac, monitor_mode=False, active=False):
        self.conn.execute("INSERT INTO interfaces (name, mac, monitor_mode, active) VALUES (?, ?, ?, ?)",
                          (name, mac, int(monitor_mode), int(active)))
        self.conn.commit()

    def set_active_interface(self, name):
        self.conn.execute("UPDATE interfaces SET active = 0")
        self.conn.execute("UPDATE interfaces SET active = 1 WHERE name = ?", (name,))
        self.conn.commit()

    def get_active_interface(self):
        cur = self.conn.execute("SELECT name FROM interfaces WHERE active = 1")
        row = cur.fetchone()
        return row[0] if row else None

    # ────────────────────────────────────────────────
    # ATTACKS
    def log_attack(self, attack_type, target_bssid, essid, status="pending", log=None):
        self.conn.execute("""
            INSERT INTO attacks (type, status, target_bssid, essid, created_at, log)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (attack_type, status, target_bssid, essid, datetime.now(), log))
        self.conn.commit()

    def update_attack_status(self, attack_id, status):
        self.conn.execute("UPDATE attacks SET status = ? WHERE id = ?", (status, attack_id))
        self.conn.commit()

    def get_recent_attacks(self, limit=10):
        cur = self.conn.execute("SELECT * FROM attacks ORDER BY created_at DESC LIMIT ?", (limit,))
        return cur.fetchall()

    def close(self):
        self.conn.close()
