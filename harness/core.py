"""Harness v0.1 -- a system built from four primitives and nothing else.

What the system is *given*:

  1. State              a tuple of numbers
  2. Difference         "the state changed", componentwise
  3. Sequence           "this came after that" -- ordering, no time axis
  4. Constraint signal  one number in [0, 1]: how undesirable this state is.
                        Nothing about *why*.

The system is not told that anything exists, that anything repeats, that two
states are the same, or that one change follows from another.

Memory -- the only structure that persists -- holds observed sequences and
their associated error values, and nothing else. Everything computed below is
recomputed from memory on every call, so the leakage claim is checkable:
audit.py asserts that a live instance holds no derived structure at all.

Deliberately absent: objects, labels, entities, ontology, causes, agents, a
self, a body, a graph, a symbol table, a time axis beyond ordering, a metric
named "similarity", a threshold named "same", a notion of truth.

What is present as a prior, and cannot be removed, is listed in PRIORS. A
prior is a way of measuring, not a conclusion. The claim of this build is
prior-minimality and the insensitivity of the verdicts to where the cut sits,
not freedom from thresholds -- that distinction is the honest result.
"""

from math import log

K = 3           # longest context the system will look back over
GAP = 2.0       # a cut is believed only when the distances separate by a factor
              # of two. The control feed (36 states, 6 episodes) throws a largest
              # chance nearest-neighbour ratio of 1.99, so a narrower rule would
              # compress noise. Every real separation in the scenarios is larger
              # (the weakest is 2.46), so this decides a control, not a pattern --
              # and the 0.7% margin is why run.py sweeps the cut instead of
              # trusting a single number.
MIN_SIDE = 2    # a separation needs this many samples on each side to be real
EPS = 1e-12     # arithmetic residue, not a notion of "close enough to be one"

PRIORS = {
    "P0": "the stream arrives as bounded sequences; an episode boundary is given",
    "P1": "magnitude of a difference = mean absolute deviation over components. "
          "Consequence: a component that never differs contributes 0, so its "
          "size is scale, not information -- a constant carries no news",
    "P2": "context = the last 1..K ordered positions, K = 3",
    "P3": "competing continuations rank by support, then by lower error",
    "P4": "the cut between 'this has happened before' and 'this is something "
          "else' is the largest relative gap in the nearest-neighbour distance "
          "distribution, ratio >= GAP. The cut is valid anywhere inside the "
          "gap; the system picks the arithmetic midpoint, and run.py sweeps "
          "the whole interval to show the verdict does not depend on where",
    "P5": "a separation needs MIN_SIDE observations on both sides, and a width of "
          "two -- the cheapest cut that still refuses an unstructured feed -- is "
          "the floor",
    "P6": "recurrence is single-linkage grouping in observation order: an "
          "observation joins the recurrence of the earlier observation nearest "
          "to it, when that distance is under the cut. Nothing is averaged",
}


def _diff(a, b):
    """componentwise |change|. The most primitive observable."""
    return tuple(abs(x - y) for x, y in zip(a, b))


def _dev(vals):
    """P1's metric on a single component: its mean deviation from its own mean."""
    m = sum(vals) / len(vals)
    return sum(abs(v - m) for v in vals) / len(vals)


def _dist(a, b):
    return sum(_diff(a, b)) / len(a)


def _log2(x):
    return log(x) / log(2.0)


def _entropy(counts):
    n = sum(counts.values())
    return -sum((c / n) * _log2(c / n) for c in counts.values() if c)


