# SPEC · χ² olumsallık tablosu güç analizi

> Oturum 1 (inceleme) bu dosyayı LEDGER.md'deki kanıtlardan üretti. Oturum 2 (yazım) YALNIZCA bu dosyayı görür.
> Her kural bir LEDGER satırına bağlanır: `(L#)`. `[AJAN]` işaretli kurallar binary'de kanıtlanamadı, yalnızca G*Power ekran çıktısıyla (kâhin) tutarlıdır.
> Beklenen sayılar `oracle/gpower_vectors.csv`'den alınmıştır; bu dosya sayı uydurmaz.

## 1. Kapsam
- Test: `chi2-contingency` (G*Power: χ² tests → Goodness-of-fit tests: Contingency tables). Modlar: `a-priori`, `post-hoc`.
- Girdiler: etki büyüklüğü `w`, `alpha`, `power` (a priori) ya da `n_total` (post hoc), `df`.
- Çıktılar: `ncp` (λ), `critical_chi2`, `n_total`, `actual_power` (a priori) / `power` (post hoc).
- CLI sözleşmesi (alan adları, JSON biçimi, hata kodları, çıkış kodları) ders gist'indeki CONTRACT ile birebir. Bu SPEC yalnızca hesap ve doğrulama davranışını tanımlar.

## 2. Matematik
- λ = w² · N. Burada N, o anda kullanılan N'dir: arama sırasında kesirli, sonuç raporlanırken tam sayı. (L1)
- c = merkezi χ²(df) dağılımının (1 − α) yüzdeliği (λ = 0 ile). (L2)
- güç(w, α, N) = 1 − F(c; df, λ), F merkezsiz χ² birikimli dağılım fonksiyonu. (L3)
- df tam sayı olmak zorunda değildir; kesirli df olduğu gibi kullanılır (G028: df=2.5 → c=6.9280761). (L21)

### 2.1 Merkezsiz χ² CDF (referans algoritma)
- λ < 1e-100 ise merkezi χ² CDF / yüzdelik kullanılır. (L26)
- Aksi halde F(x; df, λ) = Σₖ Poisson(k; λ/2) · F_merkezi(x; df + 2k).
  Toplama k₀ = ⌊λ/2⌋'den başlar, önce k artarak, sonra k₀−1'den 0'a doğru azalarak yapılır; eklenen terim, birikmiş toplamın 2.220446049250313e-16 katına eşit ya da küçük olduğunda (veya terim NaN olduğunda) o yöndeki toplama durur. (L25)
- Hazır bir kütüphane (ör. scipy `ncx2`) kullanılabilir; gösterilen basamaklarda fark beklenmez. Fark çıkarsa referans bu tariftir.

## 3. Algoritma

### 3.1 Post hoc
1. N tam sayıya çevrilir (bkz. 3.4). (L30)
2. c = χ²⁻¹(1 − α; df), λ = w²·N, güç = 1 − F(c; df, λ). (L1–L3)
3. Çıktı: `ncp` = λ, `critical_chi2` = c, `power`.

### 3.2 A priori N araması (L5–L13)
G*Power N'yi tam sayılar üzerinde tek tek denemez. Sürekli N üzerinde f(N) = güç(w, α, N) − hedef_güç fonksiyonunun kökünü arar, sonra yukarı yuvarlar.

1. **Aralık kurma** (L8, L9) — başlangıç N₀ = 100, alt sınır 1:
   - f(100) ≥ 0 ise: üst = 100, orta = (1 + 100)/2. orta ≥ 1 ve f(orta) > 0 olduğu sürece: üst = orta, orta = (orta + 1)/2 − 1. Döngü bitince alt = orta.
   - f(100) < 0 ise: alt = 100, üst = 160. f(üst) < 0 olduğu sürece: alt = üst, üst = üst · 1.6. **Üst sınır yoktur.**
   - Sonunda alt < 1 ise alt = 1.
