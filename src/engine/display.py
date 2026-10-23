"""G*Power ekran gösterimi, SPEC §5 (L31) [AJAN].

Yalnızca testler ve insan okuması içindir: CLI tam double basar (CONTRACT §2.3).
"""

LOW = 0.01   # [AJAN] eşik varsayımı: 0.00393214 < eşik ≤ 0.0157908
HIGH = 100.0


def gpower_format(x):
    if x == 0:
        return "0"
    if LOW <= abs(x) < HIGH:
        return "%.7f" % x
    return "%.7g" % x
