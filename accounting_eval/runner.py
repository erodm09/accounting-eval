"""Load tasks, query a model, and score the results."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Callable, Iterable

from .grader import grade

DATA_PATH = Path(__file__).parent / "data" / "tasks.jsonl"

SYSTEM_PROMPT = (
    "You are an expert accountant. Solve the problem. You may show brief work, "
    "but you must end your reply with a single line of the form 'ANSWER: <value>'. "
    "For numeric answers give only the number (no units). "
    "For multiple choice give only the letter."
)


def load_tasks(path: Path | str = DATA_PATH, category: str | None = None) -> list[dict]:
    tasks = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                tasks.append(json.loads(line))
    if category:
        tasks = [t for t in tasks if t["category"] == category]
    return tasks


def oracle_model(task: dict) -> str:
    """A perfect 'model' used to sanity-check the harness."""
    return f"ANSWER: {task['answer']}"


def anthropic_model(model: str, max_tokens: int = 1024) -> Callable[[dict], str]:
    try:
        import anthropic
    except ImportError as e:  # pragma: no cover
        raise SystemExit("Install the SDK first: pip install anthropic") from e
    client = anthropic.Anthropic()

    def call(task: dict) -> str:
        msg = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": task["prompt"]}],
        )
        return "".join(b.text for b in msg.content if b.type == "text")

    return call


def run(tasks: Iterable[dict], model_fn: Callable[[dict], str]) -> list[dict]:
    results = []
    for task in tasks:
        response = model_fn(task)
        r = grade(task, response)
        r["response"] = response
        results.append(r)
    return results


def grade_responses(tasks: list[dict], responses_path: Path | str) -> list[dict]:
    """Grade pre-computed responses from a JSONL file of {"id", "response"}."""
    by_id = {}
    with open(responses_path) as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                by_id[row["id"]] = row["response"]
    return run(tasks, lambda t: by_id.get(t["id"], ""))


def summarize(results: list[dict]) -> dict:
    by_cat: dict[str, list[bool]] = defaultdict(list)
    for r in results:
        by_cat[r["category"]].append(r["correct"])
    total = len(results)
    correct = sum(r["correct"] for r in results)
    return {
        "total": total,
        "correct": correct,
        "accuracy": round(correct / total, 4) if total else 0.0,
        "by_category": {
            c: {"correct": sum(v), "total": len(v), "accuracy": round(sum(v) / len(v), 4)}
            for c, v in sorted(by_cat.items())
        },
    }
