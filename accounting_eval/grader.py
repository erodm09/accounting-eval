"""Answer extraction and grading."""

from __future__ import annotations

import re

ANSWER_RE = re.compile(r"ANSWER\s*[:=]\s*(.+)", re.IGNORECASE)
NUMBER_RE = re.compile(r"-?\(?\$?\s*-?\d[\d,]*(?:\.\d+)?\)?")


def extract_answer(response: str) -> str | None:
    """Return the text after the last 'ANSWER:' marker, or None."""
    matches = ANSWER_RE.findall(response or "")
    if not matches:
        return None
    return matches[-1].strip().strip("*").strip()


def parse_number(text: str) -> float | None:
    """Parse '$1,234.50', '(500)', '35%', '-12' into a float."""
    m = NUMBER_RE.search(text)
    if not m:
        return None
    raw = m.group(0)
    negative = raw.startswith("-") or (raw.startswith("(") and raw.endswith(")"))
    digits = re.sub(r"[^\d.]", "", raw)
    try:
        value = float(digits)
    except ValueError:
        return None
    return -value if negative else value


def parse_choice(text: str) -> str | None:
    m = re.search(r"\b([A-D])\b", text.upper())
    return m.group(1) if m else None


def grade(task: dict, response: str) -> dict:
    """Grade one response against one task. Returns a result dict."""
    extracted = extract_answer(response)
    result = {"id": task["id"], "category": task["category"], "extracted": extracted,
              "expected": task["answer"], "correct": False}
    if extracted is None:
        result["error"] = "no ANSWER: line found"
        return result

    if task["type"] == "numeric":
        value = parse_number(extracted)
        result["parsed"] = value
        if value is not None:
            result["correct"] = abs(value - float(task["answer"])) <= task.get("tolerance", 0.01)
    elif task["type"] == "choice":
        choice = parse_choice(extracted)
        result["parsed"] = choice
        result["correct"] = choice == str(task["answer"]).upper()
    else:
        raise ValueError(f"unknown task type: {task['type']}")
    return result
