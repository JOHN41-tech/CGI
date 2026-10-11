"""Utilities for safely extracting structured JSON from model-generated text."""

import json
import re


def parse_model_json(text, expected_type=None):
    """Parse JSON emitted by a model, tolerating code fences and short preambles."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Gemma returned an empty response. Please try again.")

    raw = text.strip()
    code_blocks = re.findall(r"```(?:json)?\s*([\s\S]*?)```", raw, flags=re.IGNORECASE)
    candidates = code_blocks + [raw]
    decoder = json.JSONDecoder()
    wrong_shape = False

    for candidate in candidates:
        candidate = candidate.strip()
        try:
            value = json.loads(candidate)
            if expected_type is None or isinstance(value, expected_type):
                return value
            wrong_shape = True
        except json.JSONDecodeError:
            pass

        # Handle a short explanation before/after the JSON payload.
        for index, char in enumerate(candidate):
            if char not in "[{":
                continue
            try:
                value, _ = decoder.raw_decode(candidate[index:])
            except json.JSONDecodeError:
                continue
            if expected_type is None or isinstance(value, expected_type):
                return value
            wrong_shape = True

    if wrong_shape and expected_type is not None:
        raise ValueError(f"Gemma returned JSON in the wrong shape; expected {expected_type.__name__}.")
    raise ValueError("Gemma returned invalid JSON. Please try again.")
