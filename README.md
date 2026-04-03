# HC01 - Agentic Diagnostic Risk Assistant

## Problem Statement
ICU patients generate fragmented clinical data across time, including lab values, vital signs, and unstructured clinical notes. Early deterioration patterns such as sepsis may be missed because these signals are not always synthesized together in real time.

## Our Solution
We built a lightweight multi-agent clinical decision-support prototype that:
- reads ICU patient data
- builds a chronological progression timeline
- extracts warning signals from notes
- detects temporal lab trends and anomalies
- retrieves relevant clinical guideline evidence
- generates a final diagnostic risk report

## Core Modules
- Note Parser Agent
- Temporal Lab Mapper Agent
- Guideline RAG Agent
- Chief Synthesis Agent
- Outlier Detection Module
- Streamlit Frontend

## Key Features
- Temporal reasoning over ICU data
- Lightweight medical RAG
- Multi-agent synthesis
- Safety-aware outlier detection
- Interactive patient case selection
- Explainability through result interpretation and system architecture

## Dataset
Current version uses simulated ICU patient trajectories.

Future scope:
- Integrate MIMIC-III / MIMIC-IV demo ICU records

## Tech Stack
- Python
- Pandas
- Streamlit
- Rule-based multi-agent logic
- Lightweight retrieval-based RAG
- Git / GitHub

## How to Run
```bash
pip install -r requirements.txt
streamlit run app.py