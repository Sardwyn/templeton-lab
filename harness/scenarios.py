"""Scenario suite. A scenario is a stream of (state, error) observations laid
out as episodes, plus the criteria it must meet -- written down before any run
and never edited to fit a result.

Honesty caveat, up front: the generator knows structure the system does not. A
scenario supplies only what the observation channel delivers -- never a label,
an identity, a class, a rule, or a cause. Where a criterion names a class count,
the observer is checking whether the system recovered something the generator
really planted, not the system being told it exists.

Streams are 4-component. Jitter is deterministic and sits on components 0 and 3,
small enough that two observations of one region stay well below the low side of
the gap the system finds, and large enough that no distance is exactly zero.
Only a component the generator genuinely holds constant contributes an exact
zero -- which is what the self scenarios are about.

Every inter-region distance is chosen to sit above the high side of the gap the
system derives on the first visit, so a class count cannot depend on where
inside that gap the cut happens to sit.

Probe states that should be named go through `unseen`: a state never delivered,
sitting inside an existing recurrence. Naming a recurrence from a state the
system was never handed is the only version of the test that cannot be a record
lookup. The probe that must *not* be named is placed beyond the high side of the
derived gap instead: placed at the far edge of the gap it would only be unnamed
because the cut happened to land short of it, which is a coin toss, not a claim.

Support claims are measured at ask time, on the feed delivered before
`holdout_from`; the structural counts (classes, sizes, episodes) are measured on
the completed feed. A probe therefore reports what the system could claim when
it was asked, not what it holds after the run.
"""

import random

COMPONENTS = 4
GAP_MIN = 2.0          # core.GAP; only used to check the generator's geometry

# Regions sit on corners of {0.1, 0.9}^4. Two corners that differ in two
# components are 0.4 apart in the system's magnitude (P1: mean absolute
# deviation), so the nearest-neighbour distribution splits into jitter ~0.01
# and cross-region >= 0.2, with no distance anywhere in between.
CORNER = ((0.1, 0.1, 0.1, 0.1), (0.9, 0.9, 0.1, 0.1), (0.9, 0.9, 0.9, 0.9),
          (0.1, 0.1, 0.9, 0.9))


def jit(seed, amp=0.010):
    """Deterministic jitter on the two components the generator lets move."""
    r = random.Random(seed)
    return (r.uniform(-amp, amp), 0.0, 0.0, r.uniform(-amp, amp))


def jittered(state, seed, amp=0.010):
    z = jit(seed, amp)
    return tuple(x + z[i] for i, x in enumerate(state))


def unseen(state, off=0.0015):
    """A state never delivered, inside the same region as `state`.

    Offsets only component 0, so the mean deviation stays far below the low side
    of the gap while the value itself is not a record the system holds.
    """
    return tuple((state[0] + off, state[1], state[2], state[3]))


# ------------------------------------------------------------
# control
# ------------------------------------------------------------

def null_random():
    """No structure planted: independent uniform states, errors unrelated to
    anything. What the system reports here is the baseline every other
    scenario is judged against."""
    episodes = []
    for e in range(6):
        ep = []
        for t in range(6):
            z = jit_all(1000 + 17 * e + t, 0.2)
            ep.append((tuple(0.05 + 0.9 * (i + 1) / 4 + z[i]
                             for i in range(COMPONENTS)),
                       (0.05 + 0.9 * ((17 * e + t) % 7) / 6)))
        episodes.append(ep)
    return {"name": "null_random", "kind": "control",
            "blocks": episodes,
            "probes": [{"prefix": [], "expect_state": None,
                        "why": "no context to expect from"},
                       {"prefix": [s for s, _ in episodes[0][:2]],
                        "expect_state": None,
                        "why": "a uniform field has no continuation to report"}],
            "holdout_from": 3,
            "criteria": {"no_cut": True, "no_convergence": True,
                         "no_divergence": True, "no_collapse": True,
                         "below_claims": True, "no_dominance": True,
                         "err_floor": 0.05}}


def jit_all(seed, amp=0.2):
    """Jitter on every component -- the control's noise has nothing to hold."""
    r = random.Random(seed)
    return tuple(r.uniform(-amp, amp) for _ in range(COMPONENTS))


