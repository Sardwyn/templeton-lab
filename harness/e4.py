"""E4 -- does the cut survive scale? (see e4-prereg.md, frozen 2026-11-09)

Grid: n in {18, 50, 120, 300, 500}, dim in {4, 8, 16}; 50 independent random
and 50 independent structured feeds per cell. 1500 feeds, each with its own
seed derived from (n, dim, kind, index).

Random feeds: every state dim independent draws from Uniform(0,1). The null.
Structured feeds: two clusters at 0 and 0.12*1, jittered Uniform(-0.01,0.01).
The signal.

The measurement is the same scan core.gap() uses. To keep 1500 feeds finite,
the nearest-neighbour list is computed once per feed and reused; the result is
checked against the frozen Harness on the first feed of every cell, and the run
aborts if they differ.

Writes e4-out.txt and e4.json. Exit 0 on pass, 1 on fail, 2 on abort.
"""

import hashlib
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from core import Harness, GAP, MIN_SIDE, EPS   # noqa: E402

PREREG = os.path.join(HERE, "e4-prereg.md")
OUT = os.path.join(HERE, "e4-out.txt")
JSONOUT = os.path.join(HERE, "e4.json")

FROZEN = {
    "core.py": "8734d335a14810424296629c8500a5edda5b09b364c7f9387a42aee87aa0f150",
    "measure.py": "1c9f076dcaafb274947cf61e6ac88cc7e86425ffb4d79b72983fb6798967c06f",
    "run.py": "5440c370ff6c5ac764d8a02ae1bf71ab794f2b82b3a234a07abc01deccfc2b42",
    "scenarios.py": "bc8e40d22b65b1397914c1a8ad553a2184d775d90b8966b2e33a0de87342ef22",
    "audit.py": "e1cd2ee14e996ae122f8ad1633b27e1cbf0bae72f686fdc3560b40eba483e6be",
    "e1.py": "720f90ac910c48240494409174af6cb22c1bda75f1552f0c2bf3576ff4719a8f",
}

NS = [18, 50, 120, 300, 500]
DIMS = [4, 8, 16]
R = 50
D = 0.12
JIT = 0.01
Z = 1.959963984540054

lines = []


def say(text=""):
    lines.append(text)
    print(text, flush=True)


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


# ---------------------------------------------------------------- measurement
def dist(a, b, dim):
    s = 0.0
    for k in range(dim):
        s += abs(a[k] - b[k])
    return s / dim


def nearest_all(states, dim):
    """core._nearest(), inlined for speed; identical arithmetic order."""
    out, seen = [], []
    for s in states:
        if seen:
            bd, bi = None, -1
            for i, p in enumerate(seen):
                d = dist(p, s, dim)
                if bd is None or d < bd:
                    bd, bi = d, i
            out.append((bd, bi))
        else:
            out.append((None, -1))
        seen.append(s)
    return out


def gap_from_ds(ds):
    """core.Harness.gap(), over a pre-sorted nn list."""
    if len(ds) < 2 * MIN_SIDE:
        return None
    best = None
    for i in range(MIN_SIDE - 1, len(ds) - MIN_SIDE):
        lo, hi = ds[i], ds[i + 1]
        if lo <= EPS:
            continue
        ratio = hi / lo
        if ratio >= GAP and (best is None or ratio > best["ratio"]):
            best = {"ratio": ratio, "lo": lo, "hi": hi,
                    "tau": (lo + hi) / 2.0}
    return best


def chance_from_ds(ds):
    """The largest valid consecutive ratio, whether or not it reaches GAP."""
    if len(ds) < 2 * MIN_SIDE:
        return None
    best = None
    for i in range(MIN_SIDE - 1, len(ds) - MIN_SIDE):
        lo, hi = ds[i], ds[i + 1]
        if lo <= EPS:
            continue
        ratio = hi / lo
        if best is None or ratio > best:
            best = ratio
    return best


def partition(nearest, tau):
    """core.Harness.compression()'s grouping, without the retained anchors."""
    ids, nxt = [], 0
    for d, j in nearest:
        if d is not None and d < tau:
            ids.append(ids[j])
        else:
            ids.append(nxt)
            nxt += 1
    return ids, nxt


def split6(states):
    base, rem = divmod(len(states), 6)
    out, pos = [], 0
    for e in range(6):
        size = base + (1 if e < rem else 0)
        out.append(states[pos:pos + size])
        pos += size
    return out


def as_harness(states):
    h = Harness()
    for chunk in split6(states):
        h.start_episode()
        for s in chunk:
            h.observe(s, 0.0)
    return h


def verify(states, dim, nearest, gap, classes):
    """The inlined measurement must equal the frozen Harness on the sample."""
    h = as_harness(states)
    hg = h.gap()
    hcls = len(h.classes()[1]) if hg is not None else 0
    if (hg is None) != (gap is None):
        return False
    if hg is not None:
        for key in ("ratio", "lo", "hi", "tau"):
            if abs(hg[key] - gap[key]) > 1e-12:
                return False
    return hcls == classes


