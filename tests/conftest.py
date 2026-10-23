"""Ortak test yardımcıları.

CLI, kurulu `gpower-clone` yerine `python -m cli` ile (PYTHONPATH=src) çağrılır;
böylece testler kurulumdan bağımsızdır ama yine gerçek süreç sınırından geçer.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
ORACLE = ROOT / "oracle"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def run_cli(*args):
    """CLI'yi çalıştırır; (çıkış kodu, ayrıştırılmış JSON, ham stdout) döner."""
    env = dict(os.environ, PYTHONPATH=str(SRC))
    p = subprocess.run([sys.executable, "-m", "cli", *map(str, args)],
                       capture_output=True, text=True, env=env, cwd=ROOT)
    out = p.stdout
    try:
        data = json.loads(out)
    except ValueError:
        data = None
    return p.returncode, data, out


def chi2_args(mode, **fields):
    args = ["--test", "chi2-contingency", "--mode", mode]
    for k, v in fields.items():
        args += [f"--{k}", v]
    return args


def displayed_tol(s):
    """G*Power'ın gösterdiği dizenin son basamağının yarısı (SPEC §5)."""
    s = s.strip()
    mant, _, exp = s.lower().partition("e")
    dec = len(mant.split(".")[1]) if "." in mant else 0
    return 0.5 * 10.0 ** (int(exp or 0) - dec)


def assert_displayed(got, expected, field=""):
    """Tam double `got`, ekrandaki `expected` dizesine yuvarlanıyor mu?"""
    assert isinstance(got, (int, float)), f"{field}: sayı değil: {got!r}"
    tol = displayed_tol(expected)
    exp = float(expected)
    # 1e-9·tol: ekranda tam yarıda kalan değerlerde ikili gösterim payı
    assert abs(got - exp) <= tol * (1 + 1e-9), \
        f"{field}: beklenen {expected} (±{tol:g}), gelen {got!r}"
