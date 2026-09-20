# Reflection: Design Pattern Rationale

## Singleton — `Balance`

**Why this pattern:** the app needs exactly one source of truth for the
user's balance. If more than one `Balance` object could exist, two
parts of the app could disagree about the current total, or a
transaction could be applied to the wrong instance and silently
disappear from the user's real balance.

**Design intent:** `Balance.__init__` raises an error if an instance
already exists, and `Balance.get_instance()` is the only sanctioned way
to obtain the shared object. This makes the "only one instance" rule
enforced by the code itself, not just a convention developers have to
remember.

**Trade-off / challenge:** Singletons introduce global mutable state,
which made testing slightly awkward — the balance carries over between
test cases in the same process unless each test explicitly calls
`reset()`. I addressed this by resetting the balance in every test's
`setUp()`, but the underlying tension (global state vs. isolated tests)
is a real limitation of the pattern, not something fully "solved."

**How it improved the app:** every component — `main.py`, the
observers, the command objects — can safely assume there is one
balance, without needing to pass it through every layer of the
application or coordinate which instance is "the real one."

## Adapter — `TransactionAdapter`

**Why this pattern:** `ExternalFreelanceIncome` (invoice ID,
description, amount) doesn't match the internal `Transaction` shape
(amount, category). Rather than teaching `Balance` or `Transaction`
to understand every possible external data format, the Adapter isolates
that translation in one place.

**Design intent:** `TransactionAdapter.to_transaction()` reads the
external object's `.typ` field and maps it to the correct
`TransactionCategory`, then constructs a standard `Transaction`. This
keeps the "what does external data look like" concern completely
separate from "what does a Transaction mean to this app."

**Trade-off / challenge:** the adapter currently only distinguishes
`"income"` vs. anything else, since the only external source
implemented is always income. That makes part of the conditional look
redundant today, but I kept it explicit rather than hardcoding
`INCOME`, so the class is correct by design rather than correct by
coincidence — if a second external source appears later, the same
adapter shape still works.

**How it improved the app:** `TransactionAdapter` can be unit tested
completely in isolation (see `test_transaction_adapter.py`), with no
dependency on `Balance` or the Observer/Command wiring — it only cares
about one external object in, one `Transaction` out.

## Observer — `PrintObserver` and `LowBalanceAlertObserver`

**Why this pattern:** the balance needs to trigger side effects
(printing an update, raising a low-balance alert) without `Balance`
itself knowing or caring what those reactions are.

**Design intent:** `Balance` holds a list of observers and calls
`update(balance, transaction)` on each one after every transaction.
Neither observer is aware of the other, and `Balance` is not aware of
what either one does with the notification — it only knows it has to
notify.

**Trade-off / challenge:** `LowBalanceAlertObserver.alert_triggered`
is recomputed on every `update()` call rather than only ever latching
to `True` once. This was a deliberate choice so the alert correctly
turns off again once the balance recovers above the threshold — but it
means any code using this observer has to check `alert_triggered`
right after a transaction if it wants to catch the moment the alert
fires, since the flag can flip back on the very next transaction.

**How it improved the app:** new reactions to balance changes (e.g. an
email alert, a logging observer) could be added later without touching
`Balance.apply_transaction` at all — only a new class implementing
`IBalanceObserver` would be needed. This is a direct flexibility gain:
the set of things that react to a balance change is open for extension
without modifying the class that owns the balance.

## Command — `ApplyTransactionCommand` and `TransactionManager`

**Why this pattern:** applying a transaction and undoing it are
naturally symmetric operations, but `Balance.apply_transaction` alone
has no concept of history or reversal.

**Design intent:** each transaction is wrapped in an
`ApplyTransactionCommand` object exposing `execute()` and `undo()`.
`TransactionManager` acts as an invoker — it doesn't know what a
command does, only that it can call `.execute()` and later `.undo()`
on the most recent one, using a stack (`_history`, a list used with
`.append()`/`.pop()`).

Crucially, `ApplyTransactionCommand` receives `balance` through its
constructor instead of calling `Balance.get_instance()` internally.
That's a dependency-injection choice: the command doesn't need to know
`Balance` is a Singleton at all, it only needs an object with an
`apply_transaction` method. This is proven directly by
`TestApplyTransactionCommandWithFakeBalance` in
`test_transaction_command.py`, which exercises the command against a
minimal `FakeBalance` stand-in — no Singleton, no global state — and
still verifies `execute()` and `undo()` behave correctly.

**Trade-off / challenge:** this implementation only supports undoing
the single most recent command, not a full redo stack. Redo would
require a second stack to hold undone commands and a way to
distinguish "undone" from "never executed," which felt like scope
beyond what this assignment asked for, but is the natural next
extension.

**How it improved the app:** undo flows through the same
`Balance.apply_transaction` path as any other transaction, so the
existing Observer pattern reacts to an undo exactly as it would to any
other change — no special-case logic was needed anywhere else in the
app to support it.

## Summary

| Pattern   | Specific purpose in this app                          | Concrete trade-off faced                          |
|-----------|----------------------------------------------------------|-------------------------------------------------------|
| Singleton | One shared `Balance` instance, enforced by the code itself | Global state makes tests need explicit `reset()` |
| Adapter   | Translates external freelance-income data into `Transaction` | Currently only distinguishes one external format |
| Observer  | Decouples balance changes from reactions to them (print, alert) | Alert flag resets each call, must be checked promptly |
| Command   | Wraps transactions so they can be undone, via injected `Balance` | Undo-only; no redo stack implemented |

Together, these patterns keep `Balance` and `Transaction` — the two
simplest, most central classes in the app — almost entirely unaware of
external data formats, notification logic, or history tracking. Each
of those concerns lives in its own class, which is what made it
possible to unit test the Adapter, the Observers, and the Command
objects completely independently of one another and of the Singleton
itself.