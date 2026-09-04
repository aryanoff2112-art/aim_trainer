ACHIEVEMENTS = [
    {
        "id": "first_blood",
        "name": "First Blood",
        "desc": "Hit your first target",
        "check": lambda result, stats: stats["total_hits"] >= 1,
    },
    {
        "id": "sharpshooter",
        "name": "Sharpshooter",
        "desc": "95%+ precision in a session",
        "check": lambda result, stats: result["precision"] >= 95,
    },
    {
        "id": "lightning",
        "name": "Lightning",
        "desc": "Sub-200ms reaction time",
        "check": lambda result, stats: (
            result["best_reaction_ms"] is not None and result["best_reaction_ms"] < 200
        ),
    },
    {
        "id": "combo_master",
        "name": "Combo Master",
        "desc": "Land a 25-hit combo",
        "check": lambda result, stats: result["combo"] >= 25,
    },
    {
        "id": "survivor",
        "name": "Survivor",
        "desc": "Survive 60+ seconds on Hard Survival",
        "check": lambda result, stats: (
            result["mode"] == "Survival" and result["difficulty"] == "Hard" and result["duration"] >= 60
        ),
    },
    {
        "id": "aim_god",
        "name": "Aim God",
        "desc": "Score 5000+ in a single session",
        "check": lambda result, stats: result["score"] >= 5000,
    },
]

def check_achievements(result, stats):
    """Evaluates ACHIEVEMENTS against the latest session + updated totals.
    Mutates stats['achievements'] and returns the list of newly unlocked
    achievement dicts (empty if none)."""
    unlocked = set(stats.get("achievements", []))
    newly = []
    for ach in ACHIEVEMENTS:
        if ach["id"] not in unlocked and ach["check"](result, stats):
            unlocked.add(ach["id"])
            newly.append(ach)
    stats["achievements"] = sorted(unlocked)
    return newly