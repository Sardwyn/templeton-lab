"""E2 -- fixed-lag interleaving against a same-information baseline.

See `e2-prereg.md` (frozen 2026-11-09). This file imports the frozen modules
and never edits them. It re-checks every hash in `FREEZE.md` and the hash of the
pre-registration before it does anything else.

The feed: two 3-cycles, A and B, interleaved at lag two.

    A0 B0 A1 B1 A2 B2 | A0 B0 A1 B1 A2 B2 | ...   (8 episodes, 48 positions)

Eight episodes of six states each, holdout_from = 4, so 24 positions train and
24 are predicted one at a time.

The load-bearing comparison is against B1, a raw-prefix nearest neighbour that
has the same context length, the same cut, and the same memory as the harness,
but never compresses to recurrences. B0 (exact raw-suffix longest match) is
reported as a floor and is not the pass bar.

Writes e2-out.txt. Exit 0 on pass, 1 on fail, 2 on abort.
"""

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import scenarios as S          # noqa: E402
import measure as M            # noqa: E402
from core import Harness, K, GAP, _dist   # noqa: E402

PREREG = os.path.join(HERE, "e2-prereg.md")
OUT = os.path.join(HERE, "e2-out.txt")

FROZEN = {
    "core.py": "8734d335a14810424296629c8500a5edda5b09b364c7f9387a42aee87aa0f150",
    "measure.py": "1c9f076dcaafb274947cf61e6ac88cc7e86425ffb4d79b72983fb6798967c06f",
    "run.py": "5440c370ff6c5ac764d8a02ae1bf71ab794f2b82b3a234a07abc01deccfc2b42",
    "scenarios.py": "bc8e40d22b65b1397914c1a8ad553a2184d775d90b8966b2e33a0de87342ef22",
    "audit.py": "e1cd2ee14e996ae122f8ad1633b27e1cbf0bae72f686fdc3560b40eba483e6be",
    "e1.py": "720f90ac910c48240494409174af6cb22c1bda75f1552f0c2bf3576ff4719a8f",
}

HOLDOUT = 4
EPISODES = 8
ORDER = ["A0", "B0", "A1", "B1", "A2", "B2"]

BASE = {
    "A0": (0.00, 0.00, 0.0, 0.0),
    "A1": (0.50, 0.00, 0.0, 0.0),
    "A2": (0.25, 0.45, 0.0, 0.0),
    "B0": (0.00, 0.00, 0.6, 0.0),
    "B1": (0.50, 0.00, 0.6, 0.0),
    "B2": (0.25, 0.45, 0.6, 0.0),
}

ERR = {"A0": 0.10, "A1": 0.30, "A2": 0.50,
       "B0": 0.20, "B1": 0.40, "B2": 0.60}

AMP = 0.008

lines = []


def say(text=""):
    lines.append(text)
    print(text)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def check_hashes():
    good = True
    for name, want in FROZEN.items():
        got = sha(os.path.join(HERE, name))
        state = "ok" if got == want else "CHANGED"
        say("hash %-12s %s %s" % (name, got[:16], state))
        good = good and got == want
    return good


# ---------------------------------------------------------------- feed
def build():
    """Eight identical interleaved 6-cycles. The jitter seed depends on
    (episode, position), so every visit is a different observation of the same
    authored region; nothing in the feed names a family or a lag."""
    blocks = []
    for b in range(EPISODES):
        block = []
        for i, name in enumerate(ORDER):
            state = S.jittered(BASE[name], 6000 + 100 * b + i, AMP)
            block.append((state, ERR[name]))
        blocks.append(block)
    return blocks


# ---------------------------------------------------------------- baselines
def b1_predict(h, probe, tau):
    """Raw-prefix nearest neighbour with the same K, cut and memory.

    Candidate = a position with k predecessors and a successor in its own
    episode. Distance is the mean _dist between the probe's last k raw states
    and the candidate's last k raw states. Under the cut, predict the class of
    the candidate's successor; otherwise decline.
    """
    k = min(K, len(probe))
    if k <= 0 or tau is None:
        return None
    best = None
    for ep in h.memory:
        for cand in range(k - 1, len(ep) - 1):
            d = sum(_dist(probe[-k + t], ep[cand - k + 1 + t][0])
                    for t in range(k)) / k
            if best is None or d < best[0]:
                best = (d, h.classify(ep[cand + 1][0]))
    if best is None:
        return None
    d, cls = best
    return cls if (d < tau and cls is not None) else None


def b0_predict(h, probe):
    """Longest suffix of the raw probe (1..K) occurring verbatim as a
    contiguous subsequence with a successor. Among equally long matches, the
    most common successor class wins; ties go to the earliest match."""
    if not probe:
        return None
    for length in range(min(K, len(probe)), 0, -1):
        suffix = tuple(probe[-length:])
        counts, first = {}, {}
        for ep in h.memory:
            for j in range(0, len(ep) - length):
                if tuple(s for s, _ in ep[j:j + length]) == suffix:
                    cls = h.classify(ep[j + length][0])
                    if cls is not None:
                        counts[cls] = counts.get(cls, 0) + 1
                        first.setdefault(cls, j)
        if counts:
            return max(counts, key=lambda c: (counts[c], -first[c]))
    return None


