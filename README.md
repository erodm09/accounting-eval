# accounting-eval

A small, dependency-free benchmark for testing how well LLMs solve core accounting problems.

20 hand-checked tasks across 9 categories:

| Category | Examples |
|---|---|
| depreciation | straight-line, double-declining balance, units of production |
| inventory | FIFO, LIFO, weighted-average |
| ratios | current, quick, gross margin, ROE |
| reconciliation | bank reconciliation |
| adjusting-entries | prepaid expense, accrued interest, bad debt allowance |
| financial-statements | retained earnings roll-forward |
| managerial | break-even analysis |
| time-value | present value |
| journal-entries | multiple-choice debit/credit questions |

Each model reply must end with `ANSWER: <value>`. Numeric answers are graded with a per-task tolerance
(handles `$`, commas, `%`, and `(negative)` notation); multiple-choice answers are graded by letter.

## Quick start

```bash
# sanity-check the harness (should score 100%)
python -m accounting_eval run --model oracle

# list tasks
python -m accounting_eval list

# run against Claude
pip install anthropic
export ANTHROPIC_API_KEY=...
python -m accounting_eval run --model claude-sonnet-5-5 --out results.json

# grade responses you produced elsewhere (JSONL of {"id": ..., "response": ...})
python -m accounting_eval grade my_responses.jsonl
```

Filter with `--category inventory` on any command.

## Adding tasks

Append a line to `accounting_eval/data/tasks.jsonl`:

```json
{"id": "dep-004", "category": "depreciation", "type": "numeric", "prompt": "...", "answer": 1234.5, "tolerance": 0.5}
```

`type` is `numeric` (needs `answer` + optional `tolerance`) or `choice` (`answer` is a letter A–D).

## Tests

```bash
python -m unittest discover -s tests -v
```

## License

MIT
