# Kanıt defteri · chi2-contingency

Etiketler: **[DOK]** kılavuz/makale · **[REA]** binary'den kanıt (fonksiyon adresi veya dize referansı) · **[AJAN]** kanıtsız çıkarım, diferansiyel testle sınanmalı.
Puan yalnızca [REA] satırlarına verilir. Kısa alıntı + adres serbesttir; decompile bloğu yapıştırmayın.

**Hedef:** `GPowerNT.exe` 3.1.9.7, SHA-256 `C63E6A13…EFC812` (oturumda yeniden hesaplandı, eşleşti).
**Araç:** REA + Ghidra 12.1.4 (x86 PE, PDB yüklenmedi; adlar `FUN_xxxxxxxx`, sınıf adları RTTI'den).
**Adres biçimi:** Ghidra sanal adresi (görüntü tabanı 0x400000).

## Özet tablo

| # | Etiket | İddia | Kanıt (adres / dize / sayfa) | Sınayan vektör | Durum |
|---|---|---|---|---|---|
| 1 | [REA] | λ = w²·N; N bu anda nesnede tutulan N'dir (aramada kesirli, sonuçta tam sayı) | `FUN_00498770` (PowerChiCont vtable+0x50): w·w·N | G001, G029–G038 | Kâhinle tutarlı |
| 2 | [REA] | Kritik değer = merkezi χ²(df) dağılımının (1−α) yüzdeliği (λ=0 ile) | `FUN_004981d0`: dağılıma λ=0 verilir, `quantile(1−α)` çağrılır | G001, G020, G028 | Kâhinle tutarlı |
| 3 | [REA] | Güç = 1 − F(c; df, λ), F merkezsiz χ² CDF | `FUN_004981d0` (vtable+0x30): λ ayarlanır, `1 − cdf(c)` döner | G029–G035 | Kâhinle tutarlı |
| 4 | [DOK] | Kılavuz örneği: w=0.3, α=0.05, 1−β=0.95, df=5 → N=220 | G*Power 3.1 kılavuzu | G001 | Geçti (220) |
| 5 | [REA] | A priori N, sürekli N üzerinde kök bulma ile bulunur: f(N) = güç(w,α,N) − hedef | `FUN_00496aa0` (vtable+0x48) → `FUN_004968d0` (vtable+0x11c): `power(...) − target` | G001–G021 | |
| 6 | [REA] | Kök bulucu Brent yöntemi, en çok 300 iterasyon | `FUN_004f9bb0`, çağrı `0x496aed: PUSH 0x12c` (=300); ters ikinci dereceden interpolasyon + ikiye bölme dalları | G001–G021 | |
| 7 | [REA] | Brent'e 1e-10 tolerans geçilir ama döngüde kullanılmaz; durma: f(b)=0 veya \|(c−b)/2\| ≤ 2⁻⁵³·\|b\| | `0x496ae3` 1e-10 (`0x5c3f48`) → `0x4f9c33` `[ESI+8]`'e yazılır, döngüde okunmaz; tol1 = \|b\|·`[0x5c4390]`=2⁻⁵³ (`0x4f9d91`) | G013, G014 | Kapsam: yalnız `FUN_004f9bb0` |
| 8 | [REA] | Başlangıç aralığı: N₀=100'den başlar. f(100) ≥ 0 ise üst=100 ve aşağı doğru yarılar; değilse üst sınır ×1.6 ile büyütülür (üst sınır yok) | `FUN_00499150` (vtable+0x64) → `FUN_004962d0(1.0, 100.0)`; sabit 1.6 | G013, G014, G015 | |
| 9 | [REA] | Alt sınır 1: aralığın alt ucu 1'in altına inerse 1 yapılır | `FUN_004962d0` sonu (alt < 1 → 1) | G016, G017 | Geçti (N=1) |
| 10 | [REA] | Yuvarlama: N_tam = ⌈ round(N*·10¹⁰)/10¹⁰ ⌉ (önce 10 ondalığa yuvarla, sonra tavan) | `FUN_00496a20` (vtable+0x74): `floor(x·1e10+0.5)/1e10` sonra `ceil` | G001–G021 | |
| 11 | [REA] | Minimum N = 1: yuvarlanmış N alt sınırdan (1) küçükse alt sınıra eşitlenip yeniden yuvarlanır | `FUN_00496aa0` `0x496b38–0x496b64` (COMISD [ESI+0x68]) | G016, G017 | Geçti |
| 12 | [REA] | Maksimum N / iterasyon hata iletisi yok; a priori fonksiyonu Brent durum kodunu (0/1/2) okumaz | `FUN_004f9bb0` `[ESI+0x54]` ← 0/1/2; `FUN_00496aa0` bu alanı okumaz | G014 (N=7 848 861) | Kapsam: yalnız `FUN_00496aa0` |
| 13 | [REA] | Gerçek güç tam sayı N ile yeniden hesaplanır | `FUN_00496aa0` sonu: vtable+0x30(w, α, N_tam) → `[+0x108]` | G001–G021 | |
| 14 | [REA] | Güç = α kabul edilir (koşul α ≤ güç) | `FUN_004880e0`: `alpha <= power` → geçerli | G017 | Geçti |
| 15 | [REA] | Güç < α → "Power must be greater than or equal to alpha." | `FUN_004880e0`, dize `0x5c6220` | G018 | Geçti |
| 16 | [REA] | güç=α durumunda N=1 döner (f(N)>0 her yerde → aralık kurulamaz → Brent 0 döner → alt sınır 1) | `FUN_004962d0` + `FUN_004f9bb0` durum 1 (`0x4f9c5e` FLDZ) + R11 | G017 | Geçti |
| 17 | [REA] | A priori w doğrulaması: w < 1e-06 → "Effect size w must be greater 1e-06." (sonda nokta; w=1e-06 kabul) | `FUN_00498ad0` case 0 → `FUN_00487880('w', 1e-06)`; parçalar `"Effect size "` + `w` + `0x5c61c4 " must be greater "` + sayı + `0x5c4ac8 "."` | G022, G023 (ekranda nokta görülüyor) | Geçti |
| 18 | [REA] | Post hoc w doğrulaması daha gevşek: w < 0 → "Effect size w must be non-negative." (w=0 kabul, λ=0, güç=α) | `FUN_00498ad0` case 2 → `FUN_00487970` | G039 (w=0 kabul), G048 (w=−0.3 → ileti birebir) | Geçti |
| 19 | [REA] | α ∉ [1e-07, 0.9999999] → "Alpha is outside the admissible range (1e-07, 1)." (kapalı aralık; sınırlar setprecision(6) ile basılır) | `FUN_00487530`, dize `0x5c6100`, `std::setprecision(6)` | G024, G025, G043 (0.9999999 kabul), G044 (0.99999995 red) | Geçti |
| 20 | [REA] | güç ∉ [1e-07, 0.9999999] → "Power is outside the admissible range (1e-07, 1)." (kapalı aralık) | `FUN_00488110`, dize `0x5c60d8` | G026, G042 (0.9999999 kabul) | Geçti |
| 21 | [REA] | df < 1 → "Degrees of Freedom must be greater or equal one."; kesirli df kabul edilir | `FUN_00487800` (`1.0 <= df`), dize `0x5c615c`; df double okunur (`FUN_0048a8a0`) | G027, G028 | Geçti |
| 22 | [REA] | Post hoc N ∉ [1, 2147483646] → "Total sample size is outside the admissible range (1, 2147483646)" | `FUN_00488a10(N, 1, 0x7ffffffe)`, dize `0x5c6524` | G040 (N=0), G041 (N=2147483647) | Geçti |
| 23 | [REA] | Doğrulama sırası a priori: df → w → α → güç aralığı → güç ≥ α; post hoc: df → w → α → N | `FUN_00498ad0` case 0 / case 2 (df denetimi switch'ten önce) | G018, G022–G027, G044 (α, güçten önce), G045 (df, w'den önce) | Geçti |
| 24 | [REA] | Mod dağıtıcısı: 0=a priori, 1=duyarlılık, 2=post hoc, 3=kriter, 4=uzlaşı | `FUN_00498ad0` switch; case 4'te q oranı [0.01, 100] | — | |
| 25 | [REA] | Merkezsiz χ² CDF: Poisson(λ/2) ağırlıklı merkezi χ²(df+2k) CDF'lerinin toplamı; k₀=⌊λ/2⌋'den ileri ve geri toplanır, terim ≤ toplam·2.22e-16 olunca durur | `FUN_0043e7e0` (ChiDistribution cdf yolu), sabit 2.220446049250313e-16 | G029–G035 | |
| 26 | [REA] | λ < 1e-100 ise merkezi χ² yoluna geçilir (CDF ve quantile) | `FUN_0043eca0` / `FUN_0043f800`: `1e-100 <= ncp` kontrolü | G001 (kritik değer) | |
| 27 | [REA] | Dağılım hata iletileri: "ChiDist-Cdf: …"/"ChiDist-Quantile: … answer above/below search bound" ile istisna fırlatılır | `FUN_0043eca0`, `FUN_0043f800` | — | |
| 28 | [REA] | Varsayılan ekran değerleri: df=5, w=0.3, α=0.05, güç=0.95, N=100 | `FUN_00498a70`, kurucu `FUN_00498370` | — | |
| 29 | [REA] | Tam sayı alanına "=" ile ifade yazılırsa sonuç floor(x+0.5) ile yuvarlanır | `FUN_0048b8d0`: `"="` (`0x5c3aec`) aranır, `floor(v+0.5)` | — | |
| 30 | [AJAN] | Post hoc N kutusuna kesirli değer (ör. 10.5) yazılırsa N yarım-yukarı yuvarlanır (10.2→10, 10.5→11, 10.7→11) | Düz metin yolu `FUN_00439bd0` önceden ayrıştırılmış alanı döner; yuvarlamanın yeri bulunamadı. Kâhin davranışı gösteriyor | G036, G037, G038 | Kâhinle tutarlı, REA eksik |
| 31 | [AJAN] | Gösterim: x=0, 0<\|x\|<eşik (0.00393214 < eşik ≤ 0.0157908; 0.01 varsayım) veya \|x\| ≥ 100 ise `%.7g` (0 → "0", "1.570797e-06", "0.0001570879", "0.00393214", "124.3421"); 0.01 ≤ \|x\| < 100 ise 7 ondalık sabit ("0.0157908", "19.8000000"); N tam sayı. Önceki "yalnızca sıfırdan farklı rakam yoksa %.7g" kuralı G046 ve G049 ile yanlışlandı (HALLUCINATIONS H3) | Sınırlı arama, bağlanamadı: `%.7f` (`0x5db854`) yalnız `FUN_005480b0` ve `FUN_00549400`'da, tek bir alanı her zaman sabit biçimde yazıyor (0 ve 1.57e-14'ü açıklayamaz); `%.7g` (`0x5cee00`) `FUN_00561500` gibi başka diyaloglarda; `std::setprecision` çağıranları yalnız doğrulayıcılar (`FUN_00487300`…`FUN_00488560`). Çıktı alanlarını yazan kod bulunamadı | G020, G039, G043, G046, G047, G049, G050 ve tümü | Kâhinle tutarlı, eşik ve REA eksik |
| 32 | [AJAN] | Hata iletileri "Input error" başlıklı pencerede gösterilir | Dize `0x5c3b38` var; çağıran zincir izlenmedi. Ekran görüntüleri G018, G022–G027 | G018–G027 | Kâhinle tutarlı |
| 33 | [AJAN] | Kütüphaneler N'yi kesirli verir (ör. 219.x); G*Power tavan alır (R10'daki 1e-10 ön yuvarlaması dışında) | `oracle/scale_vectors.csv` `n_frac` / `n_total` | S* | |