# ---------------------------------------------------------------- feeds
def seed_for(n, dim, kind, idx):
    return (20261109 + 1000003 * n + 10007 * dim + 1009 * kind
            + 7 * idx + 13)


def random_feed(n, dim, seed):
    rng = random.Random(seed)
    return [tuple(rng.random() for _ in range(dim)) for _ in range(n)]


def structured_feed(n, dim, seed):
    rng = random.Random(seed)
    half = n // 2
    points = []
    for c in (0, 1):
        base = D * c
        for _ in range(half):
            points.append((tuple(base + rng.uniform(-JIT, JIT)
                                 for _ in range(dim)), c))
    rng.shuffle(points)
    return [p[0] for p in points], [p[1] for p in points]


def authored_interval(states, labels, dim):
    lo, hi = 0.0, float("inf")
    for i in range(len(states)):
        same, other = None, None
        for j in range(len(states)):
            if i == j:
                continue
            d = dist(states[i], states[j], dim)
            if labels[j] == labels[i]:
                if same is None or d < same:
                    same = d
            else:
                if other is None or d < other:
                    other = d
        if same is None or other is None:
            return None, lo, hi
        lo = max(lo, same)
        hi = min(hi, other)
    return (lo, hi), lo, hi


# ---------------------------------------------------------------- stats
def pct(xs, q):
    if not xs:
        return None
    ys = sorted(xs)
    pos = (len(ys) - 1) * q
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(ys) - 1)
    return ys[lo] + (ys[hi] - ys[lo]) * (pos - lo)


def wilson_upper(k, n, z=Z):
    if n == 0:
        return 1.0
    p = k / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2.0 * n)) / denom
    half = z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n)) / denom
    return centre + half


def fnum(x, places=4):
    return "n/a" if x is None else ("%%.%df" % places) % x


