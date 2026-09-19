"""This module serves as the entry point for the program."""
from balance.balance import Balance
from balance.balance_observer import LowBalanceAlertObserver
from balance.balance_observer import PrintObserver
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory
from transaction.transaction_adapter import TransactionAdapter
from transaction.external_income_transaction import ExternalFreelanceIncome
from command.transaction_command import ApplyTransactionCommand
from command.transaction_manager import TransactionManager


def main():
    print("Adding transactions...")

    balance = Balance.get_instance()
    balance.reset()

    print_observer = PrintObserver()
    low_balance_observer = LowBalanceAlertObserver(threshold=100)
    balance.register_observer(print_observer)
    balance.register_observer(low_balance_observer)

    transactions = [
        Transaction(100, TransactionCategory.INCOME),
        Transaction(50, TransactionCategory.EXPENSE),
        Transaction(200, TransactionCategory.INCOME),
        Transaction(75, TransactionCategory.EXPENSE),
    ]

    freelance_income = ExternalFreelanceIncome(1200, "INV-98765", "Mobile App Project")
    adapter = TransactionAdapter(freelance_income)
    adapted_transaction = adapter.to_transaction()

    all_transactions = transactions + [adapted_transaction]

    manager = TransactionManager()
    for transaction in all_transactions:
        manager.execute_command(ApplyTransactionCommand(balance, transaction))

    print(balance.summary())

    print("\nUndoing the last transaction...")
    manager.undo_last()
    print(balance.summary())

    if low_balance_observer.alert_triggered:
        print("Balance is currently below the alert threshold.")
    else:
        print("Balance is currently above the alert threshold.")


if __name__ == "__main__":
    main()