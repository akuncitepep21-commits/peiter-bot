#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║  PEITER STORE — ULTIMATE MERGED                                  ║
║  Powered by @PeiterStore                                         ║
║                                                                  ║
║  Semua fitur berfungsi digabung:                                 ║
║    • Telegram Bot (app.py engine)                                ║
║    • CLI Terminal                                                ║
║    • Pipeline BAN → VALID → FULL INFO                            ║
║    • Split / Filter / Dedup / Merge / Export                     ║
║    • Lookup (Role ID / Nickname)                                 ║
║    • Device ID Generator                                         ║
║    • Donasi QRIS (auto-license)                                  ║
║    • Statistik & Analytics                                       ║
╚══════════════════════════════════════════════════════════════════╝
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

print("[BOOT] PEITER STORE Ultimate starting...")

# ══════════════════════════════════════════════════════════════════
#  DEPENDENCY CHECK
# ══════════════════════════════════════════════════════════════════
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

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except Exception:
    class _D:
        def __getattr__(self, n): return ""
    Fore = Style = _D()

print("[BOOT] Deps OK")

# ══════════════════════════════════════════════════════════════════
#  IMPORT ENGINE DARI app.py (TIDAK DIUBAH)
# ══════════════════════════════════════════════════════════════════
try:
    import app as _engine
    print("[BOOT] Engine app.py loaded")
except Exception as e:
    print(f"[FATAL] Gagal import app.py: {e}")
    sys.exit(1)

# Core engine
GameLogin               = _engine.GameLogin
GameConnection          = _engine.GameConnection
lookup_player_data      = _engine.lookup_player_data
extract_player_data     = _engine.extract_player_data
check_device_ban_silent = _engine.check_device_ban_silent
check_device_ban_strict = _engine.check_device_ban_strict
save_valid_result       = _engine.save_valid_result
_load_device_ids        = _engine._load_device_ids
get_cached_device_ids   = _engine.get_cached_device_ids
SdpStruct               = _engine.SdpStruct
SdpType                 = _engine.SdpType
BAN_REASON_MAP          = _engine.BAN_REASON_MAP
parse_ban_20001         = _engine.parse_ban_20001
HERO_ID_MAP             = _engine.HERO_ID_MAP
map_rank                = _engine.map_rank
map_collector           = _engine.map_collector
fmt_ts                  = _engine.fmt_ts
DEVICE_RE               = _engine.DEVICE_RE
extract_device_ids      = _engine.extract_device_ids
PERF_PROFILES           = _engine.PERF_PROFILES
PROFILE                 = dict(_engine.PROFILE)
AdaptiveRate            = _engine.AdaptiveRate
_ADAPTIVE_RATE          = _engine._ADAPTIVE_RATE
BASE_DIR                = _engine.BASE_DIR
STORE_DIR               = _engine.STORE_DIR
RESULTS_DIR             = _engine.RESULTS_DIR
BAN_DIR                 = _engine.BAN_DIR
SPLIT_DIR               = _engine.SPLIT_DIR
LOGS_DIR                = _engine.LOGS_DIR
RESULTS_FILE            = _engine.RESULTS_FILE
TZ_WIB                  = _engine.TZ_WIB

# Telegram API helpers
tg_api        = _engine.tg_api
tg_send       = _engine.tg_send
tg_send_doc   = _engine.tg_send_doc
tg_edit       = _engine.tg_edit
tg_answer_cb  = _engine.tg_answer_cb
tg_get_file   = _engine.tg_get_file

# State management
load_state       = _engine.load_state
save_blocked     = _engine.save_blocked
save_access      = _engine.save_access
save_limits      = _engine.save_limits
get_role         = _engine.get_role
is_admin         = _engine.is_admin
is_owner         = _engine.is_owner
grant_access     = _engine.grant_access
revoke_access    = _engine.revoke_access
check_limit      = _engine.check_limit
inc_limit        = _engine.inc_limit
set_limit        = _engine.set_limit
reset_limit      = _engine.reset_limit
check_flood      = _engine.check_flood
set_pending      = _engine.set_pending
get_pending      = _engine.get_pending
clear_pending    = _engine.clear_pending
job_start        = _engine.job_start
job_update       = _engine.job_update
job_stop         = _engine.job_stop
job_check        = _engine.job_check
job_get          = _engine.job_get
job_end          = _engine.job_end
stop_job         = _engine.stop_job
rate_wait        = _engine.rate_wait
progress_bar     = _engine.progress_bar
read_valid_lines = _engine.read_valid_lines
parse_valid_line = _engine.parse_valid_line
resolve_user     = _engine.resolve_user
get_alias        = _engine.get_alias
log_activity     = _engine.log_activity
log_forensic     = _engine.log_forensic
now_wib          = _engine.now_wib
today_str        = _engine.today_str
forward_single_to_owner = _engine.forward_single_to_owner
forward_batch_to_owner  = _engine.forward_batch_to_owner

# Menu & KB dari app.py
menu_main      = _engine.menu_main
menu_status    = _engine.menu_status
menu_help      = _engine.menu_help
menu_myid      = _engine.menu_myid
menu_stats     = _engine.menu_stats
kb_main        = _engine.kb_main
kb_tools       = _engine.kb_tools
kb_bulk        = _engine.kb_bulk
kb_other       = _engine.kb_other
kb_bf          = _engine.kb_bf
kb_manage      = _engine.kb_manage
kb_system      = _engine.kb_system
kb_license     = _engine.kb_license
kb_lic_role    = _engine.kb_lic_role
kb_lic_duration= _engine.kb_lic_duration
kb_lic_uses    = _engine.kb_lic_uses
kb_back        = _engine.kb_back
kb_valid       = _engine.kb_valid

# Worker tasks dari app.py
do_gendev        = _engine.do_gendev
do_export_csv    = _engine.do_export_csv
do_export_json   = _engine.do_export_json
do_zip           = _engine.do_zip
do_backup        = _engine.do_backup
do_cleanup       = _engine.do_cleanup
do_show_log      = _engine.do_show_log
do_bulk_valid    = _engine.do_bulk_valid
do_bulk_detail   = _engine.do_bulk_detail
do_bulk_ban      = _engine.do_bulk_ban
do_bulk_lookup   = _engine.do_bulk_lookup
do_pipeline      = _engine.do_pipeline
process_file_and_reply = _engine.process_file_and_reply
handle_document  = _engine.handle_document
handle_callback  = _engine.handle_callback
handle_command   = _engine.handle_command
bot_poll         = _engine.bot_poll

# Config
BOT_TOKEN        = _engine.BOT_TOKEN
CHAT_ID          = _engine.CHAT_ID
OWNER_CHAT_ID    = _engine.OWNER_CHAT_ID
PERFORMANCE_MODE = _engine.PERFORMANCE_MODE

