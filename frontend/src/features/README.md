# Features

Feature-sliced design directory for domain features.

## Structure
Each feature should be a self-contained module:
```
features/
  suppliers/
    components/
    hooks/
    api/
    types/
  customers/
  orders/
```

## Migration Plan
Current components in `../components/` and `../pages/` will be gradually migrated here following feature-sliced architecture principles.
