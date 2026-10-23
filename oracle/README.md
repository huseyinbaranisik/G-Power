# Kâhin

## gpower_vectors.csv (asıl kâhin: G*Power arayüzü)
36 planlı vektör: tipik değerler + sınırlar (w çok küçük/büyük, güç = α, güç < α, df büyük) + geçersiz girdiler + post hoc.

Doldurma kuralları:
- Çıktıları G*Power ekranında **göründüğü gibi** yazın (basamak sayısı karşılaştırma toleransını belirler).
- a-priori satırında `power` girdi, `n_total` / `ncp` / `critical_chi2` / `actual_power` çıktıdır. post-hoc satırında `n_total` girdi, `power` sütunu beklenen güçtür.
- Geçersiz girdilerde `expect_error` şu an `?`. G*Power'ın tepkisini `note`'a yazın; hata veriyorsa `evet` yapın, sonuç üretiyorsa çıktıları doldurup `expect_error`'ı boşaltın.
- Her satırın ekran görüntüsü `screenshots/Gxxx.png`.
- En az 30 vektör zorunlu; sınırda çıkan ilginç her davranış için yeni satır ekleyin.

### Toplama yöntemi (2026-10-23)
50 vektörün tamamı (planlı 36 + kesirli N için G037–G038 + SPEC açık soruları için G039–G050) G*Power 3.1.9.7 arayüzünde
`collect_gpower.ps1` ile toplandı. Betik değerleri Win32 mesajlarıyla (`WM_SETTEXT`) giriş kutularına yazar,
**Calculate**'e basar, çıktı kutularını ekranda görüldüğü gibi okur ve pencereyi (varsa "Input error"
iletisiyle birlikte) `screenshots/Gxxx.png` olarak kaydeder. Hesabı G*Power yapar; betik yalnızca klavye
yerine girer ve okur. Yeniden üretmek için G*Power açıkken:

```powershell
.\collect_gpower.ps1 -CsvPath .\gpower_vectors.csv -ShotDir .\screenshots -OutJson run.json
```

Çapraz kontrol: her a priori N için scipy ile güç(N) ≥ hedef > güç(N−1) sağlandı; gerçek güç 7 ondalıkta eşleşti.

## scale_vectors.csv (ölçek kâhini, G*Power DEĞİL)
`python oracle/gen_scale_oracle.py` → 567 vektör. `n_frac` kütüphanenin kesirli N'si, `n_total` "güç ≥ hedef olan en küçük tam sayı". G*Power ile çelişen satır bulursanız G*Power haklıdır; farkı LEDGER'a yazın.