# Import optional modules
try:
    import license_manager as lics
    print("[BOOT] License manager OK")
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

# QRIS config
if dn:
    QRIS_CFG = dn.QRISConfig(STORE_DIR / "qris.json")
    if not QRIS_CFG.get("qris_static"):
        QRIS_CFG.set("qris_static",
            "00020101021126570011ID.DANA.WWW011893600915394696514402099469651440303UMI51440014ID.CO.QRIS.WWW0215ID10254172619100303UMI5204594553033605802ID5911PeiterStore6011Kota Bekasi61051741263041D7E")
    DONATION_TRACKER = dn.DonationTracker(STORE_DIR / "donations.json")
else:
    QRIS_CFG = DONATION_TRACKER = None

# ══════════════════════════════════════════════════════════════════
#  THEME / UI
# ══════════════════════════════════════════════════════════════════
ACCENT  = Fore.WHITE + Style.BRIGHT
TITLE   = Fore.WHITE + Style.BRIGHT
TEXT    = Fore.WHITE
VALUE   = Fore.LIGHTYELLOW_EX + Style.BRIGHT
MUTED   = Fore.LIGHTBLACK_EX
SUCCESS = Fore.LIGHTGREEN_EX + Style.BRIGHT
WARNING = Fore.LIGHTYELLOW_EX + Style.BRIGHT
DANGER  = Fore.LIGHTRED_EX + Style.BRIGHT

APP_NAME    = "PEITER STORE"
APP_CREDIT  = "@PeiterStore"
APP_VERSION = "ULTIMATE v1.0"
UI_WIDTH    = min(76, max(38, shutil.get_terminal_size(fallback=(76, 24)).columns - 2))

# Output dirs
OUTPUT_DIR       = Path(os.environ.get("PEITER_OUTPUT_DIR", str(BASE_DIR)))
TOOLS_DIR        = OUTPUT_DIR / "peiTer_Tools"
RESULTS_SPLIT    = OUTPUT_DIR / "hasil_split"
LOOKUP_RESULTS   = OUTPUT_DIR / "lookup_results"
BAN_RESULTS_DIR  = OUTPUT_DIR / "ban_results"
for d in (TOOLS_DIR, RESULTS_SPLIT, LOOKUP_RESULTS, BAN_RESULTS_DIR):
    d.mkdir(parents=True, exist_ok=True)

CLEAR_FILE   = BAN_RESULTS_DIR / "CLEAR.txt"
BAN_FILE_OUT = BAN_RESULTS_DIR / "BAN.txt"
UNKNOWN_FILE = BAN_RESULTS_DIR / "UNKNOWN.txt"
RESULTS_TXT  = OUTPUT_DIR / "results.txt"

# ══════════════════════════════════════════════════════════════════
#  UTIL
# ══════════════════════════════════════════════════════════════════
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def safe_pause(msg="Press [ENTER] to continue..."):
    try:
        input(f"\n{MUTED}{msg}{Style.RESET_ALL}")
    except (EOFError, KeyboardInterrupt):
        return

def line(char="─", width=None, color=MUTED):
    width = width or min(UI_WIDTH, 62)
    print(f"{color}{char * width}{Style.RESET_ALL}")

def center(text, color=Fore.WHITE, bold=False, width=None):
    width = width or UI_WIDTH
    style = Style.BRIGHT if bold else ""
    print(f"{color}{style}{text[:width].center(width)}{Style.RESET_ALL}")

def section(title):
    print(f"\n{ACCENT}{Style.BRIGHT}› {title}{Style.RESET_ALL}")

def footer():
    print(f"\n{MUTED}{APP_CREDIT}  •  {APP_NAME} {APP_VERSION}{Style.RESET_ALL}")

def banner(show_license=False):
    clear_screen()
    print()
    center("PEITER STORE", Fore.WHITE, True)
    center("@PeiterStore", Fore.LIGHTBLACK_EX, True)
    center("DEVICE ID CHECKER — ULTIMATE", Fore.WHITE, True)
    center(APP_VERSION, Fore.LIGHTBLACK_EX)
    center(f"ENGINE: PEITER-PERF • MODE: {PERFORMANCE_MODE.upper()}", Fore.LIGHTBLACK_EX)

# ══════════════════════════════════════════════════════════════════
#  DEVICE / SPLIT / FILTER
# ══════════════════════════════════════════════════════════════════
DEVICE_RE_LOCAL = re.compile(r"(?i)(?:and_|ios_)[A-Za-z0-9_-]+")

def extract_records(text: str):
    text = text or ""
    id_re = re.compile(r"(?i)(?:and_|ios_)[A-Za-z0-9_-]+")
    sep_re = re.compile(r"(?m)^\s*(?:={6,}|-{3,})\s*$")
    start_re = re.compile(
        r"(?i)^\s*(?:\d+[.)]\s*)?(?:device\s*id\s*[:=]?\s*)?"
        r"((?:and_|ios_)[A-Za-z0-9_-]+)(?:\s+.*)?$"
    )
    lbl_re = re.compile(r"(?i)^\s*(?:device\s*id|deviceid)\s*[:=]?\s*((?:and_|ios_)[A-Za-z0-9_-]+)")
    num_re = re.compile(r"^\s*\d+[.)]?\s*$")

    def find_id(lines):
        for raw in lines:
            m = lbl_re.search(raw)
            if m and DEVICE_RE_LOCAL.fullmatch(m.group(1)): return m.group(1)
            m = start_re.match(raw)
            if m and DEVICE_RE_LOCAL.fullmatch(m.group(1)): return m.group(1)
            m = id_re.search(raw)
            if m and DEVICE_RE_LOCAL.fullmatch(m.group(0)): return m.group(0)
        return None

    def clean(lines):
        c = [l.rstrip() for l in lines]
        while c and not c[0].strip(): c.pop(0)
        while c and not c[-1].strip(): c.pop()
        if not c: return None
        if c and num_re.fullmatch(c[0]):
            c.pop(0)
            while c and not c[0].strip(): c.pop(0)
        if not c: return None
        c[0] = re.sub(r"^\s*\d+[.)]\s+(?=(?:Device\s*id\s*[:=]?\s*)?(?:and_|ios_))",
                      "", c[0], count=1, flags=re.I)
        return c

    def make(lines):
        did = find_id(lines)
        if not did: return None
        cl = clean(lines)
        if not cl: return None
        t = "\n".join(cl).strip()
        return {"id": did, "text": t} if t else None

    if sep_re.search(text):
        recs = []
        for blk in sep_re.split(text):
            r = make(blk.splitlines())
            if r: recs.append(r)
        if recs: return recs

    lines = text.splitlines()
    starts = []
    i = 0
    while i < len(lines):
        m = start_re.match(lines[i])
        if m and DEVICE_RE_LOCAL.fullmatch(m.group(1)):
            starts.append(i); i += 1; continue
        if num_re.fullmatch(lines[i]):
            j = i + 1
            while j < len(lines) and not lines[j].strip(): j += 1
            if j < len(lines):
                dm = lbl_re.match(lines[j])
                if dm and DEVICE_RE_LOCAL.fullmatch(dm.group(1)):
                    starts.append(i); i = j + 1; continue
        i += 1

    if starts:
        recs = []
        for n, s in enumerate(starts):
            e = starts[n+1] if n+1 < len(starts) else len(lines)
            r = make(lines[s:e])
            if r: recs.append(r)
        if recs: return recs

    recs, seen = [], set()
    for ln in lines:
        for m in id_re.finditer(ln):
            c = m.group(0)
            if DEVICE_RE_LOCAL.fullmatch(c) and c.lower() not in seen:
                seen.add(c.lower())
                recs.append({"id": c, "text": c})
    return recs

