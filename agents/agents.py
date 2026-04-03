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

    diagnosis_status = "UPDATED_WITH_CURRENT_DATA"
    safety_note = "Decision-support only (not medical diagnosis)"

    # Twist 2: if outlier is detected, hold diagnosis revision
    if outlier[0]:
        diagnosis_status = "HELD_PENDING_REDRAW"
        safety_note = (
            "Potential lab anomaly detected. Diagnosis should not be updated "
            "solely on this value until redraw confirmation is received."
        )

    if score >= 5:
        risk = "HIGH"
    elif score >= 2:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return {
        "risk_level": risk,
        "signals": all_signals,
        "guidelines": rag_data,
        "outlier_flag": outlier[0],
        "outlier_msg": outlier[1],
        "score": score,
        "diagnosis_status": diagnosis_status,
        "note": safety_note
    }

def family_communication_agent(df, final_report):
    latest = df.iloc[-1]

    risk = final_report["risk_level"]
    outlier_flag = final_report["outlier_flag"]

    english_summary = (
        f"Over the last 12 hours, the patient has shown changes in temperature, blood pressure, "
        f"heart rate, and blood test results that suggest the medical team should watch the patient closely. "
        f"The current system assessment is {risk} risk. "
    )

    if risk == "HIGH":
        english_summary += "This means the patient may be getting sicker and needs close monitoring. "
    elif risk == "MEDIUM":
        english_summary += "This means there are some warning signs but not the most severe level. "
    else:
        english_summary += "This means the patient appears relatively stable right now. "

    if outlier_flag:
        english_summary += "A recent lab result looks inconsistent, so doctors may confirm it before making decisions."
    else:
        english_summary += "Current trends appear consistent for monitoring."

    hindi_summary = (
        f"पिछले 12 घंटों में मरीज की स्थिति में बदलाव देखे गए हैं। जोखिम स्तर {risk} है। "
    )

    if risk == "HIGH":
        hindi_summary += "स्थिति गंभीर हो सकती है, इसलिए ICU टीम को ध्यान देना होगा। "
    elif risk == "MEDIUM":
        hindi_summary += "कुछ चेतावनी संकेत हैं लेकिन स्थिति अत्यधिक गंभीर नहीं है। "
    else:
        hindi_summary += "मरीज अभी स्थिर दिख रहा है। "

    if outlier_flag:
        hindi_summary += "एक लैब रिपोर्ट असामान्य लग रही है, इसलिए दोबारा जांच की आवश्यकता हो सकती है।"
    else:
        hindi_summary += "रुझान अभी स्थिर हैं।"

    return {
        "english": english_summary,
        "regional": hindi_summary
    }