"""E5-D -- cut stability trajectory over Brad's blind feed (see e5d-prereg.md).

A diagnostic, not a capability rung. It replays harness/feeds/brad_e5.json one
observation at a time, records the frozen Harness's gap/cut/classes at every
prefix, marks every admissibility event, and attributes each event to the
observation that caused it and to every earlier observation whose
nearest-neighbour distance changed. It changes nothing: same feed bytes, same
frozen modules, fresh Harness per prefix.

    python harness/e5d.py

Exit 0 = trajectory complete and consistency checks C1-C4 hold.
Exit 1 = a consistency check failed (published in full).
Exit 2 = abort (frozen hash or feed hash mismatch).
"""

import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from core import Harness, GAP, MIN_SIDE, EPS   # noqa: E402

FREEZE = os.path.join(HERE, "FREEZE.md")
PREREG = os.path.join(HERE, "e5d-prereg.md")
FEED = os.path.join(HERE, "feeds", "brad_e5.json")
OUT = os.path.join(HERE, "e5d-out.txt")
JSONOUT = os.path.join(HERE, "e5d.json")

FEED_SHA = "88716892b5b5f0b5a2a414f2bca6eaa5b27d852640ac25eaf039c5a834e81bdc"

lines = []


def say(text=""):
    lines.append(text)
    print(text, flush=True)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def frozen_from_freeze():
    text = open(FREEZE, "r", encoding="utf-8").read()
    found = {}
    for line in text.splitlines():
        m = re.match(r"\|\s*`([^`]+)`\s*\|\s*`([0-9a-f]{64})`\s*\|", line)
        if m:
            found[m.group(1)] = m.group(2)
    return found


def replay(obs, p, joined):
    """Fresh Harness fed the first p observations. Separate: episodes as
    authored. Joined: one episode. Same observation order either way."""
    h = Harness()
    if joined:
        h.start_episode()
        for _, _, s, err in obs[:p]:
            h.observe(s, err)
    else:
        pos = 0
        cur = None
        for e, i, s, err in obs[:p]:
            if e != cur:
                h.start_episode()
                cur = e
            h.observe(s, err)
            pos += 1
    return h


def best_window(ds):
    """Largest consecutive ratio over the sorted NN list, whether or not it
    reaches GAP. Mirrors core.gap()'s window exactly."""
    if len(ds) < 2 * MIN_SIDE:
        return None
    best = None
    for i in range(MIN_SIDE - 1, len(ds) - MIN_SIDE):
        lo, hi = ds[i], ds[i + 1]
        if lo <= EPS:
            continue
        ratio = hi / lo
        if best is None or ratio > best["ratio"]:
            best = {"i": i, "lo": lo, "hi": hi, "ratio": ratio}
    return best


def multiset_diff(old, new):
    old_c, new_c = {}, {}
    for v in old:
        old_c[v] = old_c.get(v, 0) + 1
    for v in new:
        new_c[v] = new_c.get(v, 0) + 1
    added, removed = [], []
    for v, n in new_c.items():
        extra = n - old_c.get(v, 0)
        added.extend([v] * max(0, extra))
    for v, n in old_c.items():
        extra = n - new_c.get(v, 0)
        removed.extend([v] * max(0, extra))
    return sorted(added), sorted(removed)


def label(obs, k):
    e, i, s, err = obs[k]
    return "ep%d.pos%d" % (e, i)


