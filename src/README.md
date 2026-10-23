# src/

Oturum 2 (temiz oda) tarafından, yalnızca `SPEC.md`'den yazılacak.

Önerilen yapı (hesap tek motorda, diğerleri ince katman):

```
src/
  engine/      # tek hesap motoru
  cli/         # gpower-clone: argüman ayrıştır -> engine -> tek satır JSON
  mcp/         # (bonus) aynı engine'i çağıran MCP adaptörü
  agent/       # (bonus) Türkçe klinik soru -> MCP aracı
```
