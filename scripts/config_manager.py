import os
import json
from scripts.constants import CONFIG_FILE

def load_config():
    default_config = {"theme_index": 0, "high_score": 0, "graphics_mode": "MINIMAL", "volume": 2}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                if "volume" not in config: 
                    config["volume"] = 2
                return config
        except Exception:
            return default_config
    else:
        save_config(default_config["theme_index"], default_config["high_score"], default_config["graphics_mode"], default_config["volume"])
        return default_config

def save_config(theme_index, high_score, graphics_mode, volume):
    data = {
        "theme_index": theme_index,
        "high_score": high_score,
        "graphics_mode": graphics_mode,
        "volume": volume
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)