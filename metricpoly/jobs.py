"""Checkpointed, resumable jobs.

Layout: checkpoints/<job>/state.json   (atomic: write tmp + os.replace)
        checkpoints/<job>/results.jsonl (append-only, flushed + fsynced per record)

state.json holds: job name, params, seed, code_version, git_head, completed task ids, timestamps.
--resume continues from state.json and refuses if code_version or params differ unless --force.
Starting without --resume moves an existing checkpoint dir aside (never deletes it).
SIGINT / SIGTERM / SIGBREAK save state before exiting.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

ROOT = Path(__file__).resolve().parent.parent
CODE_DIRS = ("metricpoly", "scripts")


def code_version() -> str:
    """sha256 over all project source files (detects uncommitted edits too)."""
    h = hashlib.sha256()
    for d in CODE_DIRS:
        for p in sorted((ROOT / d).rglob("*.py")):
            h.update(p.relative_to(ROOT).as_posix().encode())
            h.update(b"\0")
            h.update(p.read_bytes())
    return h.hexdigest()[:16]


def git_head() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
        head = out.stdout.strip() if out.returncode == 0 else "no-commit"
        dirty = subprocess.run(["git", "status", "--porcelain", "--", *CODE_DIRS], cwd=ROOT,
                               capture_output=True, text=True).stdout.strip()
        return head + ("+dirty" if dirty else "")
    except FileNotFoundError:
        return "no-git"


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".tmp{os.getpid()}")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def atomic_write_json(path: Path, obj: Any) -> None:
    atomic_write_text(path, json.dumps(obj, indent=2, sort_keys=True) + "\n")


def add_job_args(ap: argparse.ArgumentParser) -> None:
    ap.add_argument("--resume", action="store_true", help="continue from latest checkpoint")
    ap.add_argument("--force", action="store_true", help="resume even if code version / params differ")
    ap.add_argument("--seed", type=int, default=20261121)


class Job:
    def __init__(self, name: str, params: Dict[str, Any], seed: int, resume: bool = False,
                 force: bool = False, root: Path = ROOT / "checkpoints"):
        self.name = name
        self.dir = root / name
        self.state_path = self.dir / "state.json"
        self.results_path = self.dir / "results.jsonl"
        cv = code_version()
        params = json.loads(json.dumps(params, sort_keys=True))
        if resume and self.state_path.exists():
            st = json.loads(self.state_path.read_text(encoding="utf-8"))
            problems = []
            if st["code_version"] != cv:
                problems.append(f"code version {st['code_version']} != current {cv}")
            if st["params"] != params:
                problems.append(f"params {st['params']} != current {params}")
            if st["seed"] != seed:
                problems.append(f"seed {st['seed']} != current {seed}")
            if problems and not force:
                raise SystemExit("Refusing to resume: " + "; ".join(problems) + " (use --force)")
            if problems:
                print("[job] --force: resuming despite: " + "; ".join(problems), flush=True)
                st.setdefault("forced_resumes", []).append({"at": time.time(), "problems": problems,
                                                             "code_version": cv})
            self.state = st
            print(f"[job] resuming {name}: {len(st['done'])} tasks already done", flush=True)
        else:
            if resume:
                print(f"[job] no checkpoint for {name}; starting fresh", flush=True)
            if self.dir.exists() and any(self.dir.iterdir()):
                bak = self.dir.with_name(f"{name}.bak-{time.strftime('%Y%m%d-%H%M%S')}")
                self.dir.rename(bak)
                print(f"[job] previous checkpoint moved to {bak.name}", flush=True)
            self.dir.mkdir(parents=True, exist_ok=True)
            self.state = {"job": name, "params": params, "seed": seed, "code_version": cv,
                          "git_head": git_head(), "python": sys.version.split()[0],
                          "done": [], "created": time.time(), "updated": time.time()}
            self.save()
        self.seed = seed
        self._install_signals()

    # -- persistence
    def save(self) -> None:
        self.state["updated"] = time.time()
        atomic_write_json(self.state_path, self.state)

    def is_done(self, task: str) -> bool:
        return task in self.state["done"]

    def record(self, task: str, result: Any, mark_done: bool = True) -> None:
        line = json.dumps({"task": task, "t": time.time(), "result": result}, sort_keys=True)
        with open(self.results_path, "a", encoding="utf-8", newline="\n") as f:
            f.write(line + "\n")
            f.flush()
            os.fsync(f.fileno())
        if mark_done and task not in self.state["done"]:
            self.state["done"].append(task)
        self.save()

    def results(self) -> Dict[str, Any]:
        """Latest result per task (later lines win)."""
        out: Dict[str, Any] = {}
        if self.results_path.exists():
            for line in self.results_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    r = json.loads(line)
                    out[r["task"]] = r["result"]
        return out

    # -- signals
    def _install_signals(self) -> None:
        def handler(signum, frame):
            try:
                self.save()
                print(f"\n[job] signal {signum}: checkpoint saved to {self.dir}; rerun with --resume", flush=True)
            finally:
                os._exit(130)
        for sig in ("SIGINT", "SIGTERM", "SIGBREAK"):
            if hasattr(signal, sig):
                signal.signal(getattr(signal, sig), handler)


class Progress:
    def __init__(self, label: str, total: int, every: float = 5.0):
        self.label, self.total, self.every = label, total, every
        self.t0 = time.time()
        self.last = 0.0
        self.done = 0

    def step(self, k: int = 1, force: bool = False) -> None:
        self.done += k
        now = time.time()
        if force or now - self.last >= self.every or self.done == self.total:
            el = now - self.t0
            rate = self.done / el if el > 0 else 0.0
            eta = (self.total - self.done) / rate if rate > 0 else float("inf")
            print(f"[{self.label}] {self.done}/{self.total}  {rate:.2f}/s  "
                  f"elapsed {el:.1f}s  eta {eta:.1f}s", flush=True)
            self.last = now
