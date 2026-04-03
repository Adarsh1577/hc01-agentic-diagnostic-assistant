import streamlit as st
import pandas as pd

from logic.timeline import build_timeline
from logic.outlier import detect_lactate_outlier
from agents.agents import (
    note_parser_agent,
    temporal_lab_mapper_agent,
    guideline_rag_agent,
    chief_synthesis_agent,
)

st.set_page_config(page_title="HC01 Diagnostic Risk Assistant", layout="wide")

st.title("HC01 - Agentic Diagnostic Risk Assistant")
st.subheader("ICU Complication Detection using Temporal Reasoning + Medical RAG")

# Load patient data
df = pd.read_csv("data/patient.csv")

# Section 1: Patient Snapshot
st.header("1. Patient Snapshot")
st.dataframe(df, use_container_width=True)

# Section 2: Timeline
st.header("2. Chronological ICU Timeline")
timeline = build_timeline("data/patient.csv")
for item in timeline:
    st.write("- " + item)

# Section 3: Note Parser Agent
st.header("3. Note Parser Agent Output")
note_signals = note_parser_agent(df)
if note_signals:
    for signal in note_signals:
        st.write("- " + signal)
else:
    st.write("No significant note-based warning signals found.")

# Section 4: Temporal Lab Mapper Agent
st.header("4. Temporal Lab Mapper Agent Output")
lab_trends = temporal_lab_mapper_agent(df)
if lab_trends:
    for trend in lab_trends:
        st.write("- " + trend)
else:
    st.write("No significant temporal lab trends found.")

# Section 5: Guideline Retrieval
st.header("5. Guideline RAG Evidence")
query = "lactate hypotension sepsis creatinine"
rag_results = guideline_rag_agent(query)

for item in rag_results:
    st.markdown(f"**Source:** {item['source']}")
    st.markdown(f"**Score:** {item['score']}")
    st.write(item["content"])
    st.markdown("---")

# Section 6: Outlier Detection
st.header("6. Outlier Detection")
lactate_values = df["lactate"].tolist()
outlier_result = detect_lactate_outlier(lactate_values)
st.write(f"**Outlier Flag:** {outlier_result[0]}")
st.write(f"**Message:** {outlier_result[1]}")

# Section 7: Final Diagnostic Risk Report
st.header("7. Final Diagnostic Risk Report")
final_report = chief_synthesis_agent(
    note_signals,
    lab_trends,
    rag_results,
    outlier_result
)

st.write(f"**Risk Level:** {final_report['risk_level']}")

st.subheader("Risk Signals")
for signal in final_report["signals"]:
    st.write("- " + signal)

st.subheader("Retrieved Guideline Evidence")
for item in final_report["guidelines"]:
    st.write(f"- {item['source']} (score: {item['score']})")

st.subheader("Safety Disclaimer")
st.warning(final_report["note"])