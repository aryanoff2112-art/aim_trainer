import json
import os
import time

from settings import STATS_FILE, MAX_SESSION_HISTORY

DEFAULT_STATS = {
    "high_scores": {},      
    "best_precision": 0,
    "best_target_accuracy": 0,
    "best_speed": 0,
    "best_reaction_ms": None,
    "best_combo": 0,
    "total_hits": 0,
    "total_clicks": 0,
    "total_play_time": 0,
    "games_played": 0,
    "achievements": [],      
    "sessions": [],         
}

def load_stats():
    if not os.path.exists(STATS_FILE):
        return dict(DEFAULT_STATS)
    try:
        with open(STATS_FILE, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_STATS)

    merged = dict(DEFAULT_STATS)
    merged.update(data)
    return merged

def save_stats(stats):
    try:
        with open(STATS_FILE, "w") as f:
            json.dump(stats, f, indent=2)
    except OSError as e:
        print(f"Warning: could not save stats ({e})")

def record_session(stats, session):
    """session is the result dict returned by GameMode._build_result():
    mode, difficulty, score, hits, clicks, misses, precision,
    target_accuracy, speed, avg_reaction_ms, best_reaction_ms, combo,
    duration, plus any mode-specific extras (e.g. tracking_pct)."""

    key = f"{session['mode']}:{session['difficulty']}"
    stats["high_scores"][key] = max(stats["high_scores"].get(key, 0), session["score"])
    stats["best_precision"] = max(stats["best_precision"], session["precision"])
    stats["best_target_accuracy"] = max(stats["best_target_accuracy"], session["target_accuracy"])
    stats["best_speed"] = max(stats["best_speed"], session["speed"])
    stats["best_combo"] = max(stats["best_combo"], session["combo"])

    if session["best_reaction_ms"] is not None:
        if stats["best_reaction_ms"] is None or session["best_reaction_ms"] < stats["best_reaction_ms"]:
            stats["best_reaction_ms"] = session["best_reaction_ms"]

    stats["total_hits"] += session["hits"]
    stats["total_clicks"] += session["clicks"]
    stats["total_play_time"] += session["duration"]
    stats["games_played"] += 1

    entry = dict(session)
    entry["date"] = time.strftime("%Y-%m-%d %H:%M")
    stats["sessions"].append(entry)
    stats["sessions"] = stats["sessions"][-MAX_SESSION_HISTORY:]

    return stats