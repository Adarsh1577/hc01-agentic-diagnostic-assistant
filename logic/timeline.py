import pandas as pd

# Build a chronological summary to show ICU deterioration over time
def build_timeline(file_path):
    df = pd.read_csv(file_path)
    timeline = []

    for _, row in df.iterrows():
        entry = (
            f"At {row['time']}, HR {row['heart_rate']} bpm, "
            f"BP {row['bp_systolic']}/{row['bp_diastolic']}, "
            f"Temp {row['temp_f']} F, WBC {row['wbc']}, "
            f"Lactate {row['lactate']}, Creatinine {row['creatinine']}."
        )
        timeline.append(entry)

    return timeline