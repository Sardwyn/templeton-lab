"""Adversarial checks on the system under test. Run: python harness/audit.py

1. Forbidden vocabulary: the forbidden words may not appear as bare tokens in
   core.py. Prose that *explains the absence* is allowed only inside docstrings
   and comments, so this scans executable lines only.
2. Nothing derived is retained: a live Harness, after real observations, must
   hold only memory, the current episode pointer, and its configuration. Any
   cached class table or expectation map would be structure smuggled past the
   'memory = observed sequences + error values' rule.
3. No per-scenario knob: constructing a Harness takes no scenario argument.
   `tau` exists only as a measurement instrument and is reported as such.
"""

import ast
import inspect
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from core import Harness
import scenarios as S

FORBIDDEN = [
    "object", "entity", "ontology", "cause", "because", "therefore", "agent",
    "intention", "identity", "similarity", "same", "truth", "symbol",
    "graph", "node", "label", "world", "model", "remember", "belief", "rule",
    "predict", "explain", "why", "want", "purpose",
]
# `self` is on the forbidden list as a concept but it is also Python's receiver,
# so it cannot be scanned as a token. Check 2 tests the concept instead: a live
# instance must hold no self, no owner, and no persistent identity of anything.


def executable_lines(src):
    """Code with every string literal and comment blanked out, line positions
    preserved. Prose that explains an absence is documentation; it cannot hide
    logic, because the logic is what remains."""
    import io
    import tokenize
    out = src.splitlines()
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type in (tokenize.STRING, tokenize.COMMENT):
            for ln in range(tok.start[0], tok.end[0] + 1):
                out[ln - 1] = ""
    return {i: l for i, l in enumerate(out, 1) if l}


def scan(path):
    src = open(path, encoding="utf-8").read()
    hits = []
    for ln, code in executable_lines(src).items():
        words = code.lower().replace("_", " ").split()
        for word in FORBIDDEN:
            if word in words:
                hits.append((ln, word, code.strip()))
    return hits


def names(path):
    """Every function and attribute name in the file, checked for the same
    words. `self` is Python's receiver and cannot be banned; check 2 covers
    the concept instead by asserting what a live instance holds."""
    src = open(path, encoding="utf-8").read()
    tree = ast.parse(src)
    found = set()
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            found.add(n.name)
        elif isinstance(n, ast.Attribute):
            found.add(n.attr)
        elif isinstance(n, ast.Name):
            found.add(n.id)
    bad = sorted(w for w in FORBIDDEN if any(w in f.lower() for f in found))
    return bad, sorted(found)


def live_state():
    h = Harness()
    sc = S.prediction()
    for blk in sc["blocks"]:
        h.start_episode()
        for s, e in blk:
            h.observe(s, e)
    for m in range(4, len(sc["blocks"])):
        h.expect([s for s, _ in sc["blocks"][m]])
    h.classes()
    h.weights()
    return sorted(h.__dict__)


def main():
    ok = True

    print("1. FORBIDDEN VOCABULARY in core.py (executable lines only)")
    hits = scan(os.path.join(HERE, "core.py"))
    if hits:
        ok = False
        for ln, word, line in hits:
            print("   FAIL line %d: '%s' in: %s" % (ln, word, line))
    else:
        print("   PASS no forbidden token appears in executable code (%d words checked)"
              % len(FORBIDDEN))

    print("1b. FORBIDDEN VOCABULARY IN IDENTIFIER NAMES (functions, attributes)")
    bad, allnames = names(os.path.join(HERE, "core.py"))
    if bad:
        ok = False
        print("   FAIL identifiers carrying a forbidden concept: %s" % bad)
    else:
        print("   PASS %d identifiers, none named after a forbidden concept"
              % len(allnames))

    print("2. NOTHING DERIVED IS RETAINED")
    attrs = live_state()
    allowed = ["episode", "memory", "tau"]
    extra = [a for a in attrs if a not in allowed]
    if extra:
        ok = False
        print("   FAIL unexpected attributes: %s" % extra)
    else:
        print("   PASS live instance holds %s -- every structure is recomputed "
              "from memory on each call" % attrs)

    print("3. NO PER-SCENARIO KNOB")
    params = list(inspect.signature(Harness.__init__).parameters)[1:]
    print("   %s __init__ takes %s; tau is a measurement instrument only"
          % ("PASS" if params == ["tau"] else "FAIL", params))
    if params != ["tau"]:
        ok = False

    print("4. MEMORY SHAPE")
    h = Harness()
    sc = S.prediction()
    h.start_episode()
    h.observe(sc["blocks"][0][0][0], sc["blocks"][0][0][1])
    leaf = h.memory[0][0]
    good = isinstance(leaf, tuple) and len(leaf) == 2 and isinstance(leaf[0], tuple) \
        and isinstance(leaf[1], float)
    print("   %s a memory entry is (%s, %s) -- state and one error value, nothing else"
          % ("PASS" if good else "FAIL", type(leaf[0]).__name__, type(leaf[1]).__name__))
    if not good:
        ok = False

    print("\n%s" % ("AUDIT CLEAN" if ok else "AUDIT FLAGGED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
