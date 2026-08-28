#!/usr/bin/env python3
"""Check the README's claims against this repository, live.

    GITHUB_TOKEN=... python3 verify.py

Reads expected.json and asserts every claim against the GitHub API: that
the required check is genuinely required, that each pull request's
required check and Gate check have the stated conclusions, and that the
analysis came from the production App rather than a development one.

An external reviewer found this repository's own README contradicting
its live state. A demonstration nobody verifies is a story.
"""
import json
import os
import sys
import urllib.error
import urllib.request

REPO = "arcifact-dev/gate-demo"
API = "https://api.github.com"


def get(path, token):
    req = urllib.request.Request(
        f"{API}{path}",
        headers={"Accept": "application/vnd.github+json",
                 "User-Agent": "gate-demo-verify",
                 **({"Authorization": f"Bearer {token}"} if token else {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def main():
    token = os.environ.get("GITHUB_TOKEN", "")
    exp = json.load(open(os.path.join(os.path.dirname(__file__),
                                      "expected.json"), encoding="utf-8"))
    problems = []

    # 1. the required check must actually be required
    want_ctx = exp["required_context"]
    try:
        rulesets = get(f"/repos/{REPO}/rulesets", token)
        required = False
        for r in rulesets:
            detail = get(f"/repos/{REPO}/rulesets/{r['id']}", token)
            for rule in detail.get("rules") or []:
                if rule.get("type") != "required_status_checks":
                    continue
                names = [c.get("context") for c in
                         (rule.get("parameters") or {})
                         .get("required_status_checks", [])]
                if want_ctx in names and detail.get("enforcement") == "active":
                    required = True
        if not required:
            problems.append(
                f"{want_ctx!r} is not actively required. The "
                f"demonstration would show a check that blocks nothing.")
    except urllib.error.HTTPError as e:
        problems.append(f"could not read rulesets: HTTP {e.code}")

    # 2. every pull request matches its stated conclusions
    for p in exp["pulls"]:
        n = p["number"]
        try:
            pr = get(f"/repos/{REPO}/pulls/{n}", token)
            runs = get(f"/repos/{REPO}/commits/{pr['head']['sha']}"
                       f"/check-runs", token)
        except urllib.error.HTTPError as e:
            problems.append(f"PR {n}: HTTP {e.code}")
            continue
        by_name = {}
        for c in runs.get("check_runs") or []:
            by_name.setdefault(c["name"], c)

        got = (by_name.get(want_ctx) or {}).get("conclusion")
        if got != p["required_check"]:
            problems.append(
                f"PR {n}: {want_ctx} is {got!r}, expected "
                f"{p['required_check']!r}")

        gate = None
        for name, c in by_name.items():
            if "rcifact" in name:
                gate = c
        if gate is None:
            problems.append(f"PR {n}: no Gate check run is present")
            continue
        if gate.get("conclusion") != p["gate"]:
            problems.append(
                f"PR {n}: Gate is {gate.get('conclusion')!r}, expected "
                f"{p['gate']!r}")
        slug = (gate.get("app") or {}).get("slug")
        if slug != exp["app"]["slug"]:
            problems.append(
                f"PR {n}: analysed by {slug!r}, not the production App "
                f"{exp['app']['slug']!r}. A visitor cannot reproduce "
                f"output from an App they cannot install.")

    if problems:
        print("  THE README AND THE REPOSITORY DISAGREE:")
        for p in problems:
            print(f"    {p}")
        return 1
    print(f"  every claim in expected.json holds against {REPO}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
