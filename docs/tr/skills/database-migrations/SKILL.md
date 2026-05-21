---
name: database-migrations
description: Şema değişiklikleri, veri migration'ları, rollback'ler ve PostgreSQL, MySQL ve yaygın ORM'ler (Prisma, Drizzle, Django, TypeORM, golang-migrate) arasında sıfır kesinti deployment'ları için veritabanı migration en iyi uygulamaları.
origin: ECC
---

# Veritabanı Migration Kalıpları

Üretim sistemleri için güvenli, geri alınabilir veritabanı şema değişiklikleri.

## Ne Zaman Aktifleştirmeli

- Veritabanı tabloları oluştururken veya değiştirirken
- Sütun veya indeks eklerken/kaldırırken
- Veri migration'ları çalıştırırken (backfill, dönüştürme)
- Sıfır kesinti şema değişiklikleri planlarken
- Yeni bir proje için migration araçları kurarken

## Temel İlkeler

1. **Her değişiklik bir migration'dır** — üretim veritabanlarını asla manuel olarak değiştirmeyin
2. **Migration'lar üretimde sadece ileri** — rollback'ler yeni forward migration'lar kullanır
3. **Şema ve veri migration'ları ayrıdır** — tek migration'da DDL ve DML'yi asla karıştırmayın
4. **Migration'ları üretim boyutundaki veriye karşı test edin**
5. **Migration'lar üretimde çalıştıktan sonra değişmezdir**

## PostgreSQL Kalıpları

### Güvenli Sütun Ekleme

```sql
-- İYİ: Nullable sütun
ALTER TABLE users ADD COLUMN avatar_url TEXT;

-- İYİ: Varsayılanlı sütun (Postgres 11+ anlık)
ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT true;

-- KÖTÜ: Varsayılansız NOT NULL (tabloyu kilitler)
ALTER TABLE users ADD COLUMN role TEXT NOT NULL;
```

### Kesinti Olmadan İndeks Ekleme

```sql
-- KÖTÜ: Büyük tablolarda yazmaları engeller
CREATE INDEX idx_users_email ON users (email);

-- İYİ: Engellemez
CREATE INDEX CONCURRENTLY idx_users_email ON users (email);
```

### Genişlet-Sözleş Kalıbı (Sıfır Kesinti)

```sql
-- Adım 1: Yeni sütun ekle
ALTER TABLE users ADD COLUMN display_name TEXT;
-- Adım 2: Backfill
UPDATE users SET display_name = username WHERE display_name IS NULL;
-- Adım 3: Uygulama her ikisine yaz
-- Adım 4: Eski sütunu kaldır
ALTER TABLE users DROP COLUMN username;
```

## Prisma

```bash
npx prisma migrate dev --name add_user_avatar
npx prisma migrate deploy
```

## Drizzle

```bash
npx drizzle-kit generate
npx drizzle-kit migrate
```

## Django

```bash
python manage.py makemigrations
python manage.py migrate
```

## golang-migrate

```bash
migrate create -ext sql -dir migrations -seq add_user_avatar
migrate -path migrations -database "$DATABASE_URL" up
```

## Anti-Kalıplar

| Anti-Kalıp | Neden Başarısız Olur | Daha İyi Yaklaşım |
|-------------|-------------|-----------------|
| Üretimde manuel SQL | Denetim izi yok | Her zaman migration dosyaları kullan |
| Deploy edilmiş migration'ları düzenleme | Ortamlar arası sapma | Yeni migration oluştur |
| Varsayılansız NOT NULL | Tabloyu kilitler | Nullable ekle, backfill et, kısıt ekle |
| Büyük tabloda inline indeks | Yazmaları engeller | CREATE INDEX CONCURRENTLY |
