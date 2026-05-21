---
name: eval-harness
description: Eval-driven development (EDD) ilkelerini uygulayan Claude Code oturumları için formal değerlendirme çerçevesi
origin: ECC
tools: Read, Write, Edit, Bash, Grep, Glob
---

# Eval Harness Skill

Claude Code oturumları için eval-driven development (EDD) ilkelerini uygulayan formal değerlendirme çerçevesi.

## Felsefe

Eval-Driven Development, eval'ları "AI geliştirmenin birim testleri" olarak ele alır:
- İmplementasyondan ÖNCE beklenen davranışı tanımla
- Geliştirme sırasında eval'ları sürekli çalıştır
- Güvenilirlik ölçümü için pass@k metriklerini kullan

## Eval Tipleri

### Capability Eval'ları
```markdown
[CAPABILITY EVAL: feature-name]
Görev: Claude'un başarması gereken şeyin açıklaması
Başarı Kriterleri:
  - [ ] Kriter 1
  - [ ] Kriter 2
```

### Regression Eval'ları
```markdown
[REGRESSION EVAL: feature-name]
Baseline: SHA veya checkpoint adı
Testler:
  - existing-test-1: PASS/FAIL
Sonuç: X/Y geçti
```

## Metrikler

- **pass@1**: İlk deneme başarı oranı
- **pass@3**: 3 denemede başarı
- **pass^3**: Ardışık 3 başarı (kararlılık)

Önerilen eşikler:
- Capability eval'ları: pass@3 >= 0.90
- Regression eval'ları: pass^3 = 1.00

## Eval İş Akışı

1. **Tanımla** - Kodlamadan önce başarı kriterlerini belirle
2. **Uygula** - Tanımlanan eval'ları geçmek için kod yaz
3. **Değerlendir** - Eval'ları çalıştır ve sonuçları kaydet
4. **Raporla** - Geçme oranlarını ve regresyonları belgele

## Eval Depolama

```
.claude/
  evals/
    feature-xyz.md      # Eval tanımı
    feature-xyz.log     # Çalıştırma geçmişi
    baseline.json       # Regression baseline'ları
```
