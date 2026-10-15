"""Build executor for the org build pipeline.

Usage:
    python worker/run_build.py --target <name> [--agent <agent>]

Looks up <name> in TARGETS, runs the build, writes a log under
org/builds/, records the result via worker.apply.record_build_event,
and prints a machine-readable result line as the final stdout line:
    BUILD_RESULT <json>
"""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

LAB = Path(r"F:\Lab")
sys.path.insert(0, str(LAB))

from worker import apply as apply_mod  # noqa: E402


def _log_path(build_id):
    d = LAB / "org" / "builds"
    d.mkdir(parents=True, exist_ok=True)
    return d / ("%s.log" % build_id)


def _summary(text, n=12):
    lines = [l for l in text.splitlines() if l.strip()]
    tail = lines[-n:]
    return "\n".join(tail)


def run_build(target, agent):
    if target not in TARGETS:
        print("unknown target: %s (known: %s)" % (target, ", ".join(TARGETS)))
        return 2
    spec = TARGETS[target]
    cwd = spec["cwd"]
    cmd = list(spec["cmd"])

    build_id = "build-%s-%s" % (
        datetime.now().strftime("%Y%m%d-%H%M"), target)
    log_path = _log_path(build_id)

    env = dict(os.environ)
    if spec.get("env"):
        env.update(spec["env"])

    print("target=%s cwd=%s" % (target, cwd))
    print("cmd=%s" % " ".join(cmd))
    started = datetime.now().isoformat(timespec="seconds")

    proc = subprocess.run(cmd, cwd=str(cwd), env=env,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = proc.stdout.decode("utf-8", "replace")
    status = "pass" if proc.returncode == 0 else "fail"

    with open(log_path, "w", encoding="utf-8") as f:
        f.write("target: %s\nagent: %s\nstatus: %s\nexit: %s\nstarted: %s\n"
                % (target, agent, status, proc.returncode, started))
        f.write("-" * 60 + "\n")
        f.write(out)

    build_file = apply_mod.record_build_event(
        target=target, agent=agent, status=status,
        exit_code=proc.returncode, log_text=_summary(out),
        log_file=str(log_path.relative_to(LAB)) if log_path.is_relative_to(LAB) else str(log_path))

    result = {
        "build_id": build_id,
        "target": target,
        "status": status,
        "exit": proc.returncode,
        "log": str(log_path),
        "build_file": build_file,
    }
    print("BUILD_RESULT %s" % json.dumps(result))
    return 0 if status == "pass" else 1


# Target registry: name -> {cwd, cmd, env?, desc}
TARGETS = {
    "selftest": {
        "desc": "Compile-check every org worker script (org toolchain build)",
        "cwd": str(LAB / "worker"),
        "cmd": [sys.executable, "-m", "compileall", "-q", str(LAB / "worker")],
    },
    "mulattice-tests": {
        "desc": "muLattice CPU unit tests (kernel invariants, scan equivalence)",
        "cwd": r"C:\Users\sardw\mLattice",
        "cmd": [r"C:\Users\sardw\mLattice\.venv\Scripts\python.exe",
                "tests/test_kernel.py"],
        "env": {"PYTHONIOENCODING": "utf-8"},
    },
}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True)
    ap.add_argument("--agent", default="qwen")
    a = ap.parse_args()
    sys.exit(run_build(a.target, a.agent))