# ---------------------------------------------------------------- main
def main():
    say("E4 -- cut scaling and chance-ratio distribution")
    say("prereg sha256 %s" % sha(PREREG))
    say("frozen set checked against FREEZE.md:")
    if not check_hashes():
        say("ABORT: the frozen implementation changed. E4 is invalid.")
        with open(OUT, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        return 2

    say()
    say("grid: n %s x dim %s, R=%d random + %d structured per cell"
        % (NS, DIMS, R, R))
    say("GAP=%.2f  MIN_SIDE=%d  EPS=%g  D=%.2f  jitter=+/-%.2f"
        % (GAP, MIN_SIDE, EPS, D, JIT))

    rand = {}
    struct = {}
    records = []
    verified = 0
    total = len(NS) * len(DIMS) * 2 * R
    done = 0

    for kind, table in (("random", rand), ("structured", struct)):
        for n in NS:
            for dim in DIMS:
                cell = []
                for idx in range(R):
                    seed = seed_for(n, dim, 0 if kind == "random" else 1, idx)
                    if kind == "random":
                        states = random_feed(n, dim, seed)
                        labels = None
                    else:
                        states, labels = structured_feed(n, dim, seed)

                    nearest = nearest_all(states, dim)
                    ds = sorted(d for d, _ in nearest[1:])
                    chance = chance_from_ds(ds)
                    g = gap_from_ds(ds)
                    cut = g["tau"] if g else None

                    if g is not None:
                        _, classes = partition(nearest, cut)
                    else:
                        classes = 0

                    rec = {"n": n, "dim": dim, "kind": kind, "index": idx,
                           "seed": seed, "chance_ratio": chance,
                           "gap_found": g is not None,
                           "gap_ratio": g["ratio"] if g else None,
                           "cut": cut, "classes": classes}
                    if kind == "structured":
                        interval, lo, hi = authored_interval(states, labels, dim)
                        rec["lo_auth"] = lo if interval else None
                        rec["hi_auth"] = hi if interval else None
                        rec["not_separable"] = interval is None
                        rec["cut_inside"] = bool(
                            interval and lo < cut < hi) if g else False
                        rec["interval_width"] = (hi - lo) if interval else None
                    cell.append(rec)
                    records.append(rec)

                    if idx == 0:
                        if not verify(states, dim, nearest, g, classes):
                            say()
                            say("ABORT: inlined measurement diverged from the "
                                "frozen Harness at n=%d dim=%d %s idx=0."
                                % (n, dim, kind))
                            with open(OUT, "w", encoding="utf-8") as f:
                                f.write("\n".join(lines) + "\n")
                            return 2
                        verified += 1

                    done += 1
                    if done % 50 == 0:
                        print("  %d/%d feeds" % (done, total), flush=True)

                table[(n, dim)] = cell
                print("cell %-10s n=%-3d dim=%-2d done" % (kind, n, dim),
                      flush=True)

    say()
    say("verification: %d cell samples matched the frozen Harness exactly"
        % verified)

    # ---- random table
    say()
    say("RANDOM FEEDS -- chance nearest-neighbour ratio")
    say("%-4s %-4s %8s %8s %8s %8s %8s %6s %7s %9s"
        % ("n", "dim", "median", "p90", "p95", "p99", "max",
           "FP", "FPfrac", "med cut"))
    pooled_fp = 0
    cell_p95 = {}
    for n in NS:
        for dim in DIMS:
            cell = rand[(n, dim)]
            xs = [r["chance_ratio"] for r in cell if r["chance_ratio"] is not None]
            fps = sum(1 for r in cell if r["gap_found"])
            cuts = [r["cut"] for r in cell if r["cut"] is not None]
            pooled_fp += fps
            cell_p95[(n, dim)] = pct(xs, 0.95)
            say("%-4d %-4d %8s %8s %8s %8s %8s %6d %7.3f %9s"
                % (n, dim, fnum(pct(xs, 0.50)), fnum(pct(xs, 0.90)),
                   fnum(pct(xs, 0.95)), fnum(pct(xs, 0.99)),
                   fnum(max(xs) if xs else None), fps, fps / len(cell),
                   fnum(pct(cuts, 0.50), 6)))

    # ---- structured table
    say()
    say("STRUCTURED FEEDS -- authored separation")
    say("%-4s %-4s %8s %8s %8s %8s %9s %10s %8s"
        % ("n", "dim", "med ch", "gap fnd", "cut in", "class2", "med cut",
           "med width", "not sep"))
    all_power_ok = True
    for n in NS:
        for dim in DIMS:
            cell = struct[(n, dim)]
            xs = [r["chance_ratio"] for r in cell if r["chance_ratio"] is not None]
            gf = sum(1 for r in cell if r["gap_found"]) / len(cell)
            ci = sum(1 for r in cell if r["cut_inside"]) / len(cell)
            c2 = sum(1 for r in cell if r["classes"] == 2) / len(cell)
            cuts = [r["cut"] for r in cell if r["cut"] is not None]
            widths = [r["interval_width"] for r in cell
                      if r["interval_width"] is not None]
            ns = sum(1 for r in cell if r["not_separable"])
            if ci < 0.80:
                all_power_ok = False
            say("%-4d %-4d %8s %8.3f %8.3f %8.3f %9s %10s %8d"
                % (n, dim, fnum(pct(xs, 0.50)), gf, ci, c2,
                   fnum(pct(cuts, 0.50), 6), fnum(pct(widths, 0.50), 4), ns))

    # ---- pooled FPR
    N = len(NS) * len(DIMS) * R
    upper = wilson_upper(pooled_fp, N)
    say()
    say("POOLED FALSE-POSITIVE RATE (random feeds)")
    say("  %d / %d = %.4f" % (pooled_fp, N, pooled_fp / N))
    say("  95%% Wilson upper bound: %.4f  (pass bar <= 0.05)" % upper)
    flagged = [(n, dim) for n in NS for dim in DIMS
               if sum(1 for r in rand[(n, dim)] if r["gap_found"]) / R > 0.10]
    say("  cells with per-cell FPR > 0.10: %s"
        % (flagged if flagged else "none"))

    # ---- trend
    say()
    say("TREND -- median and p95 chance ratio")
    say("  by n (random, pooled over dim):")
    for n in NS:
        xs = [r["chance_ratio"] for dim in DIMS for r in rand[(n, dim)]
              if r["chance_ratio"] is not None]
        say("    n=%-3d median %s  p95 %s"
            % (n, fnum(pct(xs, 0.50)), fnum(pct(xs, 0.95))))
    say("  by dim (random, pooled over n):")
    for dim in DIMS:
        xs = [r["chance_ratio"] for n in NS for r in rand[(n, dim)]
              if r["chance_ratio"] is not None]
        say("    dim=%-2d median %s  p95 %s"
            % (dim, fnum(pct(xs, 0.50)), fnum(pct(xs, 0.95))))
    at_risk = [(n, dim) for (n, dim), v in cell_p95.items()
               if v is not None and v >= GAP]
    say("  cells with per-cell p95 >= GAP: %s"
        % (at_risk if at_risk else "none"))

    # ---- verdict
    ok = upper <= 0.05 and all_power_ok
    say()
    say("E4 %s" % ("PASS" if ok else "FAIL"))
    if upper > 0.05:
        say("  FPR condition failed: pooled Wilson upper %.4f > 0.05" % upper)
    if not all_power_ok:
        bad = []
        for n in NS:
            for dim in DIMS:
                cell = struct[(n, dim)]
                ci = sum(1 for r in cell if r["cut_inside"]) / len(cell)
                if ci < 0.80:
                    bad.append((n, dim, ci))
        say("  power condition failed in %d cell(s): %s" % (len(bad), bad))

    with open(JSONOUT, "w", encoding="utf-8") as f:
        json.dump({"prereg_sha256": sha(PREREG), "gap": GAP,
                   "min_side": MIN_SIDE, "R": R, "D": D, "jitter": JIT,
                   "records": records}, f, indent=1)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    say("written -> %s, %s" % (OUT, JSONOUT))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