## [REA] bulguları

### R1 · Sınıf ve vtable
- Sınıf: `PowerChiCont` (RTTI), vtable `0x5c6b14` (RTTI COL `0x5ee8b8`; hemen önünde `"$\chi^2$ tests"` dizesi `0x5c6b00`).
- Test adı: `FUN_00498990` (vtable+0x78) `"Goodness-of-fit tests: Contingency tables"` (`0x5c6dd4`) döndürür.
- Kurucu/klonlayıcı: `FUN_00498370`; dağılım nesnesi `ChiDistribution` (vtable `0x5c3d64`) `+0x58`'e konur.
- Alan haritası (çıkarım, yazma/okuma yerlerinden): `+0x80` df, `+0xb0` α, `+0xb8` güç, `+0xd8` w, `+0xe8` N, `+0x98` kritik χ², `+0x108` gerçek güç, `+0x68/+0x70` arama aralığı alt/üst, `+0x2ac` arama hedef seçici.
- Kılavuzda var mı: Hayır.

### R2 · Mod dağıtıcısı ve doğrulama sırası
- Fonksiyon: `FUN_00498ad0` @ 0x00498ad0 (vtable+0x108, girdi `0x5c6c1c`).
- Önce df okunur ve `FUN_00487800` ile `df ≥ 1` denetlenir; sonra `switch(mod)`.
- case 0 (a priori): w (`FUN_00487880`, min 1e-06), α (`FUN_00487530`), güç aralığı (`FUN_00488110`), `FUN_004880e0` (α ≤ güç); sonra vtable+0x48 çağrılır, sonuç `+0xe8` (N).
- case 2 (post hoc): w (`FUN_00487970`, yalnız negatiflik), α, N (`FUN_00488a10`, [1, 0x7ffffffe]); sonra vtable+0x30 → `+0xb8` (güç).
- Kılavuzda var mı: Hayır.

