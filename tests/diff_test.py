"""Diferansiyel test: kâhin CSV'lerini CLI'ye verir, farkı ölçer, tests/REPORT.md yazar.

Kural (yönerge e): n_total TAM eşleşmeli. Diğer alanlar kâhinde yazılı olan
basamak sayısına kadar eşleşmeli (CSV'ye G*Power ekranında görüneni aynen yazın;
basamak sayısı o dizeden çıkarılır).

Kullanım:
  python tests/diff_test.py oracle/gpower_vectors.csv [oracle/scale_vectors.csv ...]
CLI komutu: CLONE_CMD ortam değişkeni (varsayılan: "gpower-clone").
"""
import csv
import json
import os
import shlex
import subprocess
import sys

CMD = shlex.split(os.environ.get("CLONE_CMD", "gpower-clone"))
INPUTS = {"a-priori": ["w", "alpha", "power", "df"],
          "post-hoc": ["w", "alpha", "n_total", "df"]}
OUTPUTS = {"a-priori": ["n_total", "ncp", "critical_chi2", "actual_power"],
           "post-hoc": ["ncp", "critical_chi2", "power"]}
EXACT = {"n_total"}


def decimals(s):
    return len(s.split(".")[1]) if "." in s else 0


def run(row):
    mode = row["mode"]
    args = CMD + ["--test", "chi2-contingency", "--mode", mode]
    for k in INPUTS[mode]:
        if row.get(k, "") != "":
            args += [f"--{k}", row[k]]
    p = subprocess.run(args, capture_output=True, text=True)
    try:
        return p.returncode, json.loads(p.stdout.strip().splitlines()[-1])
    except Exception:
        return p.returncode, {"error": f"JSON değil: {p.stdout!r} {p.stderr!r}"}


def compare(row):
    flag = row.get("expect_error", "").strip().lower()
    filled = any(row.get(k, "") != "" for k in OUTPUTS[row["mode"]] if k not in INPUTS[row["mode"]])
    if flag == "?" or (not flag and not filled):
        return None, "kâhin değeri henüz girilmedi (G*Power'dan doldurun)"
    code, out = run(row)
    if flag in ("evet", "yes", "1"):
        ok = code != 0 and "error" in out
        return ok, f"hata bekleniyordu; çıkış={code} çıktı={out}"
    if "error" in out:
        return False, f"beklenmeyen hata: {out}"
    # Aynı sütun bir modda girdi, diğerinde beklenen çıktıdır:
    # a-priori: power girdi, n_total çıktı · post-hoc: n_total girdi, power çıktı.
    diffs = []
    for k in OUTPUTS[row["mode"]]:
        exp = row.get(k, "")
        if exp == "":
            continue
        got = out.get(k)
        if got is None:
            diffs.append(f"{k}: çıktıda yok")
        elif k in EXACT:
            if int(got) != int(float(exp)):
                diffs.append(f"{k}: beklenen {exp}, gelen {got}")
        else:
            d = decimals(exp)
            if round(float(got), d) != round(float(exp), d):
                diffs.append(f"{k}: beklenen {exp}, gelen {got} ({d} basamak)")
    return not diffs, "; ".join(diffs)


def main(paths):
    lines, total, passed, n_total, n_pass = ["# Uyum raporu", ""], 0, 0, 0, 0
    for path in paths:
        with open(path, encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        fails = []
        pending = 0
        for r in rows:
            ok, msg = compare(r)
            if ok is None:
                pending += 1
                continue
            total += 1
            passed += ok
            if r["mode"] == "a-priori" and not r.get("expect_error"):
                n_total += 1
                n_pass += ok or "n_total" not in msg
            if not ok:
                fails.append(f"| {r['id']} | {r['mode']} | {msg} |")
        lines += [f"## {os.path.basename(path)}", f"{len(rows) - pending - len(fails)}/{len(rows) - pending} geçti · {pending} bekliyor", ""]
        if fails:
            lines += ["| id | mod | fark |", "|---|---|---|"] + fails + [""]
    rate = 100 * n_pass / n_total if n_total else 0
    lines.insert(2, f"**Toplam:** {passed}/{total} · **N tam eşleşme (a priori):** {n_pass}/{n_total} = %{rate:.1f} (kapı: %90)\n")
    rep = os.path.join(os.path.dirname(__file__), "REPORT.md")
    with open(rep, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(lines[2])
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main(sys.argv[1:] or ["oracle/gpower_vectors.csv"])