# ------------------------------------------------------------
# prediction, identity, continuity: the same three-cycle stream, read three ways
# ------------------------------------------------------------

CYCLE_SEEDS = (200, 400, 600)
CYCLE_ERR = (0.10, 0.45, 0.80)


def _cycle(episodes=9, errors=CYCLE_ERR):
    """[[a, b, c], ...] -- one repeating three-cycle, nothing else."""
    blocks = []
    for e in range(episodes):
        ep = []
        for i, corner in enumerate(CORNER[:3]):
            ep.append((jittered(corner, CYCLE_SEEDS[i] + 13 * e), errors[i]))
        blocks.append(ep)
    return blocks


def prediction():
    """Nothing is asked to predict. The claim is only that some ordered pairs
    recur, so a continuation observed many times is measurable."""
    episodes = _cycle()
    tail = [jittered(CORNER[0], 3001), jittered(CORNER[1], 3002)]
    return {"name": "prediction", "kind": "prediction",
            "blocks": episodes,
            "probes": [{"prefix": tail, "expect_state": unseen(CORNER[2]),
                        "named": True,
                        "why": "the pair at the tail has been observed to "
                               "continue this way"},
                       {"prefix": [jittered(CORNER[2], 3003)],
                        "expect_state": None,
                        "why": "nothing has ever followed this, so nothing "
                               "should be claimed"}],
            "holdout_from": 6,
            "criteria": {"classes": 3, "states": 27,
                         "episodes_separate": 9, "episodes_joined": 1,
                         "sizes": [9, 9, 9], "anticipatory": 0.80,
                         "probe_support": 6, "probe_named": True,
                         "probe_silent_joined": False,
                         "probe_silent_separate": True, "err_across_classes": 0.50}}


def identity():
    """Same stream; the question is whether a state never delivered can be
    placed where an earlier state was placed, without 'same' being given."""
    episodes = _cycle()
    probes = [
        {"prefix": [unseen(CORNER[0])], "expect_state": unseen(CORNER[1]),
         "named": True,
         "why": "named by distance under the derived cut, not by equality"},
        {"prefix": [unseen(CORNER[1])], "expect_state": unseen(CORNER[2]),
         "named": True,
         "why": "a second recurrence, named the same way"},
        {"prefix": [unseen(CORNER[2])], "expect_state": None,
         "named": True,
         "why": "a third recurrence named the same way as the other two, and the three "
                "names are different from one another"},
        {"prefix": [unseen((0.5, 0.5, 0.5, 1.5))], "expect_state": None,
         "why": "a state further than the cut from every recurrence, beyond the span of "
                "what was ever observed, should not be forced into a class"},
    ]
    return {"name": "identity", "kind": "identity",
            "blocks": episodes,
            "probes": probes,
            "holdout_from": 6,
            "criteria": {"classes": 3, "states": 27,
                         "episodes_separate": 9, "episodes_joined": 1,
                         "sizes": [9, 9, 9], "probe_named": True,
                         "probe_distinct": True, "probe_unnamed": True,
                         "err_across_classes": 0.50}}


def continuity():
    """Continuity is tested under both readings of 'sequence', because the spec
    does not say whether an episode boundary breaks the ordering. The criteria
    themselves say which readings they apply to; a criterion that does not apply
    is reported as not applicable, never as a pass."""
    episodes = _cycle()
    return {"name": "continuity", "kind": "continuity",
            "blocks": episodes,
            "probes": [{"prefix": [s for s, _ in episodes[0][:2]],
                        "expect_state": unseen(CORNER[2]),
                        "why": "inside a three-cycle the tail of a fresh "
                               "episode should name the third thing"}],
            "holdout_from": 6,
            "criteria": {"classes": 3, "states": 27,
                         "episodes_separate": 9, "episodes_joined": 1,
                         "sizes": [9, 9, 9], "anticipatory": 0.80,
                         "boundary_declined_joined": 0.0,
                         "boundary_declined_separate": 1.0}}


# ------------------------------------------------------------
# causality: one thing many things arrive at
# ------------------------------------------------------------

