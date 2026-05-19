from enum import Enum
from db import VocabularyDB
from logger import Log

class Level(Enum):
    """Vocabulary levels enum"""
    A0 = 1
    A1 = 2
    A2 = 3
    B1 = 4
    B2 = 5
    C1 = 6
    C2 = 7



def add_levels():
    """Add predefined vocabulary levels to the database"""
    db = VocabularyDB()
    for level in Level:
        if not db.get_level_by_name(level.name):
            db.add_level(level.name)
            Log.info(f"Added level: {level.name}")
        else:
            Log.warning(f"Level already exists: {level.name}")
    



