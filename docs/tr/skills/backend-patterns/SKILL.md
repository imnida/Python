---
name: backend-patterns
description: Node.js, Express ve Next.js API routes için backend mimari kalıpları, API tasarımı, veritabanı optimizasyonu ve sunucu tarafı en iyi uygulamalar.
origin: ECC
---

# Backend Geliştirme Kalıpları

Ölçeklenebilir sunucu tarafı uygulamalar için backend mimari kalıpları ve en iyi uygulamalar.

## Ne Zaman Aktifleştirmelisiniz

- REST veya GraphQL API endpoint'leri tasarlarken
- Repository, service veya controller katmanları uygularken
- Veritabanı sorgularını optimize ederken (N+1, indeksleme, bağlantı havuzu)
- Önbellekleme eklerken (Redis, in-memory, HTTP cache başlıkları)
- Arka plan işleri veya async işleme ayarlarken
- API'ler için hata yönetimi ve doğrulama yapılandırırken
- Middleware oluştururken (auth, logging, rate limiting)

## API Tasarım Kalıpları

### RESTful API Yapısı

```typescript
// PASS: Kaynak tabanlı URL'ler
GET    /api/markets                 # Kaynakları listele
GET    /api/markets/:id             # Tek kaynak getir
POST   /api/markets                 # Kaynak oluştur
PUT    /api/markets/:id             # Kayanğı değiştir (tam)
PATCH  /api/markets/:id             # Kayanğı güncelle (kısmi)
DELETE /api/markets/:id             # Kayanğı sil

// PASS: Filtreleme, sıralama, sayfalama için query parametreleri
GET /api/markets?status=active&sort=volume&limit=20&offset=0
```

### Repository Kalıbı

```typescript
// Veri erişim mantığını soyutla
interface MarketRepository {
  findAll(filters?: MarketFilters): Promise<Market[]>
  findById(id: string): Promise<Market | null>
  create(data: CreateMarketDto): Promise<Market>
  update(id: string, data: UpdateMarketDto): Promise<Market>
  delete(id: string): Promise<void>
}

class SupabaseMarketRepository implements MarketRepository {
  async findAll(filters?: MarketFilters): Promise<Market[]> {
    let query = supabase.from('markets').select('*')

    if (filters?.status) {
      query = query.eq('status', filters.status)
    }

    if (filters?.limit) {
      query = query.limit(filters.limit)
    }

    const { data, error } = await query

    if (error) throw new Error(error.message)
    return data
  }

  // Diğer metodlar...
}
```

### Service Katmanı Kalıbı

```typescript
// İş mantığı veri erişiminden ayrılmış
class MarketService {
  constructor(private marketRepo: MarketRepository) {}

  async searchMarkets(query: string, limit: number = 10): Promise<Market[]> {
    // İş mantığı
    const embedding = await generateEmbedding(query)
    const results = await this.vectorSearch(embedding, limit)

    // Tam veriyi getir
    const markets = await this.marketRepo.findByIds(results.map(r => r.id))

    // Benzerliğe göre sırala
    return markets.sort((a, b) => {
      const scoreA = results.find(r => r.id === a.id)?.score || 0
      const scoreB = results.find(r => r.id === b.id)?.score || 0
      return scoreA - scoreB
    })
  }

  private async vectorSearch(embedding: number[], limit: number) {
    // Vector arama implementasyonu
  }
}
```

### Middleware Kalıbı

```typescript
// Request/response işleme hattı
export function withAuth(handler: NextApiHandler): NextApiHandler {
  return async (req, res) => {
    const token = req.headers.authorization?.replace('Bearer ', '')

    if (!token) {
      return res.status(401).json({ error: 'Unauthorized' })
    }

    try {
      const user = await verifyToken(token)
      req.user = user
      return handler(req, res)
    } catch (error) {
      return res.status(401).json({ error: 'Invalid token' })
    }
  }
}

// Kullanım
export default withAuth(async (req, res) => {
  // Handler req.user'a erişebilir
})
```

## Veritabanı Kalıpları

### Sorgu Optimizasyonu

```typescript
// PASS: İYİ: Sadece gerekli sütunları seç
.select('id, name, status, volume')
  .eq('status', 'active')
  .order('volume', { ascending: false })
  .limit(10)

// FAIL: KÖTÜ: Her şeyi seç
.select('*')
```

### N+1 Sorgu Önleme

```typescript
// FAIL: KÖTÜ: N+1 sorgu problemi
const markets = await getMarkets()
for (const market of markets) {
  market.creator = await getUser(market.creator_id)  // N sorgu
}

// PASS: İYİ: Toplu getirme
const markets = await getMarkets()
const creatorIds = markets.map(m => m.creator_id)
const creators = await getUsers(creatorIds)  // 1 sorgu
const creatorMap = new Map(creators.map(c => [c.id, c]))

markets.forEach(market => {
  market.creator = creatorMap.get(market.creator_id)
})
```

### Transaction Kalıbı

```typescript
async function createMarketWithPosition(
  marketData: CreateMarketDto,
  positionData: CreatePositionDto
) {
  // Supabase transaction kullan
  const { data, error } = await supabase.rpc('create_market_with_position', {
    market_data: marketData,
    position_data: positionData
  })

  if (error) throw new Error('Transaction failed')
  return data
}
```

## Önbellekleme Stratejileri

### Redis Önbellekleme Katmanı

```typescript
class CachedMarketRepository implements MarketRepository {
  constructor(
    private baseRepo: MarketRepository,
    private redis: RedisClient
  ) {}

  async findById(id: string): Promise<Market | null> {
    const cached = await this.redis.get(`market:${id}`)
    if (cached) return JSON.parse(cached)
    const market = await this.baseRepo.findById(id)
    if (market) {
      await this.redis.setex(`market:${id}`, 300, JSON.stringify(market))
    }
    return market
  }
}
```

## Hata Yönetimi Kalıpları

### Merkezi Hata Yöneticisi

```typescript
class ApiError extends Error {
  constructor(
    public statusCode: number,
    public message: string,
    public isOperational = true
  ) {
    super(message)
    Object.setPrototypeOf(this, ApiError.prototype)
  }
}

export function errorHandler(error: unknown, req: Request): Response {
  if (error instanceof ApiError) {
    return NextResponse.json({
      success: false,
      error: error.message
    }, { status: error.statusCode })
  }

  if (error instanceof z.ZodError) {
    return NextResponse.json({
      success: false,
      error: 'Validation failed',
      details: error.errors
    }, { status: 400 })
  }

  console.error('Unexpected error:', error)

  return NextResponse.json({
    success: false,
    error: 'Internal server error'
  }, { status: 500 })
}
```

**Unutmayın**: Backend kalıpları ölçeklenebilir, sürdürülebilir sunucu tarafı uygulamalar sağlar. Karmaşıklık seviyenize uyan kalıpları seçin.