HUB = (0.5, 0.5, 0.5, 0.5)
# Every corner is 0.40 mean |delta| from the centre (4 x 0.4 / 4), so the three
# sources all arrive at the hub at the same cost. The terminals move ONE
# component, so leaving costs 0.10. The asymmetry is geometry, not a label --
# it was only visible after measuring: an all-corner terminal sits 0.40 from the
# hub too, and then arrival and departure are equal by construction.
SRC = ((0.1, 0.1, 0.1, 0.1), (0.9, 0.9, 0.1, 0.1), (0.9, 0.9, 0.9, 0.9))
SRC_ERR = (0.10, 0.30, 0.55)
TERM = ((0.9, 0.5, 0.5, 0.5), (0.1, 0.5, 0.5, 0.5))
TERM_ERR = (0.75, 0.95)


def _converge(rotating=9, terminal_only=3):
    """[source -> hub -> terminal] episodes, plus terminal-only episodes.

    The hub is the only state many different things arrive at, and arriving costs
    more than leaving. Errors are flat within a class and different across classes,
    so neither an error value nor a per-class label is what makes the hub special.
    """
    blocks = []
    for e in range(rotating):
        s = SRC[e % 3]
        blocks.append([(jittered(s, 5000 + 11 * e), SRC_ERR[e % 3]),
                       (jittered(HUB, 5100 + 11 * e, 0.004), 0.00),
                       (jittered(TERM[e % 2], 5200 + 11 * e), TERM_ERR[e % 2])])
    for t in range(terminal_only):
        blocks.append([(jittered(TERM[t % 2], 5300 + 11 * t), TERM_ERR[t % 2])])
    return blocks


def causality():
    """Nothing is called a cause. The claim is only that the arrival structure is
    asymmetric, and that leaving the hub is cheap while arriving at it is not."""
    blocks = _converge()
    return {"name": "causality", "kind": "causality",
            "blocks": blocks,
            "probes": [{"prefix": [jittered(SRC[0], 5401)],
                        "expect_state": jittered(HUB, 5402, 0.004),
                        "why": "the hub is the only continuation this source "
                               "has ever had"},
                       {"prefix": [jittered(TERM[0], 5403)],
                        "expect_state": None,
                        "why": "a terminal has never continued, so nothing "
                               "should be claimed after it"}],
            "holdout_from": 9,
            "criteria": {"classes": 6, "states": 30,
                         "episodes_separate": 12, "episodes_joined": 1,
                         "sizes": [9, 7, 5, 3, 3, 3],
                         "centre": True,
                         "converges": True, "arrival_gt_departure": True,
                         "err_within_class": 0.05,
                         "err_center": 0.05, "err_worse_after": True,
                         "probe_support": 3,
                         "probe_silent_joined": False,
                         "probe_silent_separate": True,
                         "closes_joined": False, "closes_separate": True}}


# ------------------------------------------------------------
# agency: one thing many different things follow
# ------------------------------------------------------------

FORK = (0.5, 0.5, 0.5, 0.5)
FORK_IN = ((0.1, 0.1, 0.1, 0.1), (0.9, 0.9, 0.1, 0.1), (0.1, 0.1, 0.9, 0.9))
BRANCH = ((0.9, 0.1, 0.9, 0.1), (0.1, 0.9, 0.1, 0.9), (0.9, 0.9, 0.9, 0.9))
BRANCH_ERR = (0.20, 0.50, 0.80)


def _diverge(episodes=9):
    """[arrival -> fork -> branch] with the branch rotating through three
    recurrences. Errors differ per branch, so the branches are distinguishable
    by more than their positions."""
    blocks = []
    for e in range(episodes):
        blocks.append([(jittered(FORK_IN[e % 3], 6000 + 13 * e), 0.05 + 0.1 * (e % 3)),
                       (jittered(FORK, 6100 + 13 * e, 0.004), 0.20),
                       (jittered(BRANCH[e % 3], 6200 + 13 * e), BRANCH_ERR[e % 3])])
    return blocks


