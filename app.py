import streamlit as st
import pandas as pd

from logic.timeline import build_timeline
from logic.outlier import detect_lactate_outlier

from agents.agents import (
    note_parser_agent,
    temporal_lab_mapper_agent,
    guideline_rag_agent,
    chief_synthesis_agent
)

# Page setup
st.set_page_config(page_title="HC01 Diagnostic Risk Assistant", layout="wide")

st.title("HC01 - Agentic Diagnostic Risk Assistant")
st.subheader("ICU Complication Detection using Temporal Reasoning + Medical RAG")

st.info(
    "This prototype analyzes ICU patient trends over time, retrieves relevant clinical guidance, "
    "and generates a diagnostic risk summary using a lightweight multi-agent workflow."
)

# Sidebar
st.sidebar.title("Project Summary")
st.sidebar.write("Domain: Healthcare & Accessibility")
st.sidebar.write("Problem Code: HC01")
st.sidebar.write("Focus: ICU Complication Detection")
st.sidebar.write("Core Modules:")
st.sidebar.write("- Temporal Reasoning")
st.sidebar.write("- Outlier Detection")
st.sidebar.write("- Medical RAG")
st.sidebar.write("- Multi-Agent Synthesis")

# -----------------------------
# SELECT PATIENT CASE
# -----------------------------
patient_file = st.selectbox(
    "Select patient case",
    ["data/patient.csv", "data/patient_case_2.csv"]
)

df = pd.read_csv(patient_file)

# -----------------------------
# SECTION 1: SNAPSHOT
# -----------------------------
st.header("1. Patient Snapshot")
st.dataframe(df, width="stretch")

# -----------------------------
# SECTION 2: TIMELINE
# -----------------------------
st.header("2. Chronological ICU Timeline")
timeline = build_timeline(patient_file)

for item in timeline:
    st.write("- " + item)

# -----------------------------
# SECTION 3: NOTE PARSER
# -----------------------------
st.header("3. Note Parser Agent Output")
note_signals = note_parser_agent(df)

if note_signals:
    for signal in note_signals:
        st.write("- " + signal)
else:
    st.write("No significant note-based warning signals found.")

# -----------------------------
# SECTION 4: LAB MAPPER
# -----------------------------
st.header("4. Temporal Lab Mapper Agent Output")
lab_trends = temporal_lab_mapper_agent(df)

if lab_trends:
    for trend in lab_trends:
        st.write("- " + trend)
else:
    st.write("No significant temporal lab trends found.")

# -----------------------------
# SECTION 5: RAG
# -----------------------------
st.header("5. Guideline RAG Evidence")

query = st.text_input(
    "Enter guideline retrieval query",
    value="lactate hypotension sepsis creatinine"
)

st.caption(f"Guideline retrieval query used: {query}")

rag_results = guideline_rag_agent(query)

for item in rag_results:
    st.markdown(f"**Source:** {item['source']}")
    st.markdown(f"**Score:** {item['score']}")
    st.write(item["content"])
    st.markdown("---")

# -----------------------------
# SECTION 6: OUTLIER
# -----------------------------
st.header("6. Outlier Detection")

lactate_values = df["lactate"].tolist()
outlier_result = detect_lactate_outlier(lactate_values)

st.write(f"Outlier Flag: {outlier_result[0]}")
st.write(f"Message: {outlier_result[1]}")

# -----------------------------
# SECTION 7: FINAL REPORT
# -----------------------------
st.header("7. Final Diagnostic Risk Report")

final_report = chief_synthesis_agent(
    note_signals,
    lab_trends,
    rag_results,
    outlier_result
)

if final_report["risk_level"] == "HIGH":
    st.error(f"Risk Level: {final_report['risk_level']}")
elif final_report["risk_level"] == "MEDIUM":
    st.warning(f"Risk Level: {final_report['risk_level']}")
else:
    st.success(f"Risk Level: {final_report['risk_level']}")

st.subheader("Risk Signals")
for signal in final_report["signals"]:
    st.write("- " + signal)

st.subheader("Retrieved Guideline Evidence")
for item in final_report["guidelines"]:
    st.write(f"- {item['source']} (score: {item['score']})")

st.subheader("Safety Disclaimer")
st.warning(final_report["note"])

# -----------------------------
# SECTION 8: EXPLAINABILITY
# -----------------------------
st.subheader("Why this result?")
st.write(
    "The system generated this risk level by combining note-based signals, "
    "temporal lab trends, retrieved guideline evidence, and anomaly detection logic."
)

st.subheader("Clinical Interpretation")
st.write(
    "This case shows worsening ICU trends such as rising lactate, rising WBC, "
    "renal stress indicators, and falling blood pressure, suggesting possible "
    "early sepsis progression or organ dysfunction."
)

# -----------------------------
# SECTION 9: ARCHITECTURE
# -----------------------------
st.header("8. System Architecture")

st.code("""
Patient CSV + Clinical Notes
    ↓
Timeline Builder + Outlier Detector
    ↓
Note Parser Agent + Temporal Lab Mapper Agent
    ↓
Guideline RAG Agent
    ↓
Chief Synthesis Agent
    ↓
Final Diagnostic Risk Report
""")

# -----------------------------
# SECTION 10: FUTURE
# -----------------------------
st.header("9. Future Upgrade Path")

st.write("- Integrate real ICU datasets such as MIMIC-III or MIMIC-IV demo records")
st.write("- Replace keyword retrieval with vector database based semantic retrieval")
st.write("- Upgrade agents to LLM-based orchestration")
st.write("- Add real-time streaming patient monitoring and clinician alerting")
st.write("- Improve note understanding using advanced clinical NLP models")