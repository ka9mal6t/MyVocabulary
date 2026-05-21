import hashlib
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "vocabulary.db"


class DBRow:
    def __init__(self, cursor, row):
        self._row = row
        self._columns = [col[0] for col in cursor.description]

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._row[key]
        if key in self._columns:
            return self._row[self._columns.index(key)]
        raise KeyError(key)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self):
        return list(self._columns)

    def items(self):
        return [(key, self[key]) for key in self._columns]

    def __iter__(self):
        return iter(self._row)

    def __len__(self):
        return len(self._row)

    def __getattr__(self, name):
        if name in self._columns:
            return self[name]
        raise AttributeError(f"{type(self).__name__!r} object has no attribute {name!r}")

    def __repr__(self):
        return f"{type(self).__name__}({dict(self.items())!r})"


class VocabularyDB:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._ensure_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = self._row_factory
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @staticmethod
    def _row_factory(cursor, row):
        if row is None:
            return None
        return DBRow(cursor, row)

    def _ensure_db(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    registration_date TEXT NOT NULL DEFAULT (datetime('now')),
                    last_seen TEXT NOT NULL DEFAULT (datetime('now'))
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS levels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    level_id INTEGER NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    FOREIGN KEY(level_id) REFERENCES levels(id)
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    word_id INTEGER NOT NULL,
                    note TEXT,
                    added_at TEXT NOT NULL DEFAULT (datetime('now')),
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(word_id) REFERENCES words(id)
                )
                """
            )
            conn.commit()

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    # User Management
    def add_user(self, username: str, password: str) -> int:
        hashed = self.hash_password(password)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed),
            )
            conn.commit()
            return cursor.lastrowid

    def get_user_by_username(self, username: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            return cursor.fetchone()

    def list_users(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users ORDER BY registration_date DESC")
            return cursor.fetchall()

    def authenticate_user(self, username: str, password: str):
        hashed = self.hash_password(password)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username = ? AND password = ?",
                (username, hashed),
            )
            user = cursor.fetchone()
            if not user:
                return None
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "UPDATE users SET last_seen = ? WHERE id = ?",
                (now, user["id"]),
            )
            conn.commit()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user["id"],))
            return cursor.fetchone()

    def update_last_seen(self, user_id: int) -> None:
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET last_seen = ? WHERE id = ?",
                (now, user_id),
            )
            conn.commit()

    def delete_user(self, user_id: int) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()


    # Levels and Words Management
    def add_level(self, name: str) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO levels (name) VALUES (?)", (name,))
            conn.commit()
            return cursor.lastrowid

    def get_level(self, level_id: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM levels WHERE id = ?", (level_id,))
            return cursor.fetchone()

    def get_level_by_name(self, name: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM levels WHERE name = ?", (name,))
            return cursor.fetchone()

    def list_levels(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM levels ORDER BY id")
            return cursor.fetchall()

    def delete_level(self, level_id: int) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM levels WHERE id = ?", (level_id,))
            conn.commit()

    def add_word(self, text: str, level_id: int) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO words (text, level_id) VALUES (?, ?)",
                (text, level_id),
            )
            conn.commit()
            return cursor.lastrowid

    def get_word(self, word_id: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM words WHERE id = ?", (word_id,))
            return cursor.fetchone()
        
    def get_word_by_name(self, name: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM words WHERE text = ?", (name,))
            return cursor.fetchone()

    def list_words(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT words.*, levels.name AS level_name FROM words "
                "LEFT JOIN levels ON words.level_id = levels.id "
                "ORDER BY words.created_at DESC"
            )
            return cursor.fetchall()

    def search_words_by_level(self, level_name: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT words.*, levels.name AS level_name FROM words "
                "JOIN levels ON words.level_id = levels.id "
                "WHERE levels.name = ? ORDER BY words.created_at DESC",
                (level_name,),
            )
            return cursor.fetchall()

    def update_word_level(self, word_id: int, level_id: int) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE words SET level_id = ? WHERE id = ?",
                (level_id, word_id),
            )
            conn.commit()

    def delete_word(self, word_id: int) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM words WHERE id = ?", (word_id,))
            conn.commit()

    # User Words Management
    def add_user_word(self, user_id: int, word_id: int, note: str = None) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO user_words (user_id, word_id, note) VALUES (?, ?, ?)",
                (user_id, word_id, note),
            )
            conn.commit()
            return cursor.lastrowid

    def get_user_words(self, user_id: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM user_words WHERE user_id = ? ORDER BY added_at DESC",
                (user_id,),
            )
            return cursor.fetchall()

    def get_user_word(self, user_id: int, word_id: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM user_words WHERE user_id = ? AND word_id = ?",
                (user_id, word_id),
            )
            return cursor.fetchone()

    def list_user_word_details(self, user_id: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT uw.*, w.text AS word_text, l.name AS level_name "
                "FROM user_words AS uw "
                "JOIN words AS w ON uw.word_id = w.id "
                "JOIN levels AS l ON w.level_id = l.id "
                "WHERE uw.user_id = ? ORDER BY uw.added_at DESC",
                (user_id,),
            )
            return cursor.fetchall()

    def update_user_word_note(self, user_word_id: int, note: str) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE user_words SET note = ? WHERE id = ?",
                (note, user_word_id),
            )
            conn.commit()

    def delete_user_word(self, user_id: int, word_id: int) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM user_words WHERE user_id = ? AND word_id = ?",
                (user_id, word_id),
            )
            conn.commit()


def init_db() -> None:
    VocabularyDB()

    
if __name__ == "__main__":
    init_db()
