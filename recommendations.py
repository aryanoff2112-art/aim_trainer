def recommend_training(result):
    """Looks at one session's numbers and names the weakest area plus a
    mode that targets it. Returns (weak_area_label, recommended_mode, text)."""
    precision = result.get("precision", 100)
    target_accuracy = result.get("target_accuracy", 100)
    avg_reaction = result.get("avg_reaction_ms")

    reaction_score = 100 if avg_reaction is None else max(0, 100 - (avg_reaction - 150) / 4)

    scores = {
        "precision (click accuracy)": (precision, "Precision"),
        "target tracking (targets missed)": (target_accuracy, "Tracking"),
        "reaction speed": (reaction_score, "Reaction"),
    }
    weakest_label, (weakest_value, recommended_mode) = min(scores.items(), key=lambda kv: kv[1][0])

    text = f"Your weakest area was {weakest_label} — try {recommended_mode} mode next."
    return weakest_label, recommended_mode, text