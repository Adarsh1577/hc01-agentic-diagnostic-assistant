import pandas as pd
from agents.agents import (
    note_parser_agent,
    temporal_lab_mapper_agent,
    guideline_rag_agent,
    chief_synthesis_agent,
)
from logic.outlier import detect_lactate_outlier

df = pd.read_csv("data/patient.csv")

print("=== NOTE AGENT ===")
note = note_parser_agent(df)
print(note)

print("\n=== LAB AGENT ===")
lab = temporal_lab_mapper_agent(df)
print(lab)

print("\n=== RAG AGENT ===")
rag = guideline_rag_agent("lactate hypotension sepsis creatinine")
for item in rag:
    print(item["source"], item["score"])

print("\n=== FINAL AGENT ===")
outlier = detect_lactate_outlier(df["lactate"].tolist())
final = chief_synthesis_agent(note, lab, rag, outlier)
print(final)