"""E3 -- coordinate-disjoint isomorphic families (see e3-prereg.md).

Frozen 2026-11-09. The original E3 (permute the components) is vacuous under P1:
mean absolute deviation is permutation-invariant, so it changes no distance, no
cut, no class and no prediction. This runner measures that no-op as S0, then
runs the non-vacuous replacement: the same triangle in two disjoint coordinate
subspaces, trained on family A and then delivered family B.

Only outcome (a) -- three classes at the derived cut, each pairing A_i with B_i
-- passes. The expected result is (b) or (c).

Writes e3-out.txt. Exit 0 on (a), 1 on any other outcome, 2 on abort.
"""

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import scenarios as S          # noqa: E402
import measure as M            # noqa: E402
from core import Harness, K, GAP, _dist   # noqa: E402

PREREG = os.path.join(HERE, "e3-prereg.md")
OUT = os.path.join(HERE, "e3-out.txt")

FROZEN = {
    "core.py": "8734d335a14810424296629c8500a5edda5b09b364c7f9387a42aee87aa0f150",
    "measure.py": "1c9f076dcaafb274947cf61e6ac88cc7e86425ffb4d79b72983fb6798967c06f",
    "run.py": "5440c370ff6c5ac764d8a02ae1bf71ab794f2b82b3a234a07abc01deccfc2b42",
    "scenarios.py": "bc8e40d22b65b1397914c1a8ad553a2184d775d90b8966b2e33a0de87342ef22",
    "audit.py": "e1cd2ee14e996ae122f8ad1633b27e1cbf0bae72f686fdc3560b40eba483e6be",
    "e1.py": "720f90ac910c48240494409174af6cb22c1bda75f1552f0c2bf3576ff4719a8f",
}

HOLDOUT = 4
CYCLES = 4
AMP = 0.008
PERM = (2, 3, 0, 1)
T = (0.0, 0.0, 2.0, 2.0)

BASE_A = [(0.00, 0.00, 0.0, 0.0),
          (0.50, 0.00, 0.0, 0.0),
          (0.25, 0.40, 0.0, 0.0)]

# Error values are not fixed by the pre-registration. They cannot affect P1 or
# P2: every 2-context in this feed has a single observed continuation, so the
# error tie-break is never reached. Fixed here, once, in the pattern used by E2.
ERR_A = [0.10, 0.30, 0.50]
ERR_B = [0.20, 0.40, 0.60]

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


def perm(x):
    return tuple(x[i] for i in PERM)


def translate(x, t):
    return tuple(a + b for a, b in zip(x, t))


BASE_B = [translate(perm(a), T) for a in BASE_A]


def build():
    """Four A cycles, then four B cycles, each a 3-state episode."""
    blocks = []
    for c in range(CYCLES):
        blocks.append([(S.jittered(BASE_A[i], 8000 + 100 * c + i, AMP), ERR_A[i])
                       for i in range(3)])
    for c in range(CYCLES):
        blocks.append([(S.jittered(BASE_B[i], 8500 + 100 * c + i, AMP), ERR_B[i])
                       for i in range(3)])
    return blocks


# ---------------------------------------------------------------- partition
def region_names(h, joined):
    """The authored region of every observation, in memory order. In the joined
    reading one episode holds the whole stream, so the global position carries
    the block; in the separate reading the episode index is the block."""
    out = []
    pos = 0
    for e, ep in enumerate(h.memory):
        for i in range(len(ep)):
            if joined:
                block, k = pos // 3, pos % 3
            else:
                block, k = e, i
            out.append(("A" if block < CYCLES else "B") + str(k))
            pos += 1
    return out


def spans_at(h, tau, nearest=None, joined=False):
    """P6 single-linkage at a chosen cut, without touching core.py."""
    if nearest is None:
        nearest = h._nearest()
    ids, nxt = [], 0
    for d, j in nearest:
        if d is not None and d < tau:
            ids.append(ids[j])
        else:
            ids.append(nxt)
            nxt += 1
    regions = region_names(h, joined)
    spans = {}
    for cid, reg in zip(ids, regions):
        spans.setdefault(cid, set()).add(reg)
    return ids, spans


def paired_three(spans):
    """Exactly three classes, each pairing A_i with B_i for the three i."""
    if len(spans) != 3:
        return False, None
    seen = set()
    for regs in spans.values():
        if len(regs) != 2:
            return False, None
        a = [r for r in regs if r.startswith("A")]
        b = [r for r in regs if r.startswith("B")]
        if len(a) != 1 or len(b) != 1 or a[0][1:] != b[0][1:]:
            return False, None
        seen.add(a[0][1:])
    return seen == {"0", "1", "2"}, seen


