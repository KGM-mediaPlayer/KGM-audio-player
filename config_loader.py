import json
import os

CONFIG_FILE = "data/config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        config = {
            "music_folder": "",
            "favorites": [],
            "playlist": []
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
    else:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            # Add missing keys if needed
            config.setdefault("favorites", [])
            config.setdefault("playlist", [])
            return config

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
