"""E1 -- the pre-registered order test (see e1-prereg.md).

Three orders of the same nine episodes: cycle, rotate, grouped. The recurrence
claims must not move when only the order of whole episodes moves; the prediction
accuracy must move when, and only when, the order breaks the cycle.

Writes e1-out.txt. Refuses to run if core.py is not the frozen build.
"""

import hashlib
import itertools
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import scenarios as S          # noqa: E402
import measure as M            # noqa: E402
from core import Harness       # noqa: E402

FROZEN_CORE = "8734d335a1481042"
HOLDOUT = 6
OUT = os.path.join(HERE, "e1-out.txt")

C = S.CORNER
TYPES = ([C[0], C[1], C[2]], [C[1], C[2], C[0]], [C[2], C[0], C[1]])
ORDERS = {
    "cycle": [0, 1, 2] * 3,
    "rotate": [1, 2, 0] * 3,
    "grouped": [0, 0, 0, 1, 1, 1, 2, 2, 2],
}

lines = []


def say(text=""):
    lines.append(text)
    print(text)


def block(t, visit):
    """One episode of type t. Seeds depend on (type, visit), never on the
    position in the order, so the same episode is byte-identical in all three
    orders and only its placement changes."""
    return [(S.jittered(st, 1000 * t + 10 * visit + i, 0.008),
             (0.1, 0.45, 0.8)[(t + i) % 3])
            for i, st in enumerate(TYPES[t])]


def build(order):
    seen = [0, 0, 0]
    blocks = []
    for t in order:
        blocks.append(block(t, seen[t]))
        seen[t] += 1
    return blocks


def run(order, joined):
    blocks = build(order)
    h = Harness()
    M.feed(h, blocks, joined, 0, HOLDOUT)
    rows = M.anticipate(h, blocks, HOLDOUT, joined)
    shape = M.shape(h)
    assign, _, _ = h.compression()
    flat, seen = [], [0, 0, 0]
    for e, t in enumerate(order):
        for i in range(len(blocks[e])):
            flat.append((t, seen[t], i))
        seen[t] += 1
    obs = [(e, i) for e, ep in enumerate(h.memory) for i in range(len(ep))]
    kmap = {k: assign.get(o) for k, o in zip(flat, obs)}
    asked = [r for r in rows if r["asked"]]
    hits = sum(1 for r in asked if r["hit"])
    return {"order": order, "blocks": blocks, "rows": rows, "shape": shape,
            "kmap": kmap, "flat": flat, "asked": len(asked), "hits": hits,
            "declined": len(rows) - len(asked),
            "acc": round(hits / len(asked), 3) if asked else 0.0}


def find_perm(base, other, keysets):
    for perm in itertools.permutations(range(3)):
        if all(perm[base[k]] == other[k] for k in keysets):
            return perm
    return None


def mapped(x, perm):
    return perm[x] if x is not None else None


def deg_sig(shape, perm):
    deg = shape["degrees"]
    sig = {}
    for cls, row in deg.items():
        nxt = tuple(sorted((perm[k], v) for k, v in row["next"].items()))
        sig[cls] = (row["in"], row["out"], row["in_src"], nxt)
    return {perm[c]: v for c, v in sig.items()}


