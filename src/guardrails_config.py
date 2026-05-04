"""
Security Guardrails Configuration
Implements input/output validation to prevent jailbreaking and data leakage.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
import re
from enum import Enum


class SafetyClassification(str, Enum):
    """Classification of input/output safety."""
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    UNSAFE = "unsafe"


class InputGuardrailConfig:
    """Deterministic input validation rules."""

    # Keywords that suggest prompt injection or jailbreak attempts
    FORBIDDEN_KEYWORDS = {
        # Jailbreak personas
        "do anything now",
        "ignore all previous",
        "forget the instructions",
        "pretend you are",
        "act as if",
        "roleplay as",
        "assume the role",
        "bypass",
        "override",
        "disable safety",
        "turn off",
        "no longer bound",
        "restriction",
        "limitation",
        "evil mode",
        "unrestricted",
        "without filters",
        "without rules",
        # SQL/Command injection patterns
        "drop table",
        "delete from",
        "delete all",
        "exec(",
        "eval(",
        "system(",
        "rm -rf",
        "rm /",
        # Sensitive operations
        "read file",
        "write file",
        "access credentials",
        "steal data",
        "exfiltrate",
        "leak",
        "malware",
        "ransomware",
        "exploit",
        "database",  # Added to catch database-related attacks
    }

    # Suspicious patterns (regex)
    SUSPICIOUS_PATTERNS = [
        r"<!--.*?-->",  # Hidden HTML comments
        r"\${.*?}",  # Template injection
        r"\[\[.*?\]\]",  # Double bracket injection
        r"prompt.*injection",  # Explicit mention of attacks
        r"jailbreak",
        r"dang.*prompt",  # DAN variant
        r"chatgpt.*jailbreak",
    ]

    # Safe topics for this agent (whitelist approach is stricter)
    ALLOWED_TOPICS = {
        "youtube",
        "url",
        "audio",
        "transcription",
        "transcript",
        "dataset",
        "download",
        "process",
        "analyze",
        "metadata",
        "video",
        "segment",
        "duration",
    }

    @staticmethod
    def validate_input(user_input: str) -> tuple[SafetyClassification, str]:
        """
        Validate user input for security threats.

        Returns:
            (classification, reason)
        """
        if not isinstance(user_input, str):
            return SafetyClassification.UNSAFE, "Input must be a string"

        # Check length
        if len(user_input) > 10000:
            return SafetyClassification.SUSPICIOUS, "Input exceeds maximum length"

        # Normalize for checking
        normalized = user_input.lower().strip()

        # Check for forbidden keywords
        for keyword in InputGuardrailConfig.FORBIDDEN_KEYWORDS:
            if keyword in normalized:
                return (
                    SafetyClassification.UNSAFE,
                    f"Forbidden keyword detected: '{keyword}'"
                )

        # Check for suspicious patterns
        for pattern in InputGuardrailConfig.SUSPICIOUS_PATTERNS:
            if re.search(pattern, normalized, re.IGNORECASE):
                return (
                    SafetyClassification.SUSPICIOUS,
                    f"Suspicious pattern detected: {pattern}"
                )

        # Check if input contains a YouTube URL (bare URL is acceptable)
        if re.search(r"(?:youtube\.com|youtu\.be)", normalized):
            return SafetyClassification.SAFE, "Input validated (YouTube URL detected)"

        # Check if input is related to allowed topics
        words = set(normalized.split())
        allowed_overlap = words & InputGuardrailConfig.ALLOWED_TOPICS

        if not allowed_overlap:
            return (
                SafetyClassification.SUSPICIOUS,
                "Input does not appear related to audio/transcript processing"
            )

        return SafetyClassification.SAFE, "Input validated"


class OutputSanitizationConfig:
    """Output validation to prevent data leakage."""

    # Patterns that should be redacted from output
    SENSITIVE_PATTERNS = [
        (r"/home/\S+", "[REDACTED_PATH]"),  # File paths with /home
        (r"/root/\S+", "[REDACTED_PATH]"),  # Root paths
        (r"C:\\.*?(?=\s|$)", "[REDACTED_PATH]"),  # Windows paths
        (r"(?:audio|dataset|transcript)\/.*?(?=\s|['\"]|$)", "[REDACTED_PATH]"),  # Relative paths
        (r"\.json\b", "[REDACTED_EXT]"),  # JSON file extensions
        (r"\.wav\b", "[REDACTED_EXT]"),  # WAV file extensions
        (r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", "[REDACTED_TIMESTAMP]"),  # ISO timestamps
        (r"sqlite_sequence", "[REDACTED_METADATA]"),  # Database metadata
        (r"__[a-z_]+__", "[REDACTED_METADATA]"),  # Python metadata
    ]

    FORBIDDEN_OUTPUT_KEYWORDS = {
        # Internal implementation details
        "intermediate_steps",
        "llm_config",
        "api_key",
        "secret",
        "password",
        "token",
        "credentials",
    }

    @staticmethod
    def sanitize_output(output: str) -> tuple[str, List[str]]:
        """
        Sanitize output to prevent data leakage.

        Returns:
            (sanitized_output, list_of_redactions)
        """
        if not isinstance(output, str):
            return str(output), []

        sanitized = output
        redactions = []

        # Apply regex replacements
        for pattern, replacement in OutputSanitizationConfig.SENSITIVE_PATTERNS:
            matches = re.findall(pattern, output)
            if matches:
                sanitized = re.sub(pattern, replacement, sanitized)
                redactions.extend([f"Redacted {len(matches)} instance(s) of pattern: {pattern}"])

        # Check for forbidden keywords
        for keyword in OutputSanitizationConfig.FORBIDDEN_OUTPUT_KEYWORDS:
            if keyword.lower() in sanitized.lower():
                sanitized = re.sub(
                    f"\\b{keyword}\\b",
                    "[REDACTED_INTERNAL]",
                    sanitized,
                    flags=re.IGNORECASE
                )
                redactions.append(f"Redacted forbidden keyword: '{keyword}'")

        return sanitized, redactions

    @staticmethod
    def check_for_pii(text: str) -> tuple[bool, List[str]]:
        """
        Check if output contains potential PII.

        Returns:
            (contains_pii, list_of_concerns)
        """
        concerns = []

        # Email pattern
        if re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text):
            concerns.append("Potential email address detected")

        # Phone pattern
        if re.search(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", text):
            concerns.append("Potential phone number detected")

        # IP address pattern
        if re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", text):
            concerns.append("Potential IP address detected")

        # File paths (internal)
        if re.search(r"(?:C:|/)[A-Za-z0-9_/\\.-]+", text):
            concerns.append("Potential file paths detected")

        return len(concerns) > 0, concerns


class GuardrailRequest(BaseModel):
    """Request model for guardrail node."""
    user_input: str = Field(..., description="The user's request")
    source: Optional[str] = Field(default="user", description="Source of the request")


class GuardrailResponse(BaseModel):
    """Response model from guardrail node."""
    is_safe: bool = Field(..., description="Whether input passed guardrails")
    classification: SafetyClassification = Field(..., description="Safety classification")
    reason: str = Field(..., description="Reason for classification")
    sanitization_needed: bool = Field(default=False, description="Whether output will need sanitization")