def load_records(path: str):
    p = Path(str(path).strip().strip('"').strip("'")).expanduser()
    if not p.is_file():
        for b in (OUTPUT_DIR, BASE_DIR, Path.cwd()):
            c = b / p.name
            if c.is_file(): p = c; break
    if not p.is_file(): raise FileNotFoundError(f"File tidak ditemukan: {path}")
    with p.open("r", encoding="utf-8-sig", errors="ignore") as f:
        return extract_records(f.read())

def unique_records_keep_order(records):
    seen, out, dup = set(), [], 0
    for r in records:
        k = r["id"].lower()
        if k in seen: dup += 1; continue
        seen.add(k); out.append(r)
    return out, dup

def save_numbered_records(path: Path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for i, rec in enumerate(records, 1):
            f.write(f"{i}. {rec['text'].rstrip()}\n")
            f.write("=" * 70 + "\n")

def save_plain_ids(path: Path, ids):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for d in ids: f.write(str(d).strip() + "\n")

# Filter helpers
def _first_int(text, patterns):
    for pat in patterns:
        m = re.search(pat, text or "", re.I | re.M)
        if m:
            try: return int(m.group(1).replace(",", "").strip())
            except (ValueError, TypeError): pass
    return None

def get_skin_count(rec):
    return _first_int(rec.get("text",""), [r"(?im)^\s*(?:skin\s*count|skin_count|skins?)\s*[:=\-]\s*([\d,]+)"])

def get_level(rec):
    return _first_int(rec.get("text",""), [r"(?im)^\s*(?:level|lvl)\s*[:=\-]\s*(\d+)"])

RANK_NAMES = ("grandmaster","mythic","legend","epic","master","elite","warrior")

def normalize_rank(v):
    v = str(v or "").strip().lower()
    v = re.sub(r"\s+", " ", v)
    for r in RANK_NAMES:
        if re.search(rf"(?<![a-z]){re.escape(r)}(?![a-z])", v): return r
    return None

def get_rank(rec):
    t = rec.get("text","") or ""
    for lbl in ("Rank","Current Rank","Highest Rank"):
        m = re.search(rf"(?im)^\s*{re.escape(lbl)}\s*[:=\-]\s*(.+?)\s*$", t)
        if m:
            r = normalize_rank(m.group(1))
            if r: return r
    for ln in t.splitlines():
        r = normalize_rank(ln)
        if r: return r
    return None

COLLECTOR_TIERS = ("Amateur Collector","Junior Collector","Seasoned Collector",
                   "Expert Collector","Renowned Collector","Exalted Collector",
                   "Mega Collector","World Collector","Supreme Collector")

def get_collector(rec):
    t = rec.get("text","") or ""
    vals = []
    for pat in (r"(?im)^\s*collector\s+(?:title|tier)\s*[:=]\s*(.+?)\s*$",
                r"(?im)^\s*collector\s*[:=]\s*(.+?)\s*$"):
        vals.extend(m.group(1).strip() for m in re.finditer(pat, t))
    for h in vals + [t]:
        n = re.sub(r"\s+", " ", h).strip().lower()
        for c in sorted(COLLECTOR_TIERS, key=len, reverse=True):
            if re.search(rf"(?<![a-z]){re.escape(c.lower())}(?![a-z])", n): return c
    return None

# ══════════════════════════════════════════════════════════════════
#  TERMINAL PROGRESS
# ══════════════════════════════════════════════════════════════════
class TerminalProgress:
    def __init__(self, title="Processing", interval=0.5):
        self.title = title
        self.interval = interval
        self.total = 0
        self.done = 0
        self.valid = 0
        self.failed = 0
        self.start_time = time.time()
        self.stop_flag = threading.Event()
        self.lock = threading.Lock()
        self._started = False

    def start(self, total):
        self.total = total
        self.start_time = time.time()
        self.stop_flag.clear()
        self._started = True
        self._render()
        threading.Thread(target=self._loop, daemon=True).start()

    def update(self, done=None, valid=None, failed=None):
        with self.lock:
            if done is not None: self.done = done
            if valid is not None: self.valid = valid
            if failed is not None: self.failed = failed
        self._render()

    def finish(self):
        self.stop_flag.set()
        self._render()
        print()

    def _render(self):
        if not self._started: return
        el = max(time.time() - self.start_time, 1e-9)
        bar = progress_bar(self.done, self.total, 24)
        spd = self.done / el
        eta = (self.total - self.done) / spd if spd > 0 else 0
        msg = (
            f"\r{ACCENT}{self.title}{Style.RESET_ALL} "
            f"{TEXT}{self.done}/{self.total}{Style.RESET_ALL} "
            f"{VALUE}[{bar}]{Style.RESET_ALL} "
            f"{SUCCESS}✓{self.valid}{Style.RESET_ALL} "
            f"{DANGER}✗{self.failed}{Style.RESET_ALL} "
            f"{MUTED}{spd:5.1f}/s ETA {int(eta):>4}s{Style.RESET_ALL}"
        )
        sys.stdout.write("\033[2K" + msg)
        sys.stdout.flush()

    def _loop(self):
        while not self.stop_flag.is_set():
            time.sleep(self.interval)
            self._render()

def run_parallel(ids, check_func, title="Processing",
                 workers=None, on_result=None, stop_check=None):
    total = len(ids)
    if total == 0: return [], 0
    if workers is None:
        workers = min(PROFILE["valid_w"] * 2, total, 100)
    workers = max(1, min(workers, total))

    results, lock = [], threading.Lock()
    done = [0]
    prog = TerminalProgress(title=title)
    prog.start(total)

    chunk_size = max(1, total // workers)
    chunks = [ids[i:i+chunk_size] for i in range(0, total, chunk_size)]

    def _chunk(chunk):
        for item in chunk:
            if stop_check and stop_check(): return
            try:
                _ADAPTIVE_RATE.wait()
                r = check_func(item)
                ok = r is not None and r is not False
                _ADAPTIVE_RATE.report(ok)
                if ok:
                    with lock:
                        results.append(r)
                        if on_result:
                            try: on_result(item, r)
                            except Exception: pass
            except Exception:
                _ADAPTIVE_RATE.report(False)
            with lock:
                done[0] += 1
                prog.update(done=done[0], valid=len(results), failed=done[0]-len(results))

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(_chunk, chunks))
    prog.finish()
    return results, total

# ══════════════════════════════════════════════════════════════════
#  PIPELINE BAN → VALID → FULL INFO
# ══════════════════════════════════════════════════════════════════
def stage_ban(input_path: Path):
    section("STAGE 1/3 — CEK BAN")
    try:
        text = input_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"{DANGER}Gagal baca: {e}{Style.RESET_ALL}"); return False
    ids = extract_device_ids(text)
    if not ids:
        print(f"{DANGER}Tidak ada Device ID.{Style.RESET_ALL}"); return False
    print(f"{MUTED}Loaded {len(ids)} Device ID{Style.RESET_ALL}")

    for f in (BAN_FILE_OUT, CLEAR_FILE, UNKNOWN_FILE):
        f.write_text("", encoding="utf-8")

    banned = [0]; unknown = [0]; lk = threading.Lock()

    def _check(did):
        st, res = check_device_ban_silent(did)
        if st == "BANNED":
            with lk:
                banned[0] += 1
                with open(BAN_FILE_OUT, "a", encoding="utf-8") as f: f.write(res + "\n")
            return None
        if st == "CLEAR":
            with open(CLEAR_FILE, "a", encoding="utf-8") as f: f.write(did + "\n")
            return did
        with lk:
            unknown[0] += 1
            with open(UNKNOWN_FILE, "a", encoding="utf-8") as f: f.write(str(res) + "\n")
        return None

    clean, total = run_parallel(ids, _check, title="BAN CHECK",
                                workers=min(PROFILE["ban_w"]*2, len(ids), 100))
    print(f"\n{SUCCESS}✓ CLEAR : {len(clean)}{Style.RESET_ALL}")
    print(f"{DANGER}✗ BANNED : {banned[0]}{Style.RESET_ALL}")
    print(f"{WARNING}⚠ UNKNOWN: {unknown[0]}{Style.RESET_ALL}")
    return len(clean) > 0