def main():
    core = os.path.join(HERE, "core.py")
    digest = hashlib.sha256(open(core, "rb").read()).hexdigest()
    say("E1 -- order test. Frozen core.py %s (expected %s)" %
        (digest[:16], FROZEN_CORE))
    if digest[:16] != FROZEN_CORE:
        say("ABORT: core.py changed since the pre-registration was frozen.")
        return 1

    res = {}
    for name, order in ORDERS.items():
        for reading, joined in (("separate", False), ("joined", True)):
            r = run(order, joined)
            res[(name, reading)] = r
            say("%-8s %-8s classes %d sizes %s acc %d/%d declined %d" %
                (name, reading, r["shape"]["classes"],
                 sorted(r["shape"]["sizes"].values()), r["hits"], r["asked"],
                 r["declined"]))

    ok = True
    keyset = sorted(res[("cycle", "joined")]["kmap"])
    say()

    # C1 -- partition invariance across all orders, up to relabelling
    base = res[("cycle", "joined")]["kmap"]
    perms = {}
    for name in ORDERS:
        other = res[(name, "joined")]["kmap"]
        perm = find_perm(base, other, keyset)
        perms[name] = perm
        sizes = sorted(res[(name, "joined")]["shape"]["sizes"].values())
        good = perm is not None and sizes == sorted(base_size(base))
        say("C1 %-8s %-16s sizes %s  errors %s" %
            (name, "matches cycle" if perm else "DOES NOT MATCH", sizes,
             [round(v, 2) for _, v in sorted(
                 res[(name, "joined")]["shape"]["err_mean"].items())]))
        ok = ok and good
    say("C1 %s" % ("PASS" if ok else "FAIL"))

    # C2 -- rotate must equal cycle exactly, up to relabelling
    say()
    p = perms["rotate"]
    same = p is not None
    if same:
        a, b = res[("cycle", "joined")], res[("rotate", "joined")]
        same = (a["hits"] == b["hits"] and a["asked"] == b["asked"]
                and a["declined"] == b["declined"]
                and deg_sig(a["shape"], p) == deg_sig(b["shape"], tuple(range(3))))
        ak = {k: p[a["kmap"][k]] for k in keyset}
        bk = {k: b["kmap"][k] for k in keyset}
        same = same and ak == bk
    say("C2 rotation identity after relabelling: %s" % ("holds" if same else "MOVED"))

    # Post-hoc diagnostic (not a frozen claim): a finite stream has one first
    # state with no predecessor and one last state with no successor. Rotating
    # the episode order moves which class carries that single missing edge, so
    # a per-class degree comparison must differ by exactly one in-degree and
    # one out-degree. The interior edges should then be identical up to the
    # same relabelling.
    if p is not None:
        q = {p[i]: i for i in range(3)}      # rotate label -> cycle label

        def edges(r):
            seq = [r["kmap"][k] for k in r["flat"]]
            return [(seq[i], seq[i + 1]) for i in range(len(seq) - 1)], seq

        a, b = res[("cycle", "joined")], res[("rotate", "joined")]
        ea, sa = edges(a)
        eb, sb = edges(b)
        full = sorted(ea) == sorted((q[u], q[v]) for u, v in eb)
        cyc_a = sorted(ea + [(sa[-1], sa[0])])
        cyc_b = sorted((q[u], q[v]) for u, v in eb + [(sb[-1], sb[0])])
        say("C2 diagnostic: directed edges %s as a sequence; %s as a cycle "
            "(the return edge added)" %
            ("identical" if full else "differ",
             "identical" if cyc_a == cyc_b else "differ"))

    say("C2 %s" % ("PASS" if same else "FAIL"))
    ok = ok and same

    # C3 -- grouped must drop, misses only at boundaries
    say()
    a, b = res[("rotate", "joined")], res[("grouped", "joined")]
    misses = [r for r in b["rows"] if r["asked"] and not r["hit"]]
    outside = [r for r in misses if not r["boundary"]]
    drop = b["acc"] < a["acc"]
    say("C3 rotate %d/%d  grouped %d/%d  miss positions %s  off-boundary %d" %
        (a["hits"], a["asked"], b["hits"], b["asked"],
         [r["pos"] for r in misses], len(outside)))
    say("C3 %s (drop %s, boundary-only %s)" %
        ("PASS" if (drop and not outside) else "FAIL", drop, not outside))
    ok = ok and drop and not outside

    # C4 -- refusal is order-independent in the separate reading
    say()
    c4 = all(res[(n, "separate")]["declined"] == 3 for n in ORDERS)
    say("C4 declined in separate: %s" %
        {n: res[(n, "separate")]["declined"] for n in ORDERS})
    say("C4 %s" % ("PASS" if c4 else "FAIL"))
    ok = ok and c4

    say()
    say("E1 %s" % ("PASS" if ok else "FAIL"))
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    say("written -> %s" % OUT)
    return 0 if ok else 1


def base_size(kmap):
    out = {}
    for v in kmap.values():
        if v is not None:
            out[v] = out.get(v, 0) + 1
    return list(out.values())


if __name__ == "__main__":
    sys.exit(main())
