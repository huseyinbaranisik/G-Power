"""Ölçek kâhini: chi2-contingency için 500+ vektör üretir.

DİKKAT: Bu dosya G*Power DEĞİLDİR. Bağımsız bir referanstır (statsmodels varsa o,
yoksa scipy). Asıl kâhin G*Power arayüzünden toplanan gpower_vectors.csv'dir.

Kütüphaneler N'yi kesirli verir (n_frac). G*Power tam sayıya yukarı yuvarlar.
n_ceil sütunu "en küçük tam sayı N, güç >= hedef" aramasıdır. İkisinin farkı
LEDGER.md'de bir bulgu olarak açıklanmalı.

Kullanım:  python oracle/gen_scale_oracle.py  ->  oracle/scale_vectors.csv
"""
import csv
import itertools
import math
import os

from scipy.optimize import brentq
from scipy.stats import chi2, ncx2

try:
    from statsmodels.stats.power import GofChisquarePower  # noqa: F401
    SOURCE = "statsmodels"
except ImportError:
    SOURCE = "scipy"


def power(w, alpha, n, df):
    crit = chi2.ppf(1 - alpha, df)
    return ncx2.sf(crit, df, w * w * n), crit


def n_fractional(w, alpha, target, df):
    if SOURCE == "statsmodels":
        from statsmodels.stats.power import GofChisquarePower
        return GofChisquarePower().solve_power(
            effect_size=w, nobs=None, alpha=alpha, power=target, n_bins=df + 1)
    f = lambda n: power(w, alpha, n, df)[0] - target
    hi = 10.0
    while f(hi) < 0:
        hi *= 2
    return brentq(f, 1e-9, hi, xtol=1e-10)


def n_ceil(w, alpha, target, df):
    n = max(1, math.floor(n_fractional(w, alpha, target, df)) - 2)
    while power(w, alpha, n, df)[0] < target:
        n += 1
    return n


def main():
    out = os.path.join(os.path.dirname(__file__), "scale_vectors.csv")
    ws = [0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.7, 0.9]
    alphas = [0.01, 0.05, 0.10]
    powers = [0.8, 0.9, 0.95]
    dfs = [1, 2, 3, 4, 6, 8, 10]
    rows = []
    for w, a, p, df in itertools.product(ws, alphas, powers, dfs):
        nf = n_fractional(w, a, p, df)
        nc = n_ceil(w, a, p, df)
        pw, crit = power(w, a, nc, df)
        rows.append(dict(id=f"S{len(rows)+1:04d}", mode="a-priori", w=w, alpha=a,
                         power=p, df=df, n_frac=f"{nf:.4f}", n_total=nc,
                         ncp=f"{w*w*nc:.4f}", critical_chi2=f"{crit:.4f}",
                         actual_power=f"{pw:.4f}", source=SOURCE))
    with open(out, "w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)
    print(f"{len(rows)} vektör -> {out} (kaynak: {SOURCE})")


if __name__ == "__main__":
    main()
