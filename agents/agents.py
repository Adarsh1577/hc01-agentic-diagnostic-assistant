from rag.retrieve import retrieve_guidelines

# Extract warning signals from the latest clinical note
def note_parser_agent(df):
    latest = df["note"].iloc[-1].lower()
    signals = []

    if "fever" in latest:
        signals.append("Fever present")
    if "infection" in latest:
        signals.append("Possible infection")
    if "hypotension" in latest:
        signals.append("Hypotension risk")
    if "mental" in latest:
        signals.append("Altered mental state")

    return signals


# Track major changes in time-series clinical values
def temporal_lab_mapper_agent(df):
    trends = []

    if df["lactate"].iloc[-1] > df["lactate"].iloc[0]:
        trends.append("Lactate rising")
    if df["wbc"].iloc[-1] > df["wbc"].iloc[0]:
        trends.append("WBC rising")
    if df["creatinine"].iloc[-1] > df["creatinine"].iloc[0]:
        trends.append("Creatinine rising")
    if df["bp_systolic"].iloc[-1] < df["bp_systolic"].iloc[0]:
        trends.append("BP dropping")

    return trends


# Retrieve guideline evidence
def guideline_rag_agent(query):
    return retrieve_guidelines(query)


# Combine all results into a final risk report
def chief_synthesis_agent(note_signals, lab_trends, rag_data, outlier):
    all_signals = note_signals + lab_trends

    risk = "LOW"
    if len(all_signals) >= 4:
        risk = "HIGH"
    elif len(all_signals) >= 2:
        risk = "MEDIUM"

    return {
        "risk_level": risk,
        "signals": all_signals,
        "guidelines": rag_data,
        "outlier_flag": outlier[0],
        "outlier_msg": outlier[1],
        "note": "Decision-support only (not medical diagnosis)"
    }