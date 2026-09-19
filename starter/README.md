# Personal Finance Manager

A simple personal finance manager built in Python, demonstrating four
classic object-oriented design patterns: Singleton, Adapter, Observer,
and Command.

## Requirements

- Python 3.8+
- No external packages — standard library only (`unittest`, `enum`)

## Project Structure

starter/
├── main.py # Entry point — run this to see the app work
├── balance/
│ ├── balance.py # Singleton: Balance
│ ├── balance_observer.py # Observer: PrintObserver, LowBalanceAlertObserver
│ ├── test_balance.py
│ └── test_balance_observer.py
├── transaction/
│ ├── transaction.py # Transaction (amount + category)
│ ├── transaction_category.py # Enum: INCOME, EXPENSE
│ ├── external_income_transaction.py # ExternalFreelanceIncome
│ ├── transaction_adapter.py # Adapter: TransactionAdapter
│ ├── test_transaction.py
│ └── test_transaction_adapter.py
├── command/
│ ├── transaction_command.py # Command: ApplyTransactionCommand
│ ├── transaction_manager.py # Invoker: TransactionManager (undo history)
│ └── test_transaction_command.py
└── REFLECTION.md # Pattern rationale and trade-offs


## Design Patterns Used

| Pattern   | Where                                      | Purpose                                              |
|-----------|---------------------------------------------|--------------------------------------------------------|
| Singleton | `balance/balance.py`                        | Ensures one shared `Balance` instance app-wide        |
| Adapter   | `transaction/transaction_adapter.py`        | Converts external freelance income into `Transaction` |
| Observer  | `balance/balance_observer.py`               | Notifies observers on balance changes and low balance |
| Command   | `command/transaction_command.py`, `command/transaction_manager.py` | Wraps transactions as undoable actions |

See `REFLECTION.md` for the full rationale behind each choice, where
each pattern fits in the app, and trade-offs encountered.

## How to Run the App

From inside the `starter/` directory:

```bash
python main.py
```

This applies a set of transactions (including one adapted from an
external freelance income source), prints balance updates as they
happen, triggers a low-balance alert, and demonstrates undoing the
most recent transaction.

## How to Run the Tests

From inside the `starter/` directory:

```bash
python -m unittest discover -v
```

This discovers and runs every `test_*.py` file across `balance/`,
`transaction/`, and `command/` — 23 tests in total, covering the
Singleton, Transaction, Adapter, Observer, and Command implementations,
including tests that use a fake balance object to demonstrate
dependency injection.