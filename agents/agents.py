from rag.retrieve import retrieve_guidelines

# Extract warning signals from the latest clinical note
def note_parser_agent(df):
    all_notes = " ".join(df["note"].astype(str)).lower()
    signals = []

    if "fever" in all_notes:
        signals.append("Fever present in notes")
    if "infection" in all_notes:
        signals.append("Possible infection mentioned")
    if "hypotension" in all_notes:
        signals.append("Hypotension risk mentioned")
    if "mental confusion" in all_notes or "altered mental" in all_notes:
        signals.append("Altered mental state mentioned")

    return signals


# Track major changes in time-series clinical values
def temporal_lab_mapper_agent(df):
    trends = []

    lactate_change = df["lactate"].iloc[-1] - df["lactate"].iloc[0]
    wbc_change = df["wbc"].iloc[-1] - df["wbc"].iloc[0]
    creatinine_change = df["creatinine"].iloc[-1] - df["creatinine"].iloc[0]
    bp_drop = df["bp_systolic"].iloc[0] - df["bp_systolic"].iloc[-1]

    if lactate_change >= 1.0:
        trends.append("Lactate rising significantly")
    if wbc_change >= 3.0:
        trends.append("WBC rising significantly")
    if creatinine_change >= 0.3:
        trends.append("Creatinine rising significantly")
    if bp_drop >= 15:
        trends.append("BP dropping significantly")

    return trends


# Retrieve guideline evidence
def guideline_rag_agent(query):
    return retrieve_guidelines(query)


# Combine all results into a final risk report
def chief_synthesis_agent(note_signals, lab_trends, rag_data, outlier):
    all_signals = note_signals + lab_trends

    score = len(note_signals) + len(lab_trends)

    if outlier[0]:
        score += 1

    if score >= 5:
        risk = "HIGH"
    elif score >= 2:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    safety_note = "Decision-support only (not medical diagnosis)"

    if outlier[0]:
        safety_note = (
            "Potential lab anomaly detected. Diagnosis should not be updated "
            "solely on this value until redraw confirmation is received."
        )

    return {
        "risk_level": risk,
        "signals": all_signals,
        "guidelines": rag_data,
        "outlier_flag": outlier[0],
        "outlier_msg": outlier[1],
        "score": score,
        "note": safety_note
    }