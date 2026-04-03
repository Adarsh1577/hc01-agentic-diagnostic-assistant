def detect_lactate_outlier(values):
    if len(values) < 4:
        return False, "Not enough historical data to validate outlier against 3 prior readings."

    previous_three = values[-4:-1]
    latest_value = values[-1]

    avg_previous = sum(previous_three) / 3
    spread = max(previous_three) - min(previous_three)

    # Check if previous values are relatively consistent
    if spread <= 0.5:
        if latest_value > avg_previous * 1.8:
            return True, (
                f"Latest lactate value {latest_value} strongly contradicts the prior "
                f"three consistent readings {previous_three}. Probable lab anomaly; "
                f"recommend redraw confirmation before altering diagnosis."
            )

    return False, "No statistically suspicious lactate anomaly detected."