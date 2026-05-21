---
name: coding-standards
description: TypeScript, JavaScript, React ve Node.js geliştirme için evrensel kodlama standartları, en iyi uygulamalar ve kalıplar.
origin: ECC
---

# Kodlama Standartları ve En İyi Uygulamalar

Tüm projelerde uygulanabilir evrensel kodlama standartları.

## Ne Zaman Aktifleştirmelisiniz

- Yeni bir proje veya modül başlatirken
- Kod kalitesi ve sürdürülebilirlik için kod incelerken
- Mevcut kodu kurallara uygun hale getirmek için refactor ederken
- İsimlendirme, biçimlendirme veya yapısal tutarlılığı zorunlu kılarken
- Linting, biçimlendirme veya tür kontrolü kuralları ayarlarken
- Yeni katkıda bulunanları kodlama kurallarına alıştırırken

## Kod Kalitesi İlkeleri

### 1. Önce Okunabilirlik
- Kod yazılmaktan çok okunur
- Net değişken ve fonksiyon isimleri
- Yorumlardan çok kendi kendini belgeleyen kod tercih edilir
- Tutarlı biçimlendirme

### 2. KISS (Keep It Simple, Stupid - Basit Tut)
- Çalışan en basit çözüm
- Aşırı mühendislikten kaçının
- Erken optimizasyon yapmayın
- Anlaşılır kod > akıllıca kod

### 3. DRY (Don't Repeat Yourself - Kendini Tekrar Etme)
- Ortak mantığı fonksiyonlara çıkarın
- Yeniden kullanılabilir bileşenler oluşturun
- Yardımcı araçları modüller arasında paylaşın
- Kopyala-yapıştr programlamadan kaçının

### 4. YAGNI (You Aren't Gonna Need It - İhtiyacın Olmayacak)
- İhtiyaç duyulmadan özellikler oluşturmayın
- Spekülatif genellemeden kaçının
- Karmaşıklığı sadece gerektiğinde ekleyin
- Basit başlayın, gerektiğinde refactor edin

**Unutmayın**: Kod kalitesi pazarlık konusu değildir. Açık, sürdürülebilir kod hızlı geliştirme ve güvenli refactoring sağlar.
