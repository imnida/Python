---
name: frontend-patterns
description: React, Next.js, state yönetimi, performans optimizasyonu ve UI en iyi uygulamaları için frontend geliştirme kalıpları.
origin: ECC
---

# Frontend Geliştirme Kalıpları

React, Next.js ve performanslı kullanıcı arayüzleri için modern frontend kalıpları.

## Bileşen Kalıpları

```typescript
// Composition
interface CardProps { children: React.ReactNode; variant?: 'default' | 'outlined' }

export function Card({ children, variant = 'default' }: CardProps) {
  return <div className={`card card-${variant}`}>{children}</div>
}
```

## Özel Hook Kalıpları

```typescript
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)
  useEffect(() => {
    const handler = setTimeout(() => setDebouncedValue(value), delay)
    return () => clearTimeout(handler)
  }, [value, delay])
  return debouncedValue
}
```

## State Yönetimi

```typescript
// Context + Reducer
type Action = { type: 'SET_MARKETS'; payload: Market[] } | { type: 'SET_LOADING'; payload: boolean }

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'SET_MARKETS': return { ...state, markets: action.payload }
    case 'SET_LOADING': return { ...state, loading: action.payload }
    default: return state
  }
}
```

## Performans Optimizasyonu

```typescript
// Memoization
const sortedMarkets = useMemo(() => markets.sort((a, b) => b.volume - a.volume), [markets])
const handleSearch = useCallback((query: string) => setSearchQuery(query), [])

// Lazy Loading
const HeavyChart = lazy(() => import('./HeavyChart'))
```

## Error Boundary

```typescript
export class ErrorBoundary extends React.Component<{ children: React.ReactNode }, { hasError: boolean }> {
  state = { hasError: false }
  static getDerivedStateFromError() { return { hasError: true } }
  render() {
    if (this.state.hasError) return <div>Bir şeyler yanlış gitti</div>
    return this.props.children
  }
}
```
