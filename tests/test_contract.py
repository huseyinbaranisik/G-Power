"""CONTRACT.md §2–§5 arayüz kuralları."""
import pytest

from conftest import chi2_args, run_cli

GOOD = dict(w="0.3", alpha="0.05", power="0.95", df="5")


def test_version():
    code, out, raw = run_cli("--version")
    assert code == 0, raw
    assert out["contract_version"] == "1.0.0"
    assert out["name"] and out["engine"].startswith("Python")


def test_single_line_json_and_int_n():
    code, out, raw = run_cli(*chi2_args("a-priori", **GOOD))
    assert code == 0
    assert raw.endswith("\n") and raw.count("\n") == 1
    assert '"n_total": 220' in raw and isinstance(out["n_total"], int)
    assert set(out) >= {"ncp", "critical_chi2", "n_total", "actual_power"}


def test_full_double_precision():
    _, out, _ = run_cli(*chi2_args("a-priori", **GOOD))
    assert out["actual_power"] != round(out["actual_power"], 7)


@pytest.mark.parametrize("drop", ["w", "alpha", "power", "df"])
def test_missing_param(drop):
    fields = {k: v for k, v in GOOD.items() if k != drop}
    code, out, raw = run_cli(*chi2_args("a-priori", **fields))
    assert code == 2, raw
    assert out["code"] == "MISSING_PARAM" and out["field"] == drop and out["error"]


def test_missing_mode():
    code, out, _ = run_cli("--test", "chi2-contingency", "--w", "0.3")
    assert code == 2 and out["code"] == "MISSING_PARAM" and out["field"] == "mode"


def test_unknown_param():
    code, out, _ = run_cli(*chi2_args("a-priori", **GOOD, foo="1"))
    assert code == 2 and out["code"] == "UNKNOWN_PARAM" and out["field"] == "foo"


def test_irrelevant_param_for_mode():
    code, out, _ = run_cli(*chi2_args("post-hoc", w="0.3", alpha="0.05", n_total="100",
                                      df="5", power="0.8"))
    assert code == 2 and out["code"] == "UNKNOWN_PARAM" and out["field"] == "power"


@pytest.mark.parametrize("field,value", [
    ("w", "abc"), ("alpha", "0,05"), ("power", "nan"), ("w", "inf"), ("df", "1.5"),
])
def test_invalid_value(field, value):
    code, out, _ = run_cli(*chi2_args("a-priori", **{**GOOD, field: value}))
    assert code == 2 and out["code"] == "INVALID_VALUE" and out["field"] == field


def test_unsupported_test():
    code, out, _ = run_cli("--test", "t2-indep", "--mode", "a-priori")
    assert code == 2 and out["code"] == "UNSUPPORTED" and out["field"] == "test"


def test_unsupported_mode():
    code, out, _ = run_cli("--test", "chi2-contingency", "--mode", "foo")
    assert code == 2 and out["code"] == "UNSUPPORTED" and out["field"] == "mode"


def test_value_missing_after_flag():
    code, out, _ = run_cli(*chi2_args("a-priori", w="0.3", alpha="0.05", power="0.95"), "--df")
    assert code == 2 and out["code"] == "INVALID_VALUE" and out["field"] == "df"


def test_contract_range_w_positive_a_priori():
    # §5 w > 0 → w=0 OUT_OF_RANGE (SPEC iletisiyle)
    code, out, _ = run_cli(*chi2_args("a-priori", **{**GOOD, "w": "0"}))
    assert code == 2 and out["code"] == "OUT_OF_RANGE" and out["field"] == "w"


def test_error_goes_to_stdout_only():
    code, _, raw = run_cli(*chi2_args("a-priori", **{**GOOD, "w": "abc"}))
    assert code == 2 and raw.count("\n") == 1 and raw.startswith("{")
