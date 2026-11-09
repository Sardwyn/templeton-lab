"""Observer-side instruments. Nothing in this file is part of the system.

The system exposes only derived measurements (recurrences, degrees, mean
differences, the null space). Deciding that a shape 'looks like a cause' or
'looks like an agent' happens here, in the reader, and is reported as the
reader's interpretation -- audit.py confirms the system's own file never uses
those words.

Two readings of the word 'sequence' are implemented, because the spec does not
settle it: episodes kept separate, or one continuous stream in which an episode
boundary is just another ordered position. Every verdict is reported for both.
"""

from math import log

from core import K, _dist      # _dist is the system's own magnitude (P1), not a
                               # second metric invented by the reader


def log2(x):
    return log(x) / log(2.0)


def entropy(counts):
    """Reader-side entropy over a count map. Kept here so core.py stays silent
    about uncertainty as a concept beyond what it already computes."""
    n = sum(counts.values())
    if not n:
        return 0.0
    return -sum((c / n) * log2(c / n) for c in counts.values() if c)


def feed(h, blocks, joined, start=0, stop=None):
    """Write blocks into memory. `joined` means the stream never restarts: an
    episode boundary exists only where the blocks list starts."""
    stop = len(blocks) if stop is None else stop
    for b in range(start, stop):
        if joined and b > 0:
            h.episode = h.memory[-1]        # same episode, more ordered positions
        else:
            h.start_episode()
        for state, err in blocks[b]:
            h.observe(state, err)


def shape(h):
    """Every derived measurement the reader uses, as numbers, with no verdict."""
    assign, centers, g = h.compression()
    sizes = {}
    for cls in assign.values():
        sizes[cls] = sizes.get(cls, 0) + 1
    deg = h.weights()
    post = h.post_delta()
    frozen, ncomp = h.invariant()

    marg = {}
    for prev, row in deg.items():
        for cls, n in row["next"].items():
            marg[cls] = marg.get(cls, 0) + n

    errs = {}
    for e, ep in enumerate(h.memory):
        for i, (_, err) in enumerate(ep):
            cls = assign.get((e, i))
            if cls is not None:
                errs.setdefault(cls, []).append(err)

    succ = {cls: entropy(row["next"]) for cls, row in deg.items()}
    return {
        "states": len(h.observations()),
        "episodes": len(h.memory),
        "gap": g,
        "tau": h._tau(g) if g else None,
        "classes": len(centers),
        "sizes": sizes,
        "degrees": deg,
        "post_delta": post,
        "invariant": sorted(frozen),
        "components": ncomp,
        "succ_entropy": succ,
        "err_spread": {cls: (max(v) - min(v)) for cls, v in errs.items()},
        "err_mean": {cls: sum(v) / len(v) for cls, v in errs.items()},
        "marg_entropy": entropy(marg) if marg else 0.0,
        "hubs": [cls for cls, row in deg.items()
                 if row["out"] >= 2 and row["in_src"] <= 1],
        "sinks": [cls for cls in sizes
                  if cls not in deg and sizes[cls] >= 2],
    }


def tail_classes(h, prefix):
    """Recurrence ids of a probe prefix; None entries are states the cut does
    not place anywhere."""
    return [c for c in (h.classify(s) for s in prefix) if c is not None]


def edge_delta(h):
    """Mean magnitude of the change that ARRIVES at each recurrence.

    core.py already reports the mean magnitude of the change DEPARTING each
    recurrence (`post_delta`). Comparing the two is the reader's act, not the
    system's: nothing in core.py ever puts them side by side. A recurrence whose
    arrivals are large and whose departures are small is where several different
    things come together and then stop moving.
    """
    assign, _, g = h.compression()
    if g is None:
        return {}
    out = {}
    for e, ep in enumerate(h.memory):
        for i in range(1, len(ep)):
            cls = assign.get((e, i))
            if cls is None:
                continue
            d = _dist(ep[i - 1][0], ep[i][0])
            n, tot = out.get(cls, (0, 0.0))
            out[cls] = (n + 1, tot + d)
    return {cls: tot / n for cls, (n, tot) in out.items()}


def anticipate(h, blocks, start, joined, k=K):
    """Expectation *before* the fact: for each held-out position, ask what the
    system would have expected, then compare with what actually arrived.

    The probe is the tail of the live episode, which is what makes the two
    readings differ: with episodes separate, a fresh episode has no precedent
    inside itself, so the first position of every episode is declined; with one
    joined stream, that same position has a predecessor and is anticipated.

    Returns per-position records. `boundary` marks the first position of a
    block -- the place where continuity is actually tested.
    """
    decline = {"context": None, "k": 0, "support": 0, "confidence": 0.0,
               "predict": None, "err": None, "competitors": []}
    out = []
    pos = 0
    for b in range(start, len(blocks)):
        if joined and h.memory:
            h.episode = h.memory[-1]    # joined stream: no new episode, ever
        else:
            h.start_episode()           # a new episode begins at each block
        first = True
        for state, err in blocks[b]:
            probe = [o[0] for o in h.memory[-1]][-k:] if h.memory else []
            e = h.expect(probe) if probe else decline
            actual = h.classify(state)
            hit = e["predict"] is not None and actual is not None \
                and e["predict"] == actual
            out.append({"block": b, "boundary": first, "pos": pos,
                        "asked": e["k"], "hit": hit, "declined": e["k"] == 0,
                        "predict": e["predict"], "actual": actual,
                        "confidence": e["confidence"],
                        "support": e["support"], "err": e["err"],
                        "rivals": len(e["competitors"]), "observed_err": err})
            h.observe(state, err)
            pos += 1
            first = False
    return out


def rate(records, key="hit"):
    if not records:
        return 0.0
    return sum(1 for r in records if r[key]) / len(records)


def rivals_of(h, prefix):
    """Competing continuations kept side by side, in the order P3 ranks them.
    `prefix` is raw states; expect() classifies them and answers in ids."""
    if not prefix:
        return []
    return h.expect(list(prefix))["competitors"]