def stage_valid(clear_file: Path):
    section("STAGE 2/3 — CEK VALID / LOGIN")
    try:
        text = clear_file.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"{DANGER}Gagal baca: {e}{Style.RESET_ALL}"); return False
    ids = [l.strip() for l in text.splitlines() if l.strip()]
    if not ids:
        print(f"{DANGER}Tidak ada device CLEAR.{Style.RESET_ALL}"); return False
    print(f"{MUTED}Loaded {len(ids)} device CLEAR{Style.RESET_ALL}")

    RESULTS_TXT.write_text("", encoding="utf-8")
    lk = threading.Lock()

    def _check(did):
        acc, zid = GameLogin(did).run()
        if acc and zid:
            line_txt = f"Device id: {did} | account id: {acc} | zone id: {zid}"
            with lk:
                with open(RESULTS_TXT, "a", encoding="utf-8") as f: f.write(line_txt + "\n")
            return did
        return None

    valid, total = run_parallel(ids, _check, title="VALID CHECK",
                                workers=min(PROFILE["valid_w"]*2, len(ids), 120))
    print(f"\n{SUCCESS}✓ VALID : {len(valid)}{Style.RESET_ALL}")
    print(f"{DANGER}✗ FAILED: {total - len(valid)}{Style.RESET_ALL}")
    return len(valid) > 0

def stage_full_info(results_file: Path):
    section("STAGE 3/3 — FULL INFO")
    try:
        text = results_file.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"{DANGER}Gagal baca: {e}{Style.RESET_ALL}"); return False

    entries = []
    for ln in text.splitlines():
        m = re.search(r"Device id:\s*((?:and_|ios_)[A-Za-z0-9_-]+)", ln, re.I)
        if not m: continue
        did = m.group(1)
        a = re.search(r"account id:\s*(\d+)", ln, re.I)
        z = re.search(r"zone id:\s*(\d+)", ln, re.I)
        if a and z:
            entries.append({"device": did, "account": int(a.group(1)), "zone": int(z.group(1))})
    if not entries:
        print(f"{DANGER}Tidak ada entry valid.{Style.RESET_ALL}"); return False
    print(f"{MUTED}Loaded {len(entries)} akun valid{Style.RESET_ALL}")

    out_file = LOOKUP_RESULTS / "full_info.txt"
    out_file.write_text("", encoding="utf-8")
    lk = threading.Lock(); ok = [0]

    def _check(e):
        r = lookup_player_data(e["account"], zone_id=e["zone"], device_id=e["device"])
        if r.get("status") != "success": return None
        pd = r["player_data"]
        with lk:
            ok[0] += 1
            with open(out_file, "a", encoding="utf-8") as f:
                f.write(f"{ok[0]}.\nDevice id: {e['device']} | account id: {e['account']} | zone id: {e['zone']}\n")
                for k, v in pd.items():
                    if k == "hero_history" and isinstance(v, list): v = ", ".join(v[:15])
                    f.write(f"  {k:<24}: {v}\n")
                f.write("=" * 70 + "\n")
        return e

    done, total = run_parallel(entries, _check, title="FULL INFO",
                               workers=min(PROFILE["detail_w"]*2, len(entries), 80))
    print(f"\n{SUCCESS}✓ FULL INFO: {len(done)}/{total}{Style.RESET_ALL}")
    print(f"  {VALUE}{out_file}{Style.RESET_ALL}")
    return len(done) > 0

def pipeline_ban_valid_full(input_file: str):
    banner()
    section("AUTO CEK • BAN / VALID / FULL INFO")
    p = Path(input_file).expanduser().resolve()
    if not p.is_file():
        print(f"{DANGER}File tidak ditemukan: {p}{Style.RESET_ALL}"); safe_pause(); return
    print(f"{TEXT}Input :{Style.RESET_ALL} {VALUE}{p}{Style.RESET_ALL}\n")

    if not stage_ban(p):
        print(f"\n{WARNING}Tidak ada device CLEAR, pipeline dihentikan.{Style.RESET_ALL}")
        safe_pause(); return
    if not stage_valid(CLEAR_FILE):
        print(f"\n{WARNING}Tidak ada akun valid, pipeline dihentikan.{Style.RESET_ALL}")
        safe_pause(); return
    stage_full_info(RESULTS_TXT)

    footer()
    safe_pause()

