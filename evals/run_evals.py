"""
Week 18 — Eval harness for DevMind code review agent.
Runs test cases against the live API and scores results.

Usage:
    python evals/run_evals.py                        # uses dev-local-key
    python evals/run_evals.py --key your-api-key     # override key
    python evals/run_evals.py --url https://...      # against production
"""

import json
import argparse
import requests
from pathlib import Path
from typing import Any

BASE_URL = "http://localhost:8000"
DEFAULT_KEY = "dev-local-key"
CASES_PATH = Path(__file__).parent / "eval_cases.json"

GREEN = "\033[92m"
RED   = "\033[91m"
YELLOW= "\033[93m"
RESET = "\033[0m"
BOLD  = "\033[1m"


def score_result(result: dict, expect: dict) -> tuple[int, int, list[str]]:
    """
    Score a single result against its expectations.
    Returns (points_earned, points_possible, list_of_failures).
    """
    earned = 0
    possible = 0
    failures = []

    # --- Check overall_score ceiling ---
    possible += 2
    if result["overall_score"] <= expect["max_score"]:
        earned += 2
    else:
        failures.append(
            f"Score {result['overall_score']} exceeds expected max {expect['max_score']}"
        )

    # --- Check overall_score floor (optional) ---
    if "min_score" in expect:
        possible += 2
        if result["overall_score"] >= expect["min_score"]:
            earned += 2
        else:
            failures.append(
                f"Score {result['overall_score']} below expected min {expect['min_score']}"
            )

    # --- Check required issue types were caught ---
    found_types = {issue["type"] for issue in result["issues"]}
    for req_type in expect["required_issues"]:
        possible += 3
        if req_type in found_types:
            earned += 3
        else:
            failures.append(f"Missing required issue type: '{req_type}'")

    # --- Check forbidden severities not present ---
    found_severities = {issue["severity"] for issue in result["issues"]}
    for forbidden in expect["forbidden_severities"]:
        possible += 2
        if forbidden not in found_severities:
            earned += 2
        else:
            failures.append(f"Found forbidden severity: '{forbidden}'")

    # --- Check has_docstring ---
    possible += 1
    if result["has_docstring"] == expect["has_docstring"]:
        earned += 1
    else:
        failures.append(
            f"has_docstring: got {result['has_docstring']}, expected {expect['has_docstring']}"
        )

    # --- Check has_type_hints ---
    possible += 1
    if result["has_type_hints"] == expect["has_type_hints"]:
        earned += 1
    else:
        failures.append(
            f"has_type_hints: got {result['has_type_hints']}, expected {expect['has_type_hints']}"
        )

    return earned, possible, failures


def run_evals(base_url: str, api_key: str) -> None:
    cases = json.loads(CASES_PATH.read_text())

    total_earned = 0
    total_possible = 0
    passed = 0
    failed = 0

    print(f"\n{BOLD}DevMind Eval Harness — Week 18{RESET}")
    print(f"Target: {base_url}")
    print("=" * 60)

    for case in cases:
        case_id    = case["id"]
        desc       = case["description"]
        code       = case["code"]
        expect     = case["expect"]

        # Call the API
        try:
            resp = requests.post(
                f"{base_url}/review/code",
                headers={"X-API-Key": api_key, "Content-Type": "application/json"},
                json={"code": code},
                timeout=30,
            )
            resp.raise_for_status()
            result: dict[str, Any] = resp.json()
        except Exception as e:
            print(f"\n{RED}[ERROR]{RESET} {case_id}: {e}")
            failed += 1
            total_possible += 5  # penalise for the crash
            continue

        earned, possible, failures = score_result(result, expect)
        total_earned   += earned
        total_possible += possible
        pct = round(earned / possible * 100) if possible else 0

        if not failures:
            passed += 1
            status = f"{GREEN}PASS{RESET}"
        else:
            failed += 1
            status = f"{RED}FAIL{RESET}"

        print(f"\n[{status}] {case_id} — {desc}")
        print(f"       Score returned by agent: {result['overall_score']}/10")
        print(f"       Eval points: {earned}/{possible} ({pct}%)")
        if failures:
            for f in failures:
                print(f"       {YELLOW}✗{RESET} {f}")
        else:
            print(f"       {GREEN}✓{RESET} All checks passed")

    # Final summary
    overall_pct = round(total_earned / total_possible * 100) if total_possible else 0
    print("\n" + "=" * 60)
    print(f"{BOLD}Results: {passed} passed, {failed} failed{RESET}")
    print(f"Total eval score: {total_earned}/{total_possible} ({overall_pct}%)")

    if overall_pct >= 80:
        print(f"{GREEN}✓ Quality gate PASSED (≥80%){RESET}")
    else:
        print(f"{RED}✗ Quality gate FAILED (<80%){RESET}")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=BASE_URL)
    parser.add_argument("--key", default=DEFAULT_KEY)
    args = parser.parse_args()
    run_evals(args.url, args.key)