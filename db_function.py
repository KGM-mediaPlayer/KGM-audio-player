import os
import sqlite3
from PyQt5.QtCore import QStandardPaths
import sys # Import sys to check if running in bundle

# Removed the old database_dir and app_database global variables

def get_database_path():
    print("--- Getting Database Path ---") # Debug print
    # Check if running in a PyInstaller bundle
    if getattr(sys, 'frozen', False):
        print("Running in PyInstaller bundle.")
        # Use AppDataLocation for bundled app data
        data_dir = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        if not data_dir:
            print("Error: QStandardPaths.AppDataLocation returned empty!")
            # Fallback option if AppDataLocation fails (less ideal but might work)
            # Using a hidden folder in the user's home directory
            home_dir = os.path.expanduser("~")
            data_dir = os.path.join(home_dir, ".kgm_audio_player_data")
            print(f"Falling back to: {data_dir}")
    else:
        print("Running in standard Python environment.")
        # For development, you might want the db in a known location relative to the script
        # This helps when running directly with `python your_app.py`
        # We'll create a .dbs_dev folder next to the db_function.py file
        script_dir = os.path.dirname(__file__)
        data_dir = os.path.join(script_dir, '.dbs_dev')
        print(f"Using development path: {data_dir}")


    print(f"Base data directory determined: {data_dir}") # Print the chosen base directory

    # Define the application-specific subdirectory within the data directory
    # It's good practice to put app files in their own subfolder within AppData
    app_data_subdir = "KGM Audio Player"
    db_app_dir = os.path.join(data_dir, app_data_subdir)

    print(f"App data directory path: {db_app_dir}") # Print the final app data directory path

    if not os.path.exists(db_app_dir):
        print(f"App data directory does NOT exist. Attempting to create: {db_app_dir}") # Debug print
        try:
            # Create the directory and any necessary parent directories
            # mode 0o755 gives owner read/write/execute, group read/execute, others read/execute
            os.makedirs(db_app_dir, mode=0o755, exist_ok=True) # exist_ok=True prevents error if it suddenly exists
            print(f"Successfully created app data directory: {db_app_dir}") # Debug print
        except OSError as e:
            print(f"!!! CRITICAL ERROR: Failed to create app data directory {db_app_dir}: {e}")
            # If directory creation fails, we cannot proceed with database connection
            return None # Indicate failure


    # Define the full path to your database file inside the app directory
    database_file = os.path.join(db_app_dir, "kgm_audio_player.db") # Consistent filename

    print(f"Attempting to use database file at: {database_file}") # Final path before connection

    return database_file

def get_db_connection():
    print("--- Getting DB Connection ---") # Debug print
    db_path = get_database_path() # Get the determined path

    if not db_path: # Check if get_database_path returned None due to creation failure
         print("!!! CRITICAL ERROR: Cannot get database connection because the path is invalid or directory creation failed.")
         return None # Return None if the path is bad

    conn = None # Initialize connection variable
    print(f"Attempting sqlite3.connect to: {db_path}") # Debug print right before connecting
    try:
        conn = sqlite3.connect(db_path)
        print(f"Successfully connected to database at: {db_path}") # Debug print on success
        # Add this line if you want to enable foreign key support (usually a good idea)
        # conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        print(f"!!! CRITICAL SQLite connection error to {db_path}: {e}") # Debug print on failure
        # The caller (e.g., create_database_or_database_table) should ideally handle this failure.
        return None # Return None if connection fails
    except Exception as e: # Catch any other unexpected errors during connection
         print(f"!!! CRITICAL UNEXPECTED error during database connection to {db_path}: {e}")
         return None

# create database table
def create_database_or_database_table(table_name):
    conn = get_db_connection() # Use get_db_connection
    if conn: # Check if connection was successful
        try:
            print(f"Attempting to create/check table: {table_name}") # Debug print
            cursor = conn.cursor()
            if table_name == "favorites":
                 cursor.execute(f'''
                     CREATE TABLE IF NOT EXISTS {table_name} (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         song_path TEXT UNIQUE NOT NULL
                     )
                 ''')
            # Add other table creation logic here if needed for other tables

            conn.commit()
            print(f"Successfully created/checked table: {table_name}") # Debug print
        except sqlite3.Error as e:
            # This print is helpful for debugging the initial setup
            print(f"Database error during creation/check of table {table_name}: {e}")
        finally:
            conn.close()
    else:
        print(f"Skipping creation/check of table {table_name} because database connection failed.")