class Harness:
    """No per-scenario knobs: one configuration for every test."""

    def __init__(self, tau=None):
        self.memory = []      # ONLY store: episodes of (state tuple, err float)
        self.episode = None
        # tau is not a system knob. It exists only so run.py can sweep the cut
        # across the whole gap interval and show that a verdict does not depend
        # on where inside the gap the cut happens to sit. audit.py flags it.
        self.tau = tau

    # ---- input ----------------------------------------------------------
    def start_episode(self):
        self.episode = []
        self.memory.append(self.episode)

    def observe(self, state, err):
        if self.episode is None:
            self.start_episode()
        self.episode.append((tuple(float(x) for x in state), float(err)))

    # ---- derived: difference + its distribution -------------------------
    def observations(self):
        out = []
        for e, ep in enumerate(self.memory):
            for i, (s, err) in enumerate(ep):
                out.append((e, i, s, err))
        return out

    def transitions(self):
        """Within-episode consecutive differences. Ordering, nothing more."""
        out = []
        for ep in self.memory:
            for i in range(1, len(ep)):
                out.append((ep[i - 1][0], ep[i][0], _diff(ep[i - 1][0], ep[i][0]),
                            _dist(ep[i - 1][0], ep[i][0])))
        return out

    def _nearest(self):
        """(distance, index) of the nearest observation seen earlier.
        'Seen earlier' is the whole of the time concept in this system.
        """
        out, seen = [], []
        for _, _, s, _ in self.observations():
            if seen:
                bd, bi = None, -1
                for i, p in enumerate(seen):
                    d = _dist(p, s)
                    if bd is None or d < bd:
                        bd, bi = d, i
                out.append((bd, bi))
            else:
                out.append((None, -1))
            seen.append(s)
        return out

    def nn(self):
        """Distances for every position that has an earlier one."""
        return [d for d, _ in self._nearest()[1:]]

    def gap(self):
        """P4/P5: where does 'this has happened before' stop and 'this is
        something else' begin? Derived from the observed nearest-neighbour
        distances by largest relative gap. None when there is no clean
        separation -- then the system declines to compress at all.
        The cut is valid anywhere inside (lo, hi); run.py sweeps that interval.
        """
        ds = sorted(self.nn())
        if len(ds) < 2 * MIN_SIDE:
            return None
        best = None
        for i in range(MIN_SIDE - 1, len(ds) - MIN_SIDE):
            lo, hi = ds[i], ds[i + 1]
            if lo <= EPS:
                continue   # an exact repeat is not a separation between classes
            ratio = hi / lo
            if ratio >= GAP and (best is None or ratio > best["ratio"]):
                best = {"ratio": ratio, "lo": lo, "hi": hi, "tau": (lo + hi) / 2.0,
                        "low": i + 1, "high": len(ds) - i - 1}
        return best

    # ---- derived: recurrence over states --------------------------------
    def _tau(self, g):
        """The cut in force. Normally the midpoint of the derived gap; run.py
        may place it anywhere else inside that same gap to test whether a
        verdict depends on the choice."""
        if self.tau is not None and g is not None and g["lo"] < self.tau < g["hi"]:
            return self.tau
        return g["tau"] if g else None

    def compression(self):
        """Group observations by recurrence under the derived cut (P6).

        Single-linkage, online, in observation order: an observation joins the
        recurrence of the earlier observation nearest to it, provided that
        distance falls under the cut. Nothing is averaged -- a recurrence is made
        of the observations that are really there, not of a centre no observation
        occupies, which would be an object the system never observed.
        Returns (assignment keyed by (episode, index), anchors, gap dict).
        """
        g = self.gap()
        if g is None:
            return {}, [], g
        tau = self._tau(g)
        ids, anchors, assign = [], [], {}
        for (d, j), (e, i, s, err) in zip(self._nearest(), self.observations()):
            if d is not None and d < tau:
                cid = ids[j]
                anchors[cid][1] += 1
            else:
                cid = len(anchors)
                anchors.append([s, 1])
            ids.append(cid)
            assign[(e, i)] = cid
        return assign, anchors, g

    def classes(self):
        """The compressed stream: episodes as sequences of recurrence ids."""
        assign, anchors, g = self.compression()
        seqs = []
        for e, ep in enumerate(self.memory):
            seqs.append([assign.get((e, i)) for i in range(len(ep))])
        return seqs, anchors, g

    # ---- derived: observed continuations --------------------------------
    def table(self):
        """counts[context][next recurrence id] = (support, mean error of the
        recurrence it was observed with).

        A table of observed sequences and their associated error values -- which
        is exactly what memory is permitted to hold. No rule syntax, no
        implication, no direction of influence.
        """
        seqs, _, _ = self.classes()
        counts = {}
        for e, seq in enumerate(seqs):
            ep = self.memory[e]
            live = [(i, x) for i, x in enumerate(seq) if x is not None]
            for pos in range(1, len(live)):
                cls = live[pos][1]
                err = ep[live[pos][0]][1]
                for k in range(1, min(K, live[pos][0]) + 1):
                    ctx = tuple(x for _, x in live[pos - k:pos])
                    slot = counts.setdefault(ctx, {})
                    n, tot = slot.get(cls, (0, 0.0))
                    slot[cls] = (n + 1, tot + err)
        return counts

    # ---- derived: expectation -------------------------------------------
    def classify(self, state):
        """Match a probe state to an existing recurrence, or return None.

        This is all 'identity' resolves to: the same distance-under-a-cut test
        that built the recurrence in the first place, applied to a state that is
        never stored. It presupposes no persistent object, and because the probe
        is not recorded an unvisited recurrence can be named and then never
        confirmed.
        """
        assign, anchors, g = self.compression()
        if g is None or not anchors:
            return None
        tau = self._tau(g)
        best, bd = -1, None
        for e, i, s, err in self.observations():
            d = _dist(s, state)
            if d < tau and (bd is None or d < bd):
                best, bd = assign[(e, i)], d
        return best if best >= 0 else None

    def expect(self, probe):
        """Longest matching continuation of the probe, with its competitors.

        'Present but not selected' is visible here: `competitors` lists every
        continuation that is supported, including the ones not chosen.
        """
        counts = self.table()
        ids = [self.classify(s) for s in probe]
        ids = [x for x in ids if x is not None]
        for k in range(min(len(ids), K), 0, -1):
            ctx = tuple(ids[len(ids) - k:])
            slot = counts.get(ctx)
            if not slot:
                continue
            cand = sorted(((n, tot / n, cls) for cls, (n, tot) in slot.items()),
                          key=lambda t: (-t[0], t[1]))
            total = sum(n for n, _, _ in cand)
            return {"context": ctx, "k": k, "support": cand[0][0],
                    "confidence": cand[0][0] / total,
                    "predict": cand[0][2], "err": cand[0][1],
                    "competitors": [{"cls": cls, "support": n, "err": e}
                                    for n, e, cls in cand]}
        return {"context": None, "k": 0, "support": 0, "confidence": 0.0,
                "predict": None, "err": None, "competitors": []}

    # ---- derived: what explains what ------------------------------------
    def weights(self):
        """Uncertainty removed by knowing the previous position.

        H(next) with and without the preceding recurrence. No causal operator
        is defined anywhere in this file; this is only a reduction, and calling
        it a cause would be importing a conclusion the system never earned.

        A source-like hub shows up as: high out-degree, large drop, near-zero
        in-degree. Nothing in the code is looking for that shape.
        """
        seqs, _, _ = self.classes()
        marg, pairs, inbound, sources = {}, {}, {}, {}
        for seq in seqs:
            live = [x for x in seq if x is not None]
            for i in range(1, len(live)):
                marg[live[i]] = marg.get(live[i], 0) + 1
                prev = live[i - 1]
                pairs.setdefault(prev, {})
                pairs[prev][live[i]] = pairs[prev].get(live[i], 0) + 1
                inbound[live[i]] = inbound.get(live[i], 0) + 1
                sources.setdefault(live[i], set()).add(prev)
        h_marg = _entropy(marg) if marg else 0.0
        out = {}
        for prev, nxt in pairs.items():
            out[prev] = {"out": len(nxt), "n": sum(nxt.values()),
                         "in": inbound.get(prev, 0),
                         "in_src": len(sources.get(prev, ())),
                         "src": sorted(sources.get(prev, ())),
                         "drop": h_marg - _entropy(nxt),
                         "next": dict(nxt)}
        return out

    def post_delta(self):
        """Mean magnitude of the change that follows each recurrence.

        Large after one recurrence, small after another, is what 'this state is
        volatile' and 'this state is stable' reduce to -- without either word.
        """
        assign, _, g = self.compression()
        if g is None:
            return {}
        out = {}
        for e, ep in enumerate(self.memory):
            for i in range(1, len(ep)):
                a = assign.get((e, i - 1))
                if a is None:
                    continue
                d = _dist(ep[i - 1][0], ep[i][0])
                n, tot = out.get(a, (0, 0.0))
                out[a] = (n + 1, tot + d)
        return {k: tot / n for k, (n, tot) in out.items()}

    # ---- derived: what never differs ------------------------------------
    def invariant(self):
        """P1 + P4: the components the difference operator cannot resolve.

        A component is left over when its own deviation across the records never
        reaches the cut that separates recurrences: nothing the system can tell
        apart includes it. That is the null space of the difference operator at
        the resolution the observations actually give -- the most a "frame" can
        be without anyone declaring one. When no cut exists nothing is left over,
        because there is nothing to be left over from.
        """
        if not self.memory:
            return set(), 0
        tau = self._tau(self.gap())
        if tau is None:
            return set(), len(self.memory[0][0][0])
        n = len(self.memory[0][0][0])
        states = [o[2] for o in self.observations()]
        return {k for k in range(n) if _dev([s[k] for s in states]) < tau}, n
