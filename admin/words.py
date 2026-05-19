from db import VocabularyDB
from logger import Log
from words.levels import Level
from models import IWord

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
            Log.warning(f"Attempt to add existing word: {word} | {level_name}")
            return False, f"Word '{word}' already exists."
        
        level = self.db.get_level_by_name(level_name)
        if not level or level_name not in Level.__members__:
            Log.warning(f"Attempt to add word with non-existent level: {level_name}")
            return False, f"Level '{level_name}' does not exist."
        
        self.db.add_word(word, level.id)
        Log.info(f"Word added successfully: {word} | {level_name}")
        return True, f"Word '{word}' added successfully."
    
    def delete_word(self, word):
        """
        Delete a word from the database
        Args:
            word (str): The word to delete
        Returns:
            tuple: A boolean indicating success and a message
        """

        word_obj = self.db.get_word_by_name(word)
        if not word_obj:
            Log.warning(f"Attempt to delete non-existent word: {word}")
            return False, f"Word '{word}' does not exist."
        
        self.db.delete_word(word_obj.id)
        Log.info(f"Word deleted successfully: {word} | {Level(word_obj.level_id).name}")
        return True, f"Word '{word}' deleted successfully."
    
    def update_word_level(self, word,  new_level_name=None):
        """
        Update a word's vocabulary level in the database
        Args:
            word (str): The word to update
            new_level_name (str, optional): The new vocabulary level of the word
        Returns:
            tuple: A boolean indicating success and a message
        """
        word_obj = self.db.get_word_by_name(word)
        if not word_obj:
            Log.warning(f"Attempt to update non-existent word: {word}")
            return False, f"Word '{word}' does not exist."
        
        if new_level_name:
            level = self.db.get_level_by_name(new_level_name)
            if not level or new_level_name not in Level.__members__:
                Log.warning(f"Attempt to update word with non-existent level: {new_level_name}")
                return False, f"Level '{new_level_name}' does not exist."
            self.db.update_word_level(word_obj.id, level_id=level.id)
        
        Log.info(f"Word updated successfully: {word} | {new_level_name if new_level_name else Level(word_obj.level_id).name}")
        return True, f"Word '{word}' updated successfully."
    
    def update_word_level_by_id(self, word_id, new_level_name=None):
        """
        Update a word's vocabulary level in the database by word ID
        Args:
            word_id (int): The ID of the word to update
            new_level_name (str, optional): The new vocabulary level of the word
        Returns:
            tuple: A boolean indicating success and a message
        """
        word_obj = self.db.get_word(word_id)
        if not word_obj:
            Log.warning(f"Attempt to update non-existent word by ID: {word_id}")
            return False, f"Word with ID '{word_id}' does not exist."
        
        if new_level_name:
            level = self.db.get_level_by_name(new_level_name)
            if not level or new_level_name not in Level.__members__:
                Log.warning(f"Attempt to update word with non-existent level: {new_level_name}")
                return False, f"Level '{new_level_name}' does not exist."
            self.db.update_word_level(word_obj.id, level_id=level.id)
        
        Log.info(f"Word updated successfully: {word_obj.name} | {new_level_name if new_level_name else Level(word_obj.level_id).name}")
        return True, f"Word '{word_obj.name}' updated successfully."
   