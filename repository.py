import sqlite3

# This is the Repository class that interacts with the SQLite database
class Tracks:
    def __init__(self ,table):
        self.table = table
        self.database = "music_catalogue.db"
        self.init_db()
        
    def init_db(self):
        with sqlite3.connect(self.database) as connection:
            cursor = connection.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tracks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    artist TEXT NOT NULL,
                    audio_base64 TEXT NOT NULL
                )
            ''')
            connection.commit()
            
    def connect_db(self):
        return sqlite3.connect(self.database)

    def clear(self,):
        with sqlite3.connect(self.database) as connection:
            cursor = connection.cursor ()
            cursor.execute(
            f"DELETE FROM {self.table}"
            )
        connection.commit ()
    
    def insert(self, title, artist, audio_base64):
        """Insert a track into the database, either by filename or Base64 audio."""
        with sqlite3.connect(self.database) as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"INSERT INTO {self.table} (title, artist, audio_base64) VALUES (?, ?, ?)",
                (title, artist, audio_base64)
            )       
        connection.commit()
        return cursor.rowcount
     
    def delete(self, trackid):
        with sqlite3.connect(self.database, timeout=10) as connection:
            cursor = connection.cursor()
            cursor.execute(f"DELETE FROM {self.table} WHERE id=?", (trackid,))
        connection.commit()
        return cursor.rowcount
    
    def get_by_id(self, track_id):
        with sqlite3.connect(self.database) as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM {self.table} WHERE id = ?", (track_id,))
            return cursor.fetchone()  
            
    def get_all(self):
        with sqlite3.connect(self.database) as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM {self.table}")
            return cursor.fetchall()
        