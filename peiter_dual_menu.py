#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PEITER STORE — Dual Engine FULL FIXED
🚀 PEITER 1 • Beast Mode
⚡ PEITER 2 • Ultra Mode
Powered by @PeiterStore
"""

import os, sys, time, json, random, secrets, hashlib, threading, re, csv
import shutil, zipfile, socket, zlib, struct, subprocess, platform
import concurrent.futures, uuid
from pathlib import Path
from datetime import datetime, timezone, timedelta

TZ_WIB = timezone(timedelta(hours=7))

print("[BOOT] PEITER STORE Dual Engine starting...")

_MISSING = []
for pkg, pip_name in [("requests","requests"),("zstandard","zstandard"),("Crypto","pycryptodome")]:
    try: __import__(pkg)
    except ImportError: _MISSING.append(pip_name)
if _MISSING:
    print(f"[FATAL] pip install {' '.join(_MISSING)}"); sys.exit(1)

import requests, zstandard as zstd
from Crypto.Cipher import AES
print("[BOOT] Deps OK")

# SERVER DETECT
CPU_COUNT = os.cpu_count() or 2
RAM_MB = 1024
try:
    import psutil
    RAM_MB = int(psutil.virtual_memory().total / (1024 * 1024))
except ImportError:
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    RAM_MB = int(line.split()[1]) // 1024
                    break
    except Exception:
        pass

if CPU_COUNT <= 1: AUTO_WORKERS = 50
elif CPU_COUNT <= 2: AUTO_WORKERS = 100
elif CPU_COUNT <= 4: AUTO_WORKERS = 200
elif CPU_COUNT <= 8: AUTO_WORKERS = 300
elif CPU_COUNT <= 16: AUTO_WORKERS = 400
else: AUTO_WORKERS = 500

if RAM_MB < 512: AUTO_WORKERS = min(AUTO_WORKERS, 100)
elif RAM_MB < 1024: AUTO_WORKERS = min(AUTO_WORKERS, 200)
elif RAM_MB < 2048: AUTO_WORKERS = min(AUTO_WORKERS, 300)
else: AUTO_WORKERS = min(AUTO_WORKERS, 500)

print(f"[BOOT] Server: {CPU_COUNT} CPU, {RAM_MB} MB RAM")
print(f"[BOOT] Auto-workers MAX: {AUTO_WORKERS}")

# IMPORT ENGINE
_engine = None
for _name in ("app", "aplikasi"):
    try:
        _engine = __import__(_name)
        print(f"[BOOT] Engine {_name}.py loaded")
        break
    except ImportError:
        continue
if _engine is None:
    print("[FATAL] Tidak bisa import app.py / aplikasi.py")
    sys.exit(1)
sys.modules["app"] = _engine

GameLogin               = _engine.GameLogin
GameConnection          = _engine.GameConnection
lookup_player_data      = _engine.lookup_player_data
check_device_ban_silent = _engine.check_device_ban_silent
save_valid_result       = _engine.save_valid_result
extract_device_ids      = _engine.extract_device_ids
PERF_PROFILES           = _engine.PERF_PROFILES
PROFILE                 = dict(_engine.PROFILE)
_ADAPTIVE_RATE          = _engine._ADAPTIVE_RATE
STORE_DIR               = _engine.STORE_DIR
LOGS_DIR                = _engine.LOGS_DIR
RESULTS_DIR             = _engine.RESULTS_DIR
BAN_DIR                 = _engine.BAN_DIR

tg_api        = _engine.tg_api
tg_send       = _engine.tg_send
tg_send_doc   = _engine.tg_send_doc
tg_edit       = _engine.tg_edit
tg_answer_cb  = _engine.tg_answer_cb
tg_get_file   = _engine.tg_get_file

load_state       = _engine.load_state
get_role         = _engine.get_role
is_admin         = _engine.is_admin
is_owner         = _engine.is_owner
grant_access     = _engine.grant_access
revoke_access    = _engine.revoke_access
check_limit      = _engine.check_limit
inc_limit        = _engine.inc_limit
set_limit        = _engine.set_limit
reset_limit      = _engine.reset_limit
set_pending      = _engine.set_pending
get_pending      = _engine.get_pending
clear_pending    = _engine.clear_pending
job_stop         = _engine.job_stop
job_check        = _engine.job_check
job_get          = _engine.job_get
stop_job         = _engine.stop_job
rate_wait        = _engine.rate_wait
progress_bar     = _engine.progress_bar
resolve_user     = _engine.resolve_user
now_wib          = _engine.now_wib
forward_single_to_owner = _engine.forward_single_to_owner
forward_batch_to_owner  = _engine.forward_batch_to_owner
menu_stats       = _engine.menu_stats
kb_main          = _engine.kb_main

do_export_csv    = _engine.do_export_csv
do_export_json   = _engine.do_export_json
do_zip           = _engine.do_zip
do_backup        = _engine.do_backup
do_cleanup       = _engine.do_cleanup
do_show_log      = _engine.do_show_log

BOT_TOKEN        = _engine.BOT_TOKEN
OWNER_CHAT_ID    = _engine.OWNER_CHAT_ID
PERFORMANCE_MODE = _engine.PERFORMANCE_MODE

try:
    import license_manager as lics
    print("[BOOT] License manager OK")
except Exception as e:
    lics = None
    print(f"[BOOT] License OFF: {e}")

ex = None
for _exname in ("extras", "ekstra"):
    try:
        ex = __import__(_exname)
        print(f"[BOOT] Extras OK ({_exname}.py)")
        break
    except ImportError:
        continue
if ex is None: print("[BOOT] Extras OFF")

dn = None
for _dname in ("donate", "donasi"):
    try:
        dn = __import__(_dname)
        print(f"[BOOT] Donate OK ({_dname}.py)")
        break
    except ImportError:
        continue
if dn is None: print("[BOOT] Donate OFF")

if dn:
    QRIS_CFG = dn.QRISConfig(STORE_DIR / "qris.json")
    if not QRIS_CFG.get("qris_static"):
        QRIS_CFG.set("qris_static",
            "00020101021126570011ID.DANA.WWW011893600915394696514402099469651440303UMI51440014ID.CO.QRIS.WWW0215ID10254172619100303UMI5204594553033605802ID5911PeiterStore6011Kota Bekasi61051741263041D7E")
    DONATION_TRACKER = dn.DonationTracker(STORE_DIR / "donations.json")
else:
    QRIS_CFG = DONATION_TRACKER = None

on = None
try:
    import output_namer as on
    print("[BOOT] OutputNamer OK")
except Exception as e:
    on = None
    print(f"[BOOT] OutputNamer OFF: {e}")

_STOP_FLAG = threading.Event()
_USER_ENGINE = {}
_ENGINE_LOCK = threading.Lock()

def set_engine(cid, engine):
    with _ENGINE_LOCK:
        _USER_ENGINE[str(cid)] = engine

def get_engine(cid):
    with _ENGINE_LOCK:
        return _USER_ENGINE.get(str(cid), None)


def game_login_with_retry(device_id, max_retries=3, delay=0.5):
    for attempt in range(max_retries):
        bot = None
        try:
            bot = GameLogin(device_id)
            acc, zid = bot.run()
            if acc and zid:
                return acc, zid
        except Exception:
            pass
        finally:
            try:
                if bot: bot.cleanup()
            except Exception:
                pass
        if attempt < max_retries - 1:
            time.sleep(delay)
    return None, None


# PARSER FULL INFO
def _extract_skin(text):
    for pat in [
        r"(?im)^\s*(?:skin\s*count|skin_count|skins?|jumlah\s*skin)\s*[:=\-]?\s*([\d,\.]+)",
        r"(?i)(?:skin\s*count|skin_count|skins?)\s*[:=]\s*([\d,\.]+)",
    ]:
        m = re.search(pat, text or "")
        if m:
            try: return int(m.group(1).replace(",", "").replace(".", ""))
            except: pass
    return None

def _extract_level(text):
    for pat in [
        r"(?im)^\s*(?:level|lvl|tingkat)\s*[:=\-]?\s*(\d+)",
        r"(?i)(?:level|lvl)\s*[:=]\s*(\d+)",
    ]:
        m = re.search(pat, text or "")
        if m:
            try: return int(m.group(1))
            except: pass
    return None

def _normalize_rank(v):
    v = str(v or "").lower()
    for needle, canonical in [
        ("mythical immortal", "mythic"), ("mythical glory", "mythic"),
        ("mythical honor", "mythic"), ("mythic", "mythic"),
        ("legend", "legend"), ("epic", "epic"),
        ("grandmaster", "grandmaster"), ("master", "master"),
        ("elite", "elite"), ("warrior", "warrior"),
    ]:
        if needle in v: return canonical
    return None

def _extract_rank(text):
    m = re.search(r"(?im)^\s*(?:current\s*rank|highest\s*rank|rank|tier)\s*[:=\-]?\s*(.+?)\s*$", text or "")
    if m:
        r = _normalize_rank(m.group(1))
        if r: return r
    for ln in (text or "").splitlines():
        r = _normalize_rank(ln)
        if r: return r
    return None

COLLECTOR_TIERS = (
    "Amateur Collector","Junior Collector","Seasoned Collector",
    "Expert Collector","Renowned Collector","Exalted Collector",
    "Mega Collector","World Collector","Supreme Collector"
)

def _extract_collector(text):
    for tier in sorted(COLLECTOR_TIERS, key=len, reverse=True):
        if re.search(rf"(?i)\b{re.escape(tier)}\b", text or ""):
            return tier
    return None


def _parse_full_info_blocks(text):
    records = []
    pattern = re.compile(r"(?i)(?:device\s*id\s*[:=]?\s*)?((?:and_|ios_)[A-Za-z0-9_-]+)")
    current_lines = []
    current_id = None
    seen_ids = set()

    for ln in (text or "").splitlines():
        m = pattern.search(ln)
        if m:
            found_id = m.group(1)
            if found_id in seen_ids:
                if current_id is not None:
                    current_lines.append(ln)
                continue
            if current_id is not None:
                block_text = "\n".join(current_lines)
                records.append({
                    "id": current_id, "text": block_text.strip(),
                    "skin": _extract_skin(block_text),
                    "level": _extract_level(block_text),
                    "rank": _extract_rank(block_text),
                    "collector": _extract_collector(block_text),
                })
                seen_ids.add(current_id)
            current_lines = [ln]
            current_id = found_id
        else:
            if current_id is not None:
                current_lines.append(ln)

    if current_id is not None and current_lines:
        block_text = "\n".join(current_lines)
        records.append({
            "id": current_id, "text": block_text.strip(),
            "skin": _extract_skin(block_text),
            "level": _extract_level(block_text),
            "rank": _extract_rank(block_text),
            "collector": _extract_collector(block_text),
        })

    return records


def _do_filter_generic(cid, username, local_path, filter_type, filter_value,
                        skin_min=None, level_min=None, rank_target=None,
                        collector_target=None, preview=True):
    try:
        text = Path(local_path).read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        tg_send(cid, f"❌ Gagal baca file: {e}")
        return

    records = _parse_full_info_blocks(text)
    if not records:
        tg_send(cid, "❌ Tidak ada record di file")
        return

    matched = []
    for r in records:
        ok = True
        if filter_type == "skin" and filter_value is not None:
            if not r.get("skin") or r["skin"] < filter_value: ok = False
        elif filter_type == "level" and filter_value is not None:
            if not r.get("level") or r["level"] < filter_value: ok = False
        elif filter_type == "rank" and filter_value is not None:
            if r.get("rank") != filter_value.lower(): ok = False
        elif filter_type == "collector" and filter_value is not None:
            if r.get("collector") != filter_value: ok = False

        if ok and skin_min is not None:
            if not r.get("skin") or r["skin"] < skin_min: ok = False
        if ok and level_min is not None:
            if not r.get("level") or r["level"] < level_min: ok = False
        if ok and rank_target is not None:
            if r.get("rank") != rank_target.lower(): ok = False
        if ok and collector_target is not None:
            if r.get("collector") != collector_target: ok = False

        if ok: matched.append(r)

    if filter_type == "skin":
        title = f"🎨 Filter Skin ≥ {filter_value}"
        prefix = f"skin_{filter_value}"
    elif filter_type == "level":
        title = f"⭐ Filter Level ≥ {filter_value}"
        prefix = f"level_{filter_value}"
    elif filter_type == "rank":
        title = f"🏆 Filter Rank: {filter_value.title()}"
        prefix = f"rank_{filter_value}"
    elif filter_type == "collector":
        title = f"💎 Filter Collector: {filter_value}"
        prefix = f"collector_{filter_value.replace(' ','_').lower()}"
    else:
        title = "🔍 Filter Kombinasi"
        parts = []
        if skin_min: parts.append(f"skin{skin_min}")
        if level_min: parts.append(f"lv{level_min}")
        if rank_target: parts.append(rank_target)
        if collector_target:
            parts.append(collector_target.replace(" ", "_").lower())
        prefix = "combo_" + "_".join(parts) if parts else "combo"

    if not matched:
        tg_send(cid,
                f"⚠️ <b>TIDAK ADA HASIL</b>\n━━━━━━━━━━━━━━━\n"
                f"📊 Total record : <b>{len(records)}</b>\n"
                f"🔍 Filter       : {title}\n"
                f"✅ Match        : <b>0</b>\n\n"
                f"Tidak ada akun yang cocok.")
        return

    if preview:
        preview_text = f"🔍 <b>PREVIEW (5 dari {len(matched)})</b>\n━━━━━━━━━━━━━━━\n"
        for r in matched[:5]:
            preview_text += (f"📱 <code>{r['id'][:40]}</code>\n"
                             f"  🎨 Skin: <b>{r.get('skin','-')}</b> | "
                             f"⭐ Level: <b>{r.get('level','-')}</b>\n"
                             f"  🏆 Rank: <b>{r.get('rank','-')}</b> | "
                             f"💎 {r.get('collector','-')}\n\n")
        tg_send(cid, preview_text)

    out_dir = STORE_DIR / "filter"
    out_dir.mkdir(exist_ok=True)
    for old in out_dir.glob(f"{prefix}_*.txt"):
        try: old.unlink()
        except Exception: pass

    parts = 0
    for i in range(0, len(matched), 50):
        parts += 1
        chunk = matched[i:i+50]
        (out_dir / f"{prefix}_part{parts:03d}.txt").write_text(
            "\n\n".join(r["text"] for r in chunk) + "\n", encoding="utf-8")

    zip_path = STORE_DIR / f"filter_{prefix}_{int(time.time())}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in out_dir.glob(f"{prefix}_*.txt"):
            zf.write(f, f.name)

    tg_send(cid,
            f"✅ <b>FILTER SELESAI</b>\n━━━━━━━━━━━━━━━\n"
            f"📊 Total record : <b>{len(records)}</b>\n"
            f"✅ Match        : <b>{len(matched)}</b>\n"
            f"🔍 Filter       : {title}\n"
            f"📦 File         : <b>{parts}</b> (50/file)")

    try:
        tg_send_doc(cid, str(zip_path), f"📁 {len(matched)} akun")
    except Exception:
        pass


class TGProgress:
    def __init__(self, cid, title="Processing", interval=3.0):
        self.cid = cid
        self.title = title
        self.interval = interval
        self.total = 0
        self.done = 0
        self.valid = 0
        self.failed = 0
        self.start_time = time.time()
        self.stop_flag = threading.Event()
        self.lock = threading.Lock()
        self.message_id = None

    def _bar(self, w=24):
        if self.total <= 0:
            return "░" * w + "  0%"
        pct = min(100, int(self.done / self.total * 100))
        fill = int(w * pct / 100)
        return f"{'█'*fill}{'░'*(w-fill)}  {pct}%"

    def _render(self):
        el = max(time.time() - self.start_time, 1e-9)
        spd = self.done / el if el > 0 else 0
        eta = int((self.total - self.done) / spd) if spd > 0 else 0
        bar = self._bar(24)
        return (f"📊 <b>{self.title}</b>\n━━━━━━━━━━━━━━━\n"
                f"⏳ Processing...\n\n<code>{bar}</code>\n\n"
                f"📊 Total  : <b>{self.total}</b>\n"
                f"✅ Valid  : <b>{self.valid}</b>\n"
                f"❌ Failed : <b>{self.failed}</b>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"⏱ ETA   : <b>{eta}s</b>\n"
                f"⚡ Speed : <b>{spd:.1f}/s</b>")

    def start(self, total):
        self.total = total
        self.start_time = time.time()
        self.stop_flag.clear()
        try:
            r = tg_api("sendMessage", chat_id=self.cid,
                       text=self._render(), parse_mode="HTML")
            if r.get("ok"):
                self.message_id = r["result"]["message_id"]
        except Exception:
            pass
        threading.Thread(target=self._loop, daemon=True).start()

    def update(self, done=None, valid=None, failed=None):
        with self.lock:
            if done is not None: self.done = done
            if valid is not None: self.valid = valid
            if failed is not None: self.failed = failed

    def finish(self, final_text=None):
        self.stop_flag.set()
        time.sleep(0.5)
        if self.message_id:
            try:
                tg_edit(self.cid, self.message_id,
                        final_text or self._render())
            except Exception:
                pass

    def _loop(self):
        while not self.stop_flag.is_set():
            time.sleep(self.interval)
            if self.stop_flag.is_set():
                break
            if self.message_id:
                try:
                    tg_edit(self.cid, self.message_id, self._render())
                except Exception:
                    pass


def progress_worker(cid, ids, check_func, title="Processing", workers=None, on_result=None):
    total = len(ids)
    if total == 0:
        return [], 0, None
    if workers is None:
        workers = min(AUTO_WORKERS, total)
    workers = max(1, min(workers, total))

    results, lock = [], threading.Lock()
    done = [0]
    prog = TGProgress(cid, title=title)
    prog.start(total)
    chunk_size = max(1, total // workers)
    chunks = [ids[i:i+chunk_size] for i in range(0, total, chunk_size)]

    def _chunk(chunk):
        for item in chunk:
            if _STOP_FLAG.is_set():
                return
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
                prog.update(done=done[0], valid=len(results),
                            failed=done[0] - len(results))

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex_:
        list(ex_.map(_chunk, chunks))
    prog.finish()
    return results, total, prog


# ══════════════════════════════════════════════════════════════════
#  MENU & KB
# ══════════════════════════════════════════════════════════════════
def start_menu(username, cid):
    return (f"🎯 <b>PEITER STORE</b>\n<i>Powered by @PeiterStore</i>\n"
            f"━━━━━━━━━━━━━━━\n👋 Halo, <b>{username}</b>\n\n"
            f"📌 Pilih engine di bawah:\n\n"
            f"🚀 <b>PEITER 1</b>  •  Beast Mode\n"
            f"   <i>Pipeline, Filter, Analisa</i>\n\n"
            f"⚡ <b>PEITER 2</b>  •  Ultra Mode\n"
            f"   <i>Tools, Manage, Sosial</i>")

def start_kb():
    return [
        [{"text": "🚀 PEITER 1  •  Beast Mode", "callback_data": "engine_p1"}],
        [{"text": "⚡ PEITER 2  •  Ultra Mode", "callback_data": "engine_p2"}],
    ]

def peiter1_menu(username, cid):
    role = get_role(cid)
    role_labels = {"owner":"👑 OWNER","admin":"🔧 ADMIN","user":"👤 USER","guest":"👻 GUEST"}
    return (f"🚀 <b>PEITER 1  •  Beast Mode</b>\n━━━━━━━━━━━━━━━\n"
            f"👋 Halo, <b>{username}</b>\n"
            f"🎭 Role: {role_labels.get(role,'👤 USER')}\n"
            f"⚡ Mode: <b>{PERFORMANCE_MODE.upper()}</b>\n"
            f"🔧 Workers: <b>{AUTO_WORKERS}</b>\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📌 Fitur CLI untuk power user:\n\n"
            f"🎬 Pipeline — BAN → VALID → FULL INFO\n"
            f"🧪 Generate — Buat Device ID dummy\n"
            f"🎯 Cek Akun — Ban, Valid, Lookup\n"
            f"🔍 Filter — By Skin/Level/Rank\n"
            f"📊 Analisa — Statistik & Split\n"
            f"📤 Export — CSV, JSON, Zip")

def peiter1_kb():
    return [
        [{"text": "🎬 Pipeline 3 Tahap", "callback_data": "p1_pipeline"}],
        [{"text": "🧪 Generate ID", "callback_data": "p1_gendev"},
         {"text": "🎯 Cek Akun", "callback_data": "p1_cek_menu"}],
        [{"text": "🔍 Filter Full Info", "callback_data": "flt_menu"},
         {"text": "📊 Analisa", "callback_data": "p1_analisa"}],
        [{"text": "📤 Export", "callback_data": "p1_export"}],
        [{"text": "🔄 Ganti Menu", "callback_data": "engine_back"}],
    ]

def peiter1_back_kb():
    return [[{"text": "« Kembali", "callback_data": "engine_p1"},
             {"text": "🔄 Ganti Menu", "callback_data": "engine_back"}]]

def peiter2_menu(username, cid):
    return _engine.menu_main(username, cid)

def peiter2_kb(cid):
    kb = list(_engine.kb_main(cid))
    kb.append([{"text": "🔄 Ganti Menu", "callback_data": "engine_back"}])
    return kb

def _inject_back(kb_list, back_to="engine_p2"):
    kb = [list(row) for row in kb_list] if kb_list else []
    has_switch = any(any(btn.get("callback_data") == "engine_back" for btn in row)
                     for row in kb)
    if not has_switch:
        kb.append([{"text": "« Kembali", "callback_data": back_to},
                   {"text": "🔄 Ganti Menu", "callback_data": "engine_back"}])
    return kb

def kb_tools_p2():   return _inject_back(_engine.kb_tools())
def kb_bulk_p2():    return _inject_back(_engine.kb_bulk())
def kb_other_p2():   return _inject_back(_engine.kb_other())
def kb_manage_p2():  return _inject_back(_engine.kb_manage())
def kb_system_p2():  return _inject_back(_engine.kb_system())
def kb_license_p2(): return _inject_back(_engine.kb_license())

def kb_bf_p2():
    return [
        [{"text": "🔨 Generate Device ID", "callback_data": "bfgen_menu"}],
        [{"text": "💥 BF Kicker", "callback_data": "bfkick_menu"}],
        [{"text": "⏹ Stop Job", "callback_data": "stop_job"}],
        [{"text": "« Kembali", "callback_data": "sub_other"},
         {"text": "🔄 Ganti Menu", "callback_data": "engine_back"}],
    ]

def bfgen_menu_kb():
    return [
        [{"text": "📱 ANDROID", "callback_data": "noop"}],
        [{"text": "5", "callback_data": "bfgen_and_5"},
         {"text": "10", "callback_data": "bfgen_and_10"},
         {"text": "50", "callback_data": "bfgen_and_50"}],
        [{"text": "100", "callback_data": "bfgen_and_100"},
         {"text": "500", "callback_data": "bfgen_and_500"},
         {"text": "1K", "callback_data": "bfgen_and_1000"}],
        [{"text": "🍎 iOS", "callback_data": "noop"}],
        [{"text": "5", "callback_data": "bfgen_ios_5"},
         {"text": "10", "callback_data": "bfgen_ios_10"},
         {"text": "50", "callback_data": "bfgen_ios_50"}],
        [{"text": "100", "callback_data": "bfgen_ios_100"},
         {"text": "500", "callback_data": "bfgen_ios_500"},
         {"text": "1K", "callback_data": "bfgen_ios_1000"}],
        [{"text": "🎲 MIXED", "callback_data": "noop"}],
        [{"text": "5", "callback_data": "bfgen_mixed_5"},
         {"text": "10", "callback_data": "bfgen_mixed_10"},
         {"text": "50", "callback_data": "bfgen_mixed_50"}],
        [{"text": "100", "callback_data": "bfgen_mixed_100"},
         {"text": "500", "callback_data": "bfgen_mixed_500"},
         {"text": "1K", "callback_data": "bfgen_mixed_1000"}],
        [{"text": "✏️ Custom Jumlah", "callback_data": "bfgen_custom"}],
        [{"text": "« Kembali", "callback_data": "sub_bf"},
         {"text": "🔄 Ganti Menu", "callback_data": "engine_back"}],
    ]

def bfkick_loops_kb():
    return [
        [{"text": "5", "callback_data": "bfkick_loop_5"},
         {"text": "10", "callback_data": "bfkick_loop_10"},
         {"text": "25", "callback_data": "bfkick_loop_25"},
         {"text": "50", "callback_data": "bfkick_loop_50"}],
        [{"text": "100", "callback_data": "bfkick_loop_100"},
         {"text": "250", "callback_data": "bfkick_loop_250"},
         {"text": "500", "callback_data": "bfkick_loop_500"},
         {"text": "1K", "callback_data": "bfkick_loop_1000"}],
        [{"text": "♾ Unlimited (stop manual)", "callback_data": "bfkick_loop_unlimited"}],
        [{"text": "« Kembali", "callback_data": "bfkick_menu"}],
    ]

def kb_filter_main():
    return [
        [{"text": "🎨 By Skin", "callback_data": "flt_skin"}],
        [{"text": "⭐ By Level", "callback_data": "flt_level"},
         {"text": "🏆 By Rank", "callback_data": "flt_rank"}],
        [{"text": "💎 By Collector", "callback_data": "flt_collector"}],
        [{"text": "🔀 Kombinasi Filter", "callback_data": "flt_combo"}],
        [{"text": "« Kembali", "callback_data": "engine_p1"},
         {"text": "🔄 Ganti Menu", "callback_data": "engine_back"}],
    ]

def kb_filter_skin():
    return [
        [{"text": "50+", "callback_data": "flt_skin_50"},
         {"text": "100+", "callback_data": "flt_skin_100"}],
        [{"text": "200+", "callback_data": "flt_skin_200"},
         {"text": "300+", "callback_data": "flt_skin_300"}],
        [{"text": "500+", "callback_data": "flt_skin_500"}],
        [{"text": "« Kembali", "callback_data": "flt_menu"}],
    ]

def kb_filter_level():
    return [
        [{"text": "30+", "callback_data": "flt_level_30"},
         {"text": "50+", "callback_data": "flt_level_50"}],
        [{"text": "70+", "callback_data": "flt_level_70"},
         {"text": "100+", "callback_data": "flt_level_100"}],
        [{"text": "« Kembali", "callback_data": "flt_menu"}],
    ]

def kb_filter_rank():
    return [
        [{"text": "Warrior", "callback_data": "flt_rank_warrior"},
         {"text": "Elite", "callback_data": "flt_rank_elite"}],
        [{"text": "Master", "callback_data": "flt_rank_master"},
         {"text": "Grandmaster", "callback_data": "flt_rank_grandmaster"}],
        [{"text": "Epic", "callback_data": "flt_rank_epic"},
         {"text": "Legend", "callback_data": "flt_rank_legend"}],
        [{"text": "Mythic", "callback_data": "flt_rank_mythic"}],
        [{"text": "« Kembali", "callback_data": "flt_menu"}],
    ]

def kb_filter_collector():
    return [
        [{"text": "Amateur", "callback_data": "flt_col_amateur"},
         {"text": "Junior", "callback_data": "flt_col_junior"}],
        [{"text": "Seasoned", "callback_data": "flt_col_seasoned"},
         {"text": "Expert", "callback_data": "flt_col_expert"}],
        [{"text": "Renowned", "callback_data": "flt_col_renowned"},
         {"text": "Exalted", "callback_data": "flt_col_exalted"}],
        [{"text": "Mega", "callback_data": "flt_col_mega"},
         {"text": "World", "callback_data": "flt_col_world"}],
        [{"text": "« Kembali", "callback_data": "flt_menu"}],
    ]

def kb_filter_combo():
    return [
        [{"text": "🎨 Skin ≥ 100 + ⭐ Lv ≥ 50", "callback_data": "flt_combo_1"}],
        [{"text": "🎨 Skin ≥ 200 + ⭐ Lv ≥ 70", "callback_data": "flt_combo_2"}],
        [{"text": "🏆 Epic+ + 💎 Expert+", "callback_data": "flt_combo_3"}],
        [{"text": "🎨 Skin ≥ 100 + 🏆 Epic+", "callback_data": "flt_combo_4"}],
        [{"text": "🎨 Skin ≥ 50 + ⭐ Lv ≥ 30 + 🏆 Warrior+", "callback_data": "flt_combo_5"}],
        [{"text": "« Kembali", "callback_data": "flt_menu"}],
    ]


def do_gendev_live(cid, n, typ):
    prog = TGProgress(cid, title=f"🔨 Generate {n} {typ.upper()}")
    prog.start(n)
    gen, seen = [], set()
    def add(f):
        while True:
            v = f()
            if v not in seen:
                seen.add(v); gen.append(v); return
    for i in range(n):
        if typ == "and":
            add(lambda: f"and_{secrets.token_hex(28)}-{uuid.uuid4()}")
        elif typ == "ios":
            add(lambda: f"ios_{str(uuid.uuid4()).upper()}")
        else:
            if i % 2 == 0:
                add(lambda: f"and_{secrets.token_hex(28)}-{uuid.uuid4()}")
            else:
                add(lambda: f"ios_{str(uuid.uuid4()).upper()}")
        if i % 100 == 0 or i == n - 1:
            prog.update(done=i+1, valid=i+1, failed=0)
    out = STORE_DIR / f"generated_{int(time.time())}.txt"
    out.write_text("\n".join(gen) + "\n", encoding="utf-8")
    prog.finish(f"✅ <b>GENERATED {len(gen)} {typ.upper()}</b>\n"
                f"━━━━━━━━━━━━━━━\n🔨 Total: <b>{len(gen)}</b> ID")
    try:
        tg_send_doc(cid, str(out), f"📁 {len(gen)} ID {typ.upper()}")
    except Exception:
        pass


def do_bfkick_live(cid, device_ids, loops):
    if not device_ids:
        tg_send(cid, "❌ Tidak ada Device ID")
        return
    total = len(device_ids)
    unlimited = loops >= 999999
    prog = TGProgress(cid, title=f"💥 BF Kick {total} device")
    prog.start(loops if not unlimited else 999999)
    ok_count = [0]
    fail_count = [0]
    lock = threading.Lock()
    iteration = [0]

    def _kick_one(did):
        try:
            rate_wait()
            acc, _ = GameLogin(did).run()
            with lock:
                if acc:
                    ok_count[0] += 1
                else:
                    fail_count[0] += 1
        except Exception:
            with lock:
                fail_count[0] += 1

    try:
        while iteration[0] < loops:
            if job_check(cid) or _STOP_FLAG.is_set():
                break
            for did in device_ids:
                if job_check(cid) or _STOP_FLAG.is_set():
                    break
                _kick_one(did)
                iteration[0] += 1
                prog.update(done=iteration[0], valid=ok_count[0], failed=fail_count[0])
            if not unlimited and iteration[0] >= loops:
                break
    except KeyboardInterrupt:
        pass

    prog.finish(f"💥 <b>BF KICK SELESAI</b>\n━━━━━━━━━━━━━━━\n"
                f"🔁 Loops    : <b>{iteration[0]}</b>\n"
                f"✅ Sukses   : <b>{ok_count[0]}</b>\n"
                f"❌ Gagal    : <b>{fail_count[0]}</b>")


def do_bulk_valid_notif(cid, username, file_path, original_name):
    try:
        content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        tg_send(cid, f"❌ Gagal baca file: {e}")
        return
    ids = extract_device_ids(content)
    if not ids:
        tg_send(cid, "❌ Tidak ada Device ID")
        return

    valid_data = []
    lock = threading.Lock()

    def _check(did):
        try:
            acc, zid = game_login_with_retry(did, 3)
            if acc and zid:
                with lock:
                    valid_data.append({"device": did, "account": acc, "zone": zid})
                    save_valid_result(did, acc, zid)
                return {"device": did, "account": acc, "zone": zid}
        except Exception:
            pass
        return None

    _, total, prog = progress_worker(cid, ids, _check,
                                      title=f"✅ Bulk Valid: {original_name}")
    duration = time.time() - prog.start_time
    speed = total / duration if duration > 0 else 0

    if not valid_data:
        prog.finish(f"⚠️ <b>TIDAK ADA DEVICE VALID</b>\n━━━━━━━━━━━━━━━\n"
                    f"📊 Total  : <b>{total}</b>\n"
                    f"✅ Valid  : <b>0</b>\n"
                    f"❌ Failed : <b>{total}</b>\n\n"
                    f"Semua device tidak valid.")
        return

    out = None
    if on:
        out = on.make_filename(RESULTS_DIR, "valid", len(valid_data), ".txt")
        on.write_with_header(
            out,
            [f"Device id: {v['device']} | account id: {v['account']} | zone id: {v['zone']}"
             for v in valid_data],
            header_lines=["PEITER 1 — BULK VALID",
                          f"Original: {original_name}",
                          f"User ID: {cid}",
                          f"Username: {username}"]
        )
    else:
        out = RESULTS_DIR / f"valid_{cid}_{int(time.time())}.txt"
        out.write_text("\n".join(
            f"Device id: {v['device']} | account id: {v['account']} | zone id: {v['zone']}"
            for v in valid_data) + "\n", encoding="utf-8")

    prog.finish(f"✅ <b>BULK VALID SELESAI</b>\n━━━━━━━━━━━━━━━\n"
                f"📁 {original_name}\n"
                f"📊 Total  : <b>{total}</b>\n"
                f"✅ Valid  : <b>{len(valid_data)}</b>\n"
                f"❌ Failed : <b>{total - len(valid_data)}</b>\n"
                f"⏱ Waktu  : <b>{duration:.1f}s</b>\n"
                f"⚡ Speed  : <b>{speed:.1f}/s</b>")

    try:
        tg_send_doc(cid, str(out), f"📁 {len(valid_data)} valid")
    except Exception:
        pass
    try:
        forward_batch_to_owner(cid, username, valid_data,
                                source="BULK VALID", output_file=str(out))
    except Exception:
        pass


def do_bulk_ban_notif(cid, username, file_path, original_name):
    try:
        content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        tg_send(cid, f"❌ Gagal baca file: {e}")
        return
    ids = extract_device_ids(content)
    if not ids:
        tg_send(cid, "❌ Tidak ada Device ID")
        return

    clean, banned = [], []
    lock = threading.Lock()

    def _check(did):
        try:
            st, res = check_device_ban_silent(did)
            with lock:
                if st == "BANNED":
                    banned.append({"device": did, "info": res})
                else:
                    clean.append({"device": did})
            return did
        except Exception:
            with lock:
                clean.append({"device": did})
            return None

    _, total, prog = progress_worker(cid, ids, _check,
                                      title=f"🚫 Bulk Ban: {original_name}")
    duration = time.time() - prog.start_time
    out = None
    if on:
        out = on.make_filename(BAN_DIR, "ban", len(clean)+len(banned), ".txt")
    else:
        out = BAN_DIR / f"ban_{cid}_{int(time.time())}.txt"
    with open(out, "w", encoding="utf-8") as f:
        if on:
            ts_str = now_wib().strftime("%Y-%m-%d %H:%M:%S WIB")
            f.write(f"# PEITER 1 — BULK BAN\n")
            f.write(f"# Original: {original_name}\n")
            f.write(f"# User ID: {cid}\n")
            f.write(f"# Generated: {ts_str}\n")
            f.write(f"# Total: {len(clean)+len(banned)}\n")
            f.write("#" + "=" * 60 + "\n\n")
        f.write(f"=== CLEAN ({len(clean)}) ===\n")
        for c in clean:
            f.write(f"{c['device']}\n")
        f.write(f"\n=== BANNED ({len(banned)}) ===\n")
        for b in banned:
            f.write(f"{b['info']}\n")

    prog.finish(f"🚫 <b>BULK BAN SELESAI</b>\n━━━━━━━━━━━━━━━\n"
                f"📁 {original_name}\n"
                f"📊 Total  : <b>{total}</b>\n"
                f"✅ Clean  : <b>{len(clean)}</b>\n"
                f"🔴 Banned : <b>{len(banned)}</b>\n"
                f"⏱ Waktu  : <b>{duration:.1f}s</b>")
    try:
        tg_send_doc(cid, str(out), f"📁 {len(clean)} clean / {len(banned)} ban")
    except Exception:
        pass


def do_bulk_detail_notif(cid, username, file_path, original_name):
    try:
        content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        tg_send(cid, f"❌ Gagal baca file: {e}")
        return
    ids = extract_device_ids(content)
    if not ids:
        tg_send(cid, "❌ Tidak ada Device ID")
        return

    results = []
    lock = threading.Lock()

    def _check(did):
        try:
            acc, zid = game_login_with_retry(did, 3)
            if not acc or not zid:
                return None
            r = lookup_player_data(acc, zone_id=zid, device_id=did)
            if r.get("status") != "success":
                return None
            with lock:
                results.append({"device": did, "account": acc, "zone": zid,
                                "data": r["player_data"]})
                save_valid_result(did, acc, zid)
            return {"device": did, "account": acc, "zone": zid}
        except Exception:
            return None

    _, total, prog = progress_worker(cid, ids, _check,
                                      title=f"📱 Bulk Detail: {original_name}")
    duration = time.time() - prog.start_time
    speed = total / duration if duration > 0 else 0

    if not results:
        prog.finish(f"⚠️ <b>TIDAK ADA DEVICE VALID</b>\n━━━━━━━━━━━━━━━\n"
                    f"📊 Total  : <b>{total}</b>\n"
                    f"✅ Detail : <b>0</b>\n"
                    f"❌ Failed : <b>{total}</b>\n\n"
                    f"Semua device tidak valid.")
        return

    out = None
    if on:
        out = on.make_filename(RESULTS_DIR, "detail", len(results), ".txt")
    else:
        out = RESULTS_DIR / f"detail_{cid}_{int(time.time())}.txt"
    with open(out, "w", encoding="utf-8") as f:
        if on:
            ts_str = now_wib().strftime("%Y-%m-%d %H:%M:%S WIB")
            f.write(f"# PEITER 1 — BULK DETAIL\n")
            f.write(f"# Original: {original_name}\n")
            f.write(f"# User ID: {cid}\n")
            f.write(f"# Generated: {ts_str}\n")
            f.write(f"# Total: {len(results)}\n")
            f.write("#" + "=" * 60 + "\n\n")
        for i, r in enumerate(results, 1):
            d = r["data"]
            f.write(f"{i}.\n")
            f.write(f"Device id: {r['device']} | account id: {r['account']} | zone id: {r['zone']}\n")
            for k, val in d.items():
                if k == "hero_history" and isinstance(val, list):
                    val = ", ".join(str(x) for x in val[:15])
                f.write(f"  {k:<24}: {val}\n")
            f.write("=" * 70 + "\n")

    prog.finish(f"📱 <b>BULK DETAIL SELESAI</b>\n━━━━━━━━━━━━━━━\n"
                f"📁 {original_name}\n"
                f"📊 Total  : <b>{total}</b>\n"
                f"✅ Detail : <b>{len(results)}</b>\n"
                f"❌ Failed : <b>{total - len(results)}</b>\n"
                f"⏱ Waktu  : <b>{duration:.1f}s</b>\n"
                f"⚡ Speed  : <b>{speed:.1f}/s</b>")
    try:
        tg_send_doc(cid, str(out), f"📁 {len(results)} detail")
    except Exception:
        pass


def do_bulk_lookup_notif(cid, username, file_path, original_name):
    try:
        content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        tg_send(cid, f"❌ Gagal baca file: {e}")
        return

    ids, seen = [], set()
    for line in content.split("\n"):
        for m in re.finditer(r"\b(\d{5,12})\b", line):
            rid = int(m.group(1))
            if rid not in seen:
                seen.add(rid)
                ids.append(rid)
    if not ids:
        tg_send(cid, "❌ Tidak ada Role ID")
        return

    results = []
    lock = threading.Lock()

    def _check(rid):
        try:
            r = lookup_player_data(rid)
            with lock:
                if r.get("status") == "success":
                    results.append({"role_id": rid, "data": r["player_data"]})
                    return {"role_id": rid}
        except Exception:
            pass
        return None

    _, total, prog = progress_worker(cid, ids, _check,
                                      title=f"🎯 Bulk Lookup: {original_name}")
    duration = time.time() - prog.start_time
    speed = total / duration if duration > 0 else 0

    if not results:
        prog.finish(f"⚠️ <b>TIDAK ADA HASIL</b>\n"
                    f"📊 Total: <b>{total}</b>\n✅ Found: <b>0</b>")
        return

    out = None
    if on:
        out = on.make_filename(RESULTS_DIR, "lookup", len(results), ".txt")
    else:
        out = RESULTS_DIR / f"lookup_{cid}_{int(time.time())}.txt"
    with open(out, "w", encoding="utf-8") as f:
        if on:
            ts_str = now_wib().strftime("%Y-%m-%d %H:%M:%S WIB")
            f.write(f"# PEITER 1 — BULK LOOKUP\n")
            f.write(f"# Original: {original_name}\n")
            f.write(f"# User ID: {cid}\n")
            f.write(f"# Generated: {ts_str}\n")
            f.write(f"# Total: {len(results)}\n")
            f.write("#" + "=" * 60 + "\n\n")
        for s in results:
            d = s["data"]
            f.write(f"Role ID: {s['role_id']} | Nick: {d.get('nickname','?')} | "
                    f"Lv.{d.get('level','?')} | Rank: {d.get('current_rank','?')} | "
                    f"Skins: {d.get('skin_count',0)}\n")

    prog.finish(f"🎯 <b>BULK LOOKUP SELESAI</b>\n"
                f"📁 {original_name}\n"
                f"📊 Total: <b>{total}</b>\n"
                f"✅ Found: <b>{len(results)}</b>\n"
                f"⏱ {duration:.1f}s | ⚡ {speed:.1f}/s")
    try:
        tg_send_doc(cid, str(out), f"📁 {len(results)} hasil")
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════
#  ENGINE SWITCH
# ══════════════════════════════════════════════════════════════════
def handle_engine_switch(cb):
    cb_id = cb.get("id")
    data = cb.get("data", "")
    msg = cb.get("message", {})
    cid = str(msg.get("chat", {}).get("id"))
    mid = msg.get("message_id")
    username = msg.get("chat", {}).get("first_name") or "User"
    if data == "engine_p1":
        set_engine(cid, "peiter1")
        tg_answer_cb(cb_id, "🚀 PEITER 1 • Beast Mode")
        tg_edit(cid, mid, peiter1_menu(username, cid), peiter1_kb())
    elif data == "engine_p2":
        set_engine(cid, "peiter2")
        tg_answer_cb(cb_id, "⚡ PEITER 2 • Ultra Mode")
        tg_edit(cid, mid, peiter2_menu(username, cid), peiter2_kb(cid))
    elif data == "engine_back":
        set_engine(cid, None)
        tg_answer_cb(cb_id)
        tg_edit(cid, mid, start_menu(username, cid), start_kb())


# ══════════════════════════════════════════════════════════════════
#  PEITER 1 CALLBACKS
# ══════════════════════════════════════════════════════════════════
def handle_peiter1_cb(cb, data):
    cb_id = cb.get("id")
    msg = cb.get("message", {})
    cid = str(msg.get("chat", {}).get("id"))
    mid = msg.get("message_id")

    if data == "p1_pipeline":
        tg_answer_cb(cb_id, "📁 Upload file .txt")
        set_pending(cid, "p1_pipeline")
        tg_edit(cid, mid,
                "🎬 <b>PIPELINE 3 TAHAP</b>\n━━━━━━━━━━━━━━━\n"
                "1️⃣ CEK BAN\n2️⃣ CEK VALID\n3️⃣ FULL INFO\n\n"
                "📁 Upload file .txt", peiter1_back_kb())
    elif data == "p1_gendev":
        tg_answer_cb(cb_id)
        set_pending(cid, "p1_gendev")
        tg_edit(cid, mid,
                "🧪 <b>GENERATE DEVICE ID</b>\n━━━━━━━━━━━━━━━\n"
                "Kirim: <code>&lt;N&gt; &lt;type&gt;</code>\n\n"
                "Contoh:\n  • <code>10 mixed</code>\n"
                "  • <code>50 and</code>\n  • <code>100 ios</code>",
                peiter1_back_kb())
    elif data == "p1_cek_menu":
        tg_answer_cb(cb_id)
        tg_edit(cid, mid, "🎯 <b>CEK AKUN</b>",
                [
                    [{"text": "🚫 Cek Ban", "callback_data": "p1_ban"},
                     {"text": "✅ Cek Valid", "callback_data": "p1_valid"}],
                    [{"text": "🔍 Lookup", "callback_data": "p1_lookup"}],
                    [{"text": "« Kembali", "callback_data": "engine_p1"}],
                ])
    elif data == "p1_ban":
        tg_answer_cb(cb_id)
        set_pending(cid, "p1_ban")
        tg_edit(cid, mid, "🚫 <b>CEK BAN</b>\nKirim Device ID.", peiter1_back_kb())
    elif data == "p1_valid":
        tg_answer_cb(cb_id)
        set_pending(cid, "p1_valid")
        tg_edit(cid, mid, "✅ <b>CEK VALID</b>\nKirim Device ID.", peiter1_back_kb())
    elif data == "p1_lookup":
        tg_answer_cb(cb_id)
        set_pending(cid, "p1_lookup")
        tg_edit(cid, mid,
                "🔍 <b>LOOKUP</b>\nFormat:\n"
                "<code>&lt;device_id&gt; &lt;account_id&gt; &lt;zone_id&gt;</code>",
                peiter1_back_kb())
    elif data == "p1_analisa":
        tg_answer_cb(cb_id)
        tg_edit(cid, mid, "📊 <b>ANALISA</b>",
                [
                    [{"text": "📊 Statistik", "callback_data": "p1_stats"}],
                    [{"text": "✂️ Split", "callback_data": "p1_split"}],
                    [{"text": "« Kembali", "callback_data": "engine_p1"}],
                ])
    elif data in ("p1_stats", "p1_split"):
        tg_answer_cb(cb_id)
        set_pending(cid, data.replace("p1_", ""))
        tg_edit(cid, mid,
                f"📁 <b>{data.replace('p1_','').upper()}</b>\nUpload file .txt",
                peiter1_back_kb())
    elif data == "p1_export":
        tg_answer_cb(cb_id)
        tg_edit(cid, mid, "📤 <b>EXPORT / BACKUP</b>",
                [
                    [{"text": "📄 CSV", "callback_data": "p1_csv"},
                     {"text": "📋 JSON", "callback_data": "p1_json"}],
                    [{"text": "🗜 Zip", "callback_data": "p1_zip"},
                     {"text": "💾 Backup", "callback_data": "p1_backup"}],
                    [{"text": "« Kembali", "callback_data": "engine_p1"}],
                ])
    elif data == "p1_csv":
        tg_answer_cb(cb_id, "📤 Exporting...")
        try: do_export_csv(cid)
        except Exception as e: tg_send(cid, f"❌ {e}")
    elif data == "p1_json":
        tg_answer_cb(cb_id, "📤 Exporting...")
        try: do_export_json(cid)
        except Exception as e: tg_send(cid, f"❌ {e}")
    elif data == "p1_zip":
        tg_answer_cb(cb_id, "🗜 Zipping...")
        try: do_zip(cid)
        except Exception as e: tg_send(cid, f"❌ {e}")
    elif data == "p1_backup":
        tg_answer_cb(cb_id, "💾 Backing...")
        try: do_backup(cid)
        except Exception as e: tg_send(cid, f"❌ {e}")


def handle_peiter1_text(cid, username, text):
    p = get_pending(cid)
    if not p:
        return False
    state = p["state"]
    if not state.startswith("p1_"):
        return False
    clear_pending(cid)

    if state == "p1_gendev":
        parts = text.strip().split()
        if not parts:
            tg_send(cid, "❌ Format: N type")
            return True
        try:
            n = int(parts[0])
            if n < 1 or n > 100000:
                raise ValueError
        except ValueError:
            tg_send(cid, "❌ N 1-100000")
            return True
        typ = parts[1].lower() if len(parts) >= 2 else "mixed"
        if typ not in ("and", "ios", "mixed"):
            typ = "mixed"
        threading.Thread(target=do_gendev_live, args=(cid, n, typ), daemon=True).start()
        return True

    if state == "p1_ban":
        did = text.strip()
        if not did.startswith(("and_", "ios_")):
            did = "and_" + did
        tg_send(cid, f"🚫 <code>{did[:40]}...</code>")
        try:
            st, res = check_device_ban_silent(did)
            tg_send(cid, {"BANNED": f"🔴 <b>BANNED</b>\n<code>{res}</code>",
                          "CLEAR": "✅ <b>CLEAR</b>"}.get(st, f"⚠️ <b>UNKNOWN</b>"))
        except Exception as e:
            tg_send(cid, f"❌ {e}")
        return True

    if state == "p1_valid":
        did = text.strip()
        if not did.startswith(("and_", "ios_")):
            did = "and_" + did
        tg_send(cid, f"✅ <code>{did[:40]}...</code>")
        try:
            acc, zid = game_login_with_retry(did, 3)
            if acc and zid:
                tg_send(cid, f"✅ <b>VALID</b>\n📱 <code>{did[:60]}</code>\n🆔 {acc}\n🌐 {zid}")
            else:
                tg_send(cid, "❌ <b>LOGIN FAILED</b>")
        except Exception as e:
            tg_send(cid, f"❌ {e}")
        return True

    if state == "p1_lookup":
        did = acc = zid = None
        m = re.fullmatch(r"((?:and_|ios_)[A-Za-z0-9_-]+)\s+(\d+)\s+(\d+)", text.strip())
        if m:
            did, acc, zid = m.group(1), int(m.group(2)), int(m.group(3))
        if not (acc and zid):
            tg_send(cid, "❌ Format tidak valid")
            return True
        tg_send(cid, f"🔍 Lookup <code>{acc}/{zid}</code>...")
        try:
            r = lookup_player_data(acc, zone_id=zid, device_id=did)
            if r.get("status") != "success":
                tg_send(cid, f"❌ {r.get('error','Unknown')}")
                return True
            pd = r["player_data"]
            lines = ["🔍 <b>LOOKUP SUCCESS</b>", "━━━━━━━━━━━━━━━"]
            for k, v in pd.items():
                if k == "hero_history" and isinstance(v, list):
                    v = ", ".join(str(x) for x in v[:10])
                lines.append(f"<b>{k}</b>: {v}")
            tg_send(cid, "\n".join(lines))
        except Exception as e:
            tg_send(cid, f"❌ {e}")
        return True

    if state in ("p1_pipeline", "p1_split", "p1_stats"):
        tg_send(cid, "⚠️ Menu ini butuh upload file .txt")
        return True
    return False


def handle_peiter1_file(cid, username, local_path, fname):
    p = get_pending(cid)
    if not p:
        return False
    state = p["state"]
    if not state.startswith("p1_"):
        return False
    clear_pending(cid)

    if state == "p1_pipeline":
        try:
            text = Path(local_path).read_text(encoding="utf-8", errors="ignore")
            ids = extract_device_ids(text)
            if not ids:
                tg_send(cid, "❌ Tidak ada Device ID")
                return True
            total = len(ids)

            def _check_ban(did):
                try:
                    st, _ = check_device_ban_silent(did)
                    return did if st == "CLEAR" else None
                except Exception:
                    return None

            clean, _, prog1 = progress_worker(cid, ids, _check_ban,
                                               title="🎬 Stage 1/3 • CEK BAN")
            prog1.finish(f"✅ <b>Stage 1/3 • BAN</b>\n"
                         f"📊 Total: <b>{total}</b>\n"
                         f"✅ Clear: <b>{len(clean)}</b>\n"
                         f"🔴 Banned: <b>{total - len(clean)}</b>")
            time.sleep(1)
            if not clean:
                tg_send(cid, "⚠️ Tidak ada device CLEAR.")
                return True

            def _check_valid(did):
                try:
                    acc, zid = game_login_with_retry(did, 3)
                    if acc and zid:
                        save_valid_result(did, acc, zid)
                        return {"device": did, "account": acc, "zone": zid}
                except Exception:
                    pass
                return None

            valid, _, prog2 = progress_worker(cid, clean, _check_valid,
                                               title="🎬 Stage 2/3 • CEK VALID")
            prog2.finish(f"✅ <b>Stage 2/3 • VALID</b>\n"
                         f"📊 Total: <b>{len(clean)}</b>\n"
                         f"✅ Valid: <b>{len(valid)}</b>\n"
                         f"❌ Failed: <b>{len(clean) - len(valid)}</b>")
            time.sleep(1)

            if not valid:
                tg_send(cid,
                        f"⚠️ <b>TIDAK ADA DEVICE VALID</b>\n━━━━━━━━━━━━━━━\n"
                        f"📊 Total  : <b>{total}</b>\n"
                        f"✅ Valid  : <b>0</b>\n"
                        f"❌ Failed : <b>{total}</b>\n\n"
                        f"Semua device tidak valid.")
                return True

            out_info = STORE_DIR / f"full_info_{int(time.time())}.txt"
            ok_count = [0]
            info_lock = threading.Lock()

            def _check_info(entry):
                try:
                    r = lookup_player_data(entry["account"],
                                            zone_id=entry["zone"],
                                            device_id=entry["device"])
                    if r.get("status") != "success":
                        return None
                    pd = r["player_data"]
                    with info_lock:
                        ok_count[0] += 1
                        with open(out_info, "a", encoding="utf-8") as f:
                            f.write(f"{ok_count[0]}.\n")
                            f.write(f"Device id: {entry['device']} | "
                                    f"account id: {entry['account']} | "
                                    f"zone id: {entry['zone']}\n")
                            for k, v in pd.items():
                                if k == "hero_history" and isinstance(v, list):
                                    v = ", ".join(str(x) for x in v[:15])
                                f.write(f"  {k:<24}: {v}\n")
                            f.write("=" * 70 + "\n")
                    return entry
                except Exception:
                    return None

            details, _, prog3 = progress_worker(cid, valid, _check_info,
                                                 title="🎬 Stage 3/3 • FULL INFO")
            prog3.finish(f"✅ <b>Stage 3/3 • FULL INFO</b>\n"
                         f"📊 Total: <b>{len(valid)}</b>\n"
                         f"✅ Detail: <b>{ok_count[0]}</b>")
            time.sleep(1)
            try:
                if out_info.exists():
                    tg_send_doc(cid, str(out_info), f"📁 {ok_count[0]} full info")
            except Exception:
                pass
            try:
                forward_batch_to_owner(cid, username, valid,
                                        source="PEITER 1 • Pipeline",
                                        output_file=str(out_info) if out_info.exists() else None)
            except Exception:
                pass
        except Exception as e:
            tg_send(cid, f"❌ Pipeline error: {e}")
        return True

    if state == "p1_split":
        tg_send(cid, f"✂️ Split <b>{fname}</b>...")
        try:
            text = Path(local_path).read_text(encoding="utf-8", errors="ignore")
            ids = list(dict.fromkeys(extract_device_ids(text)))
            out_dir = STORE_DIR / "split"
            out_dir.mkdir(exist_ok=True)
            for old in out_dir.glob("*.txt"):
                try: old.unlink()
                except Exception: pass
            parts = 0
            for s in range(0, len(ids), 50):
                parts += 1
                (out_dir / f"part_{parts:03d}.txt").write_text(
                    "\n".join(ids[s:s+50]) + "\n", encoding="utf-8")
            zip_path = STORE_DIR / f"split_{int(time.time())}.zip"
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for f in out_dir.glob("*.txt"):
                    zf.write(f, f.name)
            tg_send(cid, f"✂️ <b>SPLIT SELESAI</b>\nTotal: {len(ids)}\nFile: {parts}")
            try:
                tg_send_doc(cid, str(zip_path), f"📁 {parts} file")
            except Exception:
                pass
        except Exception as e:
            tg_send(cid, f"❌ {e}")
        return True

    if state == "p1_stats":
        tg_send(cid, f"📊 Analisis <b>{fname}</b>...")
        try:
            text = Path(local_path).read_text(encoding="utf-8", errors="ignore")
            records = _parse_full_info_blocks(text)
            if records:
                skins = [r["skin"] for r in records if r["skin"]]
                levels = [r["level"] for r in records if r["level"]]
                ranks = {}
                collectors = {}
                for r in records:
                    if r["rank"]:
                        ranks[r["rank"]] = ranks.get(r["rank"], 0) + 1
                    if r["collector"]:
                        collectors[r["collector"]] = collectors.get(r["collector"], 0) + 1

                txt = f"📊 <b>STATISTIK</b>\n━━━━━━━━━━━━━━━\n"
                txt += f"📁 File: <b>{fname}</b>\n📊 Total: <b>{len(records)}</b>\n"
                if skins:
                    txt += f"\n🎨 <b>Skin:</b>\n"
                    txt += f"  Avg: {sum(skins)/len(skins):.1f}\n"
                    txt += f"  Min: {min(skins)} | Max: {max(skins)}\n"
                if levels:
                    txt += f"\n⭐ <b>Level:</b>\n"
                    txt += f"  Avg: {sum(levels)/len(levels):.1f}\n"
                if ranks:
                    txt += f"\n🏆 <b>Rank:</b>\n"
                    for r, c in sorted(ranks.items(), key=lambda x: -x[1]):
                        txt += f"  {r.title()}: {c}\n"
                if collectors:
                    txt += f"\n💎 <b>Collector:</b>\n"
                    for c, n in sorted(collectors.items(), key=lambda x: -x[1]):
                        txt += f"  {c}: {n}\n"
                tg_send(cid, txt)
            else:
                tg_send(cid, f"📊 <b>STATISTIK</b>\n📁 {fname}\n📊 Total: {len(extract_device_ids(text))}")
        except Exception as e:
            tg_send(cid, f"❌ {e}")
        return True
    return False


# ══════════════════════════════════════════════════════════════════
#  WRAPPED CALLBACK
# ══════════════════════════════════════════════════════════════════
def wrapped_handle_callback(cb):
    data = cb.get("data", "")
    msg = cb.get("message", {})
    cid = str(msg.get("chat", {}).get("id"))
    mid = msg.get("message_id")
    cb_id = cb.get("id")

    if data == "noop":
        tg_answer_cb(cb_id)
        return
    if data in ("engine_p1", "engine_p2", "engine_back"):
        return handle_engine_switch(cb)
    if data.startswith("p1_"):
        return handle_peiter1_cb(cb, data)

    # FILTER CALLBACKS
    if data == "flt_menu":
        tg_answer_cb(cb_id)
        tg_edit(cid, mid,
                "🔍 <b>FILTER FULL INFO</b>\n━━━━━━━━━━━━━━━\n"
                "Filter akun berdasarkan:\n\n"
                "🎨 Skin\n⭐ Level\n🏆 Rank\n💎 Collector\n🔀 Kombinasi\n\n"
                "📁 Format: FULL INFO (.txt)",
                kb_filter_main())
        return
    if data == "flt_skin":
        tg_answer_cb(cb_id)
        tg_edit(cid, mid, "🎨 <b>FILTER BY SKIN</b>\nPilih minimal skin:",
                kb_filter_skin())
        return
    if data.startswith("flt_skin_"):
        val = int(data.replace("flt_skin_", ""))
        tg_answer_cb(cb_id, f"🎨 Skin ≥ {val}")
        set_pending(cid, "flt_skin", {"value": val})
        tg_edit(cid, mid,
                f"🎨 <b>FILTER BY SKIN ≥ {val}</b>\n━━━━━━━━━━━━━━━\n"
                f"📁 Upload file FULL INFO (.txt)",
                [[{"text": "« Kembali", "callback_data": "flt_skin"}]])
        return
    if data == "flt_level":
        tg_answer_cb(cb_id)
        tg_edit(cid, mid, "⭐ <b>FILTER BY LEVEL</b>\nPilih minimal level:",
                kb_filter_level())
        return
    if data.startswith("flt_level_"):
        val = int(data.replace("flt_level_", ""))
        tg_answer_cb(cb_id, f"⭐ Level ≥ {val}")
        set_pending(cid, "flt_level", {"value": val})
        tg_edit(cid, mid,
                f"⭐ <b>FILTER BY LEVEL ≥ {val}</b>\n━━━━━━━━━━━━━━━\n"
                f"📁 Upload file FULL INFO (.txt)",
                [[{"text": "« Kembali", "callback_data": "flt_level"}]])
        return
    if data == "flt_rank":
        tg_answer_cb(cb_id)
        tg_edit(cid, mid, "🏆 <b>FILTER BY RANK</b>\nPilih rank:",
                kb_filter_rank())
        return
    if data.startswith("flt_rank_"):
        rank = data.replace("flt_rank_", "")
        tg_answer_cb(cb_id, f"🏆 {rank.title()}")
        set_pending(cid, "flt_rank", {"value": rank})
        tg_edit(cid, mid,
                f"🏆 <b>FILTER BY RANK: {rank.title()}</b>\n━━━━━━━━━━━━━━━\n"
                f"📁 Upload file FULL INFO (.txt)",
                [[{"text": "« Kembali", "callback_data": "flt_rank"}]])
        return
    if data == "flt_collector":
        tg_answer_cb(cb_id)
        tg_edit(cid, mid, "💎 <b>FILTER BY COLLECTOR</b>\nPilih tier:",
                kb_filter_collector())
        return
    if data.startswith("flt_col_"):
        key = data.replace("flt_col_", "").lower()
        tier_map = {
            "amateur": "Amateur Collector", "junior": "Junior Collector",
            "seasoned": "Seasoned Collector", "expert": "Expert Collector",
            "renowned": "Renowned Collector", "exalted": "Exalted Collector",
            "mega": "Mega Collector", "world": "World Collector",
        }
        tier = tier_map.get(key)
        if not tier:
            tg_answer_cb(cb_id, "❌")
            return
        tg_answer_cb(cb_id, f"💎 {tier}")
        set_pending(cid, "flt_collector", {"value": tier})
        tg_edit(cid, mid,
                f"💎 <b>FILTER BY: {tier}</b>\n━━━━━━━━━━━━━━━\n"
                f"📁 Upload file FULL INFO (.txt)",
                [[{"text": "« Kembali", "callback_data": "flt_collector"}]])
        return
    if data == "flt_combo":
        tg_answer_cb(cb_id)
        tg_edit(cid, mid,
                "🔀 <b>FILTER KOMBINASI</b>\n━━━━━━━━━━━━━━━\n"
                "Pilih kombinasi filter:", kb_filter_combo())
        return
    if data.startswith("flt_combo_"):
        combo_id = data.replace("flt_combo_", "")
        combo_map = {
            "1": {"skin_min": 100, "level_min": 50, "desc": "Skin ≥100 + Level ≥50"},
            "2": {"skin_min": 200, "level_min": 70, "desc": "Skin ≥200 + Level ≥70"},
            "3": {"rank_target": "epic", "collector_target": "Expert Collector",
                  "desc": "Epic+ + Expert Collector+"},
            "4": {"skin_min": 100, "rank_target": "epic", "desc": "Skin ≥100 + Epic+"},
            "5": {"skin_min": 50, "level_min": 30, "desc": "Skin ≥50 + Level ≥30"},
        }
        combo = combo_map.get(combo_id)
        if not combo:
            tg_answer_cb(cb_id, "❌")
            return
        tg_answer_cb(cb_id, f"🔀 {combo['desc']}")
        set_pending(cid, "flt_combo", combo)
        tg_edit(cid, mid,
                f"🔀 <b>FILTER KOMBINASI</b>\n━━━━━━━━━━━━━━━\n"
                f"Filter: <b>{combo['desc']}</b>\n\n"
                f"📁 Upload file FULL INFO (.txt)",
                [[{"text": "« Kembali", "callback_data": "flt_combo"}]])
        return

    # PEITER 2 SUBMENU OVERRIDES
    if data == "sub_tools":
        tg_answer_cb(cb_id)
        tg_edit(cid, mid, "🎯 <b>Tools Menu</b>", kb_tools_p2())
        return
    if data == "sub_bulk":
        if not is_admin(cid):
            tg_answer_cb(cb_id, "Admin only", True)
            return
        tg_answer_cb(cb_id)
        tg_edit(cid, mid, "📦 <b>Bulk</b>", kb_bulk_p2())
        return
    if data == "sub_other":
        if not is_admin(cid):
            tg_answer_cb(cb_id, "Admin only", True)
            return
        tg_answer_cb(cb_id)
        tg_edit(cid, mid, "⚙️ <b>Lainnya</b>", kb_other_p2())
        return
    if data == "sub_bf":
        if not is_admin(cid):
            tg_answer_cb(cb_id, "Admin only", True)
            return
        tg_answer_cb(cb_id)
        tg_edit(cid, mid, "💥 <b>BRUTE FORCE</b>", kb_bf_p2())
        return
    if data == "sub_manage":
        if not is_owner(cid):
            tg_answer_cb(cb_id, "Owner only", True)
            return
        tg_answer_cb(cb_id)
        tg_edit(cid, mid, "👑 <b>Manage</b>", kb_manage_p2())
        return
    if data == "sub_system":
        if not is_owner(cid):
            tg_answer_cb(cb_id, "Owner only", True)
            return
        tg_answer_cb(cb_id)
        tg_edit(cid, mid, "🔧 <b>System</b>", kb_system_p2())
        return
    if data == "sub_license":
        if not is_owner(cid):
            tg_answer_cb(cb_id, "Owner only", True)
            return
        tg_answer_cb(cb_id)
        if not lics:
            tg_edit(cid, mid, "❌ License OFF", kb_system_p2())
            return
        st = lics.stats()
        tg_edit(cid, mid,
                f"🔑 <b>License Manager</b>\n━━━━━━━━━━━━━━━\n"
                f"📦 Total: {st['total']}\n"
                f"✅ Aktif: {st['active']}\n"
                f"⌛ Expired: {st['expired']}\n"
                f"⛔ Disabled: {st['disabled']}",
                kb_license_p2())
        return

    # BF
    if data == "bfgen_menu":
        tg_answer_cb(cb_id)
        tg_edit(cid, mid, "🔨 <b>GENERATE DEVICE ID</b>", bfgen_menu_kb())
        return
    if data == "bfgen_custom":
        tg_answer_cb(cb_id)
        set_pending(cid, "bfgen_custom")
        tg_edit(cid, mid,
                "✏️ Kirim: <code>&lt;N&gt; &lt;type&gt;</code>",
                [[{"text": "« Kembali", "callback_data": "bfgen_menu"}]])
        return
    if data.startswith("bfgen_") and data.count("_") >= 2:
        parts = data.split("_")
        if len(parts) == 3:
            typ = parts[1]
            try:
                n = int(parts[2])
            except ValueError:
                tg_answer_cb(cb_id, "❌")
                return
            tg_answer_cb(cb_id, f"🔨 {n} {typ.upper()}")
            threading.Thread(target=do_gendev_live, args=(cid, n, typ), daemon=True).start()
        return
    if data == "bfkick_menu":
        tg_answer_cb(cb_id)
        set_pending(cid, "bfkick_input")
        tg_edit(cid, mid,
                "💥 <b>BF KICKER</b>\n📁 Upload file .txt atau ketik Device ID",
                [[{"text": "« Kembali", "callback_data": "sub_bf"}]])
        return
    if data.startswith("bfkick_loop_"):
        loops_str = data.replace("bfkick_loop_", "")
        p = get_pending(cid)
        if not p or "device_ids" not in p.get("data", {}):
            tg_answer_cb(cb_id, "❌ Upload dulu", True)
            return
        device_ids = p["data"]["device_ids"]
        loops = 999999 if loops_str == "unlimited" else int(loops_str or 10)
        tg_answer_cb(cb_id, f"💥 {loops if loops < 999999 else '∞'}")
        clear_pending(cid)
        threading.Thread(target=do_bfkick_live,
                          args=(cid, device_ids, loops), daemon=True).start()
        return
    if data == "stop_job":
        stopped = job_stop(cid) or stop_job(cid)
        _STOP_FLAG.set()
        tg_answer_cb(cb_id, "⛔ Stopping..." if stopped else "❌ No job", True)
        threading.Timer(1.0, lambda: _STOP_FLAG.clear()).start()
        return

    try:
        _engine.handle_callback(cb)
    except Exception as e:
        print(f"[CB ERR] {e}")


# ══════════════════════════════════════════════════════════════════
#  WRAPPED COMMAND
# ══════════════════════════════════════════════════════════════════
def wrapped_handle_command(cid, text, username, msg=None):
    try:
        lower = text.strip().lower()
        role = get_role(cid)
        is_adm = role in ("admin", "owner")
        is_own = role == "owner"

        if lower in ("/menu", "/start", "/engine", "/switch"):
            tg_send(cid, start_menu(username, cid), start_kb())
            return

        if lower == "/speed":
            tg_send(cid,
                f"⚡ <b>SPEED INFO</b>\n━━━━━━━━━━━━━━━\n"
                f"💻 CPU     : <b>{CPU_COUNT}</b>\n"
                f"📊 RAM     : <b>{RAM_MB}</b> MB\n"
                f"🔧 Workers : <b>{AUTO_WORKERS}</b>\n"
                f"⚡ Mode    : <b>{PERFORMANCE_MODE.upper()}</b>\n"
                f"⏱ Delay   : <b>{PROFILE.get('rate', 0.010)}s</b>")
            return

        if lower == "/status":
            tg_send(cid,
                f"📊 <b>BOT STATUS</b>\n━━━━━━━━━━━━━━━\n"
                f"🕒 {now_wib().strftime('%d %B %Y, %H:%M WIB')}\n"
                f"💻 CPU: {CPU_COUNT} | 📊 RAM: {RAM_MB} MB\n"
                f"🔧 Workers: {AUTO_WORKERS}\n"
                f"⚡ Mode: <b>{PERFORMANCE_MODE.upper()}</b>")
            return

        if lower == "/myinfo":
            role_labels = {"owner": "👑 OWNER", "admin": "🔧 ADMIN", "user": "👤 USER"}
            tg_send(cid,
                f"👤 <b>MY INFO</b>\n━━━━━━━━━━━━━━━\n"
                f"👋 {username}\n"
                f"🆔 <code>{cid}</code>\n"
                f"🎭 {role_labels.get(role, '👤')}\n"
                f"🚀 {get_engine(cid) or 'Belum pilih'}")
            return

        if lower == "/ping":
            tg_send(cid, "🏓 Pong!")
            return
        if lower == "/version":
            tg_send(cid, "📦 <b>PEITER STORE v10</b>")
            return
        if lower == "/stats":
            try:
                tg_send(cid, menu_stats(), kb_main(cid))
            except Exception as e:
                tg_send(cid, f"❌ {e}")
            return

        if lower.startswith("/redeem"):
            if not lics:
                tg_send(cid, "❌ License Manager OFF")
                return
            parts = text.strip().split(maxsplit=1)
            if len(parts) < 2:
                tg_send(cid,
                        f"🔑 <b>REDEEM KEY</b>\n━━━━━━━━━━━━━━━\n"
                        f"Format:\n<code>/redeem KODE-LICENSE</code>\n\n"
                        f"Contoh:\n<code>/redeem USR-A3F2-9B1C-7D4E</code>")
                return
            key = parts[1].strip().upper()
            try:
                ok, msg_r, role_r, exp_r = lics.redeem_license(key, cid)
                if ok:
                    grant_access(cid, role=role_r, granted_by=f"lic:{key}")
                    exp_str = "♾ PERMANEN"
                    if exp_r:
                        exp_str = datetime.fromtimestamp(exp_r, TZ_WIB).strftime("%Y-%m-%d %H:%M WIB")
                    tg_send(cid,
                            f"{msg_r}\n━━━━━━━━━━━━━━━\n"
                            f"🎭 Role   : <b>{role_r.upper()}</b>\n"
                            f"📅 Expired: <b>{exp_str}</b>\n"
                            f"━━━━━━━━━━━━━━━\n"
                            f"✅ Ketik /menu untuk mulai 🚀")
                else:
                    tg_send(cid, msg_r)
            except Exception as e:
                tg_send(cid, f"❌ Error: {e}")
            return

        if lower == "/mylicense":
            if not lics:
                tg_send(cid, "❌ License Manager OFF")
                return
            my = lics.find_user_license(cid)
            if not my:
                tg_send(cid,
                        f"🔑 <b>LICENSE KAMU</b>\n━━━━━━━━━━━━━━━\n"
                        f"❌ Belum punya license\n\n"
                        f"Kirim: <code>/redeem KODE</code>")
                return
            exp = "♾ PERMANEN"
            if my.get("expires_at"):
                exp = datetime.fromtimestamp(my["expires_at"], TZ_WIB).strftime("%Y-%m-%d %H:%M WIB")
            tg_send(cid,
                    f"🔐 <b>LICENSE KAMU</b>\n━━━━━━━━━━━━━━━\n"
                    f"🔑 <code>{my['key']}</code>\n"
                    f"🎭 {my['role'].upper()}\n"
                    f"📅 {exp}\n"
                    f"👥 Used: {my['used_count']}/{my['max_uses']}")
            return

        if lower.startswith("/genlicense"):
            if not is_own:
                tg_send(cid, "🚫 Owner")
                return
            if not lics:
                tg_send(cid, "❌ License OFF")
                return
            parts = text.strip().split()
            rrole = parts[1].lower() if len(parts) >= 2 else "user"
            if rrole not in ("owner", "admin", "user", "trial"):
                rrole = "user"
            dur_str = parts[2].lower() if len(parts) >= 3 else "24h"
            dur = lics.LICENSE_DURATIONS.get(dur_str, 24)
            max_uses = 1
            if len(parts) >= 4:
                try:
                    max_uses = int(parts[3])
                except ValueError:
                    max_uses = 1
            try:
                r = lics.create_license(role=rrole, duration_hours=dur,
                                         max_uses=max_uses, created_by=str(cid))
                exp = "♾ PERMANEN"
                if r["expires_at"]:
                    exp = datetime.fromtimestamp(r["expires_at"], TZ_WIB).strftime("%Y-%m-%d %H:%M WIB")
                tg_send(cid,
                        f"🔑 <b>LICENSE BARU</b>\n━━━━━━━━━━━━━━━\n"
                        f"🔐 <code>{r['key']}</code>\n"
                        f"🎭 Role   : <b>{r['role'].upper()}</b>\n"
                        f"📅 Expired: <b>{exp}</b>\n"
                        f"👥 Max    : <b>{r['max_uses']}</b>\n"
                        f"━━━━━━━━━━━━━━━\n"
                        f"User redeem: <code>/redeem {r['key']}</code>")
            except Exception as e:
                tg_send(cid, f"❌ Error: {e}")
            return

        if lower == "/listlicenses":
            if not is_own:
                tg_send(cid, "🚫 Owner")
                return
            if not lics:
                tg_send(cid, "❌ OFF")
                return
            try:
                items = lics.list_licenses()
                if not items:
                    tg_send(cid, "📭 Belum ada license")
                    return
                now = time.time()
                txt = f"🔑 <b>License ({len(items)})</b>\n━━━━━━━━━━━━━━━\n"
                for lic in items[:30]:
                    if not lic.get("enabled", True):
                        st = "⛔"
                    elif lic["expires_at"] and now > lic["expires_at"]:
                        st = "⌛"
                    elif lic["used_count"] >= lic["max_uses"]:
                        st = "🔴"
                    else:
                        st = "✅"
                    txt += f"{st} <code>{lic['key']}</code> — {lic['role']}\n"
                tg_send(cid, txt)
            except Exception as e:
                tg_send(cid, f"❌ Error: {e}")
            return

        if lower.startswith("/revokelicense"):
            if not is_own:
                tg_send(cid, "🚫 Owner")
                return
            if not lics:
                tg_send(cid, "❌ OFF")
                return
            parts = text.strip().split(maxsplit=1)
            if len(parts) < 2:
                tg_send(cid, "❌ <code>/revokelicense KEY</code>")
                return
            try:
                if lics.revoke_license(parts[1]):
                    tg_send(cid, f"✅ Revoked <code>{parts[1].upper()}</code>")
                else:
                    tg_send(cid, "❌ Tidak ditemukan")
            except Exception as e:
                tg_send(cid, f"❌ Error: {e}")
            return

        if lower == "/license":
            if not is_own:
                tg_send(cid, "🚫 Owner")
                return
            if not lics:
                tg_send(cid, "❌ OFF")
                return
            try:
                st = lics.stats()
                tg_send(cid,
                        f"🔑 <b>LICENSE MANAGER</b>\n━━━━━━━━━━━━━━━\n"
                        f"📦 Total    : <b>{st['total']}</b>\n"
                        f"✅ Aktif    : <b>{st['active']}</b>\n"
                        f"⌛ Expired  : <b>{st['expired']}</b>\n"
                        f"⛔ Disabled : <b>{st['disabled']}</b>\n"
                        f"🔴 Habis    : <b>{st['exhausted']}</b>\n"
                        f"━━━━━━━━━━━━━━━\n"
                        f"📌 Command:\n"
                        f"• <code>/genlicense user 30d 1</code>\n"
                        f"• <code>/listlicenses</code>\n"
                        f"• <code>/revokelicense KEY</code>")
            except Exception as e:
                tg_send(cid, f"❌ Error: {e}")
            return

        try:
            _engine.handle_command(cid, text, username, msg)
        except Exception as e:
            print(f"[CMD ERR] {e}")
    except Exception as e:
        print(f"[CMD ERR] {e}")


# ══════════════════════════════════════════════════════════════════
#  WRAPPED DOCUMENT
# ══════════════════════════════════════════════════════════════════
def wrapped_handle_document(cid, username, doc):
    fname = (doc.get("file_name") or "").lower()
    file_id = doc.get("file_id")
    p = get_pending(cid)
    state = p.get("state") if p else None

    if state and state.startswith("flt_"):
        if not fname.endswith((".txt", ".csv", ".log")):
            tg_send(cid, "❌ .txt only")
            return
        tg_send(cid, f"📁 Downloading <b>{fname}</b>...")
        local = tg_get_file(file_id)
        if not local:
            tg_send(cid, "❌ Gagal download")
            return
        data_pending = p.get("data", {})
        clear_pending(cid)

        if state == "flt_skin":
            threading.Thread(target=_do_filter_generic,
                args=(cid, username, local, "skin", data_pending.get("value", 100)),
                daemon=True).start()
        elif state == "flt_level":
            threading.Thread(target=_do_filter_generic,
                args=(cid, username, local, "level", data_pending.get("value", 50)),
                daemon=True).start()
        elif state == "flt_rank":
            threading.Thread(target=_do_filter_generic,
                args=(cid, username, local, "rank", data_pending.get("value", "epic")),
                daemon=True).start()
        elif state == "flt_collector":
            threading.Thread(target=_do_filter_generic,
                args=(cid, username, local, "collector", data_pending.get("value", "Expert Collector")),
                daemon=True).start()
        elif state == "flt_combo":
            threading.Thread(target=_do_filter_generic,
                args=(cid, username, local, "combo", None),
                kwargs={"skin_min": data_pending.get("skin_min"),
                        "level_min": data_pending.get("level_min"),
                        "rank_target": data_pending.get("rank_target"),
                        "collector_target": data_pending.get("collector_target")},
                daemon=True).start()
        return

    if state == "bfkick_input":
        if not fname.endswith((".txt", ".csv", ".log")):
            tg_send(cid, "❌ .txt only")
            return
        tg_send(cid, f"📁 Downloading <b>{fname}</b>...")
        local = tg_get_file(file_id)
        if not local:
            tg_send(cid, "❌ Gagal download")
            return
        try:
            content = Path(local).read_text(encoding="utf-8", errors="ignore")
            device_ids = extract_device_ids(content)
            if not device_ids:
                tg_send(cid, "❌ Tidak ada Device ID")
                clear_pending(cid)
                return
            set_pending(cid, "bfkick_loops", {"device_ids": device_ids})
            tg_send(cid,
                    f"📁 <b>{len(device_ids)} ID loaded</b>\nPilih loops:",
                    bfkick_loops_kb())
        except Exception as e:
            tg_send(cid, f"❌ {e}")
            clear_pending(cid)
        return

    if state and state.startswith("p1_"):
        if not fname.endswith((".txt", ".csv", ".log")):
            tg_send(cid, "❌ .txt only")
            return
        tg_send(cid, f"📁 Downloading <b>{fname}</b>...")
        local = tg_get_file(file_id)
        if not local:
            tg_send(cid, "❌ Gagal download")
            return
        handle_peiter1_file(cid, username, local, fname)
        return

    if state in ("bulk_valid", "bulk_ban", "bulk_detail", "bulk_lookup"):
        clear_pending(cid)
        if not fname.endswith((".txt", ".csv", ".log")):
            tg_send(cid, "❌ .txt only")
            return
        tg_send(cid, f"📁 Downloading <b>{fname}</b>...")
        local = tg_get_file(file_id)
        if not local:
            tg_send(cid, "❌ Gagal download")
            return
        if state == "bulk_valid":
            threading.Thread(target=do_bulk_valid_notif,
                              args=(cid, username, local, fname), daemon=True).start()
        elif state == "bulk_ban":
            threading.Thread(target=do_bulk_ban_notif,
                              args=(cid, username, local, fname), daemon=True).start()
        elif state == "bulk_detail":
            threading.Thread(target=do_bulk_detail_notif,
                              args=(cid, username, local, fname), daemon=True).start()
        elif state == "bulk_lookup":
            threading.Thread(target=do_bulk_lookup_notif,
                              args=(cid, username, local, fname), daemon=True).start()
        return

    try:
        _engine.handle_document(cid, username, doc)
    except Exception as e:
        print(f"[DOC ERR] {e}")

# ══════════════════════════════════════════════════════════════════
#  MAIN — Dual Engine Polling Loop
# ══════════════════════════════════════════════════════════════════

def _dual_poll_loop():
    """Bot polling dengan dual engine support."""
    import requests as _req

    base = f"https://api.telegram.org/bot{BOT_TOKEN}"

    # Load state
    load_state()

    # Verify bot token
    try:
        r = _req.get(f"{base}/getMe", timeout=10)
        info = r.json()
        if info.get("ok"):
            print(f"✅ Bot valid: @{info['result'].get('username','?')}")
        else:
            print(f"❌ Invalid token: {info}")
            return
    except Exception as e:
        print(f"❌ Token check fail: {e}")
        return

    print("🚀 Starting DUAL ENGINE polling...")
    print(f"👑 Owner: {OWNER_CHAT_ID}")
    print()

    # Notif startup ke OWNER
    try:
        tg_send(OWNER_CHAT_ID,
            f"🚀 <b>PEITER STORE ONLINE</b>\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🔧 Engine: <b>DUAL</b>\n"
            f"⚡ Mode: <b>{PERFORMANCE_MODE.upper()}</b>\n"
            f"🔧 Workers: <b>{AUTO_WORKERS}</b>\n"
            f"💰 Donate: <b>{'ON' if dn else 'OFF'}</b>\n"
            f"🔑 License: <b>{'ON' if lics else 'OFF'}</b>\n"
            f"⚙️ Extras: <b>{'ON' if ex else 'OFF'}</b>\n"
            f"🕒 {now_wib().strftime('%Y-%m-%d %H:%M:%S WIB')}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"✅ Bot siap")
        print("[BOT] Notif owner OK")
    except Exception as e:
        print(f"[BOT] Notif owner error: {e}")

    # Notif ke user yang pernah /start
    try:
        import started_tracker as _st
        _tr = _st.StartedTracker(STORE_DIR / "started_users.json")
        if _tr.count() > 0:
            _st.broadcast_to_started(_tr,
                f"🔔 <b>BOT ONLINE</b>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"👋 Halo, bot udah nyala lagi\n"
                f"⚡ Mode: <b>{PERFORMANCE_MODE.upper()}</b>\n"
                f"🕒 {now_wib().strftime('%H:%M:%S WIB')}\n"
                f"━━━━━━━━━━━━━━━\n"
                f"Ketik /menu untuk mulai 🚀",
                tg_send, delay=0.35, skip_blocked=True)
            print(f"[BOT] Notif {_tr.count()} user OK")
    except Exception as e:
        print(f"[BOT] Broadcast error: {e}")

    last_update = 0

    while True:
        try:
            r = _req.get(
                f"{base}/getUpdates",
                params={"offset": last_update + 1, "timeout": 25},
                timeout=35)
            data = r.json()
            if not data.get("ok"):
                time.sleep(3)
                continue

            for upd in data.get("result", []):
                last_update = upd["update_id"]

                # ── Callback Query ──
                if "callback_query" in upd:
                    try:
                        wrapped_handle_callback(upd["callback_query"])
                    except Exception as e:
                        print(f"[CB ERR] {e}")
                    continue

                # ── Message ──
                msg = upd.get("message") or upd.get("edited_message")
                if not msg:
                    continue

                chat = msg.get("chat", {})
                cid = str(chat.get("id"))
                username = chat.get("first_name") or "User"
                text = msg.get("text", "")

                # Cek block & flood
                if text.startswith("/"):
                    flood, _ = _engine.check_flood(cid)
                    if flood:
                        if cid != str(OWNER_CHAT_ID):
                            _engine._BLOCKED_USERS.add(cid)
                            _engine.save_blocked()
                            tg_send(cid, "🚫 DIBLOKIR (spam)")
                        else:
                            tg_send(cid, "⚠️ Slow down")
                        continue

                if cid in _engine._BLOCKED_USERS and cid != str(OWNER_CHAT_ID):
                    continue

                # ── Document Upload ──
                doc = msg.get("document")
                if doc:
                    try:
                        wrapped_handle_document(cid, username, doc)
                    except Exception as e:
                        print(f"[DOC ERR] {e}")
                        tg_send(cid, f"❌ {type(e).__name__}")
                    continue

                if not text:
                    continue

                # ── Command (/) ──
                if text.startswith("/"):
                    try:
                        wrapped_handle_command(cid, text, username, msg)
                    except Exception as e:
                        print(f"[CMD ERR] {e}")
                    continue

                # ── Teks Biasa — Handle Pending States ──
                pending = get_pending(cid)
                if pending:
                    state = pending["state"]
                    handled = False

                    # P1 states
                    if state.startswith("p1_"):
                        try:
                            handled = handle_peiter1_text(cid, username, text)
                        except Exception as e:
                            print(f"[P1 TXT ERR] {e}")

                    # Filter states
                    elif state.startswith("flt_"):
                        handled = True  # filter butuh file, bukan teks

                    # BF custom gen
                    elif state == "bfgen_custom":
                        clear_pending(cid)
                        parts = text.split()
                        if parts:
                            try:
                                n = min(int(parts[0]), 10000)
                            except:
                                n = 10
                            typ = "mixed"
                            if len(parts) >= 2:
                                t = parts[1].lower()
                                if t in ("and", "android"):
                                    typ = "and"
                                elif t == "ios":
                                    typ = "ios"
                            import threading as _th
                            _th.Thread(target=do_gendev_live,
                                       args=(cid, n, typ), daemon=True).start()
                        handled = True

                    # Fallback ke engine app.py
                    if not handled:
                        try:
                            _engine.handle_command(cid, text, username, msg)
                        except Exception as e:
                            print(f"[ENGINE CMD ERR] {e}")
                else:
                    # Gak ada pending, teks biasa
                    try:
                        _engine.handle_command(cid, text, username, msg)
                    except Exception as e:
                        print(f"[ENGINE CMD ERR] {e}")

        except KeyboardInterrupt:
            print("\n[STOP] User interrupt")
            break
        except Exception as e:
            print(f"[POLL ERR] {e}")
            time.sleep(3)


if __name__ == "__main__":
    try:
        print("=" * 64)
        print("  PEITER STORE — DUAL ENGINE")
        print("=" * 64)
        print(f"  Token  : {BOT_TOKEN[:25]}...")
        print(f"  Owner  : {OWNER_CHAT_ID}")
        print(f"  License: {'ON' if lics else 'OFF'}")
        print(f"  Extras : {'ON' if ex else 'OFF'}")
        print(f"  Donate : {'ON' if dn else 'OFF'}")
        print("=" * 64)
        print()
        _dual_poll_loop()
    except KeyboardInterrupt:
        print("\n[STOP]")