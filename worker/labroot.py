"""Where the org record lives.

On Brad's machine the checkout is F:\\Lab, and the dashboard used to assume
that path even when it was started from somewhere else. The root is the
checkout that contains this package, which is F:\\Lab when that is where the
file lives. TEMPLETON_LAB overrides it for a throwaway copy; it is not part
of the normal run.
"""
import os
from pathlib import Path


def lab_root():
    env = os.environ.get("TEMPLETON_LAB")
    if env:
        candidate = Path(env)
        try:
            if candidate.is_dir() and (candidate / "org").is_dir():
                return candidate.resolve()
        except OSError:
            pass
    here = Path(__file__).resolve().parent.parent
    if (here / "org").is_dir() and (here / "worker").is_dir():
        return here
    legacy = Path(r"F:\Lab")
    try:
        if legacy.is_dir() and (legacy / "org").is_dir():
            return legacy.resolve()
    except OSError:
        pass
    return here