def agency():
    """Nothing is called an agent. The claim is only that one recurrence has more
    than one continuation, and that which one follows is not written in what came
    before it."""
    blocks = _diverge()
    return {"name": "agency", "kind": "agency",
            "blocks": blocks,
            "probes": [{"prefix": [jittered(FORK, 6301, 0.004)],
                        "expect_state": jittered(BRANCH[0], 6302),
                        "why": "the fork has been followed by three different "
                               "things, so a rival must survive alongside the pick"},
                       {"prefix": [jittered(BRANCH[0], 6303)],
                        "expect_state": None,
                        "why": "a branch has never continued, so nothing should "
                               "be claimed after it"}],
            "holdout_from": 6,
            "criteria": {"classes": 7, "states": 27,
                         "episodes_separate": 9, "episodes_joined": 1,
                         "sizes": [9, 3, 3, 3, 3, 3, 3],
                         "centre": True,
                         "diverges": True, "fork_successors_open": True,
                         "err_within_class": 0.05,
                         "err_center": 0.20, "err_worse_after": True,
                         "rivals_min": 2,
                         "probe_silent_joined": False,
                         "probe_silent_separate": True}}


# ------------------------------------------------------------
# self: the null space of the difference operator
# ------------------------------------------------------------

FRAME_SEEDS = (2100, 2200, 2300, 2400, 2500)
FRAME_ERR = (0.15, 0.85)      # alternating *within* a region, so an error value
FRAME_STEPS = 3               # cannot be what identifies a recurrence
FRAME_CREEP = 0.30            # drift per step, component 2 only, `self_drift`

# Regions sit on corners of the plane spanned by components 0 and 3. Component 1
# is held at exactly 0.50 everywhere. Component 2 is held at 0.35 everywhere
# except in `self_drift`, where it creeps. Two corners two components apart are
# 0.4 in magnitude (P1); one apart, 0.2.
FRAME_POINTS = ((0.1, 0.1), (0.9, 0.9), (0.1, 0.9), (0.9, 0.1), (0.5, 0.5))


def _frame(creep=0.0):
    """Three observations of each of five regions."""
    episodes = []
    for i, (c0, c3) in enumerate(FRAME_POINTS):
        ep = []
        for step in range(FRAME_STEPS):
            z = jit(FRAME_SEEDS[i] + 7 * step, 0.008)
            ep.append(((c0 + z[0], 0.50, 0.35 + creep * step, c3 + z[3]),
                       FRAME_ERR[step % 2]))
        episodes.append(ep)
    return episodes


def self_frame():
    """Nothing is asked about a self. Pass the difference operator over what was
    recorded: the components that come back empty-handed are the ones that were
    held still, and that empty set is all 'self' resolves to here."""
    episodes = _frame()
    third = episodes[2]
    return {"name": "self_frame", "kind": "self",
            "blocks": episodes,
            "probes": [{"prefix": [unseen(third[0][0])],
                        "expect_state": jittered(third[1][0], 2601, 0.008),
                        "named": True,
                        "why": "a region whose differing components never move "
                               "should name its own next thing"}],
            "holdout_from": 4,
            "criteria": {"classes": 5, "states": 15,
                         "episodes_separate": 5, "episodes_joined": 1,
                         "sizes": [3, 3, 3, 3, 3],
                         "invariant": [1, 2],
                         "err_within_class_min": 0.50,
                         "probe_named": True}}


def self_drift():
    """Same frame, one component creeping. If the region is still called one
    thing, then the only honest self is the set of components the difference
    operator cannot move -- and the creeping one must not be in that set. The
    creep is measured as a range inside a recurrence, not as a step: under the
    separate reading a creeping step never crosses an episode boundary, so a
    step-based claim would be a claim about the reader's splice.
    """
    episodes = _frame(creep=FRAME_CREEP)
    third = episodes[2]
    return {"name": "self_drift", "kind": "self",
            "blocks": episodes,
            "probes": [{"prefix": [unseen(third[0][0])],
                        "expect_state": jittered(third[1][0], 2701, 0.008),
                        "named": True,
                        "why": "the region is still one recurrence, so the "
                               "continuation should still be named"}],
            "holdout_from": 4,
            "criteria": {"classes": 5, "states": 15,
                         "episodes_separate": 5, "episodes_joined": 1,
                         "sizes": [3, 3, 3, 3, 3],
                         "invariant": [1],
                         "drift_visible": True,
                         "err_within_class_min": 0.50,
                         "probe_named": True}}


# ------------------------------------------------------------
# witness: rivals that survive being ranked
# ------------------------------------------------------------

