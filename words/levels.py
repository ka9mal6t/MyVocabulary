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
    db = VocabularyDB()
    
    if len(db.list_levels()) > 0:
        Log.info("Levels already exist in the database.")
        return
    
    for lvl in Level:
        db.add_level(lvl.name)
        Log.info(f"Levels added successfully. Current levels: {lvl.name}")


