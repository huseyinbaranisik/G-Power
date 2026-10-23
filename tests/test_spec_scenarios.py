"""SPEC.md §6 Gherkin senaryoları.

Tablolar SPEC'ten birebir aktarıldı. SPEC'in kabul ettiği ama CONTRACT §5'in
reddettiği girdiler (kesirli df, kesirli/1 olan post hoc N, post hoc w=0) burada
CONTRACT'a göre ret olarak sınanır; SPEC'in beklediği sayılar ise motorun iç
fonksiyonlarıyla ayrıca doğrulanır (aralık içi davranış SPEC'e aittir).
"""
import pytest

from conftest import assert_displayed, chi2_args, run_cli
from engine import chi2_contingency as cc
from engine.display import gpower_format


def a_priori(w, alpha, power, df):
    return run_cli(*chi2_args("a-priori", w=w, alpha=alpha, power=power, df=df))


def post_hoc(w, alpha, n, df):
    return run_cli(*chi2_args("post-hoc", w=w, alpha=alpha, n_total=n, df=df))


def check(out, **exp):
    for k, v in exp.items():
        if k == "n_total":
            assert out[k] == v and isinstance(out[k], int), f"n_total: {out[k]!r} != {v}"
        else:
            assert_displayed(out[k], v, k)


# --- Feature: a priori -------------------------------------------------------

APRIORI = """
| 0.3  | 0.05  | 0.95  | 5   | 220     | 19.8000000 | 11.0704977 | 0.9502155 |
| 0.1  | 0.05  | 0.8   | 1   | 785     | 7.8500000  | 3.8414588  | 0.8000569 |
| 0.1  | 0.05  | 0.8   | 2   | 964     | 9.6400000  | 5.9914645  | 0.8002316 |
| 0.1  | 0.05  | 0.8   | 4   | 1194    | 11.9400000 | 9.4877290  | 0.8001775 |
| 0.3  | 0.05  | 0.8   | 1   | 88      | 7.9200000  | 3.8414588  | 0.8035275 |
| 0.3  | 0.05  | 0.8   | 2   | 108     | 9.7200000  | 5.9914645  | 0.8036939 |
| 0.3  | 0.05  | 0.8   | 4   | 133     | 11.9700000 | 9.4877290  | 0.8013043 |
| 0.5  | 0.05  | 0.8   | 1   | 32      | 8.0000000  | 3.8414588  | 0.8074304 |
| 0.5  | 0.05  | 0.8   | 2   | 39      | 9.7500000  | 5.9914645  | 0.8049793 |
| 0.5  | 0.05  | 0.8   | 4   | 48      | 12.0000000 | 9.4877290  | 0.8024261 |
| 0.3  | 0.01  | 0.9   | 3   | 214     | 19.2600000 | 11.3448667 | 0.9002433 |
| 0.3  | 0.1   | 0.9   | 3   | 132     | 11.8800000 | 6.2513886  | 0.9020008 |
| 0.01 | 0.05  | 0.8   | 1   | 78489   | 7.8489000  | 3.8414588  | 0.8000020 |
| 0.3  | 0.05  | 0.999 | 2   | 325     | 29.2500000 | 5.9914645  | 0.9990204 |
| 0.3  | 0.05  | 0.8   | 100 | 451     | 40.5900000 | 124.3421   | 0.8004859 |
"""


def _table(text):
    return [[c.strip() for c in line.strip().strip("|").split("|")]
            for line in text.strip().splitlines()]


def test_manual_example():
    code, out, raw = a_priori("0.3", "0.05", "0.95", "5")
    assert code == 0, raw
    check(out, n_total=220, ncp="19.8000000", critical_chi2="11.0704977",
          actual_power="0.9502155")


@pytest.mark.parametrize("w,alpha,power,df,n,ncp,crit,ap", _table(APRIORI))
def test_smallest_integer_n(w, alpha, power, df, n, ncp, crit, ap):
    code, out, raw = a_priori(w, alpha, power, df)
    assert code == 0, raw
    check(out, n_total=int(n), ncp=ncp, critical_chi2=crit, actual_power=ap)
    w_, a_, p_, df_ = float(w), float(alpha), float(power), float(df)
    assert cc.power(w_, a_, int(n), df_) >= p_
    assert cc.power(w_, a_, int(n) - 1, df_) < p_


