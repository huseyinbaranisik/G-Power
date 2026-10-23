"""χ² olumsallık tablosu güç analizi (SPEC §2, §3).

Fonksiyonlar doğrulanmış sayılar alır; aralık denetimi `validate.py`'dedir.
"""
from decimal import ROUND_CEILING, ROUND_HALF_UP, Decimal

# scipy.stats yerine scipy.special: aynı rutinler (chi2.ppf/cdf, ncx2.cdf bunları
# çağırır), yarı içe aktarma süresi (CONTRACT §2.1: çağrı ≤ 2 s).
from scipy.special import chdtr, chdtri, chndtr

from .brent import brent

N_START = 100.0
N_FLOOR = 1.0


def critical(alpha, df):
    """c = merkezi χ²(df)'nin (1 − α) yüzdeliği (L2)."""
    q = 1.0 - alpha
    return float(chdtri(df, 1.0 - q))  # chdtri üst kuyruk alır; chi2.ppf(q) ile aynı


def _cdf(x, df, lam):
    """Merkezsiz χ² CDF; λ < 1e-100 ise merkezi (L26)."""
    if lam < 1e-100:
        return float(chdtr(df, x))
    return float(chndtr(x, df, lam))


def power(w, alpha, n, df):
    """güç = 1 − F(c; df, w²·N) (L1, L3). N kesirli olabilir."""
    return 1.0 - _cdf(critical(alpha, df), df, w * w * n)


def round_n(n):
    """Post hoc N: en yakın tam sayı, yarımlar yukarı (SPEC §3.4, L30)."""
    return int(Decimal(n).quantize(Decimal(1), ROUND_HALF_UP))


def _ceil10(x):
    """⌈round(x·10¹⁰)/10¹⁰⌉, yuvarlama yarım yukarı (L10)."""
    q = Decimal(x).quantize(Decimal("1e-10"), ROUND_HALF_UP)
    return int(q.to_integral_value(ROUND_CEILING))


def _bracket(f):
    """Aralık kurma, SPEC §3.2 adım 1 (L8, L9). Üst sınır yoktur."""
    if f(N_START) >= 0:
        hi = N_START
        mid = (N_FLOOR + N_START) / 2
        while mid >= N_FLOOR and f(mid) > 0:
            hi = mid
            mid = (mid + 1) / 2 - 1
        lo = mid
    else:
        lo, hi = N_START, N_START * 1.6
        while f(hi) < 0:
            lo, hi = hi, hi * 1.6
    return max(lo, N_FLOOR), hi


def a_priori(w, alpha, target, df):
    crit = critical(alpha, df)

    def f(n):
        return 1.0 - _cdf(crit, df, w * w * n) - target

    lo, hi = _bracket(f)
    n = _ceil10(brent(f, lo, hi))
    if n < lo:  # minimum N kuralı (L11)
        n = _ceil10(lo)
    return {"ncp": w * w * n, "critical_chi2": crit, "n_total": n,
            "actual_power": power(w, alpha, n, df)}


def post_hoc(w, alpha, n, df):
    n = round_n(n)
    crit = critical(alpha, df)
    lam = w * w * n
    return {"ncp": lam, "critical_chi2": crit,
            "power": 1.0 - _cdf(crit, df, lam)}
