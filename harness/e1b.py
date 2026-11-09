"""E1b -- the pre-registered restatement of E1's rotation claims.

See `e1-prereg.md`, Amendment E1b (2026-11-09). This file imports the frozen
E1 builders and runners; it never edits them. It re-checks every hash in
`FREEZE.md` and aborts on a mismatch.

Writes e1b-out.txt.
"""

import hashlib
import itertools
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import e1                       # noqa: E402

OUT = os.path.join(HERE, "e1b-out.txt")

FROZEN = {
    "core.py": "8734d335a14810424296629c8500a5edda5b09b364c7f9387a42aee87aa0f150",
    "measure.py": "1c9f076dcaafb274947cf61e6ac88cc7e86425ffb4d79b72983fb6798967c06f",
    "run.py": "5440c370ff6c5ac764d8a02ae1bf71ab794f2b82b3a234a07abc01deccfc2b42",
    "scenarios.py": "bc8e40d22b65b1397914c1a8ad553a2184d775d90b8966b2e33a0de87342ef22",
    "audit.py": "e1cd2ee14e996ae122f8ad1633b27e1cbf0bae72f686fdc3560b40eba483e6be",
    "e1.py": "720f90ac910c48240494409174af6cb22c1bda75f1552f0c2bf3576ff4719a8f",
}

lines = []


def say(text=""):
    lines.append(text)
    print(text)


def check_hashes():
    good = True
    for name, want in FROZEN.items():
        got = hashlib.sha256(open(os.path.join(HERE, name), "rb").read()).hexdigest()
        state = "ok" if got == want else "CHANGED"
        say("hash %-12s %s %s" % (name, got[:16], state))
        good = good and got == want
    return good


def edges(seq):
    return [(seq[i], seq[i + 1]) for i in range(len(seq) - 1)]


def presence(seq):
    succ, pred = {}, {}
    for u, v in edges(seq):
        succ.setdefault(u, set()).add(v)
        pred.setdefault(v, set()).add(u)
    return succ, pred


def norm(mapping, classes):
    return {c: set(mapping.get(c, set())) for c in classes}


def permute(mapping, p, classes):
    return {p[c]: {p[v] for v in mapping.get(c, set())} for c in classes}


