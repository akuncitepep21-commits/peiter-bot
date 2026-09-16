#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STARTED TRACKER — Simpen semua user yang pernah /start
"""

import json, threading, time
from pathlib import Path
from datetime import datetime, timezone, timedelta

TZ_WIB = timezone(timedelta(hours=7))

_LOCK = threading.Lock()


class StartedTracker:
    def __init__(self, path):
        self.path = Path(path)
        self.lock = threading.Lock()
        self.data = self._load()

    def _load(self):
        if not self.path.exists():
            return {"users": {}, "total": 0}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {"users": {}, "total": 0}

    def _save(self):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(self.data, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
        except Exception:
            pass

    def add(self, cid, username="User", first_name="", last_name="", username_tg=""):
        """Tambah user ke database. Kalau udah ada, update info."""
        cid = str(cid)
        with self.lock:
            if cid not in self.data["users"]:
                self.data["users"][cid] = {
                    "cid": cid,
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name,
                    "username_tg": username_tg,
                    "first_start": time.time(),
                    "last_start": time.time(),
                    "start_count": 1,
                    "blocked": False,
                }
                self.data["total"] = len(self.data["users"])
            else:
                u = self.data["users"][cid]
                u["last_start"] = time.time()
                u["start_count"] = u.get("start_count", 0) + 1
                if username_tg:
                    u["username_tg"] = username_tg
                if first_name:
                    u["first_name"] = first_name
            self._save()
            return self.data["users"][cid]

    def get_all(self):
        """Return semua user yang pernah start."""
        with self.lock:
            return list(self.data["users"].values())

    def get_all_cids(self):
        """Return list of Chat ID."""
        with self.lock:
            return list(self.data["users"].keys())

    def count(self):
        with self.lock:
            return len(self.data["users"])

    def mark_blocked(self, cid):
        """Tandai user yang udah block bot."""
        cid = str(cid)
        with self.lock:
            u = self.data["users"].get(cid)
            if u:
                u["blocked"] = True
                self._save()

    def remove(self, cid):
        """Hapus user dari database."""
        cid = str(cid)
        with self.lock:
            if cid in self.data["users"]:
                del self.data["users"][cid]
                self.data["total"] = len(self.data["users"])
                self._save()
                return True
        return False

    def search(self, keyword):
        """Cari user by username/nama."""
        keyword = keyword.lower()
        with self.lock:
            return [
                u for u in self.data["users"].values()
                if keyword in u.get("username_tg", "").lower()
                or keyword in u.get("first_name", "").lower()
                or keyword in u.get("username", "").lower()
                or keyword in u.get("cid", "")
            ]

    def stats(self):
        """Statistik lengkap."""
        with self.lock:
            users = list(self.data["users"].values())
            total = len(users)
            blocked = sum(1 for u in users if u.get("blocked"))
            active = total - blocked
            now = time.time()
            last_24h = sum(1 for u in users if now - u.get("last_start", 0) < 86400)
            last_7d = sum(1 for u in users if now - u.get("last_start", 0) < 604800)
            return {
                "total": total,
                "active": active,
                "blocked": blocked,
                "last_24h": last_24h,
                "last_7d": last_7d,
            }


def broadcast_to_started(tracker, message, tg_send, delay=0.35, skip_blocked=True):
    """
    Kirim pesan ke semua user yang pernah start.
    Return (sukses, gagal, blocked).
    """
    users = tracker.get_all()
    success = 0
    fail = 0
    blocked_new = 0

    for u in users:
        cid = u.get("cid")
        if not cid:
            continue
        if skip_blocked and u.get("blocked"):
            continue

        try:
            ok = tg_send(cid, message)
            if ok:
                success += 1
            else:
                fail += 1
        except Exception:
            fail += 1
            # Kalau gagal, kemungkinan user block bot
            tracker.mark_blocked(cid)
            blocked_new += 1

        time.sleep(delay)

    return success, fail, blocked_new


if __name__ == "__main__":
    # Test
    import tempfile
    tmp = Path(tempfile.gettempdir()) / "started_test.json"
    t = StartedTracker(tmp)
    t.add("123456", "User1", "Budi", "", "budi_tg")
    t.add("789012", "User2", "Ani", "", "ani_tg")
    print("Total:", t.count())
    print("Stats:", t.stats())
    print("All:", t.get_all_cids())
    tmp.unlink(missing_ok=True)