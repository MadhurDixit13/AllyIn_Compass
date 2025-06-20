import re

# Basic regex patterns for PII
EMAIL_REGEX = r"\b[\w\.-]+@[\w\.-]+\.\w+\b"
PHONE_REGEX = r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
SSN_REGEX = r"\b\d{3}-\d{2}-\d{4}\b"

def contains_pii(text):
    return any([
        re.search(EMAIL_REGEX, text),
        re.search(PHONE_REGEX, text),
        re.search(SSN_REGEX, text)
    ])
