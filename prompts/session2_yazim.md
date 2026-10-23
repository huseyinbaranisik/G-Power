# Oturum 2 · Yazım (temiz oda) · ilk prompt

Yeni bir oturumdasın. Elinde yalnızca `SPEC.md`, ders gist'indeki CLI sözleşmesi ve `oracle/` klasöründeki kâhin vektörleri var. Ghidra/REA çıktısı, decompile kodu ya da `LEDGER.md` görmeyeceksin; isteme.

Görevin: `SPEC.md`'deki χ² olumsallık tablosu güç analizini `<dil>` ile yeniden yazmak.

1. Önce testler: `oracle/gpower_vectors.csv` ve SPEC'teki Gherkin senaryolarını test olarak yaz, kırmızı olduklarını gör.
2. Tek bir hesap motoru (`src/engine`) yaz. CLI (`gpower-clone`) yalnızca argüman ayrıştırır, motoru çağırır, tek satır JSON basar. Hesap mantığı CLI'de olmaz.
3. Sözleşme: varsayılan değer yok, bilinmeyen alan hatadır, hata çıktısı `{"error","code","field"}`, çıkış kodu 2/1, `--version` desteklenir.
4. Dağılım fonksiyonları için scipy (ya da eşdeğeri) serbest; N araması, yuvarlama ve df hesabı senin kodun.
5. `python tests/diff_test.py oracle/gpower_vectors.csv oracle/scale_vectors.csv` çalıştır; her uyuşmazlık için SPEC'te eksik bir kural mı yoksa kodda hata mı olduğunu raporla. SPEC'te olmayan bir kuralı tahmin edip ekleme; eksikse "SPEC'e soru" olarak listele.
