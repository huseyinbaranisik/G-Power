"""Brent kök bulucu, SPEC §3.2 adım 2 (L6, L7, L12)."""
import math

EPS = 2.0 ** -53
MAX_ITER = 300


def brent(f, a, b, max_iter=MAX_ITER):
    """[a, b] aralığında f'nin kökü.

    - f(a)·f(b) > 0 ise 0 döner (hata yok).
    - Yakınsama: f(b) = 0 ya da |(c − b)/2| ≤ 2⁻⁵³·|b|; ayrı mutlak tolerans yok.
    - max_iter aşılırsa o anki en iyi tahmin döner (hata yok).
    """
    fa, fb = f(a), f(b)
    if fa * fb > 0:
        return 0.0
    c, fc = b, fb
    d = e = b - a
    for _ in range(max_iter):
        if (fb > 0 and fc > 0) or (fb < 0 and fc < 0):
            c, fc = a, fa
            d = e = b - a
        if abs(fc) < abs(fb):
            a, b, c = b, c, b
            fa, fb, fc = fb, fc, fb
        tol1 = EPS * abs(b)
        xm = 0.5 * (c - b)
        if abs(xm) <= tol1 or fb == 0:
            return b
        if abs(e) >= tol1 and abs(fa) > abs(fb):
            s = fb / fa
            if a == c:
                p = 2.0 * xm * s
                q = 1.0 - s
            else:
                q = fa / fc
                r = fb / fc
                p = s * (2.0 * xm * q * (q - r) - (b - a) * (r - 1.0))
                q = (q - 1.0) * (r - 1.0) * (s - 1.0)
            if p > 0:
                q = -q
            p = abs(p)
            if 2.0 * p < min(3.0 * xm * q - abs(tol1 * q), abs(e * q)):
                e, d = d, p / q
            else:
                d = e = xm
        else:
            d = e = xm
        a, fa = b, fb
        b += d if abs(d) > tol1 else math.copysign(tol1, xm)
        fb = f(b)
    return b
