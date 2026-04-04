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

    translations = {
        "English": english_summary,
        "Hindi": hindi_summary,
        "Marathi": (
            f"गेल्या 12 तासांत रुग्णाच्या प्रकृतीत काही बदल दिसून आले आहेत. सिस्टीमनुसार जोखीम पातळी {risk} आहे. "
            + (
                "याचा अर्थ रुग्णाची स्थिती गंभीर होऊ शकते आणि ICU टीमने बारकाईने लक्ष ठेवणे आवश्यक आहे. "
                if risk == "HIGH"
                else "याचा अर्थ काही इशारे दिसत आहेत, पण परिस्थिती सर्वात गंभीर स्तरावर नाही. "
                if risk == "MEDIUM"
                else "याचा अर्थ सध्या रुग्ण तुलनेने स्थिर दिसत आहे. "
            )
            + (
                "अलीकडील एक लॅब रिपोर्ट आधीच्या निकालांशी जुळत नाही, त्यामुळे डॉक्टर पुन्हा तपासणी करू शकतात."
                if outlier_flag
                else "आत्तापर्यंतचे संकेत निरीक्षणासाठी स्थिर दिसत आहेत."
            )
        ),
        "Tamil": (
            f"கடந்த 12 மணிநேரங்களில் நோயாளியின் நிலைமையில் சில மாற்றங்கள் காணப்பட்டுள்ளன. கணினி மதிப்பீட்டின்படி ஆபத்து நிலை {risk} ஆகும். "
            + (
                "இதன் அர்த்தம் நோயாளியின் நிலை மோசமடையக்கூடும் என்பதால் ICU குழு நெருக்கமாக கவனிக்க வேண்டும். "
                if risk == "HIGH"
                else "இதன் அர்த்தம் சில எச்சரிக்கை அறிகுறிகள் உள்ளன, ஆனால் இது மிகவும் கடுமையான நிலை அல்ல. "
                if risk == "MEDIUM"
                else "இதன் அர்த்தம் தற்போது நோயாளர் ஒப்பீட்டளவில் நிலையாக உள்ளார். "
            )
            + (
                "ஒரு சமீபத்திய லேப் முடிவு முந்தைய முடிவுகளுடன் பொருந்தவில்லை; அதனால் மருத்துவர்கள் அதை மீண்டும் சரிபார்க்கலாம்."
                if outlier_flag
                else "தற்போதைய மாற்றங்கள் தொடர்ந்தும் கண்காணிப்பதற்கு போதுமான அளவில் நிலையாக உள்ளன."
            )
        ),
        "Telugu": (
            f"గత 12 గంటల్లో రోగి పరిస్థితిలో కొన్ని మార్పులు కనిపించాయి. సిస్టమ్ ప్రకారం ప్రమాద స్థాయి {risk}. "
            + (
                "దీనర్థం రోగి పరిస్థితి మరింత విషమించవచ్చు కాబట్టి ICU బృందం దగ్గరగా గమనించాలి. "
                if risk == "HIGH"
                else "దీనర్థం కొన్ని హెచ్చరిక సంకేతాలు ఉన్నాయి కానీ ఇది అత్యంత ప్రమాద స్థాయి కాదు. "
                if risk == "MEDIUM"
                else "దీనర్థం ప్రస్తుతం రోగి తక్కువ ప్రమాదంతో స్థిరంగా ఉన్నట్లు కనిపిస్తోంది. "
            )
            + (
                "ఇటీవలి ల్యాబ్ ఫలితం ముందు వచ్చిన విలువలతో సరిపోలడం లేదు, కాబట్టి వైద్యులు మళ్లీ పరీక్ష చేయవచ్చు."
                if outlier_flag
                else "ప్రస్తుతం కనిపిస్తున్న మార్పులు పర్యవేక్షణకు సరిపడా స్థిరంగా ఉన్నాయి."
            )
        )
    }

    return translations