# transaction_manager.py

class TransactionManager:
    """invoker that executes commands and keeps an undo history."""

    def __init__(self):
        self._history = []

    def execute_command(self, command):
        command.execute()
        self._history.append(command)

    def undo_last(self):
        if not self._history:
            raise ValueError("No transactions to undo.")
        command = self._history.pop()
        command.undo()
        return command