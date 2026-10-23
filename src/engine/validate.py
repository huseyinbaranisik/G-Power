"""Girdi doğrulama: CONTRACT §2.1/§5 (arayüz, aralık) ∩ SPEC §4 (aralık içi davranış).

Sıra (SPEC §4): a priori df → w → α → güç → güç ≥ α; post hoc df → w → α → N.
Her alan önce ayrıştırılır (INVALID_VALUE), sonra aralığı denetlenir.
"""
import math
import re

from .errors import EngineError

_DECIMAL = re.compile(r"[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?")
_INTEGER = re.compile(r"[+-]?\d+")

N_MAX = 2147483646

MSG_DF = "Degrees of Freedom must be greater or equal one."
MSG_W_APRIORI = "Effect size w must be greater 1e-06."
MSG_W_NEG = "Effect size w must be non-negative."
MSG_W_ZERO = "Effect size w must be greater than 0 (contract range w > 0)."
MSG_ALPHA = "Alpha is outside the admissible range (1e-07, 1)."
MSG_POWER = "Power is outside the admissible range (1e-07, 1)."
MSG_POWER_ALPHA = "Power must be greater than or equal to alpha."
MSG_N = "Total sample size is outside the admissible range (1, 2147483646)"
MSG_N_MIN = "Total sample size must be at least 2 (contract range n_total >= 2)."


def decimal(params, field):
    s = params[field]
    if not _DECIMAL.fullmatch(s):
        raise EngineError("INVALID_VALUE", field, f"{field}: not a decimal number: {s!r}")
    x = float(s)
    if not math.isfinite(x):
        raise EngineError("INVALID_VALUE", field, f"{field}: not a finite number: {s!r}")
    return x


def integer(params, field):
    s = params[field]
    if not _INTEGER.fullmatch(s):
        raise EngineError("INVALID_VALUE", field, f"{field}: must be an integer: {s!r}")
    return int(s)


def _out(field, msg):
    return EngineError("OUT_OF_RANGE", field, msg)


def df(params):
    v = integer(params, "df")
    if v < 1:
        raise _out("df", MSG_DF)
    return v


def w_a_priori(params):
    v = decimal(params, "w")
    if not v >= 1e-06:
        raise _out("w", MSG_W_APRIORI)
    return v


def w_post_hoc(params):
    v = decimal(params, "w")
    if v < 0:
        raise _out("w", MSG_W_NEG)
    if v == 0:  # SPEC kabul eder (G039), CONTRACT §5 w > 0 → CONTRACT kazanır
        raise _out("w", MSG_W_ZERO)
    return v


def _unit(params, field, msg):
    v = decimal(params, field)
    if not 1e-07 <= v <= 0.9999999:
        raise _out(field, msg)
    return v


def alpha(params):
    return _unit(params, "alpha", MSG_ALPHA)


def power(params, alpha_value):
    v = _unit(params, "power", MSG_POWER)
    if v < alpha_value:
        raise EngineError("INCONSISTENT", "power", MSG_POWER_ALPHA)
    return v


def n_total(params):
    v = integer(params, "n_total")
    if v < 1 or v > N_MAX:
        raise _out("n_total", MSG_N)
    if v < 2:  # SPEC kabul eder (G035), CONTRACT §5 n_total ≥ 2
        raise _out("n_total", MSG_N_MIN)
    return v
