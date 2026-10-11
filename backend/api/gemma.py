"""Google Gemma client using the Gemini Developer API's generateContent REST endpoint."""

import itertools
import os
import threading

import requests


class GemmaClient:
    """Small REST wrapper preserving the response shape used by Voyager's backend."""

    API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
    RETRYABLE_STATUSES = {401, 403, 429, 500, 502, 503, 504}
    _rotation_lock = threading.Lock()
    _key_cursor = itertools.count()

    def __init__(self, api_keys=None, model=None, timeout=None):
        self.api_keys = self._load_api_keys(api_keys)
        self.model = model or os.getenv("GEMMA_MODEL", "gemma-4-26b-a4b-it").strip()
        self.timeout = timeout or float(os.getenv("GEMMA_API_TIMEOUT", "90"))
        if not self.api_keys:
            print("WARNING: Gemma API keys are not configured. AI features require GEMMA_API_KEYS.")

    @staticmethod
    def _load_api_keys(api_keys=None):
        if api_keys is not None:
            candidates = api_keys if isinstance(api_keys, (list, tuple)) else [api_keys]
        else:
            candidates = []
            for variable in ("GEMMA_API_KEYS", "GEMMA_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY"):
                candidates.extend(os.getenv(variable, "").replace("\n", ",").split(","))
            for index in range(1, 4):
                candidates.extend([
                    os.getenv(f"GEMMA_API_KEY_{index}", ""),
                    os.getenv(f"GEMINI_API_KEY_{index}", ""),
                ])

        keys = []
        for candidate in candidates:
            key = str(candidate).strip()
            if key and key not in keys:
                keys.append(key)
        return keys

    @classmethod
    def _rotated_keys(cls, keys):
        if len(keys) < 2:
            return list(keys)
        with cls._rotation_lock:
            offset = next(cls._key_cursor) % len(keys)
        return keys[offset:] + keys[:offset]

    @staticmethod
    def _to_gemini_contents(messages):
        system_text = []
        contents = []
        for message in messages:
            role = message.get("role", "user")
            text = str(message.get("content", ""))
            if role == "system":
                system_text.append(text)
                continue
            contents.append({
                "role": "model" if role in ("assistant", "model") else "user",
                "parts": [{"text": text}],
            })
        return system_text, contents

    def chat_completion(self, messages, model=None, temperature=0.2):
        """Call Gemma and return the legacy choices/message/content structure."""
        if not self.api_keys:
            raise RuntimeError(
                "Gemma API keys are not configured. Set GEMMA_API_KEYS in your server environment."
            )

        system_text, contents = self._to_gemini_contents(messages)
        if not contents:
            raise ValueError("At least one user or assistant message is required.")

        selected_model = model or self.model
        url = f"{self.API_BASE}/{selected_model}:generateContent"
        payload = {
            "contents": contents,
            "generationConfig": {"temperature": float(temperature)},
        }
        if selected_model.startswith("gemma-4"):
            payload["generationConfig"]["thinkingConfig"] = {"thinkingLevel": "minimal"}
        if system_text:
            payload["systemInstruction"] = {"parts": [{"text": "\n\n".join(system_text)}]}

        keys = self._rotated_keys(self.api_keys)
        last_error = None
        for index, key in enumerate(keys):
            try:
                response = requests.post(
                    url,
                    headers={"x-goog-api-key": key, "Content-Type": "application/json"},
                    json=payload,
                    timeout=(10, self.timeout),
                )
                if response.status_code in self.RETRYABLE_STATUSES and index < len(keys) - 1:
                    last_error = requests.HTTPError(
                        f"Gemma API returned HTTP {response.status_code}; trying the next configured key.",
                        response=response,
                    )
                    continue
                response.raise_for_status()
                data = response.json()
                parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                text = "".join(
                    part.get("text", "")
                    for part in parts
                    if isinstance(part, dict) and not part.get("thought", False)
                ).strip()
                if not text:
                    reason = data.get("promptFeedback", {}).get("blockReason", "No text was returned")
                    raise RuntimeError(f"Gemma returned no text. {reason}")
                return {
                    "model": selected_model,
                    "choices": [{"message": {"role": "assistant", "content": text}}],
                }
            except requests.exceptions.Timeout as error:
                raise RuntimeError(
                    f"Gemma did not respond within {self.timeout:g} seconds. Please retry."
                ) from error
            except requests.exceptions.RequestException as error:
                last_error = error
                if index == len(keys) - 1:
                    raise RuntimeError(f"Gemma API request failed: {error}") from error

        raise RuntimeError(f"All configured Gemma keys failed: {last_error}") from last_error

    def generate_roadmap(self, topic, difficulty="Intermediate"):
        system_prompt = (
            "You are an expert curriculum designer. "
            f"Create a structured learning roadmap for the given topic at an {difficulty} level. "
            "Return a clear, numbered list of main topics with short sub-points. "
            "Do not include conversational filler."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Create a learning roadmap for: {topic}"},
        ]
        result = self.chat_completion(messages)
        return result["choices"][0]["message"]["content"]
