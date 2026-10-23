# Yapılacaklar · YZM301 Teardown Sprint (χ² olumsallık tablosu)

**Özet:** G*Power'ın χ² hesabını taklit eden, terminalden çalışan küçük bir program yazacaksın. Asıl puan, programın **neden doğru olduğunu kanıtlamaktan** geliyor.

---

## 1. Kurulum (bugün, ~yarım saat)

- [ ] Terminalde `node -v` çalıştır. 22.19 veya üstü değilse nodejs.org'dan güncelle.
- [ ] `npx rea-agents setup` çalıştır, ajanını seç (ör. Claude Code), değişiklikleri onayla, ajanı yeniden başlat.
- [ ] Ghidra'yı (ghidra-sre.org) ve JDK 21'i kur.
- [ ] G*Power 3.1.9.7'yi **yalnızca** psychologie.hhu.de'den indir.
- [ ] PowerShell'de hash'i al ve README'ye yaz:
  ```powershell
  Get-FileHash .\GPower.exe -Algorithm SHA256
  ```
- [ ] Ajanına sor: *"REA araçları ve Ghidra sağlayıcısı bu oturumda kullanılabilir mi?"* Cevabın ekran görüntüsünü al, README'ye koy.

## 2. G*Power'dan doğru cevapları topla (1. gün)

Önce gerçek cevapları biliyor olman lazım ki programını onlarla kıyaslayabilesin.

- [ ] G*Power'ı aç ve şunu seç: **Test family: χ² tests → Goodness-of-fit tests: Contingency tables**.
- [ ] `oracle/gpower_vectors.csv` dosyasında 36 satır var. Her satırdaki **w, α, güç, df** değerlerini G*Power'a gir, **Calculate**'e bas.
- [ ] Ekranda çıkan **N, λ, kritik χ², gerçek güç** değerlerini CSV'ye ekranda nasıl görünüyorsa öyle yaz.
- [ ] Her satırın ekran görüntüsünü `oracle/screenshots/G001.png`, `G002.png` … diye kaydet.
- [ ] Geçersiz girdilerde (w=0, df=0 vb.) G*Power ne yapıyorsa `note` sütununa yaz. Hata veriyorsa `expect_error`'ı `evet` yap, sonuç veriyorsa çıktıları doldurup `expect_error`'ı boşalt.

## 3. Oturum 1: G*Power'ı sök (2–4. gün)

- [ ] Ajanını aç, `prompts/session1_inceleme.md` dosyasındaki metni ilk mesaj olarak yapıştır.
- [ ] Ajan REA ve Ghidra ile GPower.exe'nin içine bakıp N'nin nasıl hesaplandığını bulacak: nasıl aradığını, ne zaman durduğunu, nasıl yuvarladığını (liste: `PLAN.md` → "Avlanacak davranışlar").
- [ ] Her bulguyu `LEDGER.md`'ye yazdır:
  - **[REA]**: fonksiyon adresi veya dize referansı var → **puan bunlardan gelir**
  - **[DOK]**: yalnızca kılavuzda yazıyor
  - **[AJAN]**: kanıtı yok
- [ ] Ajan kendinden emin bir şey söylediğinde sor: *"Bunun kanıtı hangi fonksiyonda?"*
- [ ] Ajanın yanlış çıkardığı şeyleri `HALLUCINATIONS.md`'ye not et (**en az 2 tane**).
- [ ] Sonunda ajana `SPEC.md`'yi yazdır (Gherkin formatında kabul kriterleriyle).

## 4. Oturum 2: Programı yaz (4–5. gün)

- [ ] **Yeni ve temiz** bir ajan oturumu aç.
- [ ] Ona yalnızca şunları ver: `SPEC.md`, `oracle/` CSV'leri, `prompts/session2_yazim.md`. **Ghidra çıktısını kesinlikle gösterme.**
- [ ] Ajan `src/` içine programı yazsın (Python önerilir). Program şöyle çalışmalı:
  ```bash
  gpower-clone --test chi2-contingency --mode a-priori --w 0.3 --alpha 0.05 --power 0.95 --df 5
  ```
  ve tek satır JSON basmalı:
  ```json
  {"ncp":19.8,"critical_chi2":11.0705,"n_total":220,"actual_power":0.9502}
  ```
- [ ] Post hoc mod da çalışmalı (`--n_total` verilir, `power` hesaplanır).
- [ ] Geçersiz girdide `{"error":"...","code":"...","field":"..."}` basmalı ve çıkış kodu 2 olmalı.

## 5. Karşılaştır (5. gün)

- [ ] Diferansiyel testi çalıştır:
  ```bash
  python tests/diff_test.py oracle/gpower_vectors.csv oracle/scale_vectors.csv
  ```
- [ ] Oluşan `tests/REPORT.md` dosyasında N eşleşme oranı **%90'ın üstünde** olmalı (kapı).
- [ ] Uymayan her satır için nedenini yaz: ya kodda hata var ya da kaçırılan bir kural.

## 6. Bitir (6–7. gün)

- [ ] `AGENT_COST.md`'yi doldur: hangi ajan, kabaca kaç token, kaç deneme, neyi farklı yapardın.
- [ ] Programın çalıştığı **60 saniyelik ekran videosu** çek, linkini README'ye koy.
- [ ] README'deki `TODO`'ları doldur (hash, sürüm, kurulum, katmanlar).
- [ ] Klasörü GitHub'a yükle (**GPower.exe olmadan**, `.gitignore` bunu zaten dışarıda tutuyor).
- [ ] Repo linkini Classroom'a teslim et.

## Bonus (zaman kalırsa, en son)

- [ ] **+15 MCP sunucusu:** aynı motoru çağıran ince adaptör, araç şeması README'de, CLI ile MCP'nin aynı çıktıyı verdiğini gösteren test.
- [ ] **+10 AI ajanı:** Türkçe klinik soruyu MCP aracıyla yanıtlayan ajan, 10 soruluk değerlendirme seti, araç çağrı logları, MCP ve GUI token karşılaştırması.

> ⚠️ Bonuslar ancak 5. adımdaki **%90 kapısı** tutarsa puanlanır.

---

## Dikkat

- Sözleşmede tutarsızlık var: ödev metnindeki örnek `critical`, gist ise `critical_chi2` diyor. Gist'e uyuldu; Classroom'da hocaya sor.
- Programına "G*Power" adını verme. README'de yazarlara atıf yap (Faul, Erdfelder, Lang ve Buchner, 2007 ve 2009).
- Teslim edilen kodda decompile çıktısı olmayacak.
- REA'yı yalnızca resmi kaynaklardan kur: github.com/morluto/rea, rea.tools, npm `rea-agents`.
