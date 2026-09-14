"""Node-RED entry point: fixed environment, timeout, run log and overlap lock."""
from datetime import datetime, timezone
import json
import msvcrt
import os
from pathlib import Path
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent


def main():
    logs = BASE / "run_logs"
    logs.mkdir(exist_ok=True)
    with (logs / "pipeline.lock").open("a+b") as lock:
        lock.seek(0)
        if not lock.read(1):
            lock.write(b"0")
            lock.flush()
        lock.seek(0)
        try:
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            print(json.dumps({"status": "skipped", "reason": "Pipeline already running"}))
            return 2
        started = datetime.now(timezone.utc)
        timer = time.monotonic()
        status, code, output = "failed", 1, ""
        try:
            env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
            result = subprocess.run(
                [sys.executable, "-B", "-m", "analysis_automation.data_processing"],
                cwd=BASE.parent, env=env, capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=600,
            )
            code = result.returncode
            output = result.stdout + result.stderr
            if code == 0 and "Report generated:" in result.stdout:
                status = "success"
            elif code == 0:
                code = 1
        except subprocess.TimeoutExpired:
            output = "Pipeline exceeded the 600-second timeout."
        except Exception as exc:
            output = f"Unable to run pipeline: {type(exc).__name__}"
        event = {"started_at": started.isoformat(), "status": status,
                 "duration_seconds": round(time.monotonic() - timer, 2),
                 "exit_code": code, "report": str(BASE / "business_intelligence_report.md") if status == "success" else None}
        log_path = logs / (started.strftime("%Y%m%dT%H%M%S_%fZ") + ".json")
        log_path.write_text(json.dumps({**event, "output": output}, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps({**event, "log": str(log_path)}, ensure_ascii=False))
        return code


if __name__ == "__main__":
    raise SystemExit(main())