# ══════════════════════════════════════════════════════════════════
#  MENU 1 — GENERATE DEV ID + AUTO CEK
# ══════════════════════════════════════════════════════════════════
def _random_hex(n): return secrets.token_hex((n + 1) // 2)[:n]
def _random_alnum(n):
    a = "abcdefghijklmnopqrstuvwxyz0123456789"
    return "".join(secrets.choice(a) for _ in range(n))

def generate_android_id():
    return f"and_{_random_hex(32)}{_random_alnum(24)}-{uuid.uuid4()}"

def generate_ios_id():
    base = str(uuid.uuid4()).upper()
    if secrets.randbelow(2):
        return f"ios_{base}_{''.join(secrets.choice('0123456789') for _ in range(16))}"
    return f"ios_{base}"

def menu_generate_devid():
    banner()
    section("🧪 DEVICE ID GENERATOR • TEST / DEMO")
    print(
        f"\n  {TEXT}Generate Device ID dummy untuk testing.{Style.RESET_ALL}\n"
        f"  {VALUE}[1]{Style.RESET_ALL}  TEST ANDROID   {MUTED}and_...{Style.RESET_ALL}\n"
        f"  {VALUE}[2]{Style.RESET_ALL}  TEST iOS       {MUTED}ios_...{Style.RESET_ALL}\n"
        f"  {VALUE}[3]{Style.RESET_ALL}  CAMPURAN       {MUTED}Android + iOS{Style.RESET_ALL}\n"
        f"  {DANGER}[0]{Style.RESET_ALL}  KEMBALI"
    )
    footer()
    mode = input(f"\n{TITLE}PEITER STORE{Style.RESET_ALL} {VALUE}›{Style.RESET_ALL} Pilih [0-3]: ").strip()
    if mode == "0": return
    if mode not in {"1","2","3"}:
        print(f"{DANGER}Pilihan tidak valid.{Style.RESET_ALL}"); safe_pause(); return

    raw = input(f"{TEXT}Jumlah: {Style.RESET_ALL}").strip()
    try:
        count = int(raw)
        if count < 1 or count > 1_000_000: raise ValueError
    except ValueError:
        print(f"{DANGER}Masukkan 1 - 1.000.000.{Style.RESET_ALL}"); safe_pause(); return

    gen, seen = [], set()
    def add(f):
        while True:
            v = f()
            if v not in seen: seen.add(v); gen.append(v); return
    if mode == "1":
        for _ in range(count): add(generate_android_id)
    elif mode == "2":
        for _ in range(count): add(generate_ios_id)
    else:
        for i in range(count):
            add(generate_android_id if i % 2 == 0 else generate_ios_id)

    out = TOOLS_DIR / "generated.txt"
    out.write_text("\n".join(gen) + "\n", encoding="utf-8")
    print(f"\n{SUCCESS}✓ {len(gen)} ID disimpan{Style.RESET_ALL}")
    print(f"  {VALUE}{out}{Style.RESET_ALL}")

    if input(f"\n{TEXT}Jalankan AUTO CEK sekarang? [y/N]: {Style.RESET_ALL}").strip().lower() == "y":
        pipeline_ban_valid_full(str(out))
    else:
        safe_pause()

# ══════════════════════════════════════════════════════════════════
#  MENU 2 — AUTO CEK BAN + VALID + FULL INFO
# ══════════════════════════════════════════════════════════════════
def menu_auto_pipeline():
    banner()
    section("AUTO CEK • BAN / VALID / FULL INFO")
    print(
        f"\n  {TEXT}Pipeline otomatis memproses file Device ID dalam 3 tahap:{Style.RESET_ALL}\n"
        f"  {VALUE}[1]{Style.RESET_ALL} CEK BAN\n"
        f"  {VALUE}[2]{Style.RESET_ALL} CEK VALID / LOGIN\n"
        f"  {VALUE}[3]{Style.RESET_ALL} FULL INFO\n"
    )
    footer()
    fp = input(f"\n{TITLE}PEITER STORE{Style.RESET_ALL} {VALUE}›{Style.RESET_ALL} Path file Device ID: ").strip().strip('"')
    if not fp:
        print(f"{DANGER}Path kosong.{Style.RESET_ALL}"); safe_pause(); return
    pipeline_ban_valid_full(fp)

# ══════════════════════════════════════════════════════════════════
#  MENU 3 — CEK BAN SINGLE
# ══════════════════════════════════════════════════════════════════
def menu_ban_single():
    banner()
    section("CEK BAN • SINGLE")
    did = input(f"\n{TEXT}Device ID: {Style.RESET_ALL}").strip()
    if not did:
        print(f"{DANGER}Kosong.{Style.RESET_ALL}"); safe_pause(); return
    print(f"\n{MUTED}Checking...{Style.RESET_ALL}")
    st, res = check_device_ban_silent(did)
    if st == "BANNED":
        print(f"\n{DANGER}✗ BANNED{Style.RESET_ALL}")
        print(f"  {TEXT}{res}{Style.RESET_ALL}")
    elif st == "CLEAR":
        print(f"\n{SUCCESS}✓ CLEAR{Style.RESET_ALL}")
    else:
        print(f"\n{WARNING}⚠ UNKNOWN{Style.RESET_ALL}")
        print(f"  {TEXT}{res}{Style.RESET_ALL}")
    safe_pause()

# ══════════════════════════════════════════════════════════════════
#  MENU 4 — CEK VALID SINGLE
# ══════════════════════════════════════════════════════════════════
def menu_valid_single():
    banner()
    section("CEK VALID • SINGLE")
    did = input(f"\n{TEXT}Device ID: {Style.RESET_ALL}").strip()
    if not did:
        print(f"{DANGER}Kosong.{Style.RESET_ALL}"); safe_pause(); return
    print(f"\n{MUTED}Checking...{Style.RESET_ALL}")
    acc, zid = GameLogin(did).run()
    if acc and zid:
        print(f"\n{SUCCESS}✓ VALID{Style.RESET_ALL}")
        print(f"  {TEXT}Device ID : {did}{Style.RESET_ALL}")
        print(f"  {TEXT}Account ID: {acc}{Style.RESET_ALL}")
        print(f"  {TEXT}Zone ID   : {zid}{Style.RESET_ALL}")
    else:
        print(f"\n{DANGER}✗ LOGIN FAILED{Style.RESET_ALL}")
    safe_pause()

# ══════════════════════════════════════════════════════════════════
#  MENU 5 — LOOKUP SINGLE
# ══════════════════════════════════════════════════════════════════
def menu_lookup_single():
    banner()
    section("LOOKUP • SINGLE")
    print(f"{MUTED}Format: <device_id> <account_id> <zone_id>{Style.RESET_ALL}")
    print(f"{MUTED}atau  : Device id: ... | account id: ... | zone id: ...{Style.RESET_ALL}\n")
    raw = input(f"{TEXT}Input: {Style.RESET_ALL}").strip()
    if not raw:
        print(f"{DANGER}Kosong.{Style.RESET_ALL}"); safe_pause(); return

    did = None
    acc = None
    zid = None

    compact = re.fullmatch(r"((?:and_|ios_)[A-Za-z0-9_-]+)\s+(\d+)\s+(\d+)", raw)
    if compact:
        did, acc, zid = compact.group(1), int(compact.group(2)), int(compact.group(3))
    else:
        m = re.search(r"Device id:\s*((?:and_|ios_)[A-Za-z0-9_-]+)", raw, re.I)
        if m: did = m.group(1)
        a = re.search(r"account id:\s*(\d+)", raw, re.I)
        if a: acc = int(a.group(1))
        z = re.search(r"zone id:\s*(\d+)", raw, re.I)
        if z: zid = int(z.group(1))

    if not (acc and zid):
        print(f"{DANGER}Format tidak valid.{Style.RESET_ALL}"); safe_pause(); return

    print(f"\n{MUTED}Lookup {acc} / {zid}...{Style.RESET_ALL}")
    r = lookup_player_data(acc, zone_id=zid, device_id=did)
    if r.get("status") != "success":
        print(f"\n{DANGER}✗ {r.get('error','Unknown')}{Style.RESET_ALL}"); safe_pause(); return

    pd = r["player_data"]
    print(f"\n{SUCCESS}✓ LOOKUP SUCCESS{Style.RESET_ALL}\n")
    for k, v in pd.items():
        if k == "hero_history" and isinstance(v, list): v = ", ".join(v[:15])
        print(f"  {MUTED}{k:<24}{Style.RESET_ALL}: {TEXT}{v}{Style.RESET_ALL}")

    # Simpan
    out = LOOKUP_RESULTS / f"lookup_{acc}_{zid}.txt"
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"Device id: {did} | account id: {acc} | zone id: {zid}\n")
        for k, v in pd.items():
            f.write(f"  {k:<24}: {v}\n")
    print(f"\n{VALUE}✓ Saved → {out}{Style.RESET_ALL}")
    safe_pause()