def main():
    say("E1b -- restatement of E1's rotation claims (e1-prereg.md, Amendment E1b)")
    say("frozen set checked against FREEZE.md:")
    if not check_hashes():
        say("ABORT: the frozen implementation changed. E1b is invalid.")
        with open(OUT, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        return 1

    A = e1.run(e1.ORDERS["cycle"], True)
    B = e1.run(e1.ORDERS["rotate"], True)
    G = e1.run(e1.ORDERS["grouped"], True)
    As = e1.run(e1.ORDERS["cycle"], False)
    Bs = e1.run(e1.ORDERS["rotate"], False)
    Gs = e1.run(e1.ORDERS["grouped"], False)

    keys = sorted(A["kmap"])
    p = next(perm for perm in itertools.permutations(range(3))
             if all(perm[A["kmap"][k]] == B["kmap"][k] for k in keys))
    classes = (0, 1, 2)
    say()
    say("relabelling cycle -> rotate: %s" % (p,))

    seq_a = [A["kmap"][k] for k in A["flat"]]
    seq_b = [B["kmap"][k] for k in B["flat"]]
    ea, eb = edges(seq_a), edges(seq_b)

    # B1 -- the cyclic edge multiset, return edge included.
    cyc_a = sorted((p[u], p[v]) for u, v in ea + [(seq_a[-1], seq_a[0])])
    cyc_b = sorted(eb + [(seq_b[-1], seq_b[0])])
    b1 = cyc_a == cyc_b
    say()
    say("B1 circular edge multiset: %s" % ("IDENTICAL" if b1 else "DIFFERS"))
    say("   edges as a finite sequence: %s" %
        ("identical" if sorted((p[u], p[v]) for u, v in ea) == sorted(eb) else "differ"))
    say("   cycle A (mapped) %s" % cyc_a)
    say("   cycle B          %s" % cyc_b)
    say("B1 %s" % ("PASS" if b1 else "FAIL"))

    # B2 -- successor and predecessor presence sets, plus the count delta.
    sa, pa = presence(seq_a)
    sb, pb = presence(seq_b)
    succ_ok = permute(sa, p, classes) == norm(sb, classes)
    pred_ok = permute(pa, p, classes) == norm(pb, classes)
    b2 = succ_ok and pred_ok
    say()
    say("B2 presence degrees (successors / predecessors): %s / %s" %
        ("match" if succ_ok else "DIFFER", "match" if pred_ok else "DIFFER"))
    deg_a, deg_b = A["shape"]["degrees"], B["shape"]["degrees"]
    delta = {}
    for c in classes:
        rc = p[c]
        delta[c] = {
            "in": deg_a[c]["in"] - deg_b[rc]["in"],
            "n": deg_a[c]["n"] - deg_b[rc]["n"],
            "out": deg_a[c]["out"] - deg_b[rc]["out"],
        }
    say("   count delta (cycle - rotate, after relabelling): %s" % delta)
    say("   expected: one class +1 inbound, one class -1 inbound, out 0 everywhere")
    confined = (sorted(d["out"] for d in delta.values()) == [0, 0, 0]
                and sorted(d["in"] for d in delta.values()) == [-1, 0, 1]
                and sorted(d["n"] for d in delta.values()) == [-1, 0, 1])
    b2 = b2 and confined
    say("B2 %s (presence %s, one-edge count delta %s)" %
        ("PASS" if b2 else "FAIL", "holds" if (succ_ok and pred_ok) else "fails",
         "confined" if confined else "NOT confined"))

    # B3 -- grouped seam accounting.
    flat_g = G["flat"]
    seq_g = [G["kmap"][k] for k in flat_g]
    starts = [i for i in range(len(flat_g)) if flat_g[i][2] == 0]
    seams = []
    for bi, i in enumerate(starts):
        if i == 0:
            continue
        seams.append((bi, seq_g[i - 1], seq_g[i]))
    violations = [(bi, a, b) for bi, a, b in seams if (b - a) % 3 != 1]
    within_edges = [(seq_g[i], seq_g[i + 1]) for i in range(len(seq_g) - 1)
                    if flat_g[i + 1][2] != 0]
    within_bad = [(a, b) for a, b in within_edges if (b - a) % 3 != 1]
    b3 = (len(violations) == 2
          and [v[0] for v in violations] == [3, 6]
          and [(v[1], v[2]) for v in violations] == [(2, 1), (0, 2)]
          and not within_bad)
    say()
    say("B3 grouped seams: %d inter-episode edge(s), %d violation(s)" %
        (len(seams), len(violations)))
    say("   violations (block, from, to): %s" % violations)
    say("   within-episode edges: %d, violations: %s" %
        (len(within_edges), within_bad or "none"))
    say("B3 %s" % ("PASS" if b3 else "FAIL"))

    # B4 -- grouped joined must drop, misses only at the seam, no within-episode
    # degradation. The separate reading is descriptive only.
    asked = [r for r in G["rows"] if r["asked"]]
    misses = [r for r in asked if not r["hit"]]
    outside = [r for r in misses if not r["boundary"]]
    within = [r for r in asked if not r["boundary"]]
    within_hits = sum(1 for r in within if r["hit"])
    drop = G["acc"] < B["acc"]
    b4 = drop and not outside and within_hits == len(within)
    say()
    say("B4 rotate joined %d/%d, grouped joined %d/%d" %
        (B["hits"], B["asked"], G["hits"], G["asked"]))
    say("   miss positions %s; off-boundary %d; within-episode %d/%d" %
        ([r["pos"] for r in misses], len(outside), within_hits, len(within)))
    say("   separate reading (descriptive): rotate %d/%d, grouped %d/%d" %
        (Bs["hits"], Bs["asked"], Gs["hits"], Gs["asked"]))
    say("B4 %s (drop %s, boundary-only %s, within intact %s)" %
        ("PASS" if b4 else "FAIL", drop, not outside,
         within_hits == len(within)))

    ok = b1 and b2 and b3 and b4
    say()
    say("E1b %s" % ("PASS" if ok else "FAIL"))
    say("This is a post-hoc restatement, not a new blind test; E1 itself stays FAIL.")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    say("written -> %s" % OUT)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
