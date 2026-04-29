# EXPLAINER

## 1. Ledger

SELECT COALESCE(SUM(amount_paise), 0)
FROM core_ledgerentry
WHERE merchant_id = %s;

Explanation:
I used a ledger model where all transactions are stored as entries.
Credits are positive and payouts are negative.
Balance is always calculated using SUM instead of storing it.

---

## 2. Lock

merchant = Merchant.objects.select_for_update().get(id=merchant_id)

Explanation:
I used database-level locking with select_for_update().
This ensures only one transaction can modify the merchant balance at a time.
It prevents race conditions.

---

## 3. Idempotency

Explanation:
Each payout stores an idempotency_key.
Before creating a payout, I check if the key already exists.
If yes, I return the same payout instead of creating a new one.

---

## 4. State Machine

Allowed states:
pending → processing → completed
pending → processing → failed

Invalid transitions are not allowed.

---

## 5. AI Audit

AI initially suggested checking balance before transaction.
This can cause race conditions.

I fixed it by:
- using transaction.atomic()
- using select_for_update()

This ensures safe concurrent execution.