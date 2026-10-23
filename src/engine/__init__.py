"""Tek hesap motoru. Giriş noktası: `run(params)`; params alan adı → ham metin."""
import math
import sys

from . import chi2_contingency, validate
from .errors import EngineError

CONTRACT_VERSION = "1.0.0"
NAME = "G-Power (huseyinbaranisik)"


def version():
    v = sys.version_info
    return {"contract_version": CONTRACT_VERSION, "name": NAME,
            "engine": f"Python {v.major}.{v.minor}.{v.micro}"}


def _chi2_a_priori(p):
    df = validate.df(p)
    w = validate.w_a_priori(p)
    alpha = validate.alpha(p)
    power = validate.power(p, alpha)
    return chi2_contingency.a_priori(w, alpha, power, df)


def _chi2_post_hoc(p):
    df = validate.df(p)
    w = validate.w_post_hoc(p)
    alpha = validate.alpha(p)
    n = validate.n_total(p)
    return chi2_contingency.post_hoc(w, alpha, n, df)


# test → mod → (girdi alanları, doğrula + hesapla). Bonus modlar SPEC'te yok.
_MODES = {
    "chi2-contingency": {
        "a-priori": (("w", "alpha", "power", "df"), _chi2_a_priori),
        "post-hoc": (("w", "alpha", "n_total", "df"), _chi2_post_hoc),
    },
}


def run(params):
    """params: {"test": ..., "mode": ..., alan: metin}. Sonuç dict ya da EngineError."""
    for key in ("test", "mode"):
        if key not in params:
            raise EngineError("MISSING_PARAM", key, f"missing required field: {key}")
    test, mode = params["test"], params["mode"]
    if test not in _MODES:
        raise EngineError("UNSUPPORTED", "test", f"unsupported test: {test}")
    if mode not in _MODES[test]:
        raise EngineError("UNSUPPORTED", "mode", f"unsupported mode for {test}: {mode}")
    fields, handler = _MODES[test][mode]
    for key in params:
        if key not in fields and key not in ("test", "mode"):
            raise EngineError("UNKNOWN_PARAM", key, f"unknown field for {test}/{mode}: {key}")
    for key in fields:
        if key not in params:
            raise EngineError("MISSING_PARAM", key, f"missing required field: {key}")
    out = handler(params)
    if not all(math.isfinite(v) for v in out.values()):
        raise EngineError("NO_SOLUTION", None, "computation produced a non-finite result")
    return out


__all__ = ["EngineError", "run", "version"]