def main():
    say("E5-D -- cut stability trajectory (diagnostic; repairs nothing)")
    say("prereg sha256 %s" % sha(PREREG))
    say("freeze re-check (read from FREEZE.md):")
    frozen = frozen_from_freeze()
    if not frozen:
        say("ABORT: no hashes parsed from %s" % FREEZE)
        return 2
    ok = True
    for name, want in frozen.items():
        got = sha(os.path.join(HERE, name)) if os.path.exists(
            os.path.join(HERE, name)) else "MISSING"
        state = "ok" if got == want else "CHANGED"
        say("  hash %-12s %s %s" % (name, got[:16], state))
        ok = ok and got == want
    if not ok:
        say("ABORT: the frozen implementation changed. E5-D is invalid.")
        with open(OUT, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        return 2

    if not os.path.isfile(FEED):
        say("ABORT: feed not found at %s" % FEED)
        with open(OUT, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        return 2
    feed_sha = sha(FEED)
    say("feed %s" % FEED)
    say("feed sha256 %s" % feed_sha)
    c1 = feed_sha == FEED_SHA
    say("  C1 feed hash matches the feed E5 ran: %s" % ("PASS" if c1 else "FAIL"))

    feed = json.load(open(FEED, "r", encoding="utf-8"))
    obs = []
    for e, ep in enumerate(feed["blocks"]):
        for i, item in enumerate(ep):
            state, err = item
            obs.append((e, i, tuple(float(x) for x in state), float(err)))
    n = len(obs)
    probe = feed["probes"][0]

    rows = []
    events = []
    prev_nearest = None
    prev_ds = None
    prev_adm = None
    c4_all = True

    for p in range(1, n + 1):
        h = replay(obs, p, joined=False)
        g = h.gap()
        tau = h._tau(g) if g else None
        nearest = h._nearest()
        ds = sorted(d for d, _ in nearest[1:])
        win = best_window(ds)
        _, anchors, _ = h.compression()
        classes = len(anchors)

        hj = replay(obs, p, joined=True)
        gj = hj.gap()
        tj = hj._tau(gj) if gj else None
        if (g is None) != (gj is None):
            c4 = False
        elif g is not None:
            c4 = (abs(g["ratio"] - gj["ratio"]) <= 1e-12
                  and abs(g["lo"] - gj["lo"]) <= 1e-12
                  and abs(g["hi"] - gj["hi"]) <= 1e-12
                  and tau == tj)
        else:
            c4 = tau == tj
        c4_all = c4_all and c4

        newest = nearest[-1][0] if p > 1 else None
        adm = g is not None
        rows.append({
            "p": p, "ep": obs[p - 1][0], "pos": obs[p - 1][1],
            "adm": adm, "gap_ratio": g["ratio"] if g else None,
            "gap_lo": g["lo"] if g else None, "gap_hi": g["hi"] if g else None,
            "gap_low_side": g["low"] if g else None,
            "gap_high_side": g["high"] if g else None,
            "tau": tau, "classes": classes,
            "best_ratio": win["ratio"] if win else None,
            "win_i": win["i"] if win else None,
            "win_lo": win["lo"] if win else None,
            "win_hi": win["hi"] if win else None,
            "newest_nn": newest, "c4": c4,
            "ds": ds,
        })

        if prev_adm is not None and adm != prev_adm:
            changed = []
            for k in range(p - 1):
                old = prev_nearest[k][0]
                new = nearest[k][0]
                if new is not None and old is not None and new < old:
                    changed.append({"obs": label(obs, k),
                                    "old_nn": old, "new_nn": new})
            added, removed = multiset_diff(prev_ds, ds)
            before = best_window(prev_ds)
            below = [v for v in ds if prev_ds and v < min(prev_ds)]
            if before:
                inside = [v for v in added if before["lo"] < v < before["hi"]]
                at_or_below = [v for v in added if v <= before["lo"]]
            else:
                inside, at_or_below = [], []
            events.append({
                "p": p, "cause": label(obs, p - 1),
                "state": list(obs[p - 1][2]), "err": obs[p - 1][3],
                "cause_nn": newest,
                "kind": "lost" if prev_adm else "gained",
                "window_before": before,
                "window_after": win,
                "changed_nn": sorted(changed, key=lambda c: c["old_nn"] - c["new_nn"]),
                "added_distances": added,
                "removed_distances": removed,
                "added_inside_prev_window": inside,
                "added_at_or_below_prev_lo": at_or_below,
            })
        prev_nearest, prev_ds, prev_adm = nearest, ds, adm

    # ---- consistency C2 / C3
    h24 = replay(obs, 24, joined=False)
    named = h24.classify(tuple(probe["prefix"][-1]))
    ex = h24.expect([tuple(s) for s in probe["prefix"]])
    c2 = (named == 1 and ex["support"] == 1)
    say()
    say("C2 replay at p=24 reproduces the E5 probe-time facts:")
    say("  classify(probe last state) = %s (want 1); expect support = %s (want 1),"
        " context %s, k %s"
        % (named, ex["support"], ex["context"], ex["k"]))
    say("  C2 %s" % ("PASS" if c2 else "FAIL"))

    last = rows[-1]
    c3 = (last["gap_ratio"] is None and last["classes"] == 0)
    say()
    say("C3 replay at p=30 reproduces the E5 completed-feed facts: gap %s,"
        " classes %d  ->  %s"
        % ("None" if last["gap_ratio"] is None else "%.3f" % last["gap_ratio"],
           last["classes"], "PASS" if c3 else "FAIL"))
    say("C4 gap and cut identical under a joined-reading replay at every prefix:"
        " %s" % ("PASS" if c4_all else "FAIL"))

    # ---- table
    say()
    say("TRAJECTORY -- frozen Harness per prefix (n=%d observations)" % n)
    say("%-3s %-8s %9s %9s %22s %6s %4s %6s %5s"
        % ("p", "ep.pos", "gapratio", "bestratio", "window lo..hi (i)", "tau",
           "clas", "newest", "C4"))
    for r in rows:
        win_txt = "n/a" if r["win_i"] is None else \
            "%.6f..%.6f (%d)" % (r["win_lo"], r["win_hi"], r["win_i"])
        say("%-3d %-8s %9s %9s %22s %6s %4d %6s %5s"
            % (r["p"], "%d.%d" % (r["ep"], r["pos"]),
               "%.4f" % r["gap_ratio"] if r["adm"] else "-",
               "%.4f" % r["best_ratio"] if r["best_ratio"] is not None else "-",
               win_txt,
               "%.5f" % r["tau"] if r["tau"] is not None else "-",
               r["classes"],
               "%.5f" % r["newest_nn"] if r["newest_nn"] is not None else "-",
               "ok" if r["c4"] else "NO"))

    # ---- admissibility stretches
    say()
    say("ADMISSIBILITY STRETCHES")
    start = 1
    for k in range(2, n + 2):
        if k == n + 1 or rows[k - 1]["adm"] != rows[start - 1]["adm"]:
            say("  p %2d..%-2d  %s"
                % (start, k - 1,
                   "admissible" if rows[start - 1]["adm"] else "inadmissible"))
            start = k

    # ---- events
    say()
    say("EVENTS -- every prefix where admissibility flipped")
    if not events:
        say("  none")
    for ev in events:
        say()
        say("  p=%d %s observation %s (state %s, err %.2f)"
            % (ev["p"], ev["kind"], ev["cause"], ev["state"], ev["err"]))
        say("    its own nearest-neighbour distance: %s"
            % ("%.6f" % ev["cause_nn"] if ev["cause_nn"] is not None else "-"))
        wb = ev["window_before"]
        wa = ev["window_after"]
        say("    window before: %s"
            % ("ratio %.3f at lo %.6f..hi %.6f (i=%d)"
               % (wb["ratio"], wb["lo"], wb["hi"], wb["i"]) if wb else "none"))
        say("    window after:  %s"
            % ("ratio %.3f at lo %.6f..hi %.6f (i=%d)"
               % (wa["ratio"], wa["lo"], wa["hi"], wa["i"]) if wa else "none"))
        if wb and wa:
            say("    added distances inside the old window (lo,hi): %s"
               % (["%.6f" % v for v in ev["added_inside_prev_window"]] or "none"))
            say("    added distances at or below the old lo: %s"
               % (["%.6f" % v for v in ev["added_at_or_below_prev_lo"]] or "none"))
        say("    earlier observations whose NN distance changed: %d"
            % len(ev["changed_nn"]))
        for c in ev["changed_nn"]:
            say("      %-9s %.6f -> %.6f"
                % (c["obs"], c["old_nn"], c["new_nn"]))

    # ---- answers to the prereg questions
    say()
    say("ANSWERS")
    first = next((r["p"] for r in rows if r["adm"]), None)
    say("  cut first admissible at p = %s" % first)
    losses = [e for e in events if e["kind"] == "lost"]
    gains = [e for e in events if e["kind"] == "gained"]
    say("  admissible -> inadmissible at p in %s"
        % ([e["p"] for e in losses] or "never"))
    say("  inadmissible -> admissible at p in %s"
        % ([e["p"] for e in gains] or "never"))
    for e in losses:
        if e["changed_nn"]:
            worst = e["changed_nn"][0]
            say("  the gap died at p=%d: observation %s arrived (own NN %.6f);"
                " %d earlier observation(s) had their NN distance shrink, worst"
                " %s %.6f -> %.6f; %d new distance(s) landed inside the old"
                " window."
                % (e["p"], e["cause"],
                   e["cause_nn"] if e["cause_nn"] is not None else -1,
                   len(e["changed_nn"]), worst["obs"], worst["old_nn"],
                   worst["new_nn"], len(e["added_inside_prev_window"])))
        else:
            say("  the gap died at p=%d via the arriving observation's own NN"
                " distance (%.6f); no earlier NN changed."
                % (e["p"], e["cause_nn"] if e["cause_nn"] is not None else -1))

    verdict = c1 and c2 and c3 and c4_all
    say()
    say("E5-D %s -- diagnosis only; nothing was repaired and no frozen module"
        " changed." % ("COMPLETE" if verdict else "INCONSISTENT"))

    payload = {"prereg_sha256": sha(PREREG), "feed_sha256": feed_sha,
               "gap": GAP, "min_side": MIN_SIDE, "eps": EPS,
               "checks": {"C1": c1, "C2": c2, "C3": c3, "C4": c4_all},
               "rows": [{k: v for k, v in r.items()} for r in rows],
               "events": events}
    with open(JSONOUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1, default=list)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    say("written -> %s, %s" % (OUT, JSONOUT))
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
