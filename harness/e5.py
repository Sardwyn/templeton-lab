"""E5 -- blind feed, independently authored (see e5-prereg.md).

Frozen 2026-11-09, before any feed existed. The feed is authored by Brad and is
placed at harness/feeds/. This runner never edits it and never writes to it.

    1. re-checks every hash in FREEZE.md and aborts on a mismatch
    2. prints the feed file's sha256; if <file>.sha256 exists it must match
    3. validates the feed shape; a malformed feed is a failed run, printed in full
    4. runs each requested reading with run.py's run_one, then evaluates the feed's
       criteria with the registered checks plus the four E5 checks
    5. writes e5-out.txt and e5-<name>.json, and exits 0 only if every non-n/a
       claim passed

    python harness/e5.py harness/feeds/<file>.json

Exit 0 pass, 1 failed run, 2 abort (frozen hash or sidecar mismatch).
"""

import hashlib
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import run as R                       # noqa: E402  (frozen reader/driver)

FREEZE = os.path.join(HERE, "FREEZE.md")
PREREG = os.path.join(HERE, "e5-prereg.md")
OUT = os.path.join(HERE, "e5-out.txt")

KINDS = {"prediction", "identity", "continuity", "causality", "agency",
         "self", "witness"}

# The four checks E5 adds, fixed in e5-prereg.md before any feed.
EXTRA = {
    "gap_ratio_min": lambda c, need: R.yes(
        c["gap"] is not None and c["gap"]["ratio"] >= need,
        {"ratio": round(c["gap"]["ratio"], 4) if c["gap"] else None,
         "need": need}),
    "cut_inside": lambda c, need: R.yes(
        c["tau"] is not None and need[0] < c["tau"] < need[1],
        {"tau": round(c["tau"], 6) if c["tau"] is not None else None,
         "lo": need[0], "hi": need[1]}),
    "answered_min": lambda c, need: R.yes(
        R.accuracy(c["asked"])["answered"] >= need,
        R.accuracy(c["asked"])),
    "declined_max": lambda c, need: R.yes(
        R.accuracy(c["asked"])["declined"] <= need,
        R.accuracy(c["asked"])),
}

lines = []


def say(text=""):
    lines.append(text)
    print(text, flush=True)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def frozen_from_freeze():
    """Read the file -> sha256 table out of FREEZE.md, so the check is against
    the contract, not a second copy of the list."""
    text = open(FREEZE, "r", encoding="utf-8").read()
    found = {}
    for line in text.splitlines():
        m = re.match(r"\|\s*`([^`]+)`\s*\|\s*`([0-9a-f]{64})`\s*\|", line)
        if m:
            found[m.group(1)] = m.group(2)
    return found


def registered(key):
    """Resolve a criteria key exactly as run.judge does, plus the E5 extras.
    Returns (base_fn, extra_fn)."""
    reading = None
    if key.endswith("_joined"):
        reading = True
    elif key.endswith("_separate"):
        reading = False
    base = key.rsplit("_", 1)[0] if reading is not None else key
    return (R.CHECKS.get(base) or R.CHECKS.get(key),
            EXTRA.get(base) or EXTRA.get(key))


def applies(key, joined):
    if key.endswith("_joined"):
        return joined
    if key.endswith("_separate"):
        return not joined
    return True


def evaluate(ctx, criteria, joined):
    """run.judge's dispatch, with the four E5 checks in the same table."""
    rows = [("derived cut", R.na({
        "gap": ctx["gap"] and round(ctx["gap"]["ratio"], 2),
        "tau": ctx["tau"] and round(ctx["tau"], 5)}))]
    for key, need in criteria.items():
        if not applies(key, joined):
            continue
        base_fn, extra_fn = registered(key)
        fn = base_fn or extra_fn
        if fn is None:
            rows.append((key, {"pass": False,
                               "value": "no measurement registered"}))
            continue
        if need is None:
            rows.append((key, R.na(fn(ctx, 0)["value"])))
        else:
            rows.append((key, fn(ctx, need)))
    return rows


def state_ok(x, dim=None):
    if not isinstance(x, list) or not x:
        return False, "a state must be a non-empty list of numbers"
    for v in x:
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            return False, "a state must contain only numbers"
        if not math.isfinite(v):
            return False, "a state contains a non-finite number"
    if dim is not None and len(x) != dim:
        return False, "state length %d does not match %d" % (len(x), dim)
    return True, ""


