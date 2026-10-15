"""Lattice — minimal YAML task-graph runner for the org.

Usage:
    python worker/lattice.py --task <yaml> [--set key=value]...

Task file format (see mLattice/tasks/build_pipeline.yaml):
    id: <pipeline-id>
    description: <text>
    inputs: [name1, name2]
    steps:
      - id: <step-id>
        type: shell
        command: "python worker/run_build.py --target {{ build_target }}"
      - id: <step-id>
        type: python
        module: "worker.apply"
        function: "record_build_event"
        args: ["literal", "{{ build_target }}"]

Shell steps interpolate {{ key }} from inputs. Python steps import the
module (F:\\Lab on sys.path) and call the function with interpolated args.
A failing step stops the pipeline. Final stdout line:
    PIPELINE_RESULT <json>
"""
import argparse
import importlib
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

LAB = Path(r"F:\Lab")
sys.path.insert(0, str(LAB))

def _parse_scalar(s):
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        return s[1:-1]
    low = s.lower()
    if low in ("true", "yes"):
        return True
    if low in ("false", "no"):
        return False
    if low in ("null", "~", ""):
        return None
    try:
        return int(s)
    except ValueError:
        return s


def _mini_yaml(text):
    """YAML subset for org task files (no external deps): mappings,
    lists of scalars, lists of mappings, quoted/unquoted scalars."""
    toks = []
    for raw in text.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        toks.append([indent, stripped])

    pos = 0

    def parse_map(indent):
        nonlocal pos
        out = {}
        while pos < len(toks):
            ind, content = toks[pos]
            if ind < indent or ind > indent or content.startswith("- ") or content == "-":
                break
            key, _, val = content.partition(":")
            key, val = key.strip(), val.strip()
            pos += 1
            if val == "":
                if pos < len(toks) and toks[pos][0] > indent:
                    out[key] = parse_block(toks[pos][0])
                else:
                    out[key] = None
            else:
                out[key] = _parse_scalar(val)
        return out

    def parse_list(indent):
        nonlocal pos
        items = []
        while pos < len(toks):
            ind, content = toks[pos]
            if ind != indent or not (content.startswith("- ") or content == "-"):
                break
            rest = content[1:].strip()
            pos += 1
            if rest == "":
                if pos < len(toks) and toks[pos][0] > indent:
                    items.append(parse_block(toks[pos][0]))
                else:
                    items.append(None)
            elif ":" in rest and not rest[0] in ('"', "'"):
                first_key, _, first_val = rest.partition(":")
                m = {}
                if first_val.strip() == "":
                    if pos < len(toks) and toks[pos][0] > indent:
                        m[first_key.strip()] = parse_block(toks[pos][0])
                    else:
                        m[first_key.strip()] = None
                else:
                    m[first_key.strip()] = _parse_scalar(first_val)
                if pos < len(toks) and toks[pos][0] > indent and not toks[pos][1].startswith("- "):
                    m.update(parse_map(toks[pos][0]))
                items.append(m)
            else:
                items.append(_parse_scalar(rest))
        return items

    def parse_block(indent):
        if toks[pos][1].startswith("- ") or toks[pos][1] == "-":
            return parse_list(indent)
        return parse_map(indent)

    if not toks:
        return {}
    return parse_block(toks[0][0])


try:
    import yaml

    def _load_yaml(text):
        return yaml.safe_load(text)
except ImportError:
    def _load_yaml(text):
        return _mini_yaml(text)


def interpolate(text, inputs):
    if not isinstance(text, str):
        return text
    for k, v in inputs.items():
        text = text.replace("{{ %s }}" % k, str(v)).replace("{{%s}}" % k, str(v))
    return text


def run_shell_step(step, inputs):
    cmd = interpolate(step.get("command", ""), inputs)
    print("[shell] %s" % cmd)
    proc = subprocess.run(cmd, cwd=str(LAB), shell=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = proc.stdout.decode("utf-8", "replace")
    sys.stdout.write(out)
    return proc.returncode, out


def run_python_step(step, inputs):
    module_name = step.get("module", "")
    func_name = step.get("function", "")
    if not module_name or not func_name:
        print("[python] step missing module/function")
        return 1, ""
    print("[python] %s.%s" % (module_name, func_name))
    mod = importlib.import_module(module_name)
    func = getattr(mod, func_name, None)
    if func is None:
        print("[python] no such function: %s" % func_name)
        return 1, ""
    args = [interpolate(a, inputs) for a in step.get("args", [])]
    func(*args)
    return 0, ""


def run_task(task_path, inputs):
    task_path = Path(task_path)
    if not task_path.is_absolute():
        task_path = LAB / task_path
    task = _load_yaml(task_path.read_text(encoding="utf-8"))

    tid = task.get("id", task_path.stem)
    declared = task.get("inputs", []) or []
    for k in declared:
        if k not in inputs:
            print("missing required input: %s (declare --set %s=...)" % (k, k))
            return {"id": tid, "status": "fail", "error": "missing input %s" % k}

    steps = task.get("steps", []) or []
    step_results = []
    started = datetime.now().isoformat(timespec="seconds")

    for step in steps:
        sid = step.get("id", "?")
        stype = step.get("type", "")
        print("== step: %s (%s) ==" % (sid, stype))
        if stype == "shell":
            rc, out = run_shell_step(step, inputs)
        elif stype == "python":
            rc, out = run_python_step(step, inputs)
        else:
            print("unknown step type: %s" % stype)
            rc, out = 2, ""
        step_results.append({"id": sid, "type": stype, "exit": rc})
        if rc != 0:
            return {"id": tid, "status": "fail", "steps": step_results,
                    "failed_step": sid, "started": started}

    return {"id": tid, "status": "pass", "steps": step_results,
            "started": started,
            "finished": datetime.now().isoformat(timespec="seconds")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True)
    ap.add_argument("--set", action="append", default=[],
                    help="key=value (repeatable)")
    a = ap.parse_args()

    inputs = {}
    for pair in a.set:
        if "=" not in pair:
            print("bad --set: %s (want key=value)" % pair)
            sys.exit(2)
        k, v = pair.split("=", 1)
        inputs[k] = v

    result = run_task(a.task, inputs)
    print("PIPELINE_RESULT %s" % json.dumps(result))
    sys.exit(0 if result.get("status") == "pass" else 1)


if __name__ == "__main__":
    main()
