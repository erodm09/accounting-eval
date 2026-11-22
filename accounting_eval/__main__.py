"""CLI: python -m accounting_eval {run,grade,list}"""

from __future__ import annotations

import argparse
import json
import sys

from .runner import anthropic_model, grade_responses, load_tasks, oracle_model, run, summarize


def print_summary(summary: dict) -> None:
    print(f"\nOverall: {summary['correct']}/{summary['total']} ({summary['accuracy']:.1%})")
    for cat, s in summary["by_category"].items():
        print(f"  {cat:<22} {s['correct']}/{s['total']}  ({s['accuracy']:.0%})")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="accounting_eval", description="Small accounting eval for LLMs")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="query a model and score it")
    r.add_argument("--model", default="claude-sonnet-5-5",
                   help="Anthropic model id, or 'oracle' to sanity-check the harness")
    r.add_argument("--category")
    r.add_argument("--out", help="write per-task results JSON here")

    g = sub.add_parser("grade", help="score a JSONL file of {id, response}")
    g.add_argument("responses")
    g.add_argument("--category")
    g.add_argument("--out")

    ls = sub.add_parser("list", help="list tasks")
    ls.add_argument("--category")

    args = p.parse_args(argv)
    tasks = load_tasks(category=args.category)

    if args.cmd == "list":
        for t in tasks:
            print(f"{t['id']:<10} {t['category']:<22} {t['prompt'].splitlines()[0][:70]}")
        return 0

    if args.cmd == "run":
        model_fn = oracle_model if args.model == "oracle" else anthropic_model(args.model)
        results = run(tasks, model_fn)
    else:
        results = grade_responses(tasks, args.responses)

    for res in results:
        mark = "PASS" if res["correct"] else "FAIL"
        print(f"[{mark}] {res['id']:<10} expected={res['expected']!s:<10} got={res.get('parsed')}")
    summary = summarize(results)
    print_summary(summary)

    if args.out:
        with open(args.out, "w") as f:
            json.dump({"summary": summary, "results": results}, f, indent=2)
        print(f"\nWrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
