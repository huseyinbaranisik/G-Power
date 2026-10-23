# Oturum 2 raporu · chi2-contingency yeniden yazımı

Kaynaklar: yalnızca `SPEC.md`, `CONTRACT.md` (1.0.0), `oracle/`. Tarih: 2026-10-23.

## 1. Özet

| Ölçüm | Sonuç |
|---|---|
| pytest (`tests/`) | 137 geçti, 3 bilinçli xfail (bkz. §4.1) |
| `diff_test.py` · gpower_vectors.csv | 44/50 — kalan 6'nın hepsi **sözleşme çelişkisi** (§2) |
| `diff_test.py` · scale_vectors.csv | 567/567 |
| a priori N tam eşleşmesi | 589/589 = %100 (kapı %90) |
| Çağrı süresi | ~0.5 s (en kötü: w=0.001 → N=7 848 861) |
| scipy CDF ↔ SPEC §2.1 referans tarifi | en büyük fark 1.5e-14 (3000 rastgele nokta) |

Önce testler yazıldı ve kırmızı görüldü (motor yokken 75 başarısız + toplama hatası), sonra motor yazıldı.

**Kod hatası olarak sınıflanan uyuşmazlık yok. SPEC'te eksik kural yüzünden çıkan bir sayısal uyuşmazlık da yok.**

## 2. Sözleşme çelişkileri (G*Power sonuç veriyor, CONTRACT §5 reddediyor)

Arayüz kararlarında CONTRACT geçerli olduğu için bu girdiler CLI'de reddediliyor. Motorun iç fonksiyonları SPEC davranışını yine uyguluyor ve G*Power'ın sayılarını veriyor; bunu `*_engine_behaviour` testleri doğruluyor. Yani sözleşme değişirse yalnızca `validate.py` değişir.

| Kâhin | Girdi | G*Power | CONTRACT §5 | CLI yanıtı |
|---|---|---|---|---|
| G028 | a priori df = 2.5 | N=115, c=6.9280761 (SPEC L21) | df tam sayı ≥ 1 | `INVALID_VALUE`, field `df` |
| G035 | post hoc N = 1 | güç 0.0603726 | n_total ≥ 2 | `OUT_OF_RANGE`, field `n_total` |
| G036 | post hoc N = 10.5 | N=11'e yuvarlanıyor (SPEC L30) | n_total tam sayı | `INVALID_VALUE`, field `n_total` |
| G037 | post hoc N = 10.2 | N=10 | n_total tam sayı | `INVALID_VALUE`, field `n_total` |
| G038 | post hoc N = 10.7 | N=11 | n_total tam sayı | `INVALID_VALUE`, field `n_total` |
| G039 | post hoc w = 0 | güç = α (SPEC L18) | w > 0 | `OUT_OF_RANGE`, field `w` |

`diff_test.py`'nin gösterdiği 6 uyuşmazlık tam olarak bunlar. Sınıfları: SPEC eksikliği değil, kod hatası değil. CONTRACT ile G*Power arasında bilerek seçilmiş bir taraf.

Aynı girdileri kullanan SPEC Gherkin senaryoları (kesirli df, post hoc N=1, kesirli N, post hoc w=0) testlerde de CONTRACT'a göre ret olarak yazıldı.

### 2.1 SPEC ↔ CONTRACT hata kodu çelişkisi
- **güç < α (G018).** SPEC §4/§6 "aralık-dışı hatası" diyor. CONTRACT §2.4 ise tam bu durumu `INCONSISTENT` örneğiyle veriyor ("Power, alpha değerinden büyük olmalı", field `power`), ve tanımı da "tek tek geçerli ama birlikte anlamsız". Hata kodları CONTRACT'ın alanı olduğu için **`INCONSISTENT`** kullanıldı. Çıkış kodu 2, ileti G*Power'ınki.

## 3. Aralık içi davranış (SPEC'ten uygulananlar)

