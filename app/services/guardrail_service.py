import re

MAX_MESSAGE_LENGTH = 5000


def validate_input(message: str) -> None:
    # Check that a message was provided
    if not message or not message.strip():
        raise ValueError("Message cannot be empty.")

    # Remove unnecessary whitespace
    message = message.strip()

    # Prevent excessively large requests
    if len(message) > MAX_MESSAGE_LENGTH:
        raise ValueError(
            f"Message is too long. Maximum length is "
            f"{MAX_MESSAGE_LENGTH} characters."
        )


INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"ignore\s+(all\s+)?prior\s+instructions",
    r"forget\s+(all\s+)?previous\s+instructions",
    r"reveal\s+(your\s+)?system\s+prompt",
    r"show\s+(me\s+)?your\s+system\s+instructions",
    r"you\s+are\s+now\s+an?\s+unrestricted",
]


def detect_prompt_injection(message: str) -> bool:
    suspicious_patterns = [
        "ignore your instructions",
        "ignore previous instructions",
        "ignore your rules",
        "system prompt",
        "reveal your instructions",
        "tell me the api key",
    ]

    message_lower = message.lower()

    for pattern in suspicious_patterns:
        if pattern in message_lower:
            return True

    return False


SENSITIVE_DATA_PATTERNS = [
    # OpenAI-style API keys
    r"sk-[A-Za-z0-9_-]{20,}",
    # Generic API keys / secrets
    r"(?i)(api[_-]?key|secret[_-]?key)\s*[:=]\s*[A-Za-z0-9_\-]{10,}",
    # Bearer tokens
    r"(?i)bearer\s+[A-Za-z0-9\-._~+/]+=*",
    # JWT tokens
    r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",
    # Credit-card-like numbers
    r"\b(?:\d[ -]*?){13,19}\b",
]


def contains_sensitive_data(message: str) -> bool:
    for pattern in SENSITIVE_DATA_PATTERNS:
        if re.search(pattern, message):
            return True

    return False


def validate_llm_output(response: str) -> str:
    if not response or not response.strip():
        return "The AI could not generate a valid response."

    if contains_sensitive_data(response):
        return "The AI response was blocked because it contained sensitive information."

    return response
