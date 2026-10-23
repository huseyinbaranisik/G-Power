# <p align="center">🔬 χ² Power Teardown</p>
## <p align="center">G*Power'ın χ² Olumsallık Tablosu Hesabının Kanıtlı Temiz Oda Yeniden Yazımı</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Ghidra-12.1.4-B22222?style=for-the-badge" />
  <img src="https://img.shields.io/badge/REA-6.7.0-8B3FFD?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Kâhin-50%20G*Power%20Vektörü-10b981?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Ders-YZM301%20Teardown%20Sprint-17202C?style=for-the-badge" />
</p>

> ⚠️ **Bu proje G\*Power değildir ve onun yerine geçmez.** G\*Power'ın χ² olumsallık tablosu hesabı eğitim amacıyla incelenmiş, davranışı kanıtlarla belgelenmiş ve bağımsız olarak yeniden yazılmıştır. Teslim edilen kodda decompile çıktısı yoktur.

---

### 🎬 DEMO VİDEOSU

<p align="center">
  <a href="https://youtu.be/uQfWS3_VzAE">
    <img src="https://img.shields.io/badge/▶%20YouTube'da%20İzle-FF0000?style=for-the-badge&logo=youtube&logoColor=white" />
  </a>
  &nbsp;
  <a href="docs/demo.mp4">
    <img src="https://img.shields.io/badge/📁%20Video%20Dosyası%20(repo)-17202C?style=for-the-badge&logo=github&logoColor=white" />
  </a>
</p>