- Doğrulama sırası SPEC §4: a priori df → w → α → güç → güç ≥ α; post hoc df → w → α → N. Önce ayrıştırma (`INVALID_VALUE`), sonra aralık. G045 (df=0, w=0 → df hatası) geçiyor.
- Aralıklar CONTRACT ∩ SPEC: w ≥ 1e-06 (a priori), 1e-07 ≤ α, güç ≤ 0.9999999 (kapalı), N ≤ 2147483646. İletiler G*Power ile birebir.
- N araması SPEC §3.2'nin harfiyen uygulaması (`src/engine/chi2_contingency.py`, `src/engine/brent.py`): N₀=100 ile aralık kurma, ×1.6 büyütme (üst sınır yok), 300 iterasyonlu Brent, 2⁻⁵³·|b| yakınsama, aynı işarette 0 döndürme, 10 ondalığa yarım-yukarı yuvarlayıp tavan alma (`Decimal` ile kesin), minimum N kuralı.
- Dağılımlar `scipy.special` (`chdtri`, `chdtr`, `chndtr`). Bunlar `scipy.stats.chi2/ncx2`'nin kullandığı rutinlerle bit düzeyinde aynı sonucu veriyor ama yükleme süresi yarı yarıya. λ < 1e-100 dalı (L26) ayrıca uygulandı.
- SPEC §5 gösterim kuralı `engine/display.py`'de yalnızca testler için var. CLI, CONTRACT §2.3 gereği tam double basıyor.

## 4. SPEC'e sorular (tahmin edilip eklenmedi)

1. **Bonus modlar (`compromise`, `criterion`, `sensitivity`).** `public_vectors.jsonl`'de chi2 için vektörleri var ama SPEC bu modlar için hiçbir kural vermiyor (β/α oranı çözümü, α araması, w araması, aralıklar, sınır durumları). Şu an `UNSUPPORTED` (field `mode`) dönüyorlar ve 3 public vektör `xfail(strict)` olarak kırmızı tutuluyor.
2. **`%.7g` tarifindeki çelişki (SPEC §5).** Metin "üs −5'ten küçükse ya da 7'den büyükse üstel" diyor, ama hemen ardından "C `printf` `%g` kuralı" diyor. C kuralı "üs < −4 ya da üs ≥ 7". İkisi üs = −5 (ör. 1.5e-05) ve üs = 7 (ör. 12 345 678) için farklı sonuç veriyor. C kuralı uygulandı. Kâhinde bu iki üsle bir değer yok.
3. **Gösterim eşikleri (SPEC §7'de zaten açık).** Alt eşik 0.01 varsayımı ve üst eşiğin "≥ 100" mü yoksa genişlik mi olduğu belirsiz. Bu yalnızca test toleransını etkiliyor, CLI çıktısını etkilemiyor.

## 5. Sözleşmeye sorular (arayüz, SPEC'in alanı değil)

1. **Tam sayı sözdizimi.** `--df 5.0` ya da `--n_total 1e2` tam sayı mı? Şu an yalnızca `[+-]?\d+` kabul ediliyor, diğerleri `INVALID_VALUE`.
2. **İç hata kodu.** §2.4 çıkış kodu 1'i tanımlıyor ama tabloda iç hata için bir `code` yok. Beklenmeyen istisnalarda `INTERNAL`, sonlu olmayan sonuçta `NO_SOLUTION` kullanıldı; ikisi de çıkış kodu 1 ile dönüyor.
3. **Aynı alanın iki kez verilmesi** ve `--alan` değersiz bırakılması tanımlı değil. Şu an `INVALID_VALUE`, field = alan adı.
4. **Sözleşmenin reddettiği ama G*Power'ın kabul ettiği girdilerin iletisi** (§2). G*Power'da bir ileti yok; kendi İngilizce iletimiz kullanılıyor. Not: N=0 ve N > 2147483646'da G*Power iletisi korunuyor.
5. `--version` için `name` alanı takım adı bekliyor; ana repoda `G-Power (huseyinbaranisik)` olarak ayarlandı.

## 6. Dosyalar

- `src/engine/` — `__init__.py` (giriş: `run`, `version`), `validate.py`, `chi2_contingency.py`, `brent.py`, `display.py`, `errors.py`
- `src/cli/main.py` — argv → `engine.run` → tek satır JSON
- `tests/` — `test_gpower_oracle.py` (CSV), `test_spec_scenarios.py` (Gherkin), `test_public_vectors.py`, `test_contract.py`, `conftest.py`
- `tests/REPORT.md` — `diff_test.py` çıktısı
