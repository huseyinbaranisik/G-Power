# chi2-power-teardown

χ² olumsallık tablosu güç analizinin temiz oda yeniden yazımı ve ajan katmanları. YZM301 Teardown Sprint.

> Bu proje G*Power **değildir** ve onun yerine geçmez. G*Power'ın χ² olumsallık hesabı eğitim amacıyla incelenmiş, davranışı kanıtlarla belgelenmiş ve bağımsız olarak yeniden yazılmıştır.

## Yapılan katmanlar

- [ ] Temel: motor + CLI (85)
- [ ] MCP sunucusu (+15)
- [ ] AI ajanı (+10)

## Sürüm ve hedef

| | |
|---|---|
| İncelenen | G*Power 3.1.9.7 (Windows, build 143), psychologie.hhu.de'den indirildi (`GPowerWin_3.1.9.7.zip`) |
| `GPowerNT.exe` SHA-256 | `C63E6A133EB6372932F810C08CC33DC35A06D1DDB658F897BD6C34A754EFC812` |
| Zip SHA-256 | `3BB7F1F2478D74EE5BA701AE7F849373CF2B8A11F6B6216C7C6B236DB7861199` |
| Test ailesi | χ² tests · Goodness-of-fit tests: Contingency tables (`chi2-contingency`) |
| Modlar | a-priori, post-hoc |
| Sözleşme sürümü | `TODO` |

`GPowerNT.exe` (ödev metninde `GPower.exe`) bu repoda yoktur ve olmayacaktır (`.gitignore`).

## Kurulum ve çalıştırma

```bash
# TODO: oturum 2'nin seçtiği dile göre doldurun
gpower-clone --test chi2-contingency --mode a-priori --w 0.3 --alpha 0.05 --power 0.95 --df 5
# {"ncp":19.8,"critical_chi2":11.0705,"n_total":220,"actual_power":0.9502}
```

Diferansiyel test:

```bash
python oracle/gen_scale_oracle.py                      # ölçek kâhini (scipy/statsmodels)
python tests/diff_test.py oracle/gpower_vectors.csv oracle/scale_vectors.csv
# -> tests/REPORT.md
```

## REA kontrolü

`TODO: "REA araçları ve Ghidra sağlayıcısı bu oturumda kullanılabilir mi?" cevabının ekran görüntüsü`

## Repo haritası

| Yol | İçerik |
|---|---|
| `SPEC.md` | Gherkin kabul kriterleri (oturum 1 üretir) |
| `LEDGER.md` | Kanıt defteri: [DOK] / [REA] / [AJAN] |
| `HALLUCINATIONS.md` | Ajanın yanlış çıkarımları |
| `AGENT_COST.md` | Token, maliyet, iterasyon |
| `prompts/` | İki oturumun ilk prompt'ları |
| `oracle/` | G*Power vektörleri (CSV) + ekran görüntüleri + ölçek kâhini |
| `src/` | Motor + CLI (+ MCP, ajan) |
| `tests/` | Diferansiyel test ve uyum raporu |

## Demo

`TODO: 60 saniyelik CLI videosu linki`

## Atıf

Faul, F., Erdfelder, E., Lang, A.-G., & Buchner, A. (2007). G*Power 3: A flexible statistical power analysis program for the social, behavioral, and biomedical sciences. *Behavior Research Methods, 39*, 175–191.

Faul, F., Erdfelder, E., Buchner, A., & Lang, A.-G. (2009). Statistical power analyses using G*Power 3.1: Tests for correlation and regression analyses. *Behavior Research Methods, 41*, 1149–1160.

G*Power yazarları bu aracı bilim dünyasına ücretsiz sunmuştur; resmi dağıtım yalnızca psychologie.hhu.de üzerindendir.
