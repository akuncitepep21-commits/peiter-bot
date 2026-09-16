#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EXTRAS — Fitur tambahan untuk PEITER STORE"""

import time, json, threading, re
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import deque

TZ_WIB = timezone(timedelta(hours=7))

# ── Rate limit per-worker ──
_RATE_LOCAL = threading.local()

def rate_wait_local(rate):
    if not hasattr(_RATE_LOCAL, "last"):
        _RATE_LOCAL.last = 0.0
    now = time.time()
    wait = rate - (now - _RATE_LOCAL.last)
    if wait > 0:
        time.sleep(wait)
    _RATE_LOCAL.last = time.time()


# ── Notifikasi ──
class NotifStore:
    def __init__(self, path):
        self.path = Path(path)
        self.lock = threading.Lock()
        self.data = self._load()
    def _load(self):
        if not self.path.exists(): return {"users": {}}
        try: return json.loads(self.path.read_text(encoding="utf-8"))
        except: return {"users": {}}
    def _save(self):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")
        except: pass
    def set(self, cid, enabled):
        with self.lock:
            self.data["users"][str(cid)] = bool(enabled)
            self._save()
    def get(self, cid):
        with self.lock:
            return self.data["users"].get(str(cid), True)


# ── Username mapping ──
class UsernameStore:
    def __init__(self, path):
        self.path = Path(path)
        self.lock = threading.Lock()
        self.data = self._load()
    def _load(self):
        if not self.path.exists(): return {}
        try: return json.loads(self.path.read_text(encoding="utf-8"))
        except: return {}
    def _save(self):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")
        except: pass
    def save(self, username, cid):
        if not username: return
        with self.lock:
            self.data[username.lower().lstrip("@")] = str(cid)
            self._save()
    def resolve(self, username):
        if not username: return None
        with self.lock:
            return self.data.get(username.lower().lstrip("@"))


# ── Job tracking ──
class JobTracker:
    def __init__(self):
        self.jobs = {}
        self.lock = threading.Lock()
    def start(self, cid, name, total=0):
        with self.lock:
            self.jobs[str(cid)] = {"name": name, "total": total, "done": 0,
                                    "stop": False, "start": time.time()}
    def update(self, cid, done=None, total=None):
        with self.lock:
            j = self.jobs.get(str(cid))
            if not j: return
            if done is not None: j["done"] = done
            if total is not None: j["total"] = total
    def stop(self, cid):
        with self.lock:
            j = self.jobs.get(str(cid))
            if j: j["stop"] = True; return True
        return False
    def should_stop(self, cid):
        with self.lock:
            j = self.jobs.get(str(cid))
            return bool(j and j.get("stop"))
    def get(self, cid):
        with self.lock:
            return dict(self.jobs.get(str(cid), {}))
    def end(self, cid):
        with self.lock:
            self.jobs.pop(str(cid), None)
    def active_count(self):
        with self.lock:
            return len(self.jobs)


