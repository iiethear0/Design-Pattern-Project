# balance.py

from transaction.transaction_category import TransactionCategory


class Balance:
    """Singleton to track the balance."""

    _instance = None

    def __init__(self):
        """Initialize the balance. Prevent direct instantiation."""
        if Balance._instance is not None:
            raise RuntimeError(
                "balance is a singleton use Balance.get_instance() instead."
            )
        self._balance = 0.0
        self._observers = []

    @classmethod
    def get_instance(cls):
        """Return the single shared Balance instance, creating it if needed."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_observer(self, observer):
        """Register an observer to be notified on balance changes."""
        self._observers.append(observer)

    def unregister_observer(self, observer):
        """Remove a previously registered observer."""
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify_observers(self, transaction):
        """Notify all registered observers of the latest transaction."""
        for observer in self._observers:
            observer.update(self.get_balance(), transaction)

    def reset(self):
        """Reset the net balance to zero."""
        self._balance = 0.0

    def add_income(self, amount):
        """Add income to the balance."""
        self._balance += amount

    def add_expense(self, amount):
        """Subtract expense from the balance."""
        self._balance -= amount

    def apply_transaction(self, transaction):
        """Apply a Transaction object to update the balance."""
        if transaction.category == TransactionCategory.INCOME:
            self.add_income(transaction.amount)
        elif transaction.category == TransactionCategory.EXPENSE:
            self.add_expense(transaction.amount)
        else:
            raise ValueError(f"Unknown transaction category: {transaction.category}")

        self._notify_observers(transaction)

    def get_balance(self):
        """Get the current net balance."""
        return self._balance

    def summary(self):
        """Return a summary string of the net balance."""
        return f"Current balance: ${self._balance:.2f}"