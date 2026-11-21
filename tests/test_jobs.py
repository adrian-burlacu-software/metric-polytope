"""Checkpoint infrastructure: atomic state, resume, refusal on param/code mismatch, cache."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from metricpoly import core, jobs  # noqa: E402
from metricpoly.cache import DiskCache  # noqa: E402


def test_resume_and_refusal(tmp_path, monkeypatch):
    monkeypatch.setattr(jobs.Job, "_install_signals", lambda self: None)
    j = jobs.Job("t", {"a": 1}, seed=1, root=tmp_path)
    j.record("task1", {"x": 1})
    j2 = jobs.Job("t", {"a": 1}, seed=1, resume=True, root=tmp_path)
    assert j2.is_done("task1") and j2.results()["task1"] == {"x": 1}
    with pytest.raises(SystemExit):
        jobs.Job("t", {"a": 2}, seed=1, resume=True, root=tmp_path)
    with pytest.raises(SystemExit):
        jobs.Job("t", {"a": 1}, seed=2, resume=True, root=tmp_path)
    j3 = jobs.Job("t", {"a": 2}, seed=1, resume=True, force=True, root=tmp_path)
    assert j3.state["forced_resumes"]
    # fresh start moves old dir aside, never deletes
    jobs.Job("t", {"a": 1}, seed=1, root=tmp_path)
    assert any(p.name.startswith("t.bak-") for p in tmp_path.iterdir())


def test_code_version_mismatch_refused(tmp_path, monkeypatch):
    monkeypatch.setattr(jobs.Job, "_install_signals", lambda self: None)
    jobs.Job("t", {}, seed=0, root=tmp_path)
    st = json.loads((tmp_path / "t" / "state.json").read_text())
    st["code_version"] = "different"
    (tmp_path / "t" / "state.json").write_text(json.dumps(st))
    with pytest.raises(SystemExit):
        jobs.Job("t", {}, seed=0, resume=True, root=tmp_path)


def test_atomic_write_leaves_no_tmp(tmp_path):
    p = tmp_path / "x.json"
    jobs.atomic_write_json(p, {"a": 1})
    assert json.loads(p.read_text()) == {"a": 1}
    assert [f.name for f in tmp_path.iterdir()] == ["x.json"]


def test_disk_cache(tmp_path):
    c = DiskCache(tmp_path / "c.sqlite")
    p = core.Point.make(5, 3, [2] * 10)
    a = c.canonical(p)
    b = DiskCache(tmp_path / "c.sqlite").canonical(p)
    assert a == b and c.misses == 1