# ADD SONG TO DATABASE
def add_song_to_database(song, table='favorites'):
    conn = get_db_connection() # Use get_db_connection
    if conn: # Check if connection was successful
        try:
            print(f"Attempting to add song '{song}' to table '{table}'") # Debug print
            cursor = conn.cursor()
            # Use parameter binding correctly
            # INSERT OR IGNORE will prevent adding the same song_path multiple times
            cursor.execute(f"INSERT OR IGNORE INTO {table} (song_path) VALUES (?)", (song,)) # Use song_path
            conn.commit()
            print(f"Successfully added song '{song}' to table '{table}' (or it already existed).") # Debug print
        except sqlite3.Error as e:
            print(f"Database error adding song '{song}' to table '{table}': {e}")
        finally:
            conn.close()
    else:
        print(f"Skipping add song '{song}' to table '{table}' because database connection failed.")


def delete_song_from_database_table(song:str,table:str):
    conn = get_db_connection() # Use get_db_connection
    if conn: # Check if connection was successful
        try:
            print(f"Attempting to delete song '{song}' from table '{table}'") # Debug print
            cursor = conn.cursor()
            # Corrected SQL and using parameter binding
            cursor.execute(f"DELETE FROM {table} WHERE song_path = ?", (song,))
            deleted_rows = cursor.rowcount
            conn.commit()
            print(f"Successfully deleted {deleted_rows} instances of song '{song}' from table '{table}'.") # Debug print
        except sqlite3.Error as e:
            print(f"Database error deleting song '{song}' from table '{table}': {e}")
        finally:
            conn.close()
    else:
        print(f"Skipping delete song '{song}' from table '{table}' because database connection failed.")


def delete_all_song_from_database_table(table:str):
    conn = get_db_connection() # Use get_db_connection
    if conn: # Check if connection was successful
        try:
            print(f"Attempting to delete ALL songs from table '{table}'") # Debug print
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {table}")
            deleted_rows = cursor.rowcount
            conn.commit()
            print(f"Successfully deleted {deleted_rows} songs from table '{table}'.") # Debug print
        except sqlite3.Error as e:
            print(f"Database error deleting all songs from table '{table}': {e}")
        finally:
            conn.close()
    else:
        print(f"Skipping delete ALL songs from table '{table}' because database connection failed.")

# get all songs from database table
def fetch_all_songs_from_database_table(table:str):
    conn = get_db_connection() # Use get_db_connection
    data = [] # Initialize data list
    if conn: # Check if connection was successful
        try:
            print(f"Attempting to fetch all songs from table '{table}'") # Debug print
            cursor = conn.cursor()
            # Select the correct column name
            cursor.execute(f"SELECT song_path FROM {table}")
            song_data = cursor.fetchall()
            # Extract the first column from each row
            data = [song[0] for song in song_data]
            print(f"Successfully fetched {len(data)} songs from table '{table}'.") # Debug print
            return data
        except sqlite3.Error as e:
            print(f"Database error fetching songs from table '{table}': {e}")
            return [] # Return empty list in case of error
        finally:
            conn.close()
    else:
        print(f"Skipping fetch all songs from table '{table}' because database connection failed.")
        return [] # Return empty list if connection failed


# get all table from database
def get_playlist_tables():
    conn = get_db_connection() # Use get_db_connection
    tables = [] # Initialize tables list
    if conn: # Check if connection was successful
        try:
            print("Attempting to fetch all table names") # Debug print
            cursor = conn.cursor()
            # Select table names, excluding sqlite internal ones
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            table_names = cursor.fetchall()
            # Extract the table name from each row
            tables = [table_name[0] for table_name in table_names]
            print(f"Successfully fetched {len(tables)} table names: {tables}") # Debug print
            return tables
        except sqlite3.Error as e:
            print(f"Error fetching table names: {e}")
            return [] # Return empty list
        finally:
            conn.close()
    else:
        print("Skipping fetch table names because database connection failed.")
        return [] # Return empty list if connection failed


# Delete database tables
def delete_database_table(table:str):
    conn = get_db_connection() # Use get_db_connection
    if conn: # Check if connection was successful
        try:
            print(f"Attempting to delete database table: {table}") # Debug print
            cursor = conn.cursor()
            # Drop the specified table if it exists
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            conn.commit()
            print(f"Successfully deleted database table: {table}") # Debug print
        except sqlite3.Error as e:
            print(f"Database error deleting table {table}: {e}")
        finally:
            conn.close()
    else:
        print(f"Skipping delete table {table} because database connection failed.")