2. **Kök bulma** (L6, L7): [alt, üst] aralığında Brent yöntemi, en çok 300 iterasyon.
   - f(alt) ve f(üst) aynı işaretliyse (sıfırdan kesin büyük çarpım) kök bulucu **0** döndürür.
   - Yakınsama: f(b) = 0 ya da yarım aralık |(c − b)/2| ≤ 2⁻⁵³ · |b| (makine hassasiyeti ölçeğinde; ayrı bir mutlak tolerans uygulanmaz).
   - 300 iterasyon aşılırsa o anki en iyi tahmin döner; hata iletisi **yoktur**. (L12)
3. **Yuvarlama** (L10): N* önce 10 ondalık basamağa yuvarlanır (yarım yukarı), sonra tavan alınır: N = ⌈ round(N*·10¹⁰)/10¹⁰ ⌉.
4. **Minimum N** (L11): N < alt (alt ≥ 1) ise N = alt ve 3. adım yeniden uygulanır. Sonuç olarak N ≥ 1 her zaman sağlanır; df'ye bağlı alt sınır yoktur (G016).
5. **Gerçek güç** (L13): `actual_power` = güç(w, α, N) tam sayı N ile; `ncp` = w²·N tam sayı N ile; `critical_chi2` = c.

Sonuç davranışı: N, güç(N) ≥ hedef olan en küçük tam sayıdır; tek istisna, N*'ın bir tam sayının 1e-10 kadar üstünde kalmasıdır (o zaman o tam sayı seçilir).

### 3.3 Sınır davranışları
- **güç = α** kabul edilir; f(N) > 0 her N ≥ 1 için olduğundan aralık kurulamaz, kök bulucu 0 döner, minimum kuralıyla N = 1 raporlanır (G017: N=1, λ=0.09, güç=0.0568148). (L14, L16)
- **güç < α** hatadır (bkz. bölüm 4). (L15)
- **w çok küçük**: iterasyon/N üst sınırı yoktur; w=0.001 → N=7 848 861 (G014). (L8, L12)
- **w çok büyük**: N=1'e kadar inebilir (G015: N=2; G016: N=1). (L9, L11)

### 3.4 Post hoc N'nin tam sayıya çevrilmesi [AJAN] (L30)
Kesirli N hata değildir; en yakın tam sayıya, yarımlar yukarı olacak şekilde yuvarlanır: 10.2 → 10, 10.5 → 11, 10.7 → 11 (G036–G038). Banker's rounding (10.5 → 10) **kullanılmaz**.

## 4. Geçersiz girdiler (L17–L23)

Doğrulama sırası, ilk başarısız kontrol raporlanır:
- a priori: df → w → α → güç aralığı → güç ≥ α
- post hoc: df → w → α → N

| Alan | Kabul koşulu (kapalı sınırlar) | G*Power iletisi | Mod | Kâhin |
|---|---|---|---|---|
| `df` | df ≥ 1 (kesirli serbest) | `Degrees of Freedom must be greater or equal one.` | ikisi | G027, G028, G045 |
| `w` | w ≥ 1e-06 | `Effect size w must be greater 1e-06.` | a priori | G022, G023 |
| `w` | w ≥ 0 | `Effect size w must be non-negative.` | post hoc | G039 (w=0 kabul), G048 (w=−0.3 red) |
| `alpha` | 1e-07 ≤ α ≤ 0.9999999 | `Alpha is outside the admissible range (1e-07, 1).` | ikisi | G024, G025, G043, G044 |
| `power` | 1e-07 ≤ güç ≤ 0.9999999 | `Power is outside the admissible range (1e-07, 1).` | a priori | G026, G042 |
| `power` | güç ≥ α | `Power must be greater than or equal to alpha.` | a priori | G018 |
| `n_total` | 1 ≤ N ≤ 2147483646 (yuvarlamadan sonra) | `Total sample size is outside the admissible range (1, 2147483646)` | post hoc | G040, G041 |

- İletiler ekrandakiyle birebirdir (sondaki nokta dahil; N iletisinde nokta yoktur).
- İletilerde üst sınır `1` olarak görünür (6 anlamlı basamakla basıldığı için); gerçek sınır kapalı 0.9999999'dur: 0.9999999 kabul (G042, G043), 0.99999995 red (G044).
- CLI'de her satır sözleşmenin aralık-dışı hata koduyla (`{"error","code","field"}`, çıkış kodu 2) döner; `field` tablodaki alan adıdır, `error` metni olarak G*Power iletisi kullanılabilir. Kod adı sözleşmeden alınır (iskelet `OUT_OF_RANGE` öneriyordu).
- Post hoc w = 0 kabul edilir: λ = 0, güç = α (G039). (L18)