def validate(feed):
    """Fixed checks. Never repairs a value: returns every error it finds."""
    errs = []

    def bad(msg):
        errs.append(msg)
        return False

    if not isinstance(feed, dict):
        bad("top level must be a JSON object")
        return errs

    name = feed.get("name")
    if not isinstance(name, str) or not name.strip():
        bad("name must be a non-empty string")

    kind = feed.get("kind")
    if kind not in KINDS:
        bad("kind must be one of %s" % sorted(KINDS))

    blocks = feed.get("blocks")
    dim = None
    if not isinstance(blocks, list) or not blocks:
        bad("blocks must be a non-empty list of episodes")
        blocks = []
    for e, ep in enumerate(blocks):
        if not isinstance(ep, list) or not ep:
            bad("block %d must be a non-empty list of [state, error]" % e)
            continue
        for i, item in enumerate(ep):
            if not isinstance(item, list) or len(item) != 2:
                bad("block %d position %d must be [state, error]" % (e, i))
                continue
            state, err = item
            ok, why = state_ok(state, dim)
            if not ok:
                bad("block %d position %d: %s" % (e, i, why))
            elif dim is None:
                dim = len(state)
            if isinstance(err, bool) or not isinstance(err, (int, float)):
                bad("block %d position %d: error must be a number" % (e, i))
            elif not math.isfinite(err) or not (0.0 <= err <= 1.0):
                bad("block %d position %d: error %r not in [0, 1]" % (e, i, err))

    hold = feed.get("holdout_from")
    if isinstance(hold, bool) or not isinstance(hold, int):
        bad("holdout_from must be an integer")
    elif not (0 <= hold < len(blocks)):
        bad("holdout_from %r out of range for %d blocks" % (hold, len(blocks)))

    readings = feed.get("readings", ["separate", "joined"])
    if not isinstance(readings, list) or not readings:
        bad("readings must be a non-empty list")
    else:
        for r in readings:
            if r not in R.READINGS:
                bad("reading %r is not supported (only %s)"
                    % (r, sorted(R.READINGS)))
        if len(set(readings)) != len(readings):
            bad("readings contains a duplicate")

    probes = feed.get("probes", [])
    if not isinstance(probes, list):
        bad("probes must be a list")
        probes = []
    for p, probe in enumerate(probes):
        if not isinstance(probe, dict):
            bad("probe %d must be an object" % p)
            continue
        if not isinstance(probe.get("why"), str):
            bad("probe %d: why must be a string" % p)
        prefix = probe.get("prefix")
        if not isinstance(prefix, list):
            bad("probe %d: prefix must be a list of states" % p)
        else:
            for j, s in enumerate(prefix):
                ok, why = state_ok(s, dim)
                if not ok:
                    bad("probe %d prefix %d: %s" % (p, j, why))
        if "expect_state" not in probe:
            bad("probe %d: expect_state is required (may be null)" % p)
        else:
            target = probe["expect_state"]
            if target is not None:
                if not isinstance(target, list):
                    bad("probe %d: expect_state must be null or a list of states"
                        % p)
                else:
                    for j, s in enumerate(target):
                        ok, why = state_ok(s, dim)
                        if not ok:
                            bad("probe %d expect_state %d: %s" % (p, j, why))
        if "named" in probe and not isinstance(probe["named"], bool):
            bad("probe %d: named must be a boolean" % p)

    criteria = feed.get("criteria")
    if not isinstance(criteria, dict) or not criteria:
        bad("criteria must be a non-empty object")
    else:
        for key in criteria:
            if not isinstance(key, str) or not key:
                bad("criteria keys must be non-empty strings")

    return errs


def safe_name(name):
    text = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-")
    return text or "feed"


def write_outputs(feed, feed_path, feed_sha, runner_sha, payload, text_lines):
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(text_lines) + "\n")
    name = feed.get("name") if isinstance(feed, dict) else None
    jpath = os.path.join(HERE, "e5-%s.json" % safe_name(name or "invalid"))
    payload = dict(payload)
    payload["feed"] = {"path": os.path.abspath(feed_path), "sha256": feed_sha}
    payload["runner_sha256"] = runner_sha
    payload["prereg_sha256"] = sha(PREREG) if os.path.exists(PREREG) else None
    with open(jpath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1, default=list)
    return jpath