def cross_cut(h, nearest=None, joined=False):
    """Smallest cut at which any A observation joins a B observation."""
    obs = [o[2] for o in h.observations()]
    regions = region_names(h, joined)
    best = None
    for i in range(len(obs)):
        for j in range(i):
            if regions[i][0] == regions[j][0]:
                continue
            d = _dist(obs[i], obs[j])
            if best is None or d < best:
                best = d
    return best


def partition_candidates(h, nearest, joined):
    """Every distinct P6 partition as the cut rises, with its cut interval."""
    obs = [o[2] for o in h.observations()]
    ds = []
    for i in range(len(obs)):
        for j in range(i):
            ds.append(_dist(obs[i], obs[j]))
    ds = sorted(set(ds))
    cuts = []
    for k in range(len(ds) - 1):
        cuts.append((ds[k] + ds[k + 1]) / 2.0)
    cuts.append(ds[-1] * 1.01 + 1e-9 if ds else 1.0)
    out = []
    for tau in cuts:
        ids, spans = spans_at(h, tau, nearest, joined)
        out.append((tau, len(spans), spans))
    return out


# ---------------------------------------------------------------- main
def main():
    say("E3 -- coordinate-disjoint isomorphic families")
    say("prereg sha256 %s" % sha(PREREG))
    say("frozen set checked against FREEZE.md:")
    if not check_hashes():
        say("ABORT: the frozen implementation changed. E3 is invalid.")
        with open(OUT, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        return 2

    # ---- S0: the no-op the original E3 mistook for a test
    say()
    say("S0 -- P1 is permutation-invariant (the reason the original E3 cannot stand)")
    worst = 0.0
    base = BASE_A + BASE_B
    for x in base:
        for y in base:
            d0 = _dist(x, y)
            d1 = _dist(perm(x), perm(y))
            worst = max(worst, abs(d0 - d1))
    say("  worst |_dist(x,y) - _dist(perm(x),perm(y))| over all authored pairs: %.3e"
        % worst)
    s0 = worst <= 1e-12
    say("  S0 %s" % ("PASS (no-op confirmed)" if s0 else "FAIL"))

    blocks = build()
    say()
    say("feed: %d episodes x 3 states, holdout_from=%d" % (len(blocks), HOLDOUT))
    say("  A cycles 0-3: %s" % " -> ".join("A%d" % i for i in range(3)))
    say("  B cycles 4-7: %s" % " -> ".join("B%d" % i for i in range(3)))
    say("  within-family base distances: A0-A1 %.4f, A1-A2 %.4f, A0-A2 %.4f"
        % (_dist(BASE_A[0], BASE_A[1]), _dist(BASE_A[1], BASE_A[2]),
           _dist(BASE_A[0], BASE_A[2])))
    say("  nearest cross-family base distance: %.4f"
        % min(_dist(a, b) for a in BASE_A for b in BASE_B))
    say("  B = perm(A) + %s with perm=%s" % (T, PERM))

    results = {}
    for reading, joined in (("separate", False), ("joined", True)):
        h = Harness()
        M.feed(h, blocks, joined, 0, HOLDOUT)
        rows = M.anticipate(h, blocks, HOLDOUT, joined)
        shape = M.shape(h)
        g = shape["gap"]
        nearest = h._nearest()

        mapA = [h.classify(x) for x in BASE_A]
        mapB = [h.classify(x) for x in BASE_B]

        # P1: within-family prediction from the authored bases, after the feed
        p1_rows = []
        for fam, states, cmap in (("A", BASE_A, mapA), ("B", BASE_B, mapB)):
            for i in range(3):
                nxt = (i + 2) % 3
                out = h.expect([states[i], states[(i + 1) % 3]])
                p1_rows.append({
                    "fam": fam, "from": "%s%d,%s%d" % (fam, i, fam, (i + 1) % 3),
                    "want": "%s%d" % (fam, nxt),
                    "got": out["predict"], "want_cls": cmap[nxt],
                    "k": out["k"], "support": out["support"],
                    "hit": out["predict"] is not None and out["predict"] == cmap[nxt],
                })
        p1 = all(r["hit"] for r in p1_rows)

        # P2: transfer under the planted state correspondence
        transfers = []
        for i in range(3):
            nxt = (i + 2) % 3
            a = h.expect([BASE_A[i], BASE_A[(i + 1) % 3]])
            b = h.expect([BASE_B[i], BASE_B[(i + 1) % 3]])
            ok = (a["predict"] is not None and b["predict"] is not None
                  and a["predict"] == mapA[nxt] and b["predict"] == mapB[nxt])
            transfers.append({
                "i": i, "a_pred": a["predict"], "a_want": mapA[nxt],
                "b_pred": b["predict"], "b_want": mapB[nxt],
                "mapped_back": mapA[nxt], "ok": ok,
            })
        n_transfer = sum(1 for t in transfers if t["ok"])

        # derived-cut partition
        ids, spans = spans_at(h, shape["tau"], nearest, joined) if g else ([], {})
        classes = len(spans)
        a_ok, a_seen = paired_three(spans)

        # (b): is there ANY cut that yields three paired classes?
        best_b = None
        for tau, k, sp in partition_candidates(h, nearest, joined):
            ok, _ = paired_three(sp)
            if ok and (best_b is None or tau < best_b[0]):
                best_b = (tau, k, sp)
        cross = cross_cut(h, nearest, joined)
        cross_spans = spans_at(h, cross * 1.000001, nearest, joined)[1] if cross else {}

        asked = [r for r in rows if r["asked"]]
        hits = sum(1 for r in asked if r["hit"])

        results[reading] = {
            "shape": shape, "g": g, "spans": spans, "classes": classes,
            "a_ok": a_ok, "a_seen": a_seen, "best_b": best_b,
            "cross": cross, "cross_spans": cross_spans,
            "mapA": mapA, "mapB": mapB, "p1": p1, "p1_rows": p1_rows,
            "transfers": transfers, "n_transfer": n_transfer,
            "asked": len(asked), "hits": hits,
            "online_acc": hits / len(asked) if asked else 0.0,
        }

        say()
        say("--- %s reading ---" % reading)
        say("STRUCTURE")
        say("  states %d  episodes %d  classes %d  sizes %s"
            % (shape["states"], shape["episodes"], shape["classes"],
               sorted(shape["sizes"].values(), reverse=True)))
        say("  gap %s" % ("none" if g is None else
                          "ratio %.3f  lo %.6f  hi %.6f  cut %.6f"
                          % (g["ratio"], g["lo"], g["hi"], shape["tau"])))
        say("  class -> regions: %s"
            % {c: sorted(spans[c]) for c in sorted(spans)})
        say("  families per class: %s"
            % {c: sorted({r[0] for r in spans[c]}) for c in sorted(spans)})
        say("  class ids at authored bases: A %s  B %s" % (mapA, mapB))
        say("PREDICTION during delivery (descriptive only; not an E3 claim)")
        say("  asked %d  declined %d  hits %d  accuracy %.3f"
            % (len(asked), len(rows) - len(asked), hits,
               hits / len(asked) if asked else 0.0))
        say("P1 within-family prediction after the feed")
        for r in p1_rows:
            say("  %-4s -> %-3s  got %s  %s"
                % (r["from"], r["want"], r["got"], "hit" if r["hit"] else "MISS"))
        say("  P1 %s" % ("PASS" if p1 else "FAIL"))
        say("P2 transfer under the planted correspondence")
        for t in transfers:
            say("  transition %d: A pred %s (want %s); B pred %s (want %s); %s"
                % (t["i"], t["a_pred"], t["a_want"], t["b_pred"], t["b_want"],
                   "transfer" if t["ok"] else "no transfer"))
        say("  transfers %d/3" % n_transfer)
        say("OUTCOME CHECK")
        say("  classes at derived cut %d; three paired classes: %s"
            % (classes, a_ok))
        if best_b:
            say("  a cut exists that yields three paired classes: tau %.6f "
                "(outside derived gap: %s)" % (best_b[0], True))
        else:
            say("  no cut up to the largest pairwise distance yields three "
                "paired classes")
        if cross is not None:
            say("  first cross-family merge at tau %.6f: %d classes, %d span both families"
                % (cross, len(cross_spans),
                   sum(1 for s in cross_spans.values()
                       if len({r[0] for r in s}) > 1)))

    # ---- classify the joined outcome, then the separate one for completeness
    def outcome(r):
        if r["a_ok"]:
            return "a"
        if r["best_b"]:
            return "b"
        if r["classes"] == 6 and r["n_transfer"] == 3:
            return "c"
        if r["classes"] == 6 and r["n_transfer"] < 3:
            return "d"
        return "none"

    say()
    say("E3 result by reading")
    for reading in ("separate", "joined"):
        r = results[reading]
        say("  %-8s outcome (%s); classes %d; transfers %d/3"
            % (reading, outcome(r), r["classes"], r["n_transfer"]))
    say("The separate reading is primary (e3-prereg.md); the joined reading is "
        "reported but its splices add cross-family edges.")

    r = results["separate"]
    o = outcome(r)
    ok = (o == "a")
    say()
    say("E3 %s (outcome %s)" % ("PASS" if ok else "FAIL", o))
    if o != "a":
        say("Only outcome (a) passes. %s is a classified failure, not a bug: "
            "v0.1 groups by state proximity, not by delta shape."
            % o)

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    say("written -> %s" % OUT)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
