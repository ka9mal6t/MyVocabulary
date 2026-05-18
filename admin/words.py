from db import VocabularyDB
from logger import Log
from words.levels import Level

class WordAdminDAO:
    """Data Access Object for word-related operations"""
    
    def __init__(self):
        self.db = VocabularyDB()
    
    def add_word(self, word, level_name):
        """
        Add a new word to the database
        Args:
            word (str): The word to add
            level_name (str): The vocabulary level of the word
        Returns:
            tuple: A boolean indicating success and a message
        """
        if self.db.get_word_by_name(word):
            Log.info(f"Attempt to add existing word: {word} | {level_name}")
            return False, f"Word '{word}' already exists."
        
        level = self.db.get_level_by_name(level_name)
        if not level or level_name not in Level.__members__:
            Log.info(f"Attempt to add word with non-existent level: {level_name}")
            return False, f"Level '{level_name}' does not exist."
        
        self.db.add_word(word, level.id)
        Log.info(f"Word added successfully: {word} | {level_name}")
        return True, f"Word '{word}' added successfully."