### R3 · A priori N araması
- Fonksiyon: `FUN_00496aa0` @ 0x00496aa0 (vtable+0x48).
- Akış: w/α/güç saklanır → hedef seçici `+0x2ac`=0 → vtable+0x64 (`FUN_00499150` → `FUN_004962d0(1.0, 100.0)`: aralık kur) → `FUN_004f9bb0(alt, üst, 1e-10, 300)` → vtable+0x74 (`FUN_00496a20`: yuvarla) → alt sınır kontrolü → vtable+0x30 ile gerçek güç.
- Hedef fonksiyon: `FUN_00496830` (vtable+4) seçici 0 → `FUN_004968d0` (vtable+0x11c) = `power(w, α, N) − target`.
- Durma koşulu sürekli N üzerinde f(N)≈0'dır; tam sayı üzerinde "≥" karşılaştırması **yoktur**. "En küçük N, güç ≥ hedef" davranışı tavan almadan doğar.
- Kılavuzda var mı: Hayır.

### R4 · Aralık kurma (bracketing)
- Fonksiyon: `FUN_004962d0(alt=1.0, başlangıç=100.0)`.
- f(100) ≥ 0: üst=100, orta=(1+100)/2; f(orta) > 0 ve orta ≥ 1 oldukça üst=orta, orta=(orta+1)/2 − 1.
- f(100) < 0: alt=100, üst=160; f(üst) < 0 oldukça alt=üst, üst=üst·1.6 (sınırsız).
- Son: alt < 1 ise alt=1.
- Kılavuzda var mı: Hayır.

