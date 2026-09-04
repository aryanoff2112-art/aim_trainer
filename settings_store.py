import json
import os

from settings import SETTINGS_FILE

DEFAULT_SETTINGS = {
    "crosshair_style": "cross",  
    "crosshair_size": 14,
    "crosshair_gap": 4,
    "crosshair_thickness": 2,
    "sensitivity": 1.0,
    "sound_enabled": True,
    "fps_cap": 60,      
    "fullscreen": False,
}

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return dict(DEFAULT_SETTINGS)
    try:
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_SETTINGS)

    merged = dict(DEFAULT_SETTINGS)
    merged.update(data)
    return merged

def save_settings(user_settings):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(user_settings, f, indent=2)
    except OSError as e:
        print(f"Warning: could not save settings ({e})")