def test_no_upper_bound_tiny_w():
    code, out, raw = a_priori("0.001", "0.05", "0.8", "1")
    assert code == 0, raw
    check(out, n_total=7848861, ncp="7.8488610")


def test_large_w_small_n():
    code, out, raw = a_priori("2", "0.05", "0.8", "1")
    assert code == 0, raw
    check(out, n_total=2, ncp="8.0000000")


def test_minimum_n_is_one():
    code, out, raw = a_priori("5", "0.05", "0.95", "10")
    assert code == 0, raw
    check(out, n_total=1, ncp="25.0000000", critical_chi2="18.3070381",
          actual_power="0.9554779")


def test_power_equal_alpha_accepted():
    code, out, raw = a_priori("0.3", "0.05", "0.05", "2")
    assert code == 0, raw
    check(out, n_total=1, ncp="0.0900000", critical_chi2="5.9914645",
          actual_power="0.0568148")


def test_power_below_alpha():
    # SPEC "aralık-dışı hatası" diyor; kod adı CONTRACT'tan: güç<α tek tek geçerli
    # değerlerin birlikte anlamsız olması → INCONSISTENT (CONTRACT §2.4 örneği).
    code, out, raw = a_priori("0.3", "0.05", "0.04", "2")
    assert code == 2, raw
    assert out == {"error": "Power must be greater than or equal to alpha.",
                   "code": "INCONSISTENT", "field": "power"}


def test_fractional_df_rejected_by_contract():
    code, out, raw = a_priori("0.3", "0.05", "0.8", "2.5")
    assert code == 2, raw
    assert out["code"] == "INVALID_VALUE" and out["field"] == "df"


def test_fractional_df_engine_behaviour():
    # SPEC L21: motor kesirli df'yi olduğu gibi kullanır (G028).
    r = cc.a_priori(0.3, 0.05, 0.8, 2.5)
    assert r["n_total"] == 115
    check(r, ncp="10.3500000", critical_chi2="6.9280761", actual_power="0.8017509")


INVALID = """
| 0    | 0.05       | 0.8        | 1  | w     | Effect size w must be greater 1e-06.               |
| -0.3 | 0.05       | 0.8        | 1  | w     | Effect size w must be greater 1e-06.               |
| 0.3  | 0          | 0.8        | 1  | alpha | Alpha is outside the admissible range (1e-07, 1).  |
| 0.3  | 1          | 0.8        | 1  | alpha | Alpha is outside the admissible range (1e-07, 1).  |
| 0.3  | 0.99999995 | 0.99999995 | 1  | alpha | Alpha is outside the admissible range (1e-07, 1).  |
| 0.3  | 0.05       | 1          | 1  | power | Power is outside the admissible range (1e-07, 1).  |
| 0.3  | 0.05       | 0.8        | 0  | df    | Degrees of Freedom must be greater or equal one.   |
"""


@pytest.mark.parametrize("w,alpha,power,df,field,msg", _table(INVALID))
def test_invalid_inputs(w, alpha, power, df, field, msg):
    code, out, raw = a_priori(w, alpha, power, df)
    assert code == 2, raw
    assert out == {"error": msg, "code": "OUT_OF_RANGE", "field": field}


def test_closed_upper_bound_power():
    code, out, raw = a_priori("0.3", "0.05", "0.9999999", "1")
    assert code == 0, raw
    check(out, n_total=570, ncp="51.3000000", critical_chi2="3.8414588",
          actual_power="0.9999999")


def test_validation_order_df_before_w():
    code, out, raw = a_priori("0", "0.05", "0.8", "0")
    assert code == 2, raw
    assert out == {"error": "Degrees of Freedom must be greater or equal one.",
                   "code": "OUT_OF_RANGE", "field": "df"}


# --- Feature: post hoc -------------------------------------------------------

POSTHOC = """
| 0.3 | 0.05  | 50   | 5  | 0.3271785 | 4.5000000  | 11.0704977 |
| 0.3 | 0.05  | 100  | 5  | 0.6235846 | 9.0000000  | 11.0704977 |
| 0.3 | 0.05  | 220  | 5  | 0.9502155 | 19.8000000 | 11.0704977 |
| 0.3 | 0.05  | 500  | 5  | 0.9999276 | 45.0000000 | 11.0704977 |
| 0.1 | 0.05  | 1000 | 1  | 0.8853791 | 10.0000000 | 3.8414588  |
| 0.5 | 0.01  | 30   | 2  | 0.4525585 | 7.5000000  | 9.2103404  |
"""