### R5 · Brent kök bulucu
- Fonksiyon: `FUN_004f9bb0` @ 0x004f9bb0.
- f(a)·f(b) > 0 ise durum=1, **0 döner** (`0x4f9c5e`).
- Döngü: en çok `maxiter` (a priori 300) iterasyon; aşılırsa durum=2 ve son b döner (`0x4f9f83`).
- Yakınsama: f(b)=0 ya da |xm| ≤ |b|·2⁻⁵³ (`0x5c4390` = 0x3CA0000000000000). Geçilen 1e-10 `[ESI+8]`'e yazılır, bu fonksiyonda okunmaz.
- Kılavuzda var mı: Hayır.

### R6 · N yuvarlaması
- Fonksiyon: `FUN_00496a20` (vtable+0x74). Kısa alıntı: `x*10000000000.0 + 0.5` → `floor` → `/1e10` → `ceil`.
- Sonuç: 10 ondalık basamağa yuvarlanmış N*'ın tavanı. N*=219.00000000004 ise 219 olur (güç(219) hedefin ~1e-12 altında kalabilir).
- Kılavuzda var mı: Hayır.

### R7 · Güç fonksiyonu
- Fonksiyon: `FUN_004981d0` (vtable+0x30).
- df dağılıma yazılır, λ=0 → c = quantile(1−α) → `+0x98`; λ = vtable+0x50(w) = w²·N (`FUN_00498770`); güç = 1 − cdf(c).
- Kılavuzda var mı: formül evet ([DOK]), uygulama ayrıntısı hayır.

