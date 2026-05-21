---
name: django-patterns
description: DRF ile Django mimari desenleri, REST API tasarımı, ORM en iyi uygulamaları, caching, signal'ler, middleware ve production-grade Django uygulamaları.
origin: ECC
---

# Django Geliştirme Desenleri

Ölçeklenebilir, bakımı kolay uygulamalar için production-grade Django mimari desenleri.

## Proje Yapısı

```
myproject/
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
└── apps/
    ├── users/
    │   ├── models.py
    │   ├── views.py
    │   ├── serializers.py
    │   ├── services.py
    │   └── tests/
    └── products/
```

## Model Desenleri

```python
class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['-created_at']),
        ]
```

## Django REST Framework

```python
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').prefetch_related('tags')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'description']

    def get_serializer_class(self):
        if self.action == 'create':
            return ProductCreateSerializer
        return ProductSerializer
```

## Service Layer

```python
class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order(user, cart):
        order = Order.objects.create(user=user, total_price=cart.total_price)
        for item in cart.items.all():
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
        cart.items.all().delete()
        return order
```

## N+1 Önleme

```python
# Kötü
for product in Product.objects.all():
    print(product.category.name)  # Her ürün için ayrı sorgu

# İyi
for product in Product.objects.select_related('category').all():
    print(product.category.name)
```
