---
name: continuous-learning
description: Claude Code oturumlarından yeniden kullanılabilir kalıpları otomatik olarak çıkarın ve gelecekte kullanmak üzere öğrenilmiş skill'ler olarak kaydedin.
origin: ECC
---

# Sürekli Öğrenme Skill'i

Claude Code oturumlarını sonunda otomatik olarak değerlendirir ve öğrenilmiş skill'ler olarak kaydedilebilecek yeniden kullanılabilir kalıpları çıkarır.

## Ne Zaman Aktifleştirmelisiniz

- Claude Code oturumlarından otomatik kalıp çıkarma ayarlarken
- Oturum değerlendirmesi için Stop hook'u yapılandırırken
- `~/.claude/skills/learned/` içindeki öğrenilmiş skill'leri incelerken veya düzenlerken
- Çıkarma eşiklerini veya kalıp kategorilerini ayarlarken
- v1 (bu) ile v2 (instinct tabanlı) yaklaşımlarını karşılaştırırken

## Nasıl Çalışır

Bu skill her oturumun sonunda **Stop hook** olarak çalışır:

1. **Oturum Değerlendirmesi**: Oturumun yeterli mesaja sahip olup olmadığını kontrol eder (varsayılan: 10+)
2. **Kalıp Tespiti**: Oturumdan çıkarılabilir kalıpları tanımlar
3. **Skill Çıkarma**: Yararlı kalıpları `~/.claude/skills/learned/` dizinine kaydeder

## Konfigürasyon

`config.json` dosyasını düzenleyin:

```json
{
  "min_session_length": 10,
  "extraction_threshold": "medium",
  "auto_approve": false,
  "learned_skills_path": "~/.claude/skills/learned/",
  "patterns_to_detect": [
    "error_resolution",
    "user_corrections",
    "workarounds",
    "debugging_techniques",
    "project_specific"
  ]
}
```

## Hook Kurulumu

`~/.claude/settings.json` dosyanıza ekleyin:

```json
{
  "hooks": {
    "Stop": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/skills/continuous-learning/evaluate-session.sh"
      }]
    }]
  }
}
```

## İlgili

- `/learn` komutu - Oturum ortasında manuel kalıp çıkarma
