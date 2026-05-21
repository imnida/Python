---
name: continuous-learning-v2
description: Hook'lar aracılığıyla oturumları gözlemleyen, güven skorlaması ile atomik instinct'ler oluşturan ve bunları skill/command/agent'lara evriltiren instinct tabanlı öğrenme sistemi. v2.1 çapraz proje kontaminasyonunu önlemek için proje kapsamılı instinct'ler ekler.
origin: ECC
version: 2.1.0
---

# Sürekli Öğrenme v2.1 - Instinct Tabanlı Mimari

Claude Code oturumlarınızı güven skorlaması ile atomik "instinct'ler" - küçük öğrenilmiş davranışlar - aracılığıyla yeniden kullanılabilir bilgiye dönüştüren gelişmiş bir öğrenme sistemi.

**v2.1** **proje kapsamılı instinct'ler** ekler — React kalıpları React projenizde kalır, Python kuralları Python projenizde kalır ve evrensel kalıplar (örneğin "her zaman input'u doğrula") global olarak paylaşılır.

## Ne Zaman Aktifleştirmelisiniz

- Claude Code oturumlarından otomatik öğrenme ayarlarken
- Hook'lar aracılığıyla instinct tabanlı davranış çıkarmayı yapılandırırken
- Öğrenilmiş davranışlar için güven eşiklerini ayarlarken
- Instinct kütüphanelerini incelerken, dışa veya içe aktarirken
- Instinct'leri tam skill'lere, command'lara veya agent'lara evriltirken
- Proje kapsamılı vs global instinct'leri yönetirken
- Instinct'leri projeden global kapsamına yükseltirken

## v2.1'deki Yenilikler

| Özellik | v2.0 | v2.1 |
|---------|------|------|
| Depolama | Global (~/.claude/homunculus/) | Proje kapsamılı (projects/<hash>/) |
| Kapsam | Tüm instinct'ler her yerde geçerli | Proje kapsamılı + global |
| Tespit | Yok | git remote URL / repo path |
| Yükseltme | Yok | Proje → 2+ projede görülince global |
| Komutlar | 4 (status/evolve/export/import) | 6 (+promote/projects) |
| Çapraz proje | Kontaminasyon riski | Varsayılan olarak izole |

## v2'deki Yenilikler (vs v1)

| Özellik | v1 | v2 |
|---------|----|----|
| Gözlem | Stop hook (oturum sonu) | PreToolUse/PostToolUse (%100 güvenilir) |
| Analiz | Ana bağlam | Arka plan agent'ı (Haiku) |
| Granülerlik | Tam skill'ler | Atomik "instinct'ler" |
| Güven | Yok | 0.3-0.9 ağırlıklı |
| Evrim | Doğrudan skill'e | Instinct'ler -> kümeleme -> skill/command/agent |
| Paylaşım | Yok | Instinct'leri dışa/içe aktar |

## Instinct Modeli

```yaml
---
id: prefer-functional-style
trigger: "yeni fonksiyonlar yazarken"
confidence: 0.7
domain: "code-style"
source: "session-observation"
scope: project
project_id: "a1b2c3d4e5f6"
project_name: "my-react-app"
---

# Fonksiyonel Stili Tercih Et

## Aksiyon
Uygun olduğunda sınıflar yerine fonksiyonel kalıpları kullan.

## Kanıt
- 5 fonksiyonel kalıp tercihinin gözlemlenmesi
- Kullanıcı 2025-01-15'te sınıf tabanlı yaklaşımı fonksiyonele düzeltildi
```

## Nasıl Çalışır

Oturum aktivitesi → Hook'lar prompt'ları + tool kullanımını yakalar → observations.jsonl → Gözlemci agent analiz eder → Atomik instinct'ler oluşturulur/güncellenir → /evolve ile kümeleme.

## Hızlı Başlangıç

### 1. Gözlem Hook'larını Aktifleştirin

`~/.claude/settings.json` dosyanıza ekleyin:

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/skills/continuous-learning-v2/hooks/observe.sh"
      }]
    }],
    "PostToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/skills/continuous-learning-v2/hooks/observe.sh"
      }]
    }]
  }
}
```

### 2. Komutları Kullanın

```bash
/instinct-status     # Öğrenilmiş instinct'leri göster
/evolve              # İlgili instinct'leri skill/command'lara kümele
/instinct-export     # Instinct'leri dosyaya aktar
/instinct-import     # Başkalarından instinct'leri içe aktar
/promote             # Proje instinct'lerini global kapsamına yükselt
/projects            # Tüm bilinen projeleri listele
```

## Konfigrasyon

```json
{
  "version": "2.1",
  "observer": {
    "enabled": false,
    "run_interval_minutes": 5,
    "min_observations_to_analyze": 20
  }
}
```

## Gizlilik

- Gözlemler makinenizde **yerel** kalır
- Proje kapsamılı instinct'ler proje başına izoledir
- Sadece **instinct'ler** (kalıplar) dışa aktarılabilir — ham gözlemler değil
- Neyin dışa aktarılacağını ve yükseltileceğini siz kontrol edersiniz
