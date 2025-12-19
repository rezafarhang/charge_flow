# Charge Flow - Transaction Management System

A Django REST API for managing user wallets, credit requests, and mobile charge transactions with built-in race condition prevention.

## Project Overview

### Core Business Logic

**User Management:**
- JWT-based authentication (login/register/logout)
- Admin permission system for privileged operations

**Transaction System:**
- **Wallet Management**: Track user balance
- **Credit Requests**: Users request credit, admins approve/reject
- **Charge Sales**: Sell mobile phone charges to users

**Security & Performance:**
- Rate limiting on all endpoints (throttling)
- Admin-only access for credit approval
- Atomic transactions to prevent race conditions

## Architecture

<img width="1024" height="559" alt="image" src="https://github.com/user-attachments/assets/75465c4d-799c-4fd6-b9b5-baaa3ad01fbe" />


**Design Principles:**
- Serializers for validation only
- Business logic in Manager/Service classes
- Error constants with status_decorator pattern
- Split settings by concern

## Race Condition Prevention

### Database Isolation Level

PostgreSQL with `ATOMIC_REQUESTS = True` ensures each request runs in a transaction:

```python
# config/settings/settings_database.py
DATABASES = {
    'default': {
        'ATOMIC_REQUESTS': True,  # Each request is atomic
        'CONN_MAX_AGE': 600,
    }
}
```

### Atomic Transactions

All critical operations wrapped in `transaction.atomic()`:

### Atomic Updates with F() Expressions

Prevent race conditions in concurrent balance updates:

```python
from django.db.models import F

# ❌ WRONG - Race condition possible
wallet.balance += 100
wallet.save()

# ✅ CORRECT - Atomic database-level update
Wallet.objects.filter(user=user).update(
    balance=F('balance') + 100
)
```

**Key Patterns:**
1. `ATOMIC_REQUESTS = True` - Request-level transactions
2. `@transaction.atomic` - Method-level transactions
3. `F('field')` - Database-level atomic updates

## Project Standards

- **Error Handling**: Status decorator pattern with error codes
- **Throttling**: Endpoint-specific rate limits
- **Permissions**: Class-level permission checks
- **Validation**: Serializers for input, Managers for business logic
- **Constants**: All magic numbers in `consts.py`
- **Atomic Operations**

## Race Condition Examples

### Scenario 1: Concurrent Wallet Updates
```python
# Two users request credit simultaneously for same wallet

# ❌ Without atomic operations:
# Request 1: Read balance=100
# Request 2: Read balance=100
# Request 1: Write balance=150 (+50)
# Request 2: Write balance=130 (+30)
# Final: 130 (WRONG - lost update!)

# ✅ With F() expressions:
Wallet.objects.filter(id=wallet_id).update(
    balance=F('balance') + 50  # Atomic at DB level
)
# Final: 180 (CORRECT)
```