## 5. Gösterim [AJAN] (L31)
G*Power ekranındaki basamaklar (karşılaştırma toleransı buradan çıkar). Kural binary'de bulunamadı; G001–G050'nin hepsiyle tutarlı olan tarif:

- `n_total`: tam sayı.
- `ncp`, `critical_chi2`, `actual_power`, `power` için iki biçim vardır:
  - **Genel (`%.7g`)**: 7 anlamlı basamak, sondaki sıfırlar atılır; üs −5'ten küçükse ya da 7'den büyükse üstel yazılır (C `printf` `%g` kuralı).
  - **Sabit (`%.7f`)**: tam olarak 7 ondalık.
- Seçim:
  1. x = 0 → genel (`0`).
  2. 0 < |x| < 0.01 → genel. (Eşik [AJAN]: kâhine göre 0.00393214 < eşik ≤ 0.0157908; 0.01 varsayımdır.)
  3. 0.01 ≤ |x| < 100 → sabit.
  4. |x| ≥ 100 → genel.
- Örnekler:

  | Ekranda | Kural adımı | Biçim | Kâhin |
  |---|---|---|---|
  | `0` | 1 | genel | G039 (ncp) |
  | `1.570796e-14` | 2 | genel, üstel | G043 |
  | `1.570797e-06` | 2 | genel, üstel | G047 |
  | `0.0001570879` | 2 | genel, üstelsiz (sabit olsaydı `0.0001571`) | G046 |
  | `0.00393214` | 2 | genel, sondaki sıfır atılmış (sabit olsaydı `0.0039321`) | G049 |
  | `0.0157908` | 3 | sabit (genel olsaydı `0.01579077`) | G050 |
  | `19.8000000` | 3 | sabit | G001 |
  | `124.3421` | 4 | genel | G020 |

- Belirsiz kalan: (a) alt eşiğin tam değeri (0.0039–0.0158 arası), (b) üst eşik "≥ 100" mü yoksa "sabit gösterim 10 karakteri aşarsa" mı (bkz. bölüm 7).
- Diferansiyel test: her alan, G*Power'ın gösterdiği son basamağın yarısı kadar tolerans ile karşılaştırılır; genel gösterimde bu, 7. anlamlı basamağın yarısı (göreli tolerans) demektir.

## 6. Kabul kriterleri

