"""oracle/gpower_vectors.csv (G*Power 3.1.9.7 ekranı) satırları, CLI üzerinden."""
import csv
import re

import pytest

from conftest import ORACLE, assert_displayed, chi2_args, run_cli

INPUTS = {"a-priori": ["w", "alpha", "power", "df"],
          "post-hoc": ["w", "alpha", "n_total", "df"]}
OUTPUTS = {"a-priori": ["n_total", "ncp", "critical_chi2", "actual_power"],
           "post-hoc": ["ncp", "critical_chi2", "power"]}

# G*Power'ın hata verdiği satırlar: (field, code). Kodlar CONTRACT §2.4'ten.
ERRORS = {
    "G018": ("power", "INCONSISTENT"),  # güç < α: tek tek geçerli, birlikte anlamsız
    "G022": ("w", "OUT_OF_RANGE"),
    "G023": ("w", "OUT_OF_RANGE"),
    "G024": ("alpha", "OUT_OF_RANGE"),
    "G025": ("alpha", "OUT_OF_RANGE"),
    "G026": ("power", "OUT_OF_RANGE"),
    "G027": ("df", "OUT_OF_RANGE"),
    "G040": ("n_total", "OUT_OF_RANGE"),
    "G041": ("n_total", "OUT_OF_RANGE"),
    "G044": ("alpha", "OUT_OF_RANGE"),
    "G045": ("df", "OUT_OF_RANGE"),
    "G048": ("w", "OUT_OF_RANGE"),
}

# Sözleşme çelişkisi: G*Power sonuç veriyor, CONTRACT §5 reddediyor. CONTRACT kazanır.
CONTRACT_CONFLICTS = {
    "G028": ("df", "INVALID_VALUE"),       # df=2.5; §5: df tam sayı
    "G035": ("n_total", "OUT_OF_RANGE"),   # N=1; §5: n_total ≥ 2
    "G036": ("n_total", "INVALID_VALUE"),  # N=10.5; §5: n_total tam sayı
    "G037": ("n_total", "INVALID_VALUE"),  # N=10.2
    "G038": ("n_total", "INVALID_VALUE"),  # N=10.7
    "G039": ("w", "OUT_OF_RANGE"),         # post hoc w=0; §5: w > 0
}


def _rows():
    with open(ORACLE / "gpower_vectors.csv", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


ROWS = _rows()


def _call(row):
    mode = row["mode"]
    fields = {k: row[k] for k in INPUTS[mode] if row[k] != ""}
    return run_cli(*chi2_args(mode, **fields))


def _msg(note):
    m = re.search(r'"Input error": "(.*?)"', note)
    return m.group(1) if m else None


@pytest.mark.parametrize("row", [r for r in ROWS if r["expect_error"] == ""
                                 and r["id"] not in CONTRACT_CONFLICTS],
                         ids=lambda r: r["id"])
def test_values(row):
    code, out, raw = _call(row)
    assert code == 0, raw
    for k in OUTPUTS[row["mode"]]:
        if k in INPUTS[row["mode"]]:
            continue
        exp = row[k]
        if k == "n_total":
            assert out[k] == int(exp) and isinstance(out[k], int), f"n_total: {out[k]!r} != {exp}"
        else:
            assert_displayed(out[k], exp, k)
    # post hoc'ta `power` sütunu beklenen güçtür
    if row["mode"] == "post-hoc":
        assert_displayed(out["power"], row["power"], "power")


@pytest.mark.parametrize("row", [r for r in ROWS if r["expect_error"] == "evet"],
                         ids=lambda r: r["id"])
def test_errors(row):
    code, out, raw = _call(row)
    field, ecode = ERRORS[row["id"]]
    assert code == 2, raw
    assert out == {"error": _msg(row["note"]), "code": ecode, "field": field}


@pytest.mark.parametrize("rid", sorted(CONTRACT_CONFLICTS))
def test_contract_conflicts_rejected(rid):
    row = next(r for r in ROWS if r["id"] == rid)
    code, out, raw = _call(row)
    field, ecode = CONTRACT_CONFLICTS[rid]
    assert code == 2, raw
    assert out["code"] == ecode and out["field"] == field and out["error"]
