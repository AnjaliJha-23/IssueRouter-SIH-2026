"""
backend/tests/test_summary_queue.py
Contract tests for the deferred summarization queue.

Hosted summaries cost seconds each and, measured against the free NIM tier,
concurrent calls fail where sequential ones succeed. The queue therefore runs
exactly one job at a time, and these tests hold it to that.
"""
import os
import queue
import sys
import threading
import time

import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import api.challenges as challenges  # noqa: E402


@pytest.fixture(autouse=True)
def private_queue(monkeypatch):
    """Give each test its own queue and a fresh 'worker not started' flag."""
    monkeypatch.setattr(challenges, "_summary_queue", queue.Queue())
    monkeypatch.setattr(challenges, "_summary_worker_started", False)
    yield


def drain(timeout=10.0):
    deadline = time.time() + timeout
    while challenges._summary_queue.unfinished_tasks and time.time() < deadline:
        time.sleep(0.02)
    return challenges._summary_queue.unfinished_tasks == 0


def test_jobs_run_one_at_a_time_in_order(monkeypatch):
    lock = threading.Lock()
    active = 0
    max_active = 0
    order = []

    def fake_run(job):
        nonlocal active, max_active
        with lock:
            active += 1
            max_active = max(max_active, active)
        order.append(job["challenge_id"])
        time.sleep(0.15)
        with lock:
            active -= 1

    monkeypatch.setattr(challenges, "run_deferred_summary", fake_run)

    for index in range(5):
        challenges.schedule_summary({"challenge_id": f"CHL-{index}"})

    assert drain(), "the queue did not drain"
    assert max_active == 1, f"summaries overlapped (peak concurrency {max_active})"
    assert order == [f"CHL-{index}" for index in range(5)]


def test_worker_is_started_once_for_many_jobs(monkeypatch):
    started = []

    class FakeThread:
        def __init__(self, *args, **kwargs):
            started.append(args)

        def start(self):
            pass

    class FakeThreading:
        Thread = FakeThread

    monkeypatch.setattr(challenges, "threading", FakeThreading)

    for index in range(3):
        challenges.schedule_summary({"challenge_id": f"CHL-{index}"})

    assert len(started) == 1, "only one worker should ever be spawned"
    assert challenges._summary_queue.qsize() == 3


def test_a_failing_job_does_not_kill_the_worker(monkeypatch):
    seen = []
    lock = threading.Lock()

    def flaky_run(job):
        with lock:
            seen.append(job["challenge_id"])
        if job["challenge_id"] == "CHL-boom":
            raise RuntimeError("model exploded")

    monkeypatch.setattr(challenges, "run_deferred_summary", flaky_run)

    challenges.schedule_summary({"challenge_id": "CHL-boom"})
    challenges.schedule_summary({"challenge_id": "CHL-after"})

    assert drain(), "the queue did not drain"
    # The worker survived the exception and processed the next job.
    assert seen == ["CHL-boom", "CHL-after"]
