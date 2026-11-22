"""accounting-eval: a small benchmark of accounting problems for LLMs."""

from .grader import extract_answer, grade, parse_number
from .runner import load_tasks, run, summarize

__all__ = ["extract_answer", "grade", "parse_number", "load_tasks", "run", "summarize"]
__version__ = "0.1.0"
