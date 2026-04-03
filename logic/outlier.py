# Detect whether the latest lactate value rises unusually compared to previous values
def detect_lactate_outlier(values):
    if len(values) < 2:
        return False, "Not enough data to detect outlier."

    previous_values = values[:-1]
    latest_value = values[-1]
    average_previous = sum(previous_values) / len(previous_values)

    if latest_value > average_previous * 1.3:
        return True, (
            f"Latest lactate value {latest_value} is significantly above "
            f"the previous average of {average_previous:.2f}."
        )

    return False, "No significant lactate outlier detected."