---
name: deployment-patterns
description: Deployment iş akışları, CI/CD pipeline kalıpları, Docker konteynerizasyonu, sağlık kontrolleri, rollback stratejileri ve web uygulamaları için üretim hazırlığı kontrol listeleri.
origin: ECC
---

# Deployment Kalıpları

Üretim deployment iş akışları ve CI/CD en iyi uygulamaları.

## Deployment Stratejileri

### Rolling Deployment
Instance'ları kademeli olarak değiştir. Artıları: Sıfır kesinti. Eksileri: İki versiyon aynı anda çalışır.

### Blue-Green
Trafiği atomik olarak değiştir. Artıları: Anlık rollback. Eksileri: 2x altyapı.

### Canary
Önce küçük trafik yüzdesini yeni versiyona yönlendir. Artıları: Gerçek trafikle test.

## Docker Multi-Stage

```dockerfile
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --production=false

FROM node:22-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build && npm prune --production

FROM node:22-alpine AS runner
WORKDIR /app
RUN addgroup -g 1001 -S appgroup && adduser -S appuser -u 1001
USER appuser
COPY --from=builder --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --from=builder --chown=appuser:appgroup /app/dist ./dist
ENV NODE_ENV=production
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://localhost:3000/health || exit 1
CMD ["node", "dist/server.js"]
```

## GitHub Actions CI/CD

```yaml
name: CI/CD
on:
  push:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci && npm run lint && npm test
  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy
        run: echo "Deploy ${{ github.sha }}"
```

## Sağlık Kontrolleri

```typescript
app.get("/health", (req, res) => {
  res.status(200).json({ status: "ok" });
});
```

## Üretim Hazırlığı Kontrol Listesi

- [ ] Tüm testler geçiyor
- [ ] Kodda hardcode edilmiş secret yok
- [ ] Sağlık kontrolü endpoint'i anlamlı durum döndürüyor
- [ ] Ortam değişkenleri başlangıçta validate ediliyor
- [ ] Rollback planı dokümante edilmiş ve test edilmiş
- [ ] Güvenlik header'ları ayarlanmış
