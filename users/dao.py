from db import VocabularyDB
from logger import Log

class UserDAO:
    """Data Access Object for user-related operations"""
    
    def __init__(self):
        self.__db = VocabularyDB()
    
    def register_user(self, username, email):
        """
        Register a new user
        Args:
            username (str): The username of the new user
            email (str): The email address of the new user
        Returns:
            tuple: A boolean indicating success and a message
        """
        if self.__db.get_user_by_username(username):
            Log.warning(f"Attempt to register existing user: {username}")
            return False, f"User '{username}' already exists."
            
        
        self.__db.add_user(username, email)
        Log.info(f"User registered successfully: {username}")
        return True, f"User '{username}' registered successfully."
    
    def login_user(self, username, password):
        """
        Authenticate a user by username and password
        Args:
            username (str): The username of the user
            password (str): The password of the user
        Returns:
            tuple: A boolean indicating success and a message
        """
        user = self.__db.authenticate_user(username, password)
        if not user:
            Log.warning(f"Failed login attempt for user: {username}")
            return False, f"User '{username}' not found."
        Log.info(f"User logged in successfully: {username}")
        self.__db.update_last_seen(user.id)
        return True, user