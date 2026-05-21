---
name: e2e-testing
description: Playwright E2E test kalıpları, Page Object Model, yapılandırma, CI/CD entegrasyonu, artifact yönetimi ve kararssız test stratejileri.
origin: ECC
---

# E2E Test Kalıpları

Kararlı, hızlı ve sürdürülebilir E2E test paketleri oluşturmak için kapsamlı Playwright kalıpları.

## Page Object Model (POM)

```typescript
import { Page, Locator } from '@playwright/test'

export class ItemsPage {
  readonly page: Page
  readonly searchInput: Locator
  readonly itemCards: Locator

  constructor(page: Page) {
    this.page = page
    this.searchInput = page.locator('[data-testid="search-input"]')
    this.itemCards = page.locator('[data-testid="item-card"]')
  }

  async goto() {
    await this.page.goto('/items')
    await this.page.waitForLoadState('networkidle')
  }

  async search(query: string) {
    await this.searchInput.fill(query)
    await this.page.waitForResponse(resp => resp.url().includes('/api/search'))
  }
}
```

## Playwright Yapılandırması

```typescript
export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
  ],
})
```

## Kararssız Test Çözümleri

```typescript
// Kötü: keyfi timeout
await page.waitForTimeout(5000)

// İyi: belirli koşulu bekle
await page.waitForResponse(resp => resp.url().includes('/api/data'))
```

## CI/CD Entegrasyonu

```yaml
name: E2E Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npx playwright install --with-deps
      - run: npx playwright test
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
```
