"""Driver. Runs each scenario twice -- once with episodes kept separate, once as
one joined stream -- and reports which phenomena appear in measurements the
system derived without being told to look for them.

The words 'hub', 'fork', 'convergent', 'divergent', 'witness' in this file belong
to the READER. core.py never uses them and audit.py proves it.

Reader-side thresholds live here only:
    ACCURACY   what counts as an anticipation
    FAN        how many distinct continuations make a fork, how many distinct
               arrivals make a hub

    python run.py            every scenario, both readings
    python run.py --sweep    the same, plus the cut moved inside its own gap
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import scenarios as S                          # noqa: E402
import measure as M                            # noqa: E402
from core import Harness, PRIORS               # noqa: E402

EVIDENCE = os.path.join(LAB, "trials", "evidence", "harness-v01", "evidence.json")
READINGS = {"separate": False, "joined": True}

ACCURACY = 0.80
FAN = 3


def yes(cond, value):
    return {"pass": bool(cond), "value": value}


def na(value):
    return {"pass": None, "value": value}


def show(value):
    text = json.dumps(value, sort_keys=True, default=list)
    return text if len(text) <= 68 else text[:65] + "..."


def accuracy(rows):
    """Hits per position an expectation was actually issued for. Positions the
    system declined are reported alongside, not quietly dropped: a decline is a
    result too."""
    answered = [r for r in rows if r["asked"]]
    hits = sum(1 for r in answered if r["hit"])
    return {"rows": len(rows), "answered": len(answered),
            "declined": len(rows) - len(answered),
            "acc": round(hits / len(answered), 3) if answered else 0.0}


def ask(h, probe):
    """A question asked against memory already written. expect() stores nothing,
    so asking cannot perturb the harness."""
    r = h.expect(list(probe["prefix"]))
    target = probe["expect_state"]
    wanted = []
    if target is not None:
        targets = target if isinstance(target, list) else [target]
        wanted = [h.classify(list(unseen(t))) for t in targets]
    named = h.classify(list(probe["prefix"][-1])) if probe["prefix"] else None
    return {"why": probe["why"],
            "named": named,
            "should_name": bool(probe.get("named")),
            "answered": r["context"] is not None,
            "context": r["context"], "k": r["k"], "support": r["support"],
            "confidence": round(r["confidence"], 3), "err": r["err"],
            "competitors": [[c["cls"], c["support"], round(c["err"], 3)]
                            for c in r["competitors"]],
            "hit": r["predict"] is not None and bool(wanted) and
                    r["predict"] in wanted}


def unseen(state, off=0.0015):
    """A state inside the same recurrence, not on top of one."""
    return (state[0] + off,) + tuple(state[1:])


def run_one(sc, joined, tau=None):
    """One harness per scenario and reading: feed the first `holdout_from`
    episodes, ask the probes, then deliver the held episodes while asking before
    every position. Structural measurements come from the completed feed."""
    h = Harness(tau=tau)
    M.feed(h, sc["blocks"], joined, 0, sc["holdout_from"])
    probes = [ask(h, p) for p in sc["probes"]]
    asked = M.anticipate(h, sc["blocks"], sc["holdout_from"], joined)
    shape = M.shape(h)
    assign, _, _ = h.compression()
    deg = shape["degrees"]
    succs = {}
    parents = {}
    for cls, row in deg.items():
        for nxt, n in row["next"].items():
            parents.setdefault(nxt, []).append(cls)
        succs[cls] = sorted(row["next"])
    return {"scenario": sc, "kind": sc["kind"],
            "reading": "joined" if joined else "separate", "joined": joined,
            "tau_fixed": tau, "gap": shape["gap"], "tau": shape["tau"],
            "shape": shape, "assign": assign, "records": h.memory,
            "probes": probes, "asked": asked,
            "succs": succs, "parents": parents,
            "edge_delta": M.edge_delta(h)}


def hub_of(ctx):
    """The recurrence several different recurrences arrive at. Arrivals are
    counted by where they come from, so a repeat of one arrival source does not
    inflate it. Nothing here says what the arrivals are: a hub is a place
    several things lead to, not a thing several causes produce. Whether it goes
    on in only one way is a separate measurement, not part of this one -- the
    hub is the far end of an asymmetry between arriving and leaving."""
    best, score = None, -1
    for cls, row in ctx["shape"]["degrees"].items():
        if row["in"] >= FAN and row["out"] < row["in"] and row["in_src"] > score:
            best, score = cls, row["in_src"]
    return best


def fan_of(ctx):
    """The recurrence the claim lives on for a divergence claim. It is the one
    that goes on in at least FAN ways, more ways than the recurrences arriving
    into it go on in, and more ways than anything it leads into goes on in. The
    spread therefore appears at this recurrence and settles after it -- which is
    the mirror of a hub, where things arrive from several places and leave in
    one. Neither says anything was chosen: both say where the shape is."""
    deg = ctx["shape"]["degrees"]

    def mean_out(cls_list):
        vals = [deg[c]["out"] for c in cls_list if c in deg]
        return sum(vals) / len(vals) if vals else 0.0

    def mean_ent(cls_list):
        vals = [ctx["shape"]["succ_entropy"].get(c, 0.0) for c in cls_list]
        return sum(vals) / len(vals) if vals else 0.0

    best, score = None, -1
    for cls, row in deg.items():
        par = ctx["parents"].get(cls, [])
        kids = ctx["succs"].get(cls, [])
        ent = ctx["shape"]["succ_entropy"].get(cls, 0.0)
        if (row["out"] >= FAN and row["out"] > mean_out(par)
                and row["out"] > mean_out(kids) and ent > mean_ent(par)
                and ent > score):
            best, score = cls, ent
    return best


def centre_of(ctx):
    """Where the claim lives. Convergence is read at the recurrence things
    arrive at; divergence is read at the recurrence that leaves in several
    ways. Same operator, asked in the direction the scenario claims."""
    return hub_of(ctx) if ctx["scenario"]["kind"] == "causality" else fan_of(ctx)


def mean_err_gap(shape):
    means = sorted(shape["err_mean"].values())
    return round(means[-1] - means[0], 3) if len(means) > 1 else 0.0


def within_range(shape):
    return {cls: round(v, 3) for cls, v in shape["err_spread"].items()}


def component_drift(ctx):
    """Largest spread of a single component inside one recurrence. A component
    that changes by more than the cut's own lower scale (lo) while still being
    called the same recurrence is visibly creeping."""
    assign = ctx["assign"]
    lo = ctx["gap"]["lo"] if ctx["gap"] else None
    if lo is None:
        return na(None)
    spread = {}
    for e, ep in enumerate(ctx["records"]):
        for i, (state, _) in enumerate(ep):
            cls = assign.get((e, i))
            if cls is not None:
                spread.setdefault(cls, []).append(state)
    worst = 0.0
    for members in spread.values():
        if len(members) < 2:
            continue
        for c in range(len(members[0])):
            vals = [m[c] for m in members]
            worst = max(worst, max(vals) - min(vals))
    return yes(round(worst, 4) > lo, {"worst_within_class": round(worst, 4), "lo": round(lo, 4)})


def mean_err(shape, cls):
    return shape["err_mean"][cls] if cls in shape["err_mean"] else None


def err_center(ctx, need):
    """The recurrence the claim lives on was met cheaply every time it was
    arrived at, against a need."""
    cls = centre_of(ctx)
    if cls is None:
        return na({"centre": None})
    err = mean_err(ctx["shape"], cls)
    return yes(err is not None and err <= need,
               {"centre": cls, "mean_err": round(err, 4) if err is not None else None})


def err_worse_after(ctx, need):
    """Being arrived at cheaply is not the same as what follows being cheap:
    the worst error after the centre is worse than the error of arriving at it.
    Measured as a difference, so the need only says whether to report it."""
    cls = centre_of(ctx)
    if cls is None:
        return na({"centre": None})
    arrive = mean_err(ctx["shape"], cls)
    outs = ctx["shape"]["degrees"][cls]["next"]
    after = {k: round(mean_err(ctx["shape"], k), 4) for k in outs}
    if not outs or arrive is None:
        return na({"centre": cls, "arriving": arrive, "after": after})
    return yes(max(after.values()) > arrive,
               {"centre": cls, "arriving": round(arrive, 4), "after": after})


def err_floor(ctx, need):
    """Nothing was met cheaply, because there is nothing to meet: the control
    reports no recurrence, so there is no centre and no class error to bound.
    Reporting a failure here would invent a measurement the feed does not
    support, so the honest control result is 'not applicable'."""
    means = ctx["shape"]["err_mean"]
    if not means:
        return na({"classes": 0, "min_class_err": None})
    return yes(min(means.values()) >= need,
               {"classes": len(means), "min_class_err": round(min(means.values()), 4)})


CHECKS = {
    "classes": lambda c, need: yes(c["shape"]["classes"] == need, c["shape"]["classes"]),
    "states": lambda c, need: yes(c["shape"]["states"] == need, c["shape"]["states"]),
    "episodes": lambda c, need: yes(c["shape"]["episodes"] == need, c["shape"]["episodes"]),
    "sizes": lambda c, need: yes(sorted(c["shape"]["sizes"].values(), reverse=True) == need,
                                 sorted(c["shape"]["sizes"].values(), reverse=True)),
    "invariant": lambda c, need: yes(c["shape"]["invariant"] == list(need), c["shape"]["invariant"]),
    "no_cut": lambda c, need: yes(c["gap"] is None, c["gap"]),
    "no_convergence": lambda c, need: yes(
        max([r["in_src"] for r in c["shape"]["degrees"].values()] or [0]) < FAN,
        max([r["in_src"] for r in c["shape"]["degrees"].values()] or [0])),
    "no_divergence": lambda c, need: yes(
        max([r["out"] for r in c["shape"]["degrees"].values()] or [0]) < FAN,
        max([r["out"] for r in c["shape"]["degrees"].values()] or [0])),
    "no_collapse": lambda c, need: yes(hub_of(c) is None, hub_of(c)),
    "below_claims": lambda c, need: yes(accuracy(c["asked"])["acc"] < ACCURACY,
                                        accuracy(c["asked"])),
    "no_dominance": lambda c, need: yes(
        all(p["confidence"] <= 0.5 for p in c["probes"]),
        [p["confidence"] for p in c["probes"]]),
    "centre": lambda c, need: yes(centre_of(c) is not None, centre_of(c)),
    "converges": lambda c, need: yes(centre_of(c) is not None, centre_of(c)),
    "diverges": lambda c, need: yes(fan_of(c) is not None, fan_of(c)),
    "arrival_gt_departure": lambda c, need: (
        lambda cls: yes(round(c["edge_delta"].get(cls, 0.0) - c["shape"]["post_delta"].get(cls, 0.0), 4)
                        > c["shape"]["post_delta"].get(cls, 0.0),
                        {"centre": cls,
                         "arrive": round(c["edge_delta"].get(cls, 0.0), 4),
                         "depart": round(c["shape"]["post_delta"].get(cls, 0.0), 4)}))(centre_of(c)),
    "fork_successors_open": lambda c, need: (
        lambda cls: yes(len(c["succs"].get(cls, [])) >= FAN and cls not in c["succs"].get(cls, []),
                        {"centre": cls,
                         "successors": [[s, c["shape"]["degrees"][s]["out"] if s in c["shape"]["degrees"] else 0]
                                        for s in c["succs"].get(cls, [])]}))(centre_of(c)),
    "err_within_class": lambda c, need: yes(
        max(within_range(c["shape"]).values() or [1.0]) <= need, within_range(c["shape"])),
    "err_within_class_min": lambda c, need: yes(
        min(within_range(c["shape"]).values() or [0.0]) >= need, within_range(c["shape"])),
    "err_across_classes": lambda c, need: yes(mean_err_gap(c["shape"]) >= need,
                                              {cls: round(v, 3) for cls, v in c["shape"]["err_mean"].items()}),
    "err_center": lambda c, need: err_center(c, need),
    "err_worse_after": lambda c, need: err_worse_after(c, need),
    "err_floor": lambda c, need: err_floor(c, need),
    "probe_support": lambda c, need: yes(c["probes"][0]["support"] == need,
                                         {"context": c["probes"][0]["context"],
                                          "support": c["probes"][0]["support"]}),
    "probe_named": lambda c, need: yes(
        all(p["named"] is not None for p in c["probes"] if p["should_name"]),
        [p["named"] for p in c["probes"] if p["should_name"]]),
    "probe_distinct": lambda c, need: yes(
        len({p["named"] for p in c["probes"] if p["should_name"]}) ==
        len([p for p in c["probes"] if p["should_name"]]),
        [p["named"] for p in c["probes"] if p["should_name"]]),
    "probe_unnamed": lambda c, need: yes(c["probes"][-1]["named"] is None,
                                         {"named": c["probes"][-1]["named"],
                                          "context": c["probes"][-1]["context"]}),
    "probe_silent": lambda c, need: yes((not c["probes"][-1]["answered"]) == bool(need),
                                        {"answered": c["probes"][-1]["answered"],
                                         "named": c["probes"][-1]["named"],
                                         "context": c["probes"][-1]["context"],
                                         "competitors": c["probes"][-1]["competitors"]}),
    "anticipatory": lambda c, need: yes(accuracy(c["asked"])["acc"] >= need,
                                        accuracy(c["asked"])),
    "boundary_declined": lambda c, need: boundary_declined(c, need),
    "equal_support": lambda c, need: equal_rivals(c),
    "pick_is_cheaper": lambda c, need: cheap_rival(c),
    "rivals_min": lambda c, need: yes(len(c["probes"][0]["competitors"]) >= need,
                                      c["probes"][0]["competitors"]),
    "rivals_count": lambda c, need: yes(len(c["probes"][0]["competitors"]) == need,
                                        c["probes"][0]["competitors"]),
    "closes_joined": lambda c, need: yes(bool(c["shape"]["sinks"]) == need, c["shape"]["sinks"]),
    "closes_separate": lambda c, need: yes(bool(c["shape"]["sinks"]) == need, c["shape"]["sinks"]),
    "drift_visible": lambda c, need: component_drift(c),
}


def boundary(ctx):
    """Every position at the end of an episode: what follows it was never
    observed, so this is where a claim has nothing under it."""
    return [r for r in ctx["asked"] if r["boundary"]]


def boundary_declined(ctx, need):
    """The fraction of positions at an episode edge that were refused. Joined,
    the edge has been walked across before and is answered; separate, nothing
    precedes a first observation, so the edge and the whole episode decline.
    Which of these happens IS the difference between the readings, so each is
    asked only of the reading that claims it."""
    rows = boundary(ctx)
    if not rows:
        return na({"rows": 0})
    declined = sum(1 for r in rows if r["declined"])
    # Each reading claims an exact fraction -- answered everywhere, or declined
    # everywhere -- so the need is met by matching it, not by exceeding it.
    return yes(round(declined / len(rows), 3) == round(need, 3),
               {"rows": len(rows), "declined": declined,
                "fraction": round(declined / len(rows), 3)})


def rivals(ctx):
    return ctx["probes"][0]["competitors"]


def equal_rivals(ctx):
    r = rivals(ctx)
    if len(r) < 2:
        return na(r)
    return yes(r[0][1] == r[1][1] and r[0][1] > 0, r)


def cheap_rival(ctx):
    r = rivals(ctx)
    if len(r) < 2:
        return na(r)
    errs = sorted(x[2] for x in r)
    return yes(errs[0] < errs[1], {"cheapest": errs[0], "other": errs[-1]})


def judge(ctx):
    rows = []
    sc, crit = ctx["scenario"], ctx["scenario"]["criteria"]
    rows.append(("derived cut", na({"gap": ctx["gap"] and round(ctx["gap"]["ratio"], 2),
                                    "tau": ctx["tau"] and round(ctx["tau"], 5)})))
    for key, need in crit.items():
        reading = None
        if key.endswith("_joined"):
            reading = True
        elif key.endswith("_separate"):
            reading = False
        if reading is not None and reading != ctx["joined"]:
            continue
        base = key.rsplit("_", 1)[0] if reading is not None else key
        fn = CHECKS.get(base) or CHECKS.get(key)
        if fn is None:
            rows.append((key, {"pass": False,
                                      "value": "no measurement registered"}))
            continue
        if need is None:
            rows.append((key, na(fn(ctx, 0)["value"])))
        else:
            rows.append((key, fn(ctx, need)))
    return rows


def report(ctx, rows):
    print("\n%s [%s] -- %s%s" % (ctx["scenario"]["name"], ctx["kind"],
                                 ctx["reading"],
                                 "" if ctx["tau_fixed"] is None else
                                 " (cut fixed at %.4f)" % ctx["tau_fixed"]))
    fails = 0
    for name, row in rows:
        if row["pass"] is None:
            verdict = "n/a"
        elif row["pass"]:
            verdict = "pass"
        else:
            verdict = "FAIL"
            fails += 1
        print("  %-22s %-5s %s" % (name, verdict, show(row["value"])))
    return fails


def evidence_row(ctx, rows):
    return {"reading": ctx["reading"], "tau_fixed": ctx["tau_fixed"],
            "gap": ctx["gap"], "tau": ctx["tau"],
            "classes": ctx["shape"]["classes"],
            "sizes": sorted(ctx["shape"]["sizes"].values(), reverse=True),
            "invariant": ctx["shape"]["invariant"],
            "probes": ctx["probes"], "asked": ctx["asked"],
            "claims": {name: row for name, row in rows}}


def main():
    sweep = "--sweep" in sys.argv
    evidence = {"priors": PRIORS, "thresholds": {"ACCURACY": ACCURACY, "FAN": FAN},
                "scenarios": {}}
    fails = 0
    for build in S.ALL:
        sc = build()
        for reading, joined in READINGS.items():
            ctx = run_one(sc, joined)
            rows = judge(ctx)
            fails += report(ctx, rows)
            evidence["scenarios"].setdefault(sc["name"], {})[ctx["reading"]] = evidence_row(ctx, rows)
    print("\n%d failing claim(s)" % fails)

    if sweep:
        print("\n=== the cut moved: inside its own gap, and outside it ===")
        for build in S.ALL:
            sc = build()
            base = run_one(sc, False)
            if base["gap"] is None:
                print("  %-14s no separation observed: imposed cut %-18s -> classes %d,"
                      " accuracy %.3f. The harness cannot be talked into recurrences"
                      " the feed does not support." %
                      (sc["name"], "tau=0.10",
                       run_one(sc, False, 0.10)["shape"]["classes"],
                       accuracy(run_one(sc, False, 0.10)["asked"])["acc"]))
                continue
            lo, hi = base["gap"]["lo"], base["gap"]["hi"]
            cuts = [lo + f * (hi - lo) for f in (0.15, 0.50, 0.85)]
            outside = run_one(sc, False, hi * 3.0)
            for reading, joined in READINGS.items():
                want = judge(run_one(sc, joined))
                stable, moved = True, []
                for tau in cuts:
                    got = judge(run_one(sc, joined, tau))
                    for (name, row), (n2, r2) in zip(want, got):
                        if name.endswith(("_joined", "_separate")) or row["pass"] is None:
                            continue
                        if row["pass"] != r2["pass"]:
                            stable = False
                            moved.append((name, show(r2["value"])))
                print("  %-14s %-8s gap %.4f..%.4f  inside: %s%s   outside(gap): classes %d, unchanged %s" %
                      (sc["name"], reading, lo, hi,
                       "verdicts hold" if stable else "VERDICT MOVED",
                       "" if stable else " " + show(moved),
                       outside["shape"]["classes"],
                       outside["shape"]["classes"] == base["shape"]["classes"]))

    os.makedirs(os.path.dirname(EVIDENCE), exist_ok=True)
    with open(EVIDENCE, "w", encoding="utf-8") as fh:
        json.dump(evidence, fh, indent=1, sort_keys=True)
    print("evidence -> %s" % EVIDENCE)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