# ── Pagination ──
class Paginator:
    def __init__(self):
        self.states = {}
        self.lock = threading.Lock()
    def set(self, cid, items, per_page=20, formatter=None, title="List"):
        with self.lock:
            self.states[str(cid)] = {"items": items, "per_page": per_page,
                                      "formatter": formatter, "page": 0,
                                      "ts": time.time(), "title": title}
    def get(self, cid, page=None):
        with self.lock:
            s = self.states.get(str(cid))
            if not s: return None
            if time.time() - s["ts"] > 600:
                self.states.pop(str(cid), None); return None
            if page is not None:
                max_page = max(0, (len(s["items"]) - 1) // s["per_page"])
                s["page"] = max(0, min(page, max_page))
            return dict(s)
    def render(self, cid):
        s = self.get(cid)
        if not s: return "❌ Expired", None
        items = s["items"]; pp = s["per_page"]; pg = s["page"]
        total_pages = max(1, (len(items) + pp - 1) // pp)
        start = pg * pp; end = start + pp
        chunk = items[start:end]
        fmt = s["formatter"]
        body = ""
        for i, it in enumerate(chunk, start + 1):
            body += (fmt(it, i) if fmt else f"{i}. {it}") + "\n"
        title = s.get("title", "List")
        header = f"📄 <b>{title}</b> — Hal {pg+1}/{total_pages}\n\n"
        kb = []
        nav = []
        if pg > 0:
            nav.append({"text": "« Prev", "callback_data": f"page_{pg-1}"})
        nav.append({"text": f"{pg+1}/{total_pages}", "callback_data": "page_noop"})
        if pg < total_pages - 1:
            nav.append({"text": "Next »", "callback_data": f"page_{pg+1}"})
        if nav: kb.append(nav)
        kb.append([{"text": "« Kembali", "callback_data": "menu_main"}])
        return header + body, kb


# ── Confirmation ──
class Confirmer:
    def __init__(self):
        self.pending = {}
        self.lock = threading.Lock()
    def set(self, cid, action, data=None):
        with self.lock:
            self.pending[str(cid)] = {"action": action, "data": data or {}, "ts": time.time()}
    def get(self, cid):
        with self.lock:
            c = self.pending.get(str(cid))
            if not c: return None
            if time.time() - c["ts"] > 120:
                self.pending.pop(str(cid), None); return None
            return c
    def clear(self, cid):
        with self.lock:
            self.pending.pop(str(cid), None)


# ── Filter ──
def parse_filter(expr):
    m = re.match(r"(\w+)\s*(>=|<=|>|<|=|==)\s*(.+)", expr.strip())
    if not m: return None
    field, op, val = m.group(1).lower(), m.group(2), m.group(3).strip()
    try: val = float(val)
    except: val = val.lower()
    return field, op, val

def apply_filter(val, op, target):
    try:
        v = float(val); t = float(target)
    except (ValueError, TypeError):
        v = str(val).lower(); t = str(target).lower()
    if op == ">": return v > t
    if op == "<": return v < t
    if op == ">=": return v >= t
    if op == "<=": return v <= t
    if op in ("=", "=="): return v == t
    return False


# ── Merge ──
def merge_device_files(paths):
    seen, out = set(), []
    for p in paths:
        try:
            text = Path(p).read_text(encoding="utf-8", errors="ignore")
            for m in re.finditer(r"(?:and_|ios_)[A-Za-z0-9_-]+", text):
                d = m.group(0)
                if d not in seen:
                    seen.add(d); out.append(d)
        except: continue
    return out


# ── Progress bar ──
def progress_bar(done, total, width=20):
    if total <= 0: return "░" * width + " 0%"
    pct = min(100, int(done / total * 100))
    filled = int(width * pct / 100)
    return f"{'█'*filled}{'░'*(width-filled)} {pct}% ({done}/{total})"


# ── Audit log ──
class AuditLog:
    def __init__(self, path):
        self.path = Path(path)
        self.lock = threading.Lock()
    def log(self, cid, username, action, detail=""):
        try:
            ts = datetime.now(TZ_WIB).strftime("%Y-%m-%d %H:%M:%S")
            line = f"[{ts}] [{cid}] [{username}] {action}"
            if detail: line += f" | {detail}"
            with self.lock:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.path, "a", encoding="utf-8") as f:
                    f.write(line + "\n")
        except: pass
    def tail(self, n=30):
        if not self.path.exists(): return []
        try:
            lines = self.path.read_text(encoding="utf-8", errors="ignore").splitlines()
            return [l for l in lines if l.strip()][-n:]
        except: return []
    def clear(self):
        try:
            self.path.write_text("", encoding="utf-8"); return True
        except: return False


# ── User info ──
VALID_ROLES = ("owner", "admin", "user", "trial", "guest")

def build_userinfo(cid, user_access, user_limits, blocked, get_role):
    cid = str(cid)
    role = get_role(cid) or "blocked"
    rmap = {"owner": "👑 OWNER", "admin": "🔧 ADMIN", "user": "👤 USER",
            "guest": "👻 GUEST", "blocked": "🚫 BLOCKED"}
    lines = ["👤 <b>User Info</b>", "━━━━━━━━━━━━━━━",
             f"🆔 <code>{cid}</code>", f"🎭 Role: {rmap.get(role, role)}"]
    info = user_access.get(cid)
    if info:
        granted = info.get("granted", 0)
        if granted:
            lines.append(f"📅 Granted: {datetime.fromtimestamp(granted, TZ_WIB).strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"📝 By: <code>{info.get('granted_by', '?')}</code>")
        exp = info.get("expires")
        if exp:
            lines.append(f"⌛ Expires: {datetime.fromtimestamp(exp, TZ_WIB).strftime('%Y-%m-%d %H:%M')}")
    e = user_limits.get(cid, {})
    if e:
        lines.append("")
        lines.append(f"📊 <b>Limit</b> ({e.get('date', '?')})")
        lines.append(f"  🔍 Lookup: {e.get('lookup', 0)}/{e.get('custom_lookup', 10)}")
        lines.append(f"  ✅ Valid : {e.get('valid', 0)}/{e.get('custom_valid', 10)}")
        lines.append(f"  📦 Bulk  : {e.get('bulk', 0)}/{e.get('custom_bulk', 5)}")
    if cid in blocked:
        lines.append("\n🚫 <b>STATUS: BLOCKED</b>")
    return "\n".join(lines)


# ── Auto cleanup ──
def auto_cleanup(dirs, max_age_days=7, max_size_mb=100):
    total = 0
    cutoff = time.time() - (max_age_days * 86400)
    for d in dirs:
        d = Path(d)
        if not d.exists(): continue
        for f in d.rglob("*"):
            if not f.is_file(): continue
            try:
                if f.stat().st_mtime < cutoff:
                    f.unlink(); total += 1
                elif f.stat().st_size > max_size_mb * 1024 * 1024:
                    f.unlink(); total += 1
            except: continue
    return total


# ── Bot meta ──
def set_bot_meta(tg_api):
    try:
        tg_api("setMyDescription", description=(
            "🎯 PEITER STORE — Ultimate Edition\n\n"
            "Bot lookup & validasi akun MLBB.\nKetik /menu untuk mulai."
        ))
    except: pass
    try:
        tg_api("setMyShortDescription", short_description="Bot lookup & valid akun MLBB")
    except: pass


# ── Forward queue ──
class ForwardQueue:
    def __init__(self, max_size=100000):
        self.queue = deque(maxlen=max_size)
        self.cache = set()
        self.lock = threading.Lock()
    def add(self, key, data):
        with self.lock:
            if key in self.cache: return False
            self.cache.add(key)
            self.queue.append(data)
            if len(self.cache) > 100000: self.cache.clear()
            return True
    def flush(self):
        with self.lock:
            items = list(self.queue)
            self.queue.clear()
        return items
    def size(self):
        with self.lock:
            return len(self.queue)