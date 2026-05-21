---
name: golang-patterns
description: İdiomatic Go desenler, en iyi uygulamalar ve sağlam, verimli ve bakımı kolay Go uygulamaları oluşturmak için konvansiyonlar.
origin: ECC
---

# Go Geliştirme Desenleri

Sağlam, verimli ve bakımı kolay uygulamalar oluşturmak için idiomatic Go desenleri.

## Temel Prensipler

- **Interface kabul et, struct döndür** — Fonksiyonlar interface parametreleri kabul eder
- **Hatalar değerlerdir** — Hataları exception değil birinci sınıf değerler olarak ele al
- **Sıfır değeri kullanışlı yap** — Açık başlatma olmadan çalışmalı

## Hata İşleme

```go
func LoadConfig(path string) (*Config, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, fmt.Errorf("load config %s: %w", path, err)
    }
    var cfg Config
    if err := json.Unmarshal(data, &cfg); err != nil {
        return nil, fmt.Errorf("parse config %s: %w", path, err)
    }
    return &cfg, nil
}
```

## Eşzamanlılık

```go
// Worker Pool
func WorkerPool(jobs <-chan Job, results chan<- Result, numWorkers int) {
    var wg sync.WaitGroup
    for i := 0; i < numWorkers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for job := range jobs {
                results <- process(job)
            }
        }()
    }
    wg.Wait()
    close(results)
}
```

## Functional Options Deseni

```go
type Option func(*Server)

func WithTimeout(d time.Duration) Option {
    return func(s *Server) { s.timeout = d }
}

func NewServer(addr string, opts ...Option) *Server {
    s := &Server{addr: addr, timeout: 30 * time.Second}
    for _, opt := range opts { opt(s) }
    return s
}
```
