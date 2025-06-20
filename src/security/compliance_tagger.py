COMPLIANCE_KEYWORDS = [
    "restatement", "earnings risk", "litigation", "whistleblower", "penalty"
]

def tag_compliance_flags(text):
    flags = [word for word in COMPLIANCE_KEYWORDS if word.lower() in text.lower()]
    return flags