# ---------------------------------------------------------------- anticipation
def anticipate_with_baselines(h, blocks, start, joined, k=K):
    """A line-for-line mirror of measure.anticipate that also asks B0 and B1
    *before* the state is observed. The caller asserts the harness fields match
    measure.anticipate exactly, so the mirror cannot quietly drift."""
    decline = {"context": None, "k": 0, "support": 0, "confidence": 0.0,
               "predict": None, "err": None, "competitors": []}
    out = []
    pos = 0
    for b in range(start, len(blocks)):
        if joined and h.memory:
            h.episode = h.memory[-1]
        else:
            h.start_episode()
        first = True
        for state, err in blocks[b]:
            probe = [o[0] for o in h.memory[-1]][-k:] if h.memory else []
            tau = h._tau(h.gap())
            e = h.expect(probe) if probe else decline
            actual = h.classify(state)
            hit = e["predict"] is not None and actual is not None \
                and e["predict"] == actual
            out.append({
                "block": b, "boundary": first, "pos": pos,
                "asked": e["k"], "hit": hit, "declined": e["k"] == 0,
                "predict": e["predict"], "actual": actual,
                "confidence": e["confidence"], "support": e["support"],
                "err": e["err"], "rivals": len(e["competitors"]),
                "observed_err": err,
                "b1": b1_predict(h, probe, tau),
                "b0": b0_predict(h, probe),
                "tau": tau,
            })
            h.observe(state, err)
            pos += 1
            first = False
    return out


ROW_FIELDS = ("block", "boundary", "pos", "asked", "hit", "declined",
              "predict", "actual", "confidence", "support", "err", "rivals",
              "observed_err")


def same_harness_rows(a, b):
    if len(a) != len(b):
        return False
    return all(tuple(x[f] for f in ROW_FIELDS) == tuple(y[f] for f in ROW_FIELDS)
               for x, y in zip(a, b))


# ---------------------------------------------------------------- measurement
def region_of(episode, index):
    return ORDER[index % len(ORDER)]


def region_map(h):
    assign, _, _ = h.compression()
    members, spans = {}, {}
    for (e, i), cid in assign.items():
        members.setdefault(cid, []).append((e, i))
    for cid, ms in members.items():
        spans[cid] = sorted({region_of(e, i) for e, i in ms})
    return assign, members, spans


def acc(rows, pred_key, hit_key):
    answered = [r for r in rows if r[hit_key] is not None]
    hits = sum(1 for r in answered if r[hit_key])
    return len(answered), hits, (hits / len(answered) if answered else 0.0)


def harness_stats(rows):
    asked = [r for r in rows if r["asked"]]
    hits = sum(1 for r in asked if r["hit"])
    return len(asked), hits, (hits / len(asked) if asked else 0.0)


def baseline_stats(rows, key):
    answered = [r for r in rows if r[key] is not None]
    hits = sum(1 for r in answered
               if r["actual"] is not None and r[key] == r["actual"])
    return len(answered), hits, (hits / len(answered) if answered else 0.0)


