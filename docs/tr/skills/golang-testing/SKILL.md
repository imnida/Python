---
name: golang-testing
description: Table-driven testler, subtestler, benchmark'lar, fuzzing ve test coverage içeren Go test desenleri.
origin: ECC
---

# Go Test Desenleri

TDD metodolojisini takip eden güvenilir, bakımı kolay testler yazmak için kapsamlı Go test desenleri.

## Table-Driven Testler

```go
func TestAdd(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"positive numbers", 2, 3, 5},
        {"negative numbers", -1, -2, -3},
        {"zero values", 0, 0, 0},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := Add(tt.a, tt.b)
            if got != tt.expected {
                t.Errorf("Add(%d, %d) = %d; want %d", tt.a, tt.b, got, tt.expected)
            }
        })
    }
}
```

## Mock Interface'ler

```go
type MockUserRepository struct {
    GetUserFunc func(id string) (*User, error)
}

func (m *MockUserRepository) GetUser(id string) (*User, error) {
    return m.GetUserFunc(id)
}
```

## Benchmark'lar

```go
func BenchmarkProcess(b *testing.B) {
    data := generateTestData(1000)
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        Process(data)
    }
}
// go test -bench=. -benchmem ./...
```

## Test Komutları

```bash
go test ./...
go test -race ./...
go test -cover -coverprofile=coverage.out ./...
go test -bench=. -benchmem ./...
go test -fuzz=FuzzParse -fuzztime=30s ./...
```
