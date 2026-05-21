from db import VocabularyDB
from logger import Log
from words.levels import Level
from models import IWord

class WordUserDAO:

    def __init__(self, user_id: int):
        self.__db = VocabularyDB()
        self.user_id = user_id

    def add_word(self, word_id: int, note: str = ""):
        """
        Add a word to the user's vocabulary list
        Args:
            word_id (int): The ID of the word to add
            note (str): A note about the word
        Returns:
            tuple: A boolean indicating success and a message
        """
        word_obj: IWord = self.__db.get_word(word_id)
        if not word_obj:
            Log.warning(f"Attempt to add non-existent word: {word_id}")
            return False, f"Word with ID '{word_id}' does not exist."
        
        if self.__db.get_user_word(self.user_id, word_obj.id):
            Log.warning(f"Attempt to add already added word: {word_id} | User ID: {self.user_id}")
            return False, f"Word with ID '{word_id}' is already in your vocabulary list."
        
        self.__db.add_user_word(self.user_id, word_obj.id, note)
        Log.info(f"Word added to user vocabulary successfully: {word_id} | User ID: {self.user_id}")
        return True, f"Word with ID '{word_id}' added to your vocabulary list successfully."

    def get_words(self):
        """
        Retrieve all words associated with the user
        Returns:
            list: A list of words associated with the user
        """
        return self.__db.get_user_words(self.user_id)
    
    def get_words_by_level(self, level_name):
        """
        Retrieve words associated with the user filtered by vocabulary level
        Args:
            level_name (str): The vocabulary level to filter by
        Returns:
            list: A list of words associated with the user and the specified level
        """
        level: Level = self.__db.get_level_by_name(level_name)
        if not level or level_name not in Level.__members__:
            Log.warning(f"Attempt to retrieve words with non-existent level: {level_name}")
            return []
        
        return self.__db.get_user_words(self.user_id, level.id)


