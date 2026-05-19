from datetime import datetime

@staticmethod
class IUser:
    id: int
    username: str
    password: str
    registration_date: datetime
    last_seen: datetime

@staticmethod
class IWord:
    id: int
    text: str
    level_id: int
    created_at: datetime


@staticmethod
class IUserWord:
    id: int
    user_id: int
    word_id: int
    note: str
    added_at: datetime