> **Videoda:** `demo.ps1` ile sırayla a priori (N = 220, yandaki G\*Power ile aynı), post hoc (güç = 0.6236), geçersiz girdi (`w = 0` → G\*Power'ın hata iletisi, çıkış kodu 2) ve uyum raporu (**N eşleşmesi %100**).

---

### 📝 PROJE HAKKINDA

**χ² Power Teardown**, istatistikte yaygın kullanılan G\*Power programının *"χ² tests → Goodness-of-fit tests: Contingency tables"* hesabını taklit eden, terminalden çalışan küçük bir programdır. Etki büyüklüğü **w**, **α**, **güç** ve **df** verildiğinde gereken örneklem büyüklüğünü (a priori) ya da verilen örneklemle ulaşılan gücü (post hoc) hesaplar.

Projenin asıl amacı programın kendisi değil, **neden doğru olduğunun kanıtıdır**. Bu yüzden iş üç ayrı aşamada yapıldı:

1. 🎯 **Kâhin:** Doğru cevaplar önce G\*Power'ın kendisinden toplandı (50 vektör, her biri ekran görüntülü).
2. 🕵️ **İnceleme (Oturum 1):** Bir yapay zeka ajanı REA + Ghidra ile `GPowerNT.exe`'nin içine bakıp hesabın nasıl yapıldığını buldu. Her iddia bir fonksiyon adresine bağlandı ve bu bulgulardan bir şartname (`SPEC.md`) yazıldı.
3. 🧼 **Temiz oda yazım (Oturum 2):** Ghidra çıktısını hiç görmeyen ayrı bir ajan, programı **yalnızca** şartnameden ve kâhinden yazdı.

---

### 🌟 TEMEL ÖZELLİKLER

* 📐 **İki mod:** `a-priori` (gereken N) ve `post-hoc` (ulaşılan güç)
* 🧾 **Tek satır JSON çıktı:** `ncp`, `critical_chi2`, `n_total`, `actual_power` / `power`
* 🚫 **G\*Power ile aynı doğrulama:** Aynı aralıklar, aynı sıra, aynı hata iletileri; hatada çıkış kodu `2`
* 🔎 **Kanıt defteri:** Her davranış `[REA]` (binary kanıtı), `[DOK]` (kılavuz) ya da `[AJAN]` (kanıtsız) olarak etiketli
* 🧪 **Diferansiyel test:** G\*Power vektörleri + 567 scipy ölçek vektörü ile otomatik karşılaştırma
* 🤖 **Halüsinasyon günlüğü:** Ajanın kendinden emin ama yanlış çıkan 3 iddiası ve onları yakalayan testler

---

### 🧩 YAPILAN KATMANLAR

| Katman | Puan | Durum |
| :--- | :---: | :---: |
| Temel: motor + CLI | 85 | ✅ Tamam |
| MCP sunucusu | +15 | ⏳ Bonus |
| AI ajanı | +10 | ⏳ Bonus |

---

### 🎯 SÜRÜM VE HEDEF

| | |
| :--- | :--- |
| İncelenen | G\*Power 3.1.9.7 (Windows, build 143), yalnızca psychologie.hhu.de'den indirildi (`GPowerWin_3.1.9.7.zip`) |
| `GPowerNT.exe` SHA-256 | `C63E6A133EB6372932F810C08CC33DC35A06D1DDB658F897BD6C34A754EFC812` |
| Zip SHA-256 | `3BB7F1F2478D74EE5BA701AE7F849373CF2B8A11F6B6216C7C6B236DB7861199` |
| Test ailesi | χ² tests · Goodness-of-fit tests: Contingency tables (`chi2-contingency`) |
| Modlar | `a-priori`, `post-hoc` |
| Sözleşme sürümü | `1.0.0` ([CONTRACT.md](CONTRACT.md), [ders gist'i](https://gist.github.com/seyyah/08d3e031781d853b17366be8ba264211)) |
| Araçlar | REA 6.7.0 (`rea-agents`), Ghidra 12.1.4, Eclipse Temurin JDK 21.0.12 |

`GPowerNT.exe` (ödev metninde `GPower.exe`) bu repoda yoktur ve olmayacaktır (`.gitignore`).

---

### 🏗️ YÖNTEM VE VERİ AKIŞI

```text
[ G*Power 3.1.9.7 arayüzü ]
        │  collect_gpower.ps1 → 50 vektör + 50 ekran görüntüsü
        ▼
[ oracle/gpower_vectors.csv ] ◄──────────────────────────────┐
        │                                                     │
        ▼  Oturum 1 · REA + Ghidra                            │
[ GPowerNT.exe ] → LEDGER.md (31 [REA] kanıtı) → SPEC.md      │
        │                    └→ HALLUCINATIONS.md (H1–H3)     │
        ▼  Oturum 2 · temiz oda (yalnızca SPEC + kâhin)       │
[ src/engine ] ← [ src/cli: gpower-clone ]                    │
        │                                                     │
        ▼  tests/diff_test.py ────────────────────────────────┘
[ tests/REPORT.md ]  kapı: a priori N tam eşleşmesi ≥ %90
```

---

### 🔍 ÖNE ÇIKAN BULGULAR

Kılavuzda yazmayan, G\*Power'ın ekranında ve binary'sinde bulunan davranışlar (ayrıntı: `SPEC.md`, `LEDGER.md`):

| Davranış | G\*Power ne yapıyor? | Kâhin |
| :--- | :--- | :---: |
| N araması | Tam sayıları tek tek denemiyor; sürekli N üzerinde kök arıyor (Brent), sonra yukarı yuvarlıyor | G001–G021 |
| Üst sınır | Yok: w=0.001 için N=7 848 861 | G014 |
| Minimum N | 1; df'ye bağlı alt sınır yok | G016 |
| Güç = α | Kabul ediliyor, N=1 dönüyor; güç < α ise hata | G017, G018 |
| Kesirli N (post hoc) | Hata yok, en yakın tam sayıya yuvarlanıyor (10.2→10, 10.5→11) | G036–G038 |
| Kesirli df | Hata yok, olduğu gibi kullanılıyor (df=2.5) | G028 |
| Gösterim | Normalde 7 ondalık; çok küçük (< ~0.01) ve ≥ 100 değerler `%.7g` | G020, G039–G050 |

---

### ⚖️ SÖZLEŞME İLE G\*POWER ARASINDAKİ ÇELİŞKİLER

`CONTRACT.md` §5, aralık dışındaki girdilerin `OUT_OF_RANGE` ile reddedilmesini istiyor. G\*Power ise bu girdilerin bir kısmını hatasız hesaplıyor:

| Vektör | Girdi | Sözleşme §5 | G\*Power 3.1.9.7 |
| :---: | :--- | :--- | :--- |
| G028 | `df = 2.5` | df tam sayı ≥ 1 → red | Kesirli df olduğu gibi kullanılır, N=115 |
| G035 | post hoc `n_total = 1` | n_total ≥ 2 → red | Güç = 0.0603726 |
| G036–G038 | post hoc `n_total = 10.2 / 10.5 / 10.7` | tam sayı → red | En yakın tam sayıya yuvarlanır (10 / 11 / 11) |
| G039 | post hoc `w = 0` | w > 0 → red | Güç = α = 0.05 |

Gizli testler sözleşmenin düzeneğiyle çalıştığı için bu uygulama **aralık dışında sözleşmeye**, aralık içinde G\*Power'a uyar. Belirsizlik ders gönderisine bildirilmelidir (sözleşme §11).

---

### 🚀 KURULUM VE ÇALIŞTIRMA

```bash
# 1. Repoyu klonla
git clone https://github.com/huseyinbaranisik/G-Power.git
cd G-Power

# 2. Kurulum (Python ≥ 3.10; tek bağımlılık scipy)
python -m venv .venv && .venv/Scripts/python -m pip install -e ".[test]"
# macOS / Linux: .venv/bin/python -m pip install -e ".[test]"

# 3. Komut artık .venv/Scripts/gpower-clone (macOS/Linux: .venv/bin/gpower-clone)
.venv/Scripts/gpower-clone --version
# {"contract_version": "1.0.0", "name": "G-Power (huseyinbaranisik)", "engine": "Python 3.14.3"}
```

```bash
# A priori: gereken örneklem büyüklüğü
gpower-clone --test chi2-contingency --mode a-priori --w 0.3 --alpha 0.05 --power 0.95 --df 5
# {"ncp": 19.8, "critical_chi2": 11.070497693516351, "n_total": 220, "actual_power": 0.9502155018970164}

# Post hoc: ulaşılan güç
gpower-clone --test chi2-contingency --mode post-hoc --w 0.3 --alpha 0.05 --n_total 50 --df 5
# {"ncp": 4.5, "critical_chi2": 11.070497693516351, "power": 0.32717853371574623}

# Geçersiz girdi → hata JSON'u, çıkış kodu 2
gpower-clone --test chi2-contingency --mode a-priori --w 0 --alpha 0.05 --power 0.8 --df 1
# {"error": "Effect size w must be greater 1e-06.", "code": "OUT_OF_RANGE", "field": "w"}
```

Sayılar sözleşme gereği tam double hassasiyetle basılır (CONTRACT §2.3); karşılaştırma toleransı 1e-6'dır.

Testler:

```bash
.venv/Scripts/python -m pytest -q                      # 137 test + 3 bilinçli xfail (bonus modlar)

# Diferansiyel test (gpower-clone PATH'te olmalı)
PATH="$PWD/.venv/Scripts:$PATH" python tests/diff_test.py oracle/gpower_vectors.csv oracle/scale_vectors.csv
# -> tests/REPORT.md
```

---

### 📊 UYUM RAPORU

| Ölçüm | Sonuç |
| :--- | :--- |
| 🚪 **Kapı:** a priori N tam eşleşmesi | **589 / 589 = %100** (eşik %90) ✅ |
| `gpower_vectors.csv` (G\*Power ekranı) | 44 / 50; kalan 6'sı yukarıdaki **sözleşme çelişkileri** |
| `scale_vectors.csv` (scipy ölçek kâhini) | 567 / 567 |
| Sözleşme toleransıyla (≤ 1e-6) bağımsız kontrol | 50 kâhin satırı + 2 açık chi2 vektörü: sorun yok |
| pytest | 137 geçti, 3 bilinçli xfail (SPEC'te kuralı olmayan bonus modlar) |
| En yavaş çağrı | 0.69 s (sınır 2 s) |

Ayrıntı: [tests/REPORT.md](tests/REPORT.md) ve Oturum 2'nin raporu [RAPOR.md](RAPOR.md) (SPEC'e ve sözleşmeye açık sorular dahil).

---

### 🛠️ REA KONTROLÜ

> *"REA araçları ve Ghidra sağlayıcısı bu oturumda kullanılabilir mi?"*

`TODO: cevabın ekran görüntüsü (ör. docs/rea_kontrol.png)`

Oturumun kendi kontrolüne (`binary_session`) göre Ghidra sağlayıcısı **available**: sürüm 12.1.4, sekiz kontrolün sekizi geçti (yapılandırma, platform, mimari, kurulum, sürüm, headless, native decompiler, Java).

---

### 📁 PROJE YAPISI

```
G-Power/
├── README.md               # Bu dosya
├── CONTRACT.md             # Ders CLI sözleşmesi v1.0.0 (gist'ten)
├── SPEC.md                 # Algoritma tarifi + Gherkin kabul kriterleri (Oturum 1)
├── LEDGER.md               # Kanıt defteri: [REA] / [DOK] / [AJAN]
├── HALLUCINATIONS.md       # Ajanın yanlış çıkarımları (H1–H3)
├── AGENT_COST.md           # Ajan, token, deneme sayısı
├── prompts/
│   ├── session1_inceleme.md   # Oturum 1'in ilk mesajı
│   └── session2_yazim.md      # Oturum 2'nin ilk mesajı
├── oracle/
│   ├── gpower_vectors.csv     # 50 G*Power vektörü (asıl kâhin)
│   ├── screenshots/           # Her vektörün G*Power ekran görüntüsü
│   ├── collect_gpower.ps1     # Vektörleri G*Power'dan toplayan betik
│   ├── public_vectors.jsonl   # Sözleşmedeki 25 açık referans vektörü
│   ├── scale_vectors.csv      # 567 scipy vektörü (ölçek kâhini)
│   └── gen_scale_oracle.py
├── RAPOR.md                # Oturum 2 raporu: çelişkiler, SPEC'e sorular
├── demo.ps1                # 60 saniyelik video demosu
├── docs/
│   └── demo.mp4               # Demo videosu
├── pyproject.toml          # Paket tanımı, gpower-clone komutu
├── src/
│   ├── engine/                # Tek hesap motoru (doğrulama, N araması, Brent)
│   └── cli/                   # gpower-clone: argüman → motor → tek satır JSON
└── tests/
    ├── test_*.py              # Kâhin, Gherkin senaryoları, açık vektörler, sözleşme
    ├── diff_test.py           # Diferansiyel test (ders düzeneği)
    └── REPORT.md              # Uyum raporu
```

---

### 📚 ATIF

Faul, F., Erdfelder, E., Lang, A.-G., & Buchner, A. (2007). G\*Power 3: A flexible statistical power analysis program for the social, behavioral, and biomedical sciences. *Behavior Research Methods, 39*, 175–191.

Faul, F., Erdfelder, E., Buchner, A., & Lang, A.-G. (2009). Statistical power analyses using G\*Power 3.1: Tests for correlation and regression analyses. *Behavior Research Methods, 41*, 1149–1160.

G\*Power yazarları bu aracı bilim dünyasına ücretsiz sunmuştur; resmi dağıtım yalnızca psychologie.hhu.de üzerindendir.
