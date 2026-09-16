#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OUTPUT NAMER — Nama file rapih & berurut"""

import os, re, time, threading
from pathlib import Path
from datetime import datetime, timezone, timedelta

TZ_WIB = timezone(timedelta(hours=7))
_LOCK = threading.Lock()


def next_number(dir_path, prefix, ext=".txt"):
    """Cari nomor urut berikutnya. Contoh: valid-50-001.txt → next = 002"""
    dir_path = Path(dir_path)
    dir_path.mkdir(parents=True, exist_ok=True)
    max_n = 0
    ext_clean = ext.lstrip(".")
    pat = re.compile(rf"^{re.escape(prefix)}-(\d{{3}})\.{re.escape(ext_clean)}$", re.I)
    for f in dir_path.iterdir():
        if not f.is_file():
            continue
        m = pat.match(f.name)
        if m:
            try:
                n = int(m.group(1))
                if n > max_n:
                    max_n = n
            except Exception:
                pass
    return max_n + 1


def make_filename(dir_path, prefix, count, ext=".txt"):
    """Bikin nama file: {prefix}-{count}-{urut:03d}.{ext}"""
    with _LOCK:
        n = next_number(dir_path, prefix, ext)
    return Path(dir_path) / f"{prefix}-{count}-{n:03d}{ext}"


def write_with_header(path, lines, header_lines=None):
    """Tulis file dengan header timestamp."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(TZ_WIB).strftime("%Y-%m-%d %H:%M:%S WIB")
    with open(path, "w", encoding="utf-8") as f:
        if header_lines:
            for h in header_lines:
                f.write(f"# {h}\n")
            f.write(f"# Generated: {ts}\n")
            f.write(f"# Total: {len(lines)}\n")
            f.write("#" + "=" * 60 + "\n\n")
        for line in lines:
            f.write(str(line).rstrip() + "\n")
    return path


def append_with_lock(path, line):
    """Append 1 baris, thread-safe."""
    with _LOCK:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(str(line).rstrip() + "\n")
            f.flush()