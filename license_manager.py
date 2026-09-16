#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LICENSE MANAGER — Sistem License untuk PEITER STORE
Mendukung: create, redeem, revoke, delete, extend, reset, search, export CSV
Powered by @PeiterStore
"""

import json
import time
import secrets
import threading
import csv
from pathlib import Path
from datetime import datetime, timezone, timedelta

TZ_WIB = timezone(timedelta(hours=7))

# ══════════════════════════════════════════════════════════════════
#  DURASI LICENSE
# ══════════════════════════════════════════════════════════════════
LICENSE_DURATIONS = {
    "1h": 1, "6h": 6, "12h": 12,
    "24h": 24, "1d": 24,
    "3d": 72, "7d": 168, "14d": 336,
    "30d": 720, "1m": 720,
    "90d": 2160, "1y": 8760,
    "permanent": None, "perm": None, "inf": None,
}

VALID_ROLES = ("owner", "admin", "user", "trial")

_LOCK = threading.Lock()
_LIC_FILE = Path(__file__).resolve().parent / "peiter_store" / "licenses.json"
_LIC_FILE.parent.mkdir(parents=True, exist_ok=True)


# ══════════════════════════════════════════════════════════════════
#  INTERNAL
# ══════════════════════════════════════════════════════════════════
def _load():
    if not _LIC_FILE.exists():
        return {"licenses": {}}
    try:
        data = json.loads(_LIC_FILE.read_text(encoding="utf-8"))
        if "licenses" not in data:
            data["licenses"] = {}
        return data
    except Exception:
        return {"licenses": {}}


def _save(data):
    _LIC_FILE.parent.mkdir(parents=True, exist_ok=True)
    _LIC_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def _gen_key(role="user"):
    prefix = {
        "owner": "OWN",
        "admin": "ADM",
        "user": "USR",
        "trial": "TRL",
    }.get(role, "LIC")
    return f"{prefix}-{secrets.token_hex(4).upper()}-{secrets.token_hex(4).upper()}-{secrets.token_hex(4).upper()}"


# ══════════════════════════════════════════════════════════════════
#  CREATE
# ══════════════════════════════════════════════════════════════════
def create_license(role="user", duration_hours=24, max_uses=1,
                   created_by="system", note=""):
    """
    Bikin license baru.
    role: owner | admin | user | trial
    duration_hours: None = permanent
    max_uses: berapa kali bisa dipakai
    """
    if role not in VALID_ROLES:
        role = "user"

    with _LOCK:
        data = _load()
        key = _gen_key(role)
        while key in data["licenses"]:
            key = _gen_key(role)

        now = time.time()
        expires_at = None if duration_hours is None else now + (duration_hours * 3600)

        entry = {
            "key": key,
            "role": role,
            "created_at": now,
            "created_by": str(created_by),
            "expires_at": expires_at,
            "duration_hours": duration_hours,
            "max_uses": int(max_uses),
            "used_count": 0,
            "used_by": [],
            "enabled": True,
            "note": note,
        }
        data["licenses"][key] = entry
        _save(data)
        return entry


# ══════════════════════════════════════════════════════════════════
#  REDEEM
# ══════════════════════════════════════════════════════════════════
def redeem_license(key, user_id):
    """
    Return: (ok, message, role, expires_at)
    """
    key = str(key).strip().upper()
    with _LOCK:
        data = _load()
        lic = data["licenses"].get(key)

        if not lic:
            return False, "❌ License tidak ditemukan", None, None

        if not lic.get("enabled", True):
            return False, "⛔ License dinonaktifkan", None, None

        if lic.get("expires_at") and time.time() > lic["expires_at"]:
            return False, "⌛ License expired", None, None

        if lic["used_count"] >= lic["max_uses"]:
            return False, "🔴 License sudah habis dipakai", None, None

        uid = str(user_id)

        # Kalau user sudah pernah pakai, tetap valid
        if uid in lic["used_by"]:
            return True, "✅ License kamu masih aktif", lic["role"], lic["expires_at"]

        lic["used_by"].append(uid)
        lic["used_count"] += 1
        _save(data)
        return True, "✅ License berhasil diaktifkan!", lic["role"], lic["expires_at"]


# ══════════════════════════════════════════════════════════════════
#  REVOKE / DELETE
# ══════════════════════════════════════════════════════════════════
def revoke_license(key):
    key = str(key).strip().upper()
    with _LOCK:
        data = _load()
        if key not in data["licenses"]:
            return False
        data["licenses"][key]["enabled"] = False
        _save(data)
        return True


def delete_license(key):
    key = str(key).strip().upper()
    with _LOCK:
        data = _load()
        if key not in data["licenses"]:
            return False
        del data["licenses"][key]
        _save(data)
        return True


# ══════════════════════════════════════════════════════════════════
#  READ
# ══════════════════════════════════════════════════════════════════
def list_licenses():
    with _LOCK:
        data = _load()
        return list(data["licenses"].values())


def get_license(key):
    key = str(key).strip().upper()
    with _LOCK:
        data = _load()
        return data["licenses"].get(key)


def find_user_license(user_id):
    uid = str(user_id)
    for lic in list_licenses():
        if uid in lic.get("used_by", []):
            return lic
    return None


def find_user_licenses(user_id):
    """Return semua license yang dipakai user."""
    uid = str(user_id)
    return [lic for lic in list_licenses() if uid in lic.get("used_by", [])]


# ══════════════════════════════════════════════════════════════════
#  STATS
# ══════════════════════════════════════════════════════════════════
def stats():
    items = list_licenses()
    now = time.time()
    total = len(items)
    active = expired = disabled = exhausted = 0

    for lic in items:
        if not lic.get("enabled", True):
            disabled += 1
            continue
        if lic.get("expires_at") and now > lic["expires_at"]:
            expired += 1
            continue
        if lic["used_count"] >= lic["max_uses"]:
            exhausted += 1
            continue
        active += 1

    return {
        "total": total,
        "active": active,
        "expired": expired,
        "disabled": disabled,
        "exhausted": exhausted,
    }


# ══════════════════════════════════════════════════════════════════
#  UPDATE / EXTEND / RESET
# ══════════════════════════════════════════════════════════════════
def update_license(key, **kwargs):
    key = str(key).strip().upper()
    with _LOCK:
        data = _load()
        lic = data["licenses"].get(key)
        if not lic:
            return False
        for k in ("role", "max_uses", "enabled", "note", "expires_at", "duration_hours"):
            if k in kwargs:
                lic[k] = kwargs[k]
        _save(data)
        return True


def extend_license(key, additional_hours):
    key = str(key).strip().upper()
    with _LOCK:
        data = _load()
        lic = data["licenses"].get(key)
        if not lic:
            return False
        if lic["expires_at"] is None:
            return True  # permanent, gak perlu extend
        lic["expires_at"] += additional_hours * 3600
        _save(data)
        return True


def reset_usage(key):
    key = str(key).strip().upper()
    with _LOCK:
        data = _load()
        lic = data["licenses"].get(key)
        if not lic:
            return False
        lic["used_count"] = 0
        lic["used_by"] = []
        _save(data)
        return True


def enable_license(key):
    return update_license(key, enabled=True)


def disable_license(key):
    return update_license(key, enabled=False)


# ══════════════════════════════════════════════════════════════════
#  CLEANUP
# ══════════════════════════════════════════════════════════════════
def cleanup_expired(also_disabled=True):
    """Hapus license yang expired & disabled."""
    with _LOCK:
        data = _load()
        now = time.time()
        removed = []
        for key, lic in list(data["licenses"].items()):
            expired = lic.get("expires_at") and now > lic["expires_at"]
            disabled = not lic.get("enabled", True)
            if expired and (disabled or not also_disabled):
                if disabled:
                    del data["licenses"][key]
                    removed.append(key)
        if removed:
            _save(data)
        return removed


def cleanup_all_expired():
    """Hapus SEMUA license yang expired."""
    with _LOCK:
        data = _load()
        now = time.time()
        removed = []
        for key, lic in list(data["licenses"].items()):
            if lic.get("expires_at") and now > lic["expires_at"]:
                del data["licenses"][key]
                removed.append(key)
        if removed:
            _save(data)
        return removed


# ══════════════════════════════════════════════════════════════════
#  SEARCH
# ══════════════════════════════════════════════════════════════════
def search_licenses(keyword):
    keyword = str(keyword).strip().lower()
    if not keyword:
        return []
    results = []
    for lic in list_licenses():
        if (keyword in lic["key"].lower()
                or keyword in lic.get("role", "").lower()
                or keyword in str(lic.get("created_by", "")).lower()
                or keyword in str(lic.get("note", "")).lower()):
            results.append(lic)
    return results


def list_by_role(role):
    role = str(role).strip().lower()
    return [lic for lic in list_licenses() if lic.get("role") == role]


def list_active():
    now = time.time()
    results = []
    for lic in list_licenses():
        if not lic.get("enabled", True):
            continue
        if lic.get("expires_at") and now > lic["expires_at"]:
            continue
        if lic["used_count"] >= lic["max_uses"]:
            continue
        results.append(lic)
    return results


# ══════════════════════════════════════════════════════════════════
#  FORMAT HELPERS
# ══════════════════════════════════════════════════════════════════
def fmt_expires(lic):
    if lic.get("expires_at") is None:
        return "♾ PERMANEN"
    try:
        return datetime.fromtimestamp(lic["expires_at"], TZ_WIB).strftime("%Y-%m-%d %H:%M WIB")
    except Exception:
        return "?"


def fmt_created(lic):
    try:
        return datetime.fromtimestamp(lic["created_at"], TZ_WIB).strftime("%Y-%m-%d %H:%M WIB")
    except Exception:
        return "?"


def lic_status_emoji(lic):
    now = time.time()
    if not lic.get("enabled", True):
        return "⛔"
    if lic.get("expires_at") and now > lic["expires_at"]:
        return "⌛"
    if lic["used_count"] >= lic["max_uses"]:
        return "🔴"
    return "✅"


def format_license_detail(lic):
    if not lic:
        return "❌ License tidak ditemukan"

    exp = fmt_expires(lic)
    created = fmt_created(lic)
    emoji = lic_status_emoji(lic)
    used_by = ", ".join(f"<code>{u}</code>" for u in lic["used_by"][:10]) or "—"

    return (
        f"{emoji} <b>LICENSE DETAIL</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🔑 Key      : <code>{lic['key']}</code>\n"
        f"🎭 Role     : <b>{lic['role'].upper()}</b>\n"
        f"📅 Dibuat   : {created}\n"
        f"⌛ Expired  : <b>{exp}</b>\n"
        f"👥 Max Uses : <b>{lic['max_uses']}</b>\n"
        f"📊 Terpakai : <b>{lic['used_count']}/{lic['max_uses']}</b>\n"
        f"👤 Digunakan: {used_by}\n"
        f"⚡ Status   : <b>{'ON' if lic.get('enabled', True) else 'OFF'}</b>\n"
        f"📝 Catatan  : {lic.get('note', '-')}\n"
        f"🏷 Dibuat   : <code>{lic.get('created_by', '?')}</code>"
    )


def format_license_list(licenses, max_show=30):
    if not licenses:
        return "📭 Belum ada license"

    total = len(licenses)
    txt = f"🔑 <b>LICENSE LIST ({total})</b>\n━━━━━━━━━━━━━━━\n"

    for lic in licenses[:max_show]:
        emoji = lic_status_emoji(lic)
        exp = "♾" if lic.get("expires_at") is None else fmt_expires(lic)[:10]
        txt += (
            f"{emoji} <code>{lic['key']}</code>\n"
            f"   {lic['role'].upper()} • {lic['used_count']}/{lic['max_uses']} • {exp}\n"
        )

    if total > max_show:
        txt += f"\n<i>... +{total - max_show} lainnya</i>"

    return txt


def format_license_stats():
    st = stats()
    return (
        f"📊 <b>LICENSE STATS</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📦 Total    : <b>{st['total']}</b>\n"
        f"✅ Aktif    : <b>{st['active']}</b>\n"
        f"⌛ Expired  : <b>{st['expired']}</b>\n"
        f"⛔ Disabled : <b>{st['disabled']}</b>\n"
        f"🔴 Habis    : <b>{st['exhausted']}</b>"
    )


# ══════════════════════════════════════════════════════════════════
#  EXPORT
# ══════════════════════════════════════════════════════════════════
def export_licenses_csv(path):
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([
                "Key", "Role", "Created", "Expires",
                "Duration Hours", "Max Uses", "Used Count",
                "Enabled", "Created By", "Note",
            ])
            for lic in list_licenses():
                w.writerow([
                    lic["key"],
                    lic["role"],
                    fmt_created(lic),
                    fmt_expires(lic),
                    lic.get("duration_hours", "-"),
                    lic["max_uses"],
                    lic["used_count"],
                    lic.get("enabled", True),
                    lic.get("created_by", ""),
                    lic.get("note", ""),
                ])
        return True
    except Exception:
        return False


def export_licenses_json(path):
    try:
        data = {"licenses": list_licenses(), "stats": stats(),
                "exported_at": datetime.now(TZ_WIB).isoformat()}
        Path(path).write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        return True
    except Exception:
        return False


# ══════════════════════════════════════════════════════════════════
#  BACKUP / RESTORE
# ══════════════════════════════════════════════════════════════════
def backup_to(path):
    try:
        with _LOCK:
            data = _load()
        Path(path).write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        return True
    except Exception:
        return False


def restore_from(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if "licenses" not in data:
            return False
        with _LOCK:
            _save(data)
        return True
    except Exception:
        return False


# ══════════════════════════════════════════════════════════════════
#  INFO
# ══════════════════════════════════════════════════════════════════
def get_file_path():
    return str(_LIC_FILE)


def get_summary():
    st = stats()
    return (
        f"License Manager\n"
        f"  File    : {_LIC_FILE}\n"
        f"  Total   : {st['total']}\n"
        f"  Active  : {st['active']}\n"
        f"  Expired : {st['expired']}\n"
        f"  Disabled: {st['disabled']}\n"
        f"  Exhausted: {st['exhausted']}"
    )


# ══════════════════════════════════════════════════════════════════
#  TEST
# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("  LICENSE MANAGER — TEST")
    print("=" * 60)
    print(f"  File: {_LIC_FILE}")
    print()
    print("[1] Bikin license test...")
    r = create_license(role="user", duration_hours=24, max_uses=1,
                       created_by="test", note="Test license")
    print(f"    Key: {r['key']}")
    print(f"    Role: {r['role']}")
    print(f"    Expires: {fmt_expires(r)}")
    print()
    print("[2] Redeem...")
    ok, msg, role, exp = redeem_license(r["key"], "123456789")
    print(f"    OK: {ok}")
    print(f"    Msg: {msg}")
    print()
    print("[3] Stats...")
    st = stats()
    print(f"    {st}")
    print()
    print("[4] List...")
    for lic in list_licenses()[:3]:
        print(f"    {lic_status_emoji(lic)} {lic['key']} — {lic['role']}")
    print()
    print("[5] Revoke...")
    print(f"    {revoke_license(r['key'])}")
    print()
    print("[6] Delete...")
    print(f"    {delete_license(r['key'])}")
    print()
    print("=" * 60)
    print("  TEST SELESAI")
    print("=" * 60)