# Sprint planı · χ² olumsallık tablosu (`chi2-contingency`)

> Bu dosya kişisel çalışma planıdır, teslimin parçası olması gerekmez.

G*Power'daki karşılığı: **Test family: χ² tests → Statistical test: Goodness-of-fit tests: Contingency tables**.
Girdiler: etki büyüklüğü **w**, **α**, **güç (1−β)**, **df**. Çıktılar: **λ (ncp)**, **kritik χ²**, **toplam N**, **gerçek güç**.

## Gün gün

| Gün | İş | Çıktı |
|---|---|---|
| 1 | Kurulum: Node ≥ 22.19, `npx rea-agents setup`, Ghidra + JDK 21, G*Power 3.1.9.7 (yalnızca psychologie.hhu.de). `GPower.exe` SHA-256'sını al. REA kontrol ekran görüntüsü. | README'de sürüm + hash + ekran görüntüsü |
| 1–2 | **Kâhin önce.** `oracle/gpower_vectors.csv`'deki 36 vektörü G*Power'a gir, ekranda görüneni AYNEN yaz, her birinin ekran görüntüsünü `oracle/screenshots/Gxxx.png` olarak kaydet. Geçersiz girdilerde G*Power'ın ne yaptığını (hata, sessizce düzeltme, kilitlenme) `note`'a yaz, `expect_error`'ı `evet`/boş yap. | Doldurulmuş CSV + 36 PNG |
| 2–4 | **Oturum 1 (inceleme)**: `prompts/session1_inceleme.md` ile REA + Ghidra. Aşağıdaki "Avlanacak davranışlar"ı fonksiyon adresi / dize referansıyla kanıtla. | `LEDGER.md`, `SPEC.md`, `HALLUCINATIONS.md` taslağı |
| 4–5 | **Oturum 2 (yazım)**: YENİ oturum, yalnızca `SPEC.md` + `CONTRACT` bilgisi + `oracle/`. Motor + CLI. | `src/` |
| 5 | Diferansiyel test: `python tests/diff_test.py oracle/gpower_vectors.csv oracle/scale_vectors.csv`. Her uyuşmazlığı açıkla (senin hatan mı, kaçırılan kural mı). | `tests/REPORT.md` |
| 6 | Kapı ≥ %90 tutuyorsa: MCP (+15), sonra ajan (+10). | `src/mcp/`, `src/agent/` |
| 7 | 60 sn CLI demo videosu, `AGENT_COST.md`, README son hâli. | Teslim |

## Avlanacak davranışlar (kılavuzda OLMAYAN → [REA] puanı buradan)

1. **N arama algoritması:** N=1'den tek tek mi artıyor, ikiye bölme (bisection) mi, sürekli çözüp `ceil` mi? Başlangıç değeri ve üst sınır ne?
2. **Durma koşulu:** `güç ≥ hedef` mi, `güç > hedef` mi? Bir tolerans (ε) var mı? Gerçek güç tam hedefe eşit çıkarsa ne oluyor?
3. **Yuvarlama:** N tam sayıya nasıl yuvarlanıyor; λ = w²·N hesabında hangi N kullanılıyor (kesirli mi tam mı)?
4. **Minimum N:** w çok büyükken N=1, 2 mi çıkıyor, yoksa df'ye bağlı bir alt sınır mı var?
5. **İterasyon sınırı:** w çok küçükken (0.001) N milyonlarca olur; bir üst sınır / hata iletisi var mı? İleti dizesini bul.
6. **güç ≤ α:** Kılavuz söylemiyor. N=1 mi döner, hata mı verir? Dize referansı.
7. **Geçersiz girdi:** w ≤ 0, df ≤ 0 ya da kesirli, α ∉ (0,1). Alan doğrulayıcı nerede, hangi ileti?
8. **Noncentral χ² hesabı:** Hangi algoritma (seri açılımı, yakınsama ölçütü)? Uç değerlerde scipy ile fark buradan çıkar.
9. **Gösterim basamakları:** Ekranda kaç basamak gösteriliyor (λ, kritik χ², güç)? Format dizesi (`%.6f` vb.) bul → yönerge (e) toleransı.

Her madde için: Ghidra'da fonksiyon adresi + kısa alıntı/dize → LEDGER'da `[REA]`; ardından `gpower_vectors.csv`'de onu sınayan vektör.

## Sözleşmede dikkat edilecekler

- Yönergedeki örnek `critical` alanını kullanıyor; gist'teki CONTRACT χ² için **`critical_chi2`** diyor. Gist'e uy, sınıf gönderisinde sor.
- Varsayılan değer yok: her alan zorunlu; bilinmeyen alan → `UNKNOWN_PARAM`. Hata çıktısı `{"error","code","field"}`, çıkış kodu 2 (geçersiz girdi) / 1 (iç hata).
- `--version` → `{"contract_version","name","engine"}`.
- Zorunlu modlar a-priori ve post-hoc; compromise / criterion / sensitivity bonus.
- İsim: aracın adı "G*Power" olamaz (komut adı sözleşme gereği `gpower-clone`, ama README'de "G*Power değildir" de).