### R8 · Merkezsiz χ² dağılımı
- `ChiDistribution` vtable `0x5c3d64`: +4 `FUN_0043eca0` (cdf), +8 `FUN_0043f800` (quantile), +0x2c `FUN_0043e520` (λ yaz).
- Merkezsiz CDF `FUN_0043e7e0`: Poisson ağırlıkları `PoissonDistribution` ile, k₀=⌊λ/2⌋'den ileri sonra geri toplanır; durma terim ≤ toplam·DBL_EPSILON veya NaN.
- λ < 1e-100 ise merkezi yol (`func_0x0044b7d0`, DCDFLIB tarzı arama; "answer below/above search bound" kodları).
- Kılavuzda var mı: Hayır.

### R9 · Doğrulama iletileri (tam metin)
| Koşul | İleti | Kaynak |
|---|---|---|
| df < 1 | `Degrees of Freedom must be greater or equal one.` | `FUN_00487800`, `0x5c615c` |
| a priori w < 1e-06 | `Effect size w must be greater 1e-06.` | `FUN_00487880` (parçalar `"Effect size "` + `w` + `0x5c61c4` + sayı + `0x5c4ac8 "."`) |
| post hoc w < 0 | `Effect size w must be non-negative.` | `FUN_00487970` |
| α ∉ [1e-07, 0.9999999] | `Alpha is outside the admissible range (1e-07, 1).` | `FUN_00487530`, `0x5c6100`, ayraç `0x5c4abc ", "`, `0x5c60d4 ")."` |
| güç ∉ [1e-07, 0.9999999] | `Power is outside the admissible range (1e-07, 1).` | `FUN_00488110`, `0x5c60d8` |
| güç < α | `Power must be greater than or equal to alpha.` | `FUN_004880e0`, `0x5c6220` |
| N ∉ [1, 2147483646] | `Total sample size is outside the admissible range (1, 2147483646)` | `FUN_00488a10`, `0x5c6524`, `0x5c64f0 ")"` |

Not: sınır 0.9999999 ekranda setprecision(6) yüzünden `1` olarak basılır; gerçek kabul sınırı 0.9999999'dur (kapalı aralık).

## Açık kalanlar (bu oturumda kanıtlanamadı)
- Post hoc N kutusundaki kesirli metnin nerede yarım-yukarı yuvarlandığı (L30).
- Çıktı kutularına yazan biçimlendirme kodu (L31). İkinci turda `%.7f`'in iki çağıranı, `%.7g`'nin bir çağıranı (`FUN_00561500`) ve `std::setprecision`'ın bütün çağıranları incelendi; hiçbiri bu testin çıktı alanlarına bağlanamadı. `%.7g`'nin diğer ~55 çağıranı ve `%#.06g` (`0x5e2434`) incelenmedi.
- Brent durum kodu 1/2'nin GUI'de bir uyarıya dönüşüp dönüşmediği (L12 kapsam dışı).
- `+0xa8` alanındaki 1.0000000000000009 varsayılanının anlamı.