def main():
    if len(sys.argv) != 2:
        print("usage: python harness/e5.py harness/feeds/<file>.json")
        return 2
    feed_path = sys.argv[1]
    runner_sha = sha(os.path.abspath(__file__))

    say("E5 -- blind feed, independently authored")
    say("runner sha256 %s" % runner_sha)
    say("prereg sha256 %s"
        % (sha(PREREG) if os.path.exists(PREREG) else "MISSING"))
    say("freeze re-check (read from FREEZE.md):")
    frozen = frozen_from_freeze()
    if not frozen:
        say("ABORT: no hashes parsed from %s" % FREEZE)
        return 2
    ok = True
    for name, want in frozen.items():
        path = os.path.join(HERE, name)
        got = sha(path) if os.path.exists(path) else "MISSING"
        state = "ok" if got == want else "CHANGED"
        say("  hash %-12s %s %s" % (name, got[:16], state))
        ok = ok and got == want
    if not ok:
        say("ABORT: the frozen implementation changed. E5 is invalid.")
        with open(OUT, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        return 2

    if not os.path.isfile(feed_path):
        say()
        say("ABORT: feed not found at %s" % os.path.abspath(feed_path))
        with open(OUT, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        return 2
    raw = open(feed_path, "rb").read()
    feed_sha = hashlib.sha256(raw).hexdigest()
    say()
    say("feed %s" % os.path.abspath(feed_path))
    say("feed sha256 %s" % feed_sha)

    sidecar = feed_path + ".sha256"
    if os.path.exists(sidecar):
        side = open(sidecar, "r", encoding="utf-8").read().strip().split()
        want = side[0].lower() if side else ""
        say("sidecar sha256 %s" % (want or "EMPTY"))
        if want != feed_sha:
            say("ABORT: feed hash does not match its sidecar.")
            with open(OUT, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
            return 2
    else:
        say("sidecar: none (feed hash recorded above)")

    try:
        feed = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        say("ABORT: feed does not parse as UTF-8 JSON: %s" % exc)
        with open(OUT, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        return 1

    say()
    if isinstance(feed, dict):
        say("name %s" % feed.get("name", "n/a"))
        say("authored_by %s" % feed.get("authored_by", "n/a"))
        say("created %s" % feed.get("created", "n/a"))
        say("kind %s" % feed.get("kind", "n/a"))
    errs = validate(feed)
    if errs:
        say("VALIDATION FAILED (%d error(s)); the feed is not run:" % len(errs))
        for e in errs:
            say("  - %s" % e)
        payload = {"name": feed.get("name") if isinstance(feed, dict) else None,
                   "valid": False, "errors": errs, "readings": {}}
        jpath = write_outputs(feed, feed_path, feed_sha, runner_sha, payload, lines)
        say("written -> %s, %s" % (OUT, jpath))
        return 1
    say("validation PASS")

    readings = feed.get("readings", ["separate", "joined"])
    spec = {
        "name": feed["name"],
        "kind": feed["kind"],
        "blocks": feed["blocks"],
        "holdout_from": feed["holdout_from"],
        "probes": feed.get("probes", []),
        "criteria": feed["criteria"],
    }

    total = passed = failed = na = 0
    payload = {"name": spec["name"], "valid": True, "errors": [],
               "authored_by": feed.get("authored_by"),
               "created": feed.get("created"), "kind": spec["kind"],
               "holdout_from": spec["holdout_from"], "readings": {}}

    for reading in readings:
        joined = R.READINGS[reading]
        ctx = R.run_one(spec, joined)
        rows = evaluate(ctx, spec["criteria"], joined)

        say()
        say("--- %s reading ---" % reading)
        say("STRUCTURE")
        say("  states %d  episodes %d  classes %d  sizes %s"
            % (ctx["shape"]["states"], ctx["shape"]["episodes"],
               ctx["shape"]["classes"],
               sorted(ctx["shape"]["sizes"].values(), reverse=True)))
        say("  gap %s"
            % ("none" if ctx["gap"] is None else
               "ratio %.4f  lo %.6f  hi %.6f  cut %.6f"
               % (ctx["gap"]["ratio"], ctx["gap"]["lo"], ctx["gap"]["hi"],
                  ctx["tau"])))
        say("  invariant components %s" % ctx["shape"]["invariant"])
        say("PREDICTION")
        acc = R.accuracy(ctx["asked"])
        say("  asked %d  answered %d  declined %d  hits %d  accuracy %.3f"
            % (acc["rows"], acc["answered"], acc["declined"],
               sum(1 for r in ctx["asked"] if r["hit"]), acc["acc"]))
        for p, pr in enumerate(ctx["probes"]):
            say("  probe %d: answered %s  support %s  named %s  hit %s"
                % (p, pr["answered"], pr["support"], pr["named"], pr["hit"]))
        say("CLAIMS")
        for name, row in rows:
            if row["pass"] is None:
                verdict = "n/a"
                na += 1
            elif row["pass"]:
                verdict = "pass"
                passed += 1
            else:
                verdict = "FAIL"
                failed += 1
            if name != "derived cut":
                total += 1
            say("  %-22s %-5s %s" % (name, verdict, R.show(row["value"])))

        payload["readings"][reading] = {
            "gap": ctx["gap"], "tau": ctx["tau"],
            "classes": ctx["shape"]["classes"],
            "sizes": sorted(ctx["shape"]["sizes"].values(), reverse=True),
            "invariant": ctx["shape"]["invariant"],
            "accuracy": acc, "probes": ctx["probes"],
            "asked": ctx["asked"],
            "claims": {name: row for name, row in rows},
        }

    say()
    say("SUMMARY  claims %d  pass %d  FAIL %d  n/a %d"
        % (total, passed, failed, na))
    verdict = (failed == 0)
    say("E5 %s" % ("PASS" if verdict else "FAIL"))
    if failed:
        say("  every failing claim above is published as-is; no feed value was"
            " changed and no claim was dropped.")
    jpath = write_outputs(feed, feed_path, feed_sha, runner_sha, payload, lines)
    say("written -> %s, %s" % (OUT, jpath))
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
