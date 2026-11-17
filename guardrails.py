import re


BLOCKED_WORDS = [
    "steal password",
    "create malware",
    "hack someone",
    "bypass security"
]


def validate_input(user_input):

    if not user_input or not user_input.strip():
        return False, "Please enter a valid message."

    if len(user_input) > 2000:
        return False, "Message is too long. Maximum 2000 characters."

    text = user_input.lower()

    for word in BLOCKED_WORDS:
        if word in text:
            return False, "Request blocked by security guardrails."

    return True, "Input validated."


def validate_output(response):

    if not response or not response.strip():
        return False, "AI generated an empty response."

    if len(response) > 10000:
        return False, "Output exceeds the allowed length."

    if re.search(r"-----BEGIN .*PRIVATE KEY-----", response):
        return False, "Sensitive information detected."

    return True, response