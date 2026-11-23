"""Resource guards for long jobs: free disk on the project drive, and memory of a child process.

Defaults (override with environment variables):
  METRIC_MIN_DISK_GB  = 15   a job stops cleanly (checkpoint kept) when free disk on the project drive falls below this
  METRIC_NMZ_MEM_GB   = 40   a Normaliz child is killed when its committed (private) memory exceeds this
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path

import psutil

ROOT = Path(__file__).resolve().parents[1]
MIN_DISK_GB = float(os.environ.get("METRIC_MIN_DISK_GB", 15))
NMZ_MEM_GB = float(os.environ.get("METRIC_NMZ_MEM_GB", 40))


class LowDisk(RuntimeError):
    pass


def free_disk_gb(path: Path = ROOT) -> float:
    return shutil.disk_usage(path).free / 2 ** 30


def disk_ok(min_gb: float = MIN_DISK_GB, path: Path = ROOT) -> bool:
    return free_disk_gb(path) >= min_gb


def require_disk(min_gb: float = MIN_DISK_GB, path: Path = ROOT) -> None:
    f = free_disk_gb(path)
    if f < min_gb:
        raise LowDisk(f"only {f:.1f} GB free on {path.anchor} (minimum {min_gb:.0f} GB); stopping, checkpoint kept")


def private_gb(pid: int) -> float:
    """Committed memory of a process (Windows: private bytes; elsewhere: RSS)."""
    try:
        mi = psutil.Process(pid).memory_info()
    except psutil.Error:
        return 0.0
    return getattr(mi, "private", mi.rss) / 2 ** 30
