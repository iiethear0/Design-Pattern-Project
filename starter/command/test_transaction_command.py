import unittest
from balance.balance import Balance
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory
from command.transaction_command import ApplyTransactionCommand
from command.transaction_manager import TransactionManager


class TestApplyTransactionCommand(unittest.TestCase):

    def setUp(self):
        self.balance = Balance.get_instance()
        self.balance.reset()

    def test_execute_applies_income(self):
        command = ApplyTransactionCommand(
            self.balance, Transaction(
                100, TransactionCategory.INCOME))
        command.execute()
        self.assertEqual(self.balance.get_balance(), 100)

    def test_execute_applies_expense(self):
        command = ApplyTransactionCommand(
            self.balance, Transaction(
                40, TransactionCategory.EXPENSE))
        command.execute()
        self.assertEqual(self.balance.get_balance(), -40)

    def test_undo_reverses_income(self):
        command = ApplyTransactionCommand(
            self.balance, Transaction(
                100, TransactionCategory.INCOME))
        command.execute()
        command.undo()
        self.assertEqual(self.balance.get_balance(), 0)

    def test_undo_reverses_expense(self):
        command = ApplyTransactionCommand(
            self.balance, Transaction(
                40, TransactionCategory.EXPENSE))
        command.execute()
        command.undo()
        self.assertEqual(self.balance.get_balance(), 0)


class TestTransactionManager(unittest.TestCase):

    def setUp(self):
        self.balance = Balance.get_instance()
        self.balance.reset()
        self.manager = TransactionManager()

    def test_execute_command_updates_balance(self):
        command = ApplyTransactionCommand(
            self.balance, Transaction(
                50, TransactionCategory.INCOME))
        self.manager.execute_command(command)
        self.assertEqual(self.balance.get_balance(), 50)

    def test_undo_last_reverts_most_recent_command(self):
        first = ApplyTransactionCommand(
            self.balance, Transaction(
                100, TransactionCategory.INCOME))
        second = ApplyTransactionCommand(
            self.balance, Transaction(
                30, TransactionCategory.EXPENSE))
        self.manager.execute_command(first)
        self.manager.execute_command(second)
        self.assertEqual(self.balance.get_balance(), 70)

        self.manager.undo_last()
        self.assertEqual(self.balance.get_balance(), 100)

    def test_undo_last_raises_when_history_empty(self):
        with self.assertRaises(ValueError):
            self.manager.undo_last()


class TestApplyTransactionCommandWithFakeBalance(unittest.TestCase):
    """
    Demonstrates the payoff of dependency injection: ApplyTransactionCommand
    accepts a balance-like object via its constructor, so it can be tested
    against a lightweight fake instead of the real Balance Singleton.
    No global state is touched by this test at all.
    """

    class FakeBalance:
        """A minimal stand-in that only implements what Command needs."""

        def __init__(self):
            self.applied_transactions = []

        def apply_transaction(self, transaction):
            self.applied_transactions.append(transaction)

    def test_execute_calls_apply_transaction_on_injected_balance(self):
        fake_balance = self.FakeBalance()
        transaction = Transaction(100, TransactionCategory.INCOME)
        command = ApplyTransactionCommand(fake_balance, transaction)

        command.execute()

        self.assertEqual(fake_balance.applied_transactions, [transaction])

    def test_undo_calls_apply_transaction_with_reversed_transaction(self):
        fake_balance = self.FakeBalance()
        transaction = Transaction(100, TransactionCategory.INCOME)
        command = ApplyTransactionCommand(fake_balance, transaction)

        command.execute()
        command.undo()

        self.assertEqual(len(fake_balance.applied_transactions), 2)
        reversed_transaction = fake_balance.applied_transactions[1]
        self.assertEqual(reversed_transaction.amount, 100)
        self.assertEqual(
            reversed_transaction.category,
            TransactionCategory.EXPENSE)


if __name__ == "__main__":
    unittest.main()