@pytest.mark.parametrize("w,alpha,n,df,power,ncp,crit", _table(POSTHOC))
def test_post_hoc(w, alpha, n, df, power, ncp, crit):
    code, out, raw = post_hoc(w, alpha, n, df)
    assert code == 0, raw
    check(out, power=power, ncp=ncp, critical_chi2=crit)


def test_post_hoc_n1_rejected_by_contract():
    # SPEC tablosunun son satırı (n=1); CONTRACT §5 n_total ≥ 2.
    code, out, raw = post_hoc("0.3", "0.05", "1", "1")
    assert code == 2, raw
    assert out["code"] == "OUT_OF_RANGE" and out["field"] == "n_total"


def test_post_hoc_n1_engine_behaviour():
    check(cc.post_hoc(0.3, 0.05, 1, 1), power="0.0603726", ncp="0.0900000",
          critical_chi2="3.8414588")


@pytest.mark.parametrize("n", ["10.2", "10.5", "10.7"])
def test_fractional_n_rejected_by_contract(n):
    code, out, raw = post_hoc("0.3", "0.05", n, "1")
    assert code == 2, raw
    assert out["code"] == "INVALID_VALUE" and out["field"] == "n_total"


@pytest.mark.parametrize("n,rounded,ncp,power", [
    (10.2, 10, "0.9000000", "0.1577560"),
    (10.5, 11, "0.9900000", "0.1688419"),
    (10.7, 11, "0.9900000", "0.1688419"),
])
def test_fractional_n_engine_behaviour(n, rounded, ncp, power):
    # SPEC §3.4 (L30): yarım yukarı yuvarlama, banker's değil.
    assert cc.round_n(n) == rounded
    check(cc.post_hoc(0.3, 0.05, n, 1), ncp=ncp, power=power)


def test_post_hoc_w0_rejected_by_contract():
    code, out, raw = post_hoc("0", "0.05", "100", "1")
    assert code == 2, raw
    assert out["code"] == "OUT_OF_RANGE" and out["field"] == "w"


def test_post_hoc_w0_engine_behaviour():
    r = cc.post_hoc(0.0, 0.05, 100, 1)
    assert r["ncp"] == 0 and gpower_format(r["ncp"]) == "0"
    check(r, power="0.0500000", critical_chi2="3.8414588")


def test_closed_upper_bound_alpha():
    code, out, raw = post_hoc("0.3", "0.9999999", "10", "1")
    assert code == 0, raw
    check(out, power="0.9999999", ncp="0.9000000", critical_chi2="1.570796e-14")
    assert gpower_format(out["critical_chi2"]) == "1.570796e-14"


@pytest.mark.parametrize("alpha,power,crit", [
    ("0.999", "0.9993624", "1.570797e-06"),
    ("0.99", "0.9936236", "0.0001570879"),
    ("0.95", "0.9680998", "0.00393214"),
    ("0.9", "0.9360864", "0.0157908"),
])
def test_small_value_display(alpha, power, crit):
    code, out, raw = post_hoc("0.3", alpha, "10", "1")
    assert code == 0, raw
    check(out, power=power, ncp="0.9000000", critical_chi2=crit)
    assert gpower_format(out["critical_chi2"]) == crit


def test_post_hoc_negative_w():
    code, out, raw = post_hoc("-0.3", "0.05", "100", "1")
    assert code == 2, raw
    assert out == {"error": "Effect size w must be non-negative.",
                   "code": "OUT_OF_RANGE", "field": "w"}


@pytest.mark.parametrize("n", ["0", "2147483647"])
def test_n_outside_admissible_range(n):
    code, out, raw = post_hoc("0.3", "0.05", n, "1")
    assert code == 2, raw
    assert out == {"error": "Total sample size is outside the admissible range (1, 2147483646)",
                   "code": "OUT_OF_RANGE", "field": "n_total"}


# --- SPEC §5 gösterim örnekleri ---------------------------------------------

@pytest.mark.parametrize("x,shown", [
    (0.0, "0"), (1.570796e-14, "1.570796e-14"), (19.8, "19.8000000"),
    (124.342099, "124.3421"), (0.0157908, "0.0157908"), (0.00393214, "0.00393214"),
])
def test_display_rule(x, shown):
    assert gpower_format(x) == shown
