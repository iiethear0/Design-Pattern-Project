# transaction_command.py

from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class Command:
    """abstract base class for a command that can be executed and undone."""

    def execute(self):
        raise NotImplementedError("subclasses must implement execute().")

    def undo(self):
        raise NotImplementedError("subclasses must implement undo().")


class ApplyTransactionCommand(Command):
    """wraps applying a transaction to a balance so it can be undone later."""

    def __init__(self, balance, transaction):
        self.balance = balance
        self.transaction = transaction

    def execute(self):
        self.balance.apply_transaction(self.transaction)

    def undo(self):
        reverse_category = (
            TransactionCategory.EXPENSE
            if self.transaction.category == TransactionCategory.INCOME
            else TransactionCategory.INCOME
        )
        reverse_transaction = Transaction(self.transaction.amount, reverse_category)
        self.balance.apply_transaction(reverse_transaction)