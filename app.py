import streamlit as st
import pandas as pd
from io import StringIO

from logic.timeline import build_timeline
from logic.outlier import detect_lactate_outlier

from agents.agents import (
    note_parser_agent,
    temporal_lab_mapper_agent,
    guideline_rag_agent,
    chief_synthesis_agent,
    family_communication_agent
)

st.set_page_config(page_title="HC01 Diagnostic Risk Assistant", layout="wide")

st.markdown("""
<style>
.main {
    padding-top: 1rem;
}
div[data-testid="stMetric"] {
    background-color: #111827;
    border: 1px solid #374151;
    padding: 12px;
    border-radius: 12px;
}
div[data-testid="stMetricLabel"] {
    font-size: 16px;
}
div[data-testid="stMetricValue"] {
    font-size: 24px;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

st.title("HC01 - Agentic Diagnostic Risk Assistant")
st.subheader("ICU Complication Detection using Temporal Reasoning + Medical RAG")

st.info(
    "This prototype analyzes ICU patient trends over time, retrieves relevant clinical guidance, "
    "and generates a diagnostic risk summary using a lightweight multi-agent workflow."
)

st.sidebar.title("Project Summary")
st.sidebar.write("Domain: Healthcare & Accessibility")
st.sidebar.write("Problem Code: HC01")
st.sidebar.write("Focus: ICU Complication Detection")
st.sidebar.write("Core Modules:")
st.sidebar.write("- Temporal Reasoning")
st.sidebar.write("- Outlier Detection")
st.sidebar.write("- Medical RAG")
st.sidebar.write("- Multi-Agent Synthesis")
st.sidebar.write("- Family Communication Output")

# -----------------------------
# INPUT MODE
# -----------------------------
st.header("Input Mode")
input_mode = st.radio(
    "Choose data source",
    ["Preloaded Patient Case", "Manual Entry"]
)

def get_manual_dataframe():
    st.subheader("Manual Patient Input")
    st.caption("Enter 4 timepoints as comma-separated values.")

    times = st.text_input("Time", "08:00,12:00,16:00,20:00")
    heart_rate = st.text_input("Heart Rate", "90,100,110,120")
    bp_systolic = st.text_input("BP Systolic", "120,110,100,90")
    bp_diastolic = st.text_input("BP Diastolic", "80,72,66,58")
    temp_f = st.text_input("Temperature (F)", "98.9,100.1,101.0,102.0")
    wbc = st.text_input("WBC", "10.5,12.8,15.0,17.2")
    lactate = st.text_input("Lactate", "1.2,1.8,2.6,3.1")
    creatinine = st.text_input("Creatinine", "0.9,1.0,1.3,1.6")
    spo2 = st.text_input("SpO2", "98,96,94,92")
    notes = st.text_area(
        "Clinical Notes (4 notes, one per line)",
        "Patient alert, mild fatigue.\nFever noted, possible infection.\nIncreased respiratory effort, hypotension emerging.\nAltered mental status, concern for sepsis progression."
    )

    if st.button("Generate Analysis from Manual Input"):
        note_lines = [x.strip() for x in notes.split("\n") if x.strip()]

        df_manual = pd.DataFrame({
            "time": [x.strip() for x in times.split(",")],
            "heart_rate": [int(x.strip()) for x in heart_rate.split(",")],
            "bp_systolic": [int(x.strip()) for x in bp_systolic.split(",")],
            "bp_diastolic": [int(x.strip()) for x in bp_diastolic.split(",")],
            "temp_f": [float(x.strip()) for x in temp_f.split(",")],
            "wbc": [float(x.strip()) for x in wbc.split(",")],
            "lactate": [float(x.strip()) for x in lactate.split(",")],
            "creatinine": [float(x.strip()) for x in creatinine.split(",")],
            "spo2": [int(x.strip()) for x in spo2.split(",")],
            "note": note_lines
        })

        return df_manual

    return None

if input_mode == "Preloaded Patient Case":
    patient_file = st.selectbox(
        "Select patient case",
        ["data/patient.csv", "data/patient_case_2.csv", "data/patient_outlier_case.csv"]
    )
    df = pd.read_csv(patient_file)
    timeline = build_timeline(patient_file)
else:
    df = get_manual_dataframe()
    if df is not None:
        temp_buffer = StringIO()
        df.to_csv(temp_buffer, index=False)
        temp_buffer.seek(0)

        # build manual timeline directly
        timeline = []
        for _, row in df.iterrows():
            timeline.append(
                f"At {row['time']}, HR {row['heart_rate']} bpm, "
                f"BP {row['bp_systolic']}/{row['bp_diastolic']}, "
                f"Temp {row['temp_f']} F, WBC {row['wbc']}, "
                f"Lactate {row['lactate']}, Creatinine {row['creatinine']}."
            )
    else:
        st.warning("Please enter manual values and click 'Generate Analysis from Manual Input'.")
        st.stop()

# -----------------------------
# MAIN PIPELINE
# -----------------------------
query = st.text_input(
    "Enter guideline retrieval query",
    value="lactate hypotension sepsis creatinine"
)

note_signals = note_parser_agent(df)
lab_trends = temporal_lab_mapper_agent(df)
rag_results = guideline_rag_agent(query)
lactate_values = df["lactate"].tolist()
outlier_result = detect_lactate_outlier(lactate_values)
final_report = chief_synthesis_agent(
    note_signals,
    lab_trends,
    rag_results,
    outlier_result
)
family_summary = family_communication_agent(df, final_report)

# -----------------------------
# TABS
# -----------------------------
tab1, tab2 = st.tabs(["Clinical Dashboard", "Family Communication"])

with tab1:
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Risk Level", final_report["risk_level"])

    with col2:
        st.metric("Signals Detected", len(final_report["signals"]))

    with col3:
        st.metric("Outlier Flag", "Yes" if final_report["outlier_flag"] else "No")

    with col4:
        st.metric("Guidelines Retrieved", len(final_report["guidelines"]))

    st.divider()
    st.header("1. Patient Snapshot")
    st.dataframe(df, width="stretch")

    st.divider()
    st.header("2. Chronological ICU Timeline")
    for item in timeline:
        st.write("- " + item)

    st.divider()
    st.header("3. Final Diagnostic Risk Report")

    if final_report["risk_level"] == "HIGH":
        st.error(f"Risk Level: {final_report['risk_level']}")
    elif final_report["risk_level"] == "MEDIUM":
        st.warning(f"Risk Level: {final_report['risk_level']}")
    else:
        st.success(f"Risk Level: {final_report['risk_level']}")

    st.write(f"Diagnosis Status: {final_report['diagnosis_status']}")
    st.write(f"Computed Score: {final_report['score']}")

    st.subheader("Risk Signals")
    for signal in final_report["signals"]:
        st.write("- " + signal)

    st.subheader("Retrieved Guideline Evidence")
    for item in final_report["guidelines"]:
        st.write(f"- {item['source']} (score: {item['score']})")

    st.subheader("Safety Disclaimer")
    st.warning(final_report["note"])

    st.header("4. Note Parser Agent Output")
    if note_signals:
        for signal in note_signals:
            st.write("- " + signal)
    else:
        st.write("No significant note-based warning signals found.")

    st.header("5. Temporal Lab Mapper Agent Output")
    if lab_trends:
        for trend in lab_trends:
            st.write("- " + trend)
    else:
        st.write("No significant temporal lab trends found.")

    st.header("6. Guideline RAG Evidence")
    st.caption(f"Guideline retrieval query used: {query}")

    for item in rag_results:
        st.markdown(f"**Source:** {item['source']}")
        st.markdown(f"**Score:** {item['score']}")
        st.write(item["content"])
        st.markdown("---")

    st.header("7. Outlier Detection")
    st.write(f"Outlier Flag: {outlier_result[0]}")
    st.write(f"Message: {outlier_result[1]}")

    st.divider()
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

    st.divider()
    st.header("8. System Architecture")
    st.code("""
Patient CSV / Manual Input + Clinical Notes
        ↓
Timeline Builder + Outlier Detector
        ↓
Note Parser Agent + Temporal Lab Mapper Agent
        ↓
Guideline RAG Agent
        ↓
Chief Synthesis Agent
        ↓
Diagnostic Risk Report
""")

    st.header("9. Future Upgrade Path")
    st.write("- Integrate real ICU datasets such as MIMIC-III or MIMIC-IV demo records")
    st.write("- Replace keyword retrieval with vector database based semantic retrieval")
    st.write("- Upgrade agents to LLM-based orchestration")
    st.write("- Add real-time streaming patient monitoring and clinician alerting")
    st.write("- Improve note understanding using advanced clinical NLP models")

with tab2:
    st.divider()
    st.header("Family Communication Summary")
    st.info("This section explains the patient's condition in a more compassionate and non-technical way.")

    selected_language = st.selectbox(
        "Select family communication language",
        ["English", "Hindi", "Marathi", "Tamil", "Telugu"]
    )

    st.subheader(selected_language)
    st.success(family_summary[selected_language])