WIT_OPEN = (CORNER[0], CORNER[1])   # 0.8 apart: no cut found here can join them
WIT_X = CORNER[2]                   # the dearer ending
WIT_Y = CORNER[3]                   # the cheaper ending
# A fourth recurrence that continues nothing and is never carried across an
# episode edge. It sits beyond the high side of the gap from every ending, so it
# is its own recurrence at any cut inside the gap -- and it is cheap (0.15), so
# if cost alone decided what is kept, this would be the thing kept.
WIT_Z = (0.5, 0.5, 0.5, 0.9)
WIT_SEEDS = (2800, 2900)
WIT_Z_ERR = 0.15


def _fan(last_err, z_episodes=0):
    """Alternating [a, b, x] and [a, b, y] episodes: one shared opening, two
    endings, each observed the same number of times. Every episode holds exactly
    one observation of one ending, so keeping the holdout out of the feed leaves
    both endings answerable and neither preferred. The opening's own errors are
    fixed, so the choice is made on what the third observation cost, not on the
    opening. `z_episodes` puts single-observation [z] episodes at the front: they
    are in memory when the probe is asked and continue nothing.
    """
    blocks = []
    for e in range(z_episodes):
        blocks.append([(jittered(WIT_Z, 3100 + e, 0.008), WIT_Z_ERR)])
    for e in range(6):
        blocks.append([(jittered(WIT_OPEN[0], WIT_SEEDS[0] + e, 0.008), 0.20),
                       (jittered(WIT_OPEN[1], WIT_SEEDS[1] + e, 0.008), 0.30),
                       (jittered(WIT_X, 2400 + e, 0.008), 0.25)])
        blocks.append([(jittered(WIT_OPEN[0], WIT_SEEDS[0] + e, 0.008), 0.20),
                       (jittered(WIT_OPEN[1], WIT_SEEDS[1] + e, 0.008), 0.30),
                       (jittered(WIT_Y, 2500 + e, 0.008), last_err)])
    return blocks


def witness_equal():
    """Both endings cost the same when observed. The system keeps both, answers
    neither preference, and reports them as two rivals -- the selection is not
    made for it.
    """
    return {"name": "witness_equal", "kind": "witness",
            "blocks": _fan(0.60),
            "probes": [{"prefix": [jittered(WIT_OPEN[0], 3001),
                                   jittered(WIT_OPEN[1], 3002)],
                        "expect_state": [jittered(WIT_X, 3003), jittered(WIT_Y, 3004)],
                        "named": True,
                        "why": "two equally dear endings, neither preferred"}],
            "holdout_from": 6,
            "criteria": {"classes": 4, "states": 36,
                         "episodes_separate": 12, "episodes_joined": 1,
                         "sizes": [12, 12, 6, 6],
                         "err_across_classes": 0.30,
                         "rivals_count": 2, "equal_support": True,
                         "probe_support": 3, "probe_named": True}}


def witness_ranked():
    """The endings cost different errors, and a cheap recurrence that continues
    nothing is present as well. The system keeps both endings, ranks them, and
    the claim it makes is the cheaper ending -- not the cheapest thing in memory.
    """
    return {"name": "witness_ranked", "kind": "witness",
            "blocks": _fan(0.90, z_episodes=1),
            "probes": [{"prefix": [jittered(WIT_OPEN[0], 3001),
                                   jittered(WIT_OPEN[1], 3002)],
                        "expect_state": [jittered(WIT_X, 3003), jittered(WIT_Y, 3004)],
                        "named": True,
                        "why": "two endings of different cost; the claim should "
                               "follow the cheaper one, and the cheap recurrence "
                               "that continues nothing should not become a rival"}],
            "holdout_from": 7,
            "criteria": {"classes": 5, "states": 37,
                         "episodes_separate": 13, "episodes_joined": 1,
                         "sizes": [12, 12, 6, 6, 1],
                         "err_across_classes": 0.30,
                         "pick_is_cheaper": True, "rivals_count": 2,
                         "probe_support": 3, "probe_named": True}}

ALL = (null_random, prediction, identity, continuity, causality, agency,
       self_frame, self_drift, witness_equal, witness_ranked)