def main():
    say("E2 -- fixed-lag interleaving vs a same-information raw-prefix baseline")
    say("prereg sha256 %s" % sha(PREREG))
    say("frozen set checked against FREEZE.md:")
    if not check_hashes():
        say("ABORT: the frozen implementation changed. E2 is invalid.")
        with open(OUT, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        return 2

    blocks = build()
    say()
    say("feed: %d episodes x %d states, holdout_from=%d, %d positions predicted"
        % (len(blocks), len(blocks[0]), HOLDOUT,
           (len(blocks) - HOLDOUT) * len(blocks[0])))
    say("order per episode: %s" % " ".join(ORDER))
    say("jitter amp %.3f on components 0 and 3; per-visit seeds" % AMP)

    results = {}
    for reading, joined in (("joined", True), ("separate", False)):
        # official rows, from the frozen instrument
        h_off = Harness()
        M.feed(h_off, blocks, joined, 0, HOLDOUT)
        rows_off = M.anticipate(h_off, blocks, HOLDOUT, joined)
        shape_off = M.shape(h_off)

        # mirror rows, with the baselines asked at the same instant
        h = Harness()
        M.feed(h, blocks, joined, 0, HOLDOUT)
        rows = anticipate_with_baselines(h, blocks, HOLDOUT, joined)
        if not same_harness_rows(rows_off, rows):
            say()
            say("ABORT: the E2 mirror diverged from measure.anticipate in the "
                "%s reading. No result is reported." % reading)
            with open(OUT, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
            return 2

        shape = M.shape(h)
        assign, members, spans = region_map(h)
        asked, hits, h_acc = harness_stats(rows)
        b1_n, b1_hits, b1_acc = baseline_stats(rows, "b1")
        b0_n, b0_hits, b0_acc = baseline_stats(rows, "b0")
        paired = [r for r in rows if r["asked"] and r["b1"] is not None]
        p_hits = sum(1 for r in paired if r["hit"])
        p_b1 = sum(1 for r in paired
                   if r["actual"] is not None and r["b1"] == r["actual"])
        p_h = p_hits / len(paired) if paired else 0.0
        p_b = p_b1 / len(paired) if paired else 0.0

        results[reading] = {
            "joined": joined, "shape": shape, "rows": rows,
            "members": members, "spans": spans,
            "asked": asked, "hits": hits, "h_acc": h_acc,
            "b1_n": b1_n, "b1_hits": b1_hits, "b1_acc": b1_acc,
            "b0_n": b0_n, "b0_hits": b0_hits, "b0_acc": b0_acc,
            "paired": len(paired), "p_h": p_h, "p_b": p_b,
        }

        say()
        say("--- %s reading ---" % reading)
        g = shape["gap"]
        say("STRUCTURE")
        say("  states %d  episodes %d  classes %d  sizes %s"
            % (shape["states"], shape["episodes"], shape["classes"],
               sorted(shape["sizes"].values(), reverse=True)))
        say("  gap %s" % ("none" if g is None else
                          "ratio %.3f  lo %.6f  hi %.6f  cut %.6f"
                          % (g["ratio"], g["lo"], g["hi"], shape["tau"])))
        say("  class -> authored region(s): %s"
            % {c: spans[c] for c in sorted(spans)})
        crosses = [c for c in spans if len(spans[c]) != 1]
        say("  classes spanning more than one region: %s"
            % (crosses if crosses else "none"))

        say("PREDICTION (harness)")
        say("  asked %d  declined %d  hits %d  accuracy %.3f"
            % (asked, len(rows) - asked, hits, h_acc))
        say("PREDICTION (B1 raw-prefix NN, same K/cut/memory)")
        say("  answered %d  hits %d  accuracy %.3f" % (b1_n, b1_hits, b1_acc))
        say("PREDICTION (B0 exact-suffix longest match, floor)")
        say("  answered %d  hits %d  accuracy %.3f" % (b0_n, b0_hits, b0_acc))
        say("PAIRED (both answer)")
        say("  positions %d  harness %.3f  B1 %.3f  delta %+.3f"
            % (len(paired), p_h, p_b, p_h - p_b))

        # ---- claims, per reading
        gap_ok = g is not None and g["ratio"] >= GAP
        sizes_ok = sorted(shape["sizes"].values()) == [8] * 6
        s1 = (shape["classes"] == 6 and sizes_ok and gap_ok
              and not crosses)
        regions_seen = set()
        for c in spans:
            regions_seen.update(spans[c])
        s2 = (len(spans) == 6 and not crosses
              and regions_seen == set(ORDER)
              and all(len(spans[c]) == 1 for c in spans))
        p1 = h_acc >= 0.80
        p2_engaged = len(paired) >= 3
        p2 = (p2_engaged and (p_h >= p_b + 0.10)
              and asked >= b1_n)
        say("CLAIMS")
        say("  S1 six classes of 8 at a gap >= %.2f, no cross-region merge: %s"
            % (GAP, "PASS" if s1 else "FAIL"))
        say("  S2 region-to-class bijection, no composite label: %s"
            % ("PASS" if s2 else "FAIL"))
        say("  P1 harness accuracy >= 0.80: %s (%.3f)"
            % ("PASS" if p1 else "FAIL", h_acc))
        if not p2_engaged:
            say("  P2 harness >= B1 + 0.10 on paired positions: FAIL "
                "(inconclusive: baseline answered %d paired position(s) < 3)"
                % len(paired))
        else:
            say("  P2 harness >= B1 + 0.10 on paired positions: %s "
                "(%.3f vs %.3f; answered %d vs %d)"
                % ("PASS" if p2 else "FAIL", p_h, p_b, asked, b1_n))
        say("  P3 B0 floor: reported, not a pass bar (answered %d)" % b0_n)

        results[reading]["verdict"] = {
            "S1": s1, "S2": s2, "P1": p1, "P2": p2,
            "P2_engaged": p2_engaged,
        }

    # ---- E2 is decided on the joined reading, stated before the run
    r = results["joined"]
    v = r["verdict"]
    ok = v["S1"] and v["S2"] and v["P1"] and v["P2"]
    say()
    say("E2 is decided on the joined reading (e2-prereg.md).")
    say("E2 %s" % ("PASS" if ok else "FAIL"))
    if not v["P2_engaged"]:
        say("P2 was not applicable: the baseline did not engage. This is "
            "recorded as FAIL (inconclusive), not as a pass.")
    say("Separate reading reported alongside; it does not decide the rung.")

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    say("written -> %s" % OUT)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
