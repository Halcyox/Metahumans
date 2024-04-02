import ZODB
import ZODB.FileStorage
import transaction

class ConversationHistory:
    def __init__(self):
        storage = ZODB.FileStorage.FileStorage('conversation_history.fs')
        self.db = ZODB.DB(storage)
        self.connection = self.db.open()
        self.root = self.connection.root

        if not hasattr(self.root, 'history'):
            self.root.history = []

        self.history = self.root.history

    def add_message(self, message):
        self.history.append(message)
        self.commit()

    def get_history(self):
        return self.history
    def print_history(self):
        for message in self.history:
            print(message)
    def get_history_string(self):
        return '\n'.join(self.history) # append new lines between all lines
        
            

    def commit(self):
        if self.connection is not None:
            transaction.commit()
            self.connection.transaction_manager.begin()  # Begin a new transaction

    def close(self):
        if self.connection is not None:
            self.commit()
            self.connection.close()
            self.connection = None
        if self.db is not None:
            self.db.close()
            self.db = None

# Create an instance of ConversationHistory
conversation_history = ConversationHistory()
