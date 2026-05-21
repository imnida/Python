---
name: docker-patterns
description: Yerel geliştirme, konteyner güvenliği, ağ, volume stratejileri ve multi-servis orkestrasyon için Docker ve Docker Compose kalıpları.
origin: ECC
---

# Docker Kalıpları

Konteynerize edilmiş geliştirme için Docker ve Docker Compose en iyi uygulamaları.

## Yerel Geliştirme için Docker Compose

```yaml
services:
  app:
    build:
      context: .
      target: dev
    ports:
      - "3000:3000"
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      - DATABASE_URL=postgres://postgres:postgres@db:5432/app_dev
    depends_on:
      db:
        condition: service_healthy
    command: npm run dev

  db:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: app_dev
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 5

volumes:
  pgdata:
```

## Konteyner Güvenliği

```dockerfile
# Root olmayan kullanıcı olarak çalıştır
RUN addgroup -g 1001 -S appgroup && adduser -S appuser -u 1001
USER appuser
```

## .dockerignore

```
node_modules
.git
.env
dist
coverage
*.log
```

## Yaygın Komutlar

```bash
docker compose logs -f app
docker compose exec app sh
docker compose up --build
docker compose down -v  # Volume'leri de kaldır (Yıkıcı)
```
