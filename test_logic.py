from logic.timeline import build_timeline
from logic.outlier import detect_lactate_outlier
import pandas as pd

print("=== TIMELINE ===")
timeline = build_timeline("data/patient.csv")
for item in timeline:
    print(item)

print("\n=== OUTLIER CHECK ===")
df = pd.read_csv("data/patient.csv")
lactate_values = df["lactate"].tolist()
print(detect_lactate_outlier(lactate_values))