# ══════════════════════════════════════════════════════════════════
#  MENU 6 — SPLIT / FILTER / DEVICE MANAGER
# ══════════════════════════════════════════════════════════════════
def menu_split():
    while True:
        banner()
        section("SPLIT / DEVICE MANAGER")
        print(
            f"\n  {VALUE}[1]{Style.RESET_ALL}  SPLIT FULL INFO\n"
            f"  {VALUE}[2]{Style.RESET_ALL}  SPLIT DEVICE ID\n"
            f"  {VALUE}[3]{Style.RESET_ALL}  SPLIT ANDROID / iOS\n"
            f"  {VALUE}[4]{Style.RESET_ALL}  DEDUP + EXPORT\n"
            f"  {VALUE}[5]{Style.RESET_ALL}  FILTER (Skin / Level / Rank / Collector)\n"
            f"  {DANGER}[0]{Style.RESET_ALL}  KEMBALI"
        )
        footer()
        ch = input(f"\n{TITLE}PEITER STORE{Style.RESET_ALL} {VALUE}›{Style.RESET_ALL} Pilih [0-5]: ").strip()
        if ch == "0": return
        if ch not in {"1","2","3","4","5"}:
            print(f"{DANGER}Pilihan tidak valid.{Style.RESET_ALL}"); safe_pause(); continue

        fp = input(f"\n{TEXT}FILE TXT: {Style.RESET_ALL}").strip().strip('"').strip("'")
        try:
            records = load_records(fp)
        except Exception as e:
            print(f"\n{DANGER}Gagal baca: {e}{Style.RESET_ALL}"); safe_pause(); continue

        clean, dup = unique_records_keep_order(records)
        if not clean:
            print(f"\n{DANGER}Tidak ada Device ID valid.{Style.RESET_ALL}"); safe_pause(); continue

        try:
            size = int(input(f"{TEXT}Jumlah per file [default 50]: {Style.RESET_ALL}").strip() or "50")
        except ValueError:
            size = 50
        size = max(1, size)

        out_dir = RESULTS_SPLIT / "split"
        out_dir.mkdir(parents=True, exist_ok=True)
        for old in out_dir.glob("*.txt"): old.unlink()

        def write_chunks(items, prefix, full_info=False):
            parts = 0
            for s in range(0, len(items), size):
                parts += 1
                chunk = items[s:s+size]
                p = out_dir / f"{prefix}_{parts:03d}.txt"
                if full_info:
                    save_numbered_records(p, chunk)
                else:
                    with p.open("w", encoding="utf-8") as f:
                        for it in chunk: f.write(str(it).strip() + "\n")
            return parts

        if ch == "1":
            parts = write_chunks(clean, "full_info", True)
            print(f"\n{SUCCESS}✓ Split FULL INFO: {parts} file{Style.RESET_ALL}")
        elif ch == "2":
            ids = [r["id"] for r in clean]
            parts = write_chunks(ids, "device_id")
            print(f"\n{SUCCESS}✓ Split DEVICE ID: {parts} file{Style.RESET_ALL}")
        elif ch == "3":
            ids_and = [r["id"] for r in clean if r["id"].lower().startswith("and_")]
            ids_ios = [r["id"] for r in clean if r["id"].lower().startswith("ios_")]
            pa = write_chunks(ids_and, "android_and")
            pi = write_chunks(ids_ios, "ios")
            print(f"\n{SUCCESS}✓ Android: {len(ids_and)} ({pa} file) | iOS: {len(ids_ios)} ({pi} file){Style.RESET_ALL}")
        elif ch == "4":
            save_numbered_records(RESULTS_SPLIT / "all_devices.txt", clean)
            save_numbered_records(RESULTS_SPLIT / "android_and.txt",
                                  [r for r in clean if r["id"].lower().startswith("and_")])
            save_numbered_records(RESULTS_SPLIT / "ios.txt",
                                  [r for r in clean if r["id"].lower().startswith("ios_")])
            print(f"\n{SUCCESS}✓ Export selesai ({len(clean)} unik, {dup} duplikat){Style.RESET_ALL}")
        elif ch == "5":
            filter_menu(clean, out_dir, size)

        print(f"  {VALUE}{out_dir}{Style.RESET_ALL}")
        safe_pause()