```gherkin
Feature: chi2-contingency a priori örneklem büyüklüğü

  Scenario: Kılavuz örneği (L4)
    Given test "chi2-contingency" ve mod "a-priori"
    When w=0.3, alpha=0.05, power=0.95, df=5 verilir
    Then n_total = 220
    And ncp = 19.8000000
    And critical_chi2 = 11.0704977
    And actual_power = 0.9502155

  Scenario Outline: N, gücü hedefe ulaştıran en küçük tam sayıdır (L5–L13)
    When w=<w>, alpha=<alpha>, power=<power>, df=<df> verilir
    Then n_total = <n>
    And ncp = <ncp>
    And critical_chi2 = <crit>
    And actual_power = <ap>
    And power(n_total) >= <power>
    And power(n_total - 1) < <power>
    Examples:
      | w    | alpha | power | df  | n       | ncp        | crit       | ap        |
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

  Scenario: Üst sınır yok, iterasyon hatası yok (L8, L12)
    When w=0.001, alpha=0.05, power=0.8, df=1 verilir
    Then hata dönmez
    And n_total = 7848861
    And ncp = 7.8488610

  Scenario: Büyük w ile N küçülür (L9, L11)
    When w=2, alpha=0.05, power=0.8, df=1 verilir
    Then n_total = 2
    And ncp = 8.0000000

  Scenario: Minimum N = 1, df'ye bağlı alt sınır yok (L9, L11)
    When w=5, alpha=0.05, power=0.95, df=10 verilir
    Then n_total = 1
    And ncp = 25.0000000
    And critical_chi2 = 18.3070381
    And actual_power = 0.9554779

  Scenario: Güç alfaya eşit — kabul edilir, N=1 döner (L14, L16)
    When w=0.3, alpha=0.05, power=0.05, df=2 verilir
    Then hata dönmez
    And n_total = 1
    And ncp = 0.0900000
    And critical_chi2 = 5.9914645
    And actual_power = 0.0568148

  Scenario: Güç alfadan küçük (L15)
    When w=0.3, alpha=0.05, power=0.04, df=2 verilir
    Then aralık-dışı hatası döner, field = "power", çıkış kodu 2
    And ileti "Power must be greater than or equal to alpha."

  Scenario: Kesirli df kabul edilir (L21)
    When w=0.3, alpha=0.05, power=0.8, df=2.5 verilir
    Then hata dönmez
    And n_total = 115
    And ncp = 10.3500000
    And critical_chi2 = 6.9280761
    And actual_power = 0.8017509

  Scenario Outline: Geçersiz girdiler (L17–L23)
    Given mod "a-priori"
    When w=<w>, alpha=<alpha>, power=<power>, df=<df> verilir
    Then aralık-dışı hatası döner, field = "<field>", çıkış kodu 2
    And ileti "<msg>"
    Examples:
      | w    | alpha      | power      | df | field | msg                                                |
      | 0    | 0.05       | 0.8        | 1  | w     | Effect size w must be greater 1e-06.               |
      | -0.3 | 0.05       | 0.8        | 1  | w     | Effect size w must be greater 1e-06.               |
      | 0.3  | 0          | 0.8        | 1  | alpha | Alpha is outside the admissible range (1e-07, 1).  |
      | 0.3  | 1          | 0.8        | 1  | alpha | Alpha is outside the admissible range (1e-07, 1).  |
      | 0.3  | 0.99999995 | 0.99999995 | 1  | alpha | Alpha is outside the admissible range (1e-07, 1).  |
      | 0.3  | 0.05       | 1          | 1  | power | Power is outside the admissible range (1e-07, 1).  |
      | 0.3  | 0.05       | 0.8        | 0  | df    | Degrees of Freedom must be greater or equal one.   |
    # Kâhin: G022, G023, G024, G025, G044, G026, G027 (sırasıyla)

  Scenario: Kapalı üst sınır — güç = 0.9999999 kabul edilir (L20)
    When w=0.3, alpha=0.05, power=0.9999999, df=1 verilir
    Then hata dönmez
    And n_total = 570
    And ncp = 51.3000000
    And critical_chi2 = 3.8414588
    And actual_power = 0.9999999
    # Kâhin: G042

  Scenario: Doğrulama sırası — df, w'den önce denetlenir (L23)
    When w=0, alpha=0.05, power=0.8, df=0 verilir
    Then aralık-dışı hatası döner, field = "df", çıkış kodu 2
    And ileti "Degrees of Freedom must be greater or equal one."
    # Kâhin: G045 (w=0 hatası raporlanmaz)

Feature: chi2-contingency post hoc güç

  Scenario Outline: Post hoc güç (L1–L3)
    Given test "chi2-contingency" ve mod "post-hoc"
    When w=<w>, alpha=<alpha>, n_total=<n>, df=<df> verilir
    Then power = <power>
    And ncp = <ncp>
    And critical_chi2 = <crit>
    Examples:
      | w   | alpha | n    | df | power     | ncp        | crit       |
      | 0.3 | 0.05  | 50   | 5  | 0.3271785 | 4.5000000  | 11.0704977 |
      | 0.3 | 0.05  | 100  | 5  | 0.6235846 | 9.0000000  | 11.0704977 |
      | 0.3 | 0.05  | 220  | 5  | 0.9502155 | 19.8000000 | 11.0704977 |
      | 0.3 | 0.05  | 500  | 5  | 0.9999276 | 45.0000000 | 11.0704977 |
      | 0.1 | 0.05  | 1000 | 1  | 0.8853791 | 10.0000000 | 3.8414588  |
      | 0.5 | 0.01  | 30   | 2  | 0.4525585 | 7.5000000  | 9.2103404  |
      | 0.3 | 0.05  | 1    | 1  | 0.0603726 | 0.0900000  | 3.8414588  |

  Scenario Outline: Kesirli N yarım-yukarı yuvarlanır [AJAN] (L30)
    When w=0.3, alpha=0.05, n_total=<n>, df=1 verilir
    Then hata dönmez
    And ncp = <ncp>
    And power = <power>
    Examples:
      | n    | ncp       | power     |
      | 10.2 | 0.9000000 | 0.1577560 |
      | 10.5 | 0.9900000 | 0.1688419 |
      | 10.7 | 0.9900000 | 0.1688419 |

  Scenario: Post hoc w = 0 kabul edilir, güç = alfa (L18, L31)
    When w=0, alpha=0.05, n_total=100, df=1 verilir
    Then hata dönmez
    And power = 0.0500000
    And ncp = 0 (ekranda "0")
    And critical_chi2 = 3.8414588
    # Kâhin: G039

  Scenario: Kapalı üst sınır — alfa = 0.9999999 kabul edilir, küçük kritik değer üstel gösterilir (L19, L31)
    When w=0.3, alpha=0.9999999, n_total=10, df=1 verilir
    Then hata dönmez
    And power = 0.9999999
    And ncp = 0.9000000
    And critical_chi2 = 1.570796e-14 (ekranda üstel gösterim)
    # Kâhin: G043

  Scenario Outline: Küçük değerlerin gösterimi — eşiğin altında genel biçim (L31) [AJAN]
    When w=0.3, alpha=<alpha>, n_total=10, df=1 verilir
    Then hata dönmez
    And power = <power>
    And ncp = 0.9000000
    And critical_chi2 ekranda "<crit>" olarak gösterilir (<bicim>)
    Examples:
      | alpha | power     | crit         | bicim                   |
      | 0.999 | 0.9993624 | 1.570797e-06 | genel, üstel            |
      | 0.99  | 0.9936236 | 0.0001570879 | genel, üstelsiz         |
      | 0.95  | 0.9680998 | 0.00393214   | genel                   |
      | 0.9   | 0.9360864 | 0.0157908    | sabit 7 ondalık         |
    # Kâhin: G047, G046, G049, G050

  Scenario: Post hoc w < 0 reddedilir (L18)
    When w=-0.3, alpha=0.05, n_total=100, df=1 verilir
    Then aralık-dışı hatası döner, field = "w", çıkış kodu 2
    And ileti "Effect size w must be non-negative."
    # Kâhin: G048

  Scenario Outline: N admissible range dışında (L22)
    When w=0.3, alpha=0.05, n_total=<n>, df=1 verilir
    Then aralık-dışı hatası döner, field = "n_total", çıkış kodu 2
    And ileti "Total sample size is outside the admissible range (1, 2147483646)"
    Examples:
      | n          |
      | 0          |
      | 2147483647 |
    # Kâhin: G040, G041
```

## 7. SPEC'e açık sorular
Önceki sürümdeki dört sorunun hepsi kâhinde sınandı ve SPEC'e işlendi:
- Post hoc w = 0 → kabul, güç = α (G039).
- Post hoc N = 0 ve N = 2147483647 → N iletisi (G040, G041).
- α = 0.9999999 ve güç = 0.9999999 → kabul (G042, G043); α = 0.99999995 → red (G044).
- Doğrulama sırası df → w (G045).

G046–G050 ile küçük değer gösterimi ve post hoc w<0 iletisi de sınandı. Gösterim kuralında (L31, bölüm 5) kalan açık konular ve önerilen vektörler:
- Alt eşiğin tam değeri (0.00393214 < eşik ≤ 0.0157908): kritik χ²'yi 0.01'in iki yanına düşüren post hoc vektörler, ör. w=0.3, n_total=10, df=1 ile alpha=0.92 ve alpha=0.925.
- Üst eşik: değeri 100'e çok yakın bir çıktı (ör. kritik χ² ≈ 99.99 veren df ile). Eşik "≥ 100" mü, genişlik mi?
