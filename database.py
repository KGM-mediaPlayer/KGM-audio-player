import sqlite3

DB_NAME = "music_library.db"

def create_tables():
    connect = sqlite3.connect(DB_NAME)
    cursor = connect.cursor()

    # Corrected schema with consistent column names
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS music_library (
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            album TEXT NOT NULL,
            path TEXT NOT NULL UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS playlist (
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            album TEXT NOT NULL,
            path TEXT NOT NULL UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favourites (
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            album TEXT NOT NULL,
            path TEXT NOT NULL UNIQUE
        )
    ''')

    connect.commit()
    connect.close()

# Add song to a specified table
def add_song(table_name, title, artist, album, path):
    connect = sqlite3.connect(DB_NAME)
    cursor = connect.cursor()

    query = f'''
        INSERT OR IGNORE INTO {table_name} (title, artist, album, path)
        VALUES (?, ?, ?, ?)
    '''
    cursor.execute(query, (title, artist, album, path))
    connect.commit()
    connect.close()

# Remove song by title
def remove_song(table_name, title):
    connect = sqlite3.connect(DB_NAME)
    cursor = connect.cursor()

    query = f'''
        DELETE FROM {table_name} WHERE path= ?
    '''
    cursor.execute(query, (title,))
    connect.commit()
    connect.close()

def remove_all_songs(table_name):
    connect = sqlite3.connect(DB_NAME)
    cursor = connect.cursor()

    query = f'''
        DELETE FROM {table_name}
    '''
    cursor.execute(query)
    connect.commit()
    connect.close()

# Get all songs from a table
def get_all_songs(table_name):
    connect = sqlite3.connect(DB_NAME)
    cursor = connect.cursor()

    query = f'''
        SELECT * FROM {table_name}
    '''
    cursor.execute(query)
    songs = cursor.fetchall()
    connect.close()
    return songs

# check if a song exists in a table
def song_exists(table_name, title):
    connect = sqlite3.connect(DB_NAME)
    cursor = connect.cursor()

    query = f'''
        SELECT * FROM {table_name} WHERE path= ?
    '''
    cursor.execute(query, (title,))
    song = cursor.fetchone()
    connect.close()
    return song is not None

    #song exist by name (for track info)

def get_song_by_filepath(table_name, file_path):
    import sqlite3
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    query = f'''
        SELECT title, artist, album, path FROM {table_name} WHERE path = ?
    '''
    cursor.execute(query, (file_path,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            'title': row[0],
            'artist': row[1],
            'album': row[2],
            'path': row[3]
        }
    return None



# EQ presets
def create_eq_table():
    conn = sqlite3.connect('music_library.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS equalizer_presets (
            name TEXT PRIMARY KEY,
            band_60 REAL,
            band_170 REAL,
            band_310 REAL,
            band_600 REAL,
            band_1000 REAL,
            band_3000 REAL,
            band_6000 REAL,
            band_12000 REAL,
            band_14000 REAL,
            band_16000 REAL
        );
    ''')
    conn.commit()
    conn.close()

def save_eq_preset(name, values):
    conn = sqlite3.connect('music_library.db')
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO equalizer_presets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, *values))
    conn.commit()
    conn.close()

def get_eq_presets():
    conn = sqlite3.connect('music_library.db')
    c = conn.cursor()
    c.execute("SELECT * FROM equalizer_presets")
    rows = c.fetchall()
    conn.close()
    return {row[0]: row[1:] for row in rows}