def filter_menu(records, out_dir, size):
    while True:
        print(
            f"\n{TEXT}FILTER SPLIT{Style.RESET_ALL}\n"
            f"  {VALUE}[1]{Style.RESET_ALL} Skin 50+/100+/200+/300+\n"
            f"  {VALUE}[2]{Style.RESET_ALL} Level 50+/75+/100+\n"
            f"  {VALUE}[3]{Style.RESET_ALL} Rank (Warrior → Mythic)\n"
            f"  {VALUE}[4]{Style.RESET_ALL} Kombinasi Skin + Level + Rank\n"
            f"  {VALUE}[5]{Style.RESET_ALL} Collector Tier\n"
            f"  {DANGER}[0]{Style.RESET_ALL} Kembali"
        )
        ch = input(f"{TITLE}›{Style.RESET_ALL} Pilih [0-5]: ").strip()
        if ch == "0": return

        skin_min = level_min = None
        ranks = []; collectors = []; prefix = "filtered"

        if ch == "1":
            try: skin_min = int(input("Skin min [50/100/200/300]: ").strip())
            except ValueError: continue
            if skin_min not in (50,100,200,300):
                print(f"{WARNING}Gunakan 50/100/200/300.{Style.RESET_ALL}"); continue
            prefix = f"skin_{skin_min}plus"
        elif ch == "2":
            try: level_min = int(input("Level min [50/75/100]: ").strip())
            except ValueError: continue
            if level_min not in (50,75,100):
                print(f"{WARNING}Gunakan 50/75/100.{Style.RESET_ALL}"); continue
            prefix = f"level_{level_min}plus"
        elif ch == "3":
            rmap = {"1":"warrior","2":"elite","3":"master","4":"grandmaster",
                    "5":"epic","6":"legend","7":"mythic"}
            print("  [1]Warrior [2]Elite [3]Master [4]Grandmaster [5]Epic [6]Legend [7]Mythic")
            sel = input("Pilih (contoh 1,3,7): ").replace(" ","").split(",")
            ranks = [rmap[x] for x in sel if x in rmap]
            if not ranks: continue
            prefix = "rank_" + "_".join(ranks)
        elif ch == "4":
            raw = input("Skin min [kosong=semua]: ").strip()
            if raw:
                try: skin_min = int(raw)
                except ValueError: continue
            raw = input("Level min [kosong=semua]: ").strip()
            if raw:
                try: level_min = int(raw)
                except ValueError: continue
            rmap = {"1":"warrior","2":"elite","3":"master","4":"grandmaster",
                    "5":"epic","6":"legend","7":"mythic"}
            print("  [1]Warrior [2]Elite [3]Master [4]Grandmaster [5]Epic [6]Legend [7]Mythic")
            raw = input("Pilih rank [kosong=semua]: ").strip()
            if raw:
                sel = [x for x in re.split(r"[,\s]+", raw) if x]
                ranks = list(dict.fromkeys(rmap[x] for x in sel if x in rmap))
            if skin_min is None and level_min is None and not ranks:
                print(f"{WARNING}Isi minimal satu filter.{Style.RESET_ALL}"); continue
            prefix = "combined_filter"
        elif ch == "5":
            for i, t in enumerate(COLLECTOR_TIERS, 1):
                print(f"  [{i}] {t}")
            raw = input("Pilih (contoh 3,4 atau 3-6): ").strip()
            sel = []
            for tok in re.split(r"[,\s]+", raw):
                if re.fullmatch(r"\d+-\d+", tok):
                    a,b = map(int, tok.split("-",1)); step = 1 if b>=a else -1
                    sel.extend(str(n) for n in range(a, b+step, step))
                elif tok.isdigit(): sel.append(tok)
            sel = list(dict.fromkeys(sel))
            collectors = [COLLECTOR_TIERS[int(x)-1] for x in sel
                          if x.isdigit() and 1 <= int(x) <= len(COLLECTOR_TIERS)]
            if not collectors: continue
            prefix = "collector_" + "_".join(c.lower().replace(" ","_") for c in collectors)

        ncol = {c.lower() for c in collectors} if collectors else None
        nr = {normalize_rank(r) for r in ranks}; nr.discard(None)

        matched = []
        for r in records:
            if skin_min is not None:
                v = get_skin_count(r)
                if v is None or v < skin_min: continue
            if level_min is not None:
                v = get_level(r)
                if v is None or v < level_min: continue
            if nr:
                v = get_rank(r)
                if v is None or v not in nr: continue
            if ncol:
                v = (get_collector(r) or "").lower()
                if v not in ncol: continue
            matched.append(r)

        if not matched:
            print(f"\n{WARNING}Tidak ada record cocok.{Style.RESET_ALL}"); continue

        for old in out_dir.glob(f"{prefix}_*.txt"): old.unlink()
        parts = 0
        for s in range(0, len(matched), size):
            parts += 1
            save_numbered_records(out_dir / f"{prefix}_{parts:03d}.txt",
                                  matched[s:s+size])
        print(f"\n{SUCCESS}✓ {len(matched)} record, {parts} file{Style.RESET_ALL}")
        print(f"  {VALUE}{out_dir}{Style.RESET_ALL}")

# ══════════════════════════════════════════════════════════════════
#  MENU 7 — STATISTIK
# ══════════════════════════════════════════════════════════════════
def menu_statistics():
    banner()
    section("📊 ACCOUNT STATISTICS")
    fp = input(f"\n{TEXT}FILE FULL INFO (.txt): {Style.RESET_ALL}").strip().strip('"')
    try:
        records = load_records(fp)
    except Exception as e:
        print(f"\n{DANGER}Gagal baca: {e}{Style.RESET_ALL}"); safe_pause(); return

    clean, _ = unique_records_keep_order(records)
    if not clean:
        print(f"\n{DANGER}Tidak ada record.{Style.RESET_ALL}"); safe_pause(); return

    skins, logins = [], []
    tiers = {}
    for r in clean:
        s = get_skin_count(r)
        if s is not None: skins.append(s)
        lvl = get_level(r)
        if lvl is not None: logins.append(lvl)
        t = get_collector(r)
        if t: tiers[t] = tiers.get(t, 0) + 1

    total = len(clean)
    print(f"\n{ACCENT}📊 SUMMARY{Style.RESET_ALL}")
    line()
    print(f"  {TEXT}Total Records{Style.RESET_ALL} : {VALUE}{total}{Style.RESET_ALL}")
    if skins:
        print(f"  {TEXT}Avg Skin{Style.RESET_ALL}      : {VALUE}{sum(skins)/len(skins):.1f}{Style.RESET_ALL}")
        print(f"  {TEXT}Min / Max Skin{Style.RESET_ALL}: {VALUE}{min(skins)} / {max(skins)}{Style.RESET_ALL}")
    if logins:
        print(f"  {TEXT}Avg Level{Style.RESET_ALL}     : {VALUE}{sum(logins)/len(logins):.1f}{Style.RESET_ALL}")

    if tiers:
        print(f"\n{ACCENT}🏷️ COLLECTOR TIER{Style.RESET_ALL}")
        line()
        for t in COLLECTOR_TIERS:
            if t in tiers:
                print(f"  {TEXT}{t:<28}{Style.RESET_ALL}: {VALUE}{tiers[t]}{Style.RESET_ALL}")
    print()
    footer()
    safe_pause()

