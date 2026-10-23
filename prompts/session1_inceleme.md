# Oturum 1 · İnceleme (REA + Ghidra) · ilk prompt

Bu oturumda G*Power 3.1.9.7 (Windows) içindeki **χ² testleri → Goodness-of-fit tests: Contingency tables** hesabını tersine mühendislikle inceleyeceğiz. Eğitim amaçlı, YZM301 dersi kapsamında; yalnızca bu binary hedeftir.

Hedef binary: `<yol>\GPower.exe` (SHA-256: `<hash>`).

Görevin:
1. REA ve Ghidra ile bu testin hesap motorunu bul: güç fonksiyonu, merkezsiz χ² dağılımı, kritik değer ve a priori N arama döngüsü.
2. Şu davranışları kanıtla (fonksiyon adresi ya da dize referansıyla): N arama algoritması ve başlangıç değeri, durma koşulu (≥ mi > mı, tolerans), N yuvarlaması, minimum/maksimum N ve iterasyon sınırı, güç ≤ α davranışı, geçersiz girdi doğrulaması ve iletileri, gösterim format dizeleri.
3. Her iddiayı `LEDGER.md`'ye yaz: kanıtın varsa [REA] + adres + kısa alıntı; yalnızca kılavuzdaysa [DOK]; kanıtın yoksa [AJAN]. Emin olmadığında [AJAN] yaz, asla uydurma adres verme.
4. Kanıtlardan `SPEC.md` üret: algoritma tarifi + Gherkin kabul kriterleri. SPEC'e decompile kodu KOYMA; davranışı ve algoritmayı kendi cümlelerinle anlat.

Kurallar:
- Kod yazma. Bu oturumun çıktısı yalnızca `LEDGER.md` ve `SPEC.md`.
- Her açıklamanda "bunun kanıtı hangi fonksiyonda?" sorusuna cevap verebilmelisin.
- Beklenen değerleri sen belirlemezsin; G*Power belirler (`oracle/gpower_vectors.csv`).
