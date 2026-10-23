"""oracle/public_vectors.jsonl içindeki chi2-contingency vektörleri (CONTRACT §9)."""
import json

import pytest

from conftest import ORACLE, assert_displayed, run_cli

with open(ORACLE / "public_vectors.jsonl", encoding="utf-8") as fh:
    VECTORS = [v for v in map(json.loads, filter(str.strip, fh))
               if v["input"]["test"] == "chi2-contingency"]

# SPEC yalnızca a-priori ve post-hoc'u tanımlıyor; bonus modlar için davranış
# kuralı yok (tahmin edilmez, "SPEC'e soru"). Bu vektörler bilinçli olarak kırmızı.
NOT_IN_SPEC = {"compromise", "criterion", "sensitivity"}


def _params(v):
    marks = []
    if v["input"]["mode"] in NOT_IN_SPEC:
        marks.append(pytest.mark.xfail(strict=True, reason="mod SPEC'te tanımlı değil"))
    return pytest.param(v, id=v["id"], marks=marks)


@pytest.mark.parametrize("vec", [_params(v) for v in VECTORS])
def test_public_vector(vec):
    args = []
    for k, val in vec["input"].items():
        args += [f"--{k}", str(val)]
    code, out, raw = run_cli(*args)
    assert code == 0, raw
    for k, exp in vec["expected"].items():
        if k == "n_total":
            assert out[k] == exp and isinstance(out[k], int)
        else:
            # JSON 19.8000000'ı 19.8 olarak okur; ekrandaki 7 ondalık esas alınır.
            assert_displayed(out[k], f"{exp:.7f}" if abs(exp) < 100 else f"{exp:.7g}", k)


@pytest.mark.parametrize("mode", sorted(NOT_IN_SPEC))
def test_bonus_modes_unsupported(mode):
    code, out, raw = run_cli("--test", "chi2-contingency", "--mode", mode,
                             "--w", "0.3", "--n_total", "100", "--df", "5")
    assert code == 2, raw
    assert out["code"] == "UNSUPPORTED" and out["field"] == "mode"
