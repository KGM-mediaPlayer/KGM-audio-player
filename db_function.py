import os
import sqlite3

database_dir=os.path.join(os.getcwd(), '.dbs')
app_database= os.path.join(database_dir, 'app_db.db')

# create databse table
def create_database_or_database_table(table_name: str):
    connection =sqlite3.connect(app_database)
    cursor=connection.cursor()
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table_name}(song TEXT)""")
    connection.commit()
    connection.close()

# ADD SONG TO DATABASE
def add_song_to_database(song, table='favorites'):
    connection = sqlite3.connect(app_database)
    cursor = connection.cursor()
    cursor.execute(f"INSERT INTO {table} (song) VALUES (?)", (song,))
    connection.commit()
    connection.close()

def delete_song_from_database_table(song:str,table:str,):
        connection = sqlite3.connect(app_database)
        cursor = connection.cursor()
        cursor.execute(
             f""""
             DELETE FROM{table} favourites WHERE ROWID=(SELECT min(ROWID) FROM favourites WHERE song= '{song}');
             """
             )
        connection.commit()
        connection.close()

def delete_all_song_from_database_table(table:str,):
        connection = sqlite3.connect(app_database)
        cursor = connection.cursor()
        cursor.execute(f"DELETE FROM {table}")
        connection.commit()
        connection.close()

# get all songs from database table
def fetch_all_songs_from_database_table(table:str,):
        connection = sqlite3.connect(app_database)
        cursor = connection.cursor()
        cursor.execute(f"SELECT song FROM {table}")
        song_data=cursor.fetchall()
        data=[song[0] for song in song_data]
        connection.commit()
        connection.close()

        return data

# get all table from database
def get_playlist_tables():
    try:
          connection=sqlite3.connect(app_database)
          cursor=connection.cursor()
          cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
          table_names=cursor.fetchall()
          tables=[table_name[1] for table_name in table_names]

          return tables
    except sqlite3.Error as e:
          print(f"Error fetching table names: {e}")
    finally:
          connection.close()
    
    # Delete databse tables
def delete_database_table(table:str):
        connection = sqlite3.connect(app_database)
        cursor = connection.cursor()
        cursor.execute(f"DROP TABLE {table}")
        connection.commit()
        connection.close()