# ══════════════════════════════════════════════════════════════════
#  MENU 8 — EXPORT / BACKUP
# ══════════════════════════════════════════════════════════════════
def menu_export():
    banner()
    section("EXPORT / BACKUP")
    print(
        f"\n  {VALUE}[1]{Style.RESET_ALL}  Export valid.txt → CSV\n"
        f"  {VALUE}[2]{Style.RESET_ALL}  Export valid.txt → JSON\n"
        f"  {VALUE}[3]{Style.RESET_ALL}  Zip semua hasil\n"
        f"  {VALUE}[4]{Style.RESET_ALL}  Backup penuh\n"
        f"  {DANGER}[0]{Style.RESET_ALL}  Kembali"
    )
    footer()
    ch = input(f"\n{TITLE}PEITER STORE{Style.RESET_ALL} {VALUE}›{Style.RESET_ALL} Pilih [0-4]: ").strip()

    if ch == "0": return
    ts = int(time.time())

    if ch == "1":
        lines = read_valid_lines()
        if not lines:
            print(f"{DANGER}valid.txt kosong.{Style.RESET_ALL}"); safe_pause(); return
        out = OUTPUT_DIR / f"export_{ts}.csv"
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["No","Device ID","Account ID","Zone ID"])
            for i, ln in enumerate(lines, 1):
                info = parse_valid_line(ln) or {}
                w.writerow([i, info.get("device",""), info.get("account",""), info.get("zone","")])
        print(f"\n{SUCCESS}✓ {out}{Style.RESET_ALL}")
    elif ch == "2":
        lines = read_valid_lines()
        if not lines:
            print(f"{DANGER}valid.txt kosong.{Style.RESET_ALL}"); safe_pause(); return
        data = []
        for i, ln in enumerate(lines, 1):
            info = parse_valid_line(ln) or {}; info["no"] = i; data.append(info)
        out = OUTPUT_DIR / f"export_{ts}.json"
        out.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"\n{SUCCESS}✓ {out}{Style.RESET_ALL}")
    elif ch == "3":
        out = OUTPUT_DIR / f"zip_{ts}.zip"
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in OUTPUT_DIR.rglob("*.txt"):
                if f.is_file(): zf.write(f, f.relative_to(OUTPUT_DIR))
        print(f"\n{SUCCESS}✓ {out}{Style.RESET_ALL}")
    elif ch == "4":
        bd = OUTPUT_DIR / "backup"; bd.mkdir(exist_ok=True)
        out = bd / f"backup_{ts}.zip"
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in OUTPUT_DIR.rglob("*"):
                if f.is_file() and not f.name.startswith("backup_") and f.suffix != ".zip":
                    zf.write(f, f.relative_to(OUTPUT_DIR))
        print(f"\n{SUCCESS}✓ {out}{Style.RESET_ALL}")

    safe_pause()

# ══════════════════════════════════════════════════════════════════
#  MAIN MENU
# ══════════════════════════════════════════════════════════════════
def _menu_item(number, title, desc, danger=False):
    color = DANGER if danger else VALUE
    print(f"  {color}[{number}]{Style.RESET_ALL} {TITLE}{title}{Style.RESET_ALL}")
    print(f"       {MUTED}{desc}{Style.RESET_ALL}")

def main_menu():
    while True:
        banner()
        section("MAIN MENU")
        print()
        _menu_item("1", "GENERATE DEV ID + AUTO CEK", "Generate ID dummy lalu jalankan pipeline")
        _menu_item("2", "AUTO CEK BAN + VALID + FULL INFO", "Pipeline 3 tahap dari file Device ID")
        _menu_item("3", "CEK BAN SINGLE", "Cek status ban 1 Device ID")
        _menu_item("4", "CEK VALID SINGLE", "Login 1 Device ID")
        _menu_item("5", "LOOKUP SINGLE", "Ambil info akun lengkap")
        _menu_item("6", "SPLIT / FILTER / DEVICE MANAGER", "Split, filter, dedup, export")
        _menu_item("7", "STATISTIK", "Analisis file FULL INFO")
        _menu_item("8", "EXPORT / BACKUP", "CSV, JSON, ZIP, backup")
        _menu_item("9", "TELEGRAM BOT", "Jalankan bot Telegram (app.py engine)")
        _menu_item("0", "KELUAR", "Tutup program dengan aman", danger=True)
        footer()

        ch = input(f"\n{TITLE}PEITER STORE{Style.RESET_ALL} {VALUE}›{Style.RESET_ALL} Pilih [0-9]: ").strip()

        try:
            if ch == "1": menu_generate_devid()
            elif ch == "2": menu_auto_pipeline()
            elif ch == "3": menu_ban_single()
            elif ch == "4": menu_valid_single()
            elif ch == "5": menu_lookup_single()
            elif ch == "6": menu_split()
            elif ch == "7": menu_statistics()
            elif ch == "8": menu_export()
            elif ch == "9":
                banner()
                section("TELEGRAM BOT")
                print(f"\n  {TEXT}Menjalankan bot Telegram...{Style.RESET_ALL}")
                print(f"  {MUTED}Owner : {OWNER_CHAT_ID}{Style.RESET_ALL}")
                print(f"  {MUTED}Mode  : {PERFORMANCE_MODE.upper()}{Style.RESET_ALL}\n")
                try:
                    load_state()
                    bot_poll()
                except KeyboardInterrupt:
                    print(f"\n{MUTED}Bot dihentikan.{Style.RESET_ALL}")
                    safe_pause()
            elif ch == "0":
                clear_screen()
                print()
                center("PEITER STORE", Fore.WHITE, True)
                center("@PeiterStore", Fore.LIGHTBLACK_EX)
                center("Program selesai. Terima kasih.", Fore.LIGHTBLACK_EX)
                print()
                break
            else:
                print(f"\n{DANGER}Pilihan tidak valid.{Style.RESET_ALL}")
                safe_pause()
        except KeyboardInterrupt:
            print(f"\n{MUTED}Operasi dibatalkan.{Style.RESET_ALL}")
            safe_pause()
        except Exception as e:
            print(f"\n{DANGER}Error: {e}{Style.RESET_ALL}")
            import traceback
            traceback.print_exc()
            safe_pause()

# ══════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 64)
    print("  PEITER STORE — ULTIMATE MERGED")
    print("  Powered by @PeiterStore")
    print("=" * 64)
    print(f"  Owner   : {OWNER_CHAT_ID}")
    print(f"  Mode    : {PERFORMANCE_MODE.upper()}")
    print(f"  License : {'ON' if lics else 'OFF'}")
    print(f"  Extras  : {'ON' if ex else 'OFF'}")
    print(f"  Donate  : {'ON' if dn else 'OFF'}")
    print("=" * 64)
    print()
    main_menu()