#!/usr/bin/env python3
"""Agentic team performance metrics, computed from GitHub (the system of record).

Reads story/bug issues, PRs with their verdict comments, and releases via the `gh` CLI,
then reports productivity, quality, coordination and human-involvement metrics.
See docs/06-evaluation.md for definitions.

  python3 scripts/metrics.py [--repo owner/name] [--since YYYY-MM-DD] [--json]
  python3 scripts/metrics.py --fixture scripts/tests/fixtures/sample.json
"""
import argparse
import json
import re
import statistics
import subprocess
import sys
from datetime import datetime, timezone

MARKER = re.compile(r"<!--\s*agentic-verdict\s+(\{.*?\})\s*-->", re.S)
STORY_BRANCH = re.compile(r"^story/(\d+)-")
FOUND_IN = re.compile(r"###\s*Where it was found\s*\n+\s*([^\n]+)", re.I)


def gh_json(args, repo):
    cmd = ["gh", *args] + (["--repo", repo] if repo else [])
    return json.loads(subprocess.run(cmd, check=True, capture_output=True, text=True).stdout or "[]")


def fetch(repo):
    data = {
        "stories": gh_json(["issue", "list", "--state", "all", "--label", "type:story", "--limit", "1000",
                            "--json", "number,title,state,createdAt,closedAt,labels"], repo),
        "bugs": gh_json(["issue", "list", "--state", "all", "--label", "type:bug", "--limit", "1000",
                         "--json", "number,createdAt,labels,body"], repo),
        "prs": gh_json(["pr", "list", "--state", "all", "--limit", "1000",
                        "--json", "number,headRefName,state,createdAt,mergedAt,comments"], repo),
    }
    try:
        data["releases"] = gh_json(["release", "list", "--limit", "200",
                                    "--json", "tagName,publishedAt,isDraft"], repo)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        data["releases"] = []
    return data


def ts(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")) if value else None


def hours(start, end):
    return (end - start).total_seconds() / 3600 if start and end else None


def labels(item):
    return {lbl["name"] if isinstance(lbl, dict) else lbl for lbl in item.get("labels", [])}


def verdicts(prs):
    out = []
    for pr in prs:
        for comment in pr.get("comments", []):
            for raw in MARKER.findall(comment.get("body", "")):
                try:
                    out.append(json.loads(raw))
                except json.JSONDecodeError:
                    pass
    return out


def median(values):
    values = [v for v in values if v is not None]
    return round(statistics.median(values), 1) if values else None


def compute(data, since=None, now=None):
    now = now or datetime.now(timezone.utc)
    since_dt = ts(since + "T00:00:00Z") if since else None
    prs_by_story = {}
    for pr in data.get("prs", []):
        m = STORY_BRANCH.match(pr.get("headRefName", ""))
        if m:
            prs_by_story.setdefault(int(m.group(1)), []).append(pr)

    rows = []
    for st in data.get("stories", []):
        created = ts(st["createdAt"])
        if since_dt and created < since_dt:
            continue
        prs = prs_by_story.get(st["number"], [])
        vs = verdicts(prs)
        gate_vs = [v for v in vs if v.get("agent") in ("qa", "reviewer")]
        merged = [ts(p["mergedAt"]) for p in prs if p.get("mergedAt")]
        risk = next((l for l in sorted(labels(st)) if l.startswith("risk:")), "risk:?")
        rows.append({
            "number": st["number"],
            "risk": risk,
            "done": st.get("state", "").upper() == "CLOSED" and bool(merged),
            "lead_time_h": hours(created, ts(st.get("closedAt"))),
            "pr_cycle_h": hours(min(ts(p["createdAt"]) for p in prs), max(merged)) if merged else None,
            "cycles": max((int(v.get("cycle", 1)) for v in gate_vs), default=0),
            "first_pass": any(v.get("agent") == "qa" and v.get("verdict") == "PASS" and v.get("cycle") == 1 for v in vs)
                          and any(v.get("agent") == "reviewer" and v.get("verdict") == "APPROVE" and v.get("cycle") == 1 for v in vs),
            "qa_fails": sum(1 for v in vs if v.get("agent") == "qa" and v.get("verdict") == "FAIL"),
            "review_rejects": sum(1 for v in vs if v.get("agent") == "reviewer" and v.get("verdict") == "CHANGES_REQUESTED"),
            "escalations": sum(1 for v in vs if v.get("verdict") in ("ESCALATED", "BLOCKED")),
            "cost_usd": sum(float(v.get("cost_usd", 0) or 0) for v in vs),
        })

    done = [r for r in rows if r["done"]]
    bugs = [b for b in data.get("bugs", []) if not since_dt or ts(b["createdAt"]) >= since_dt]

    def found_in(bug):
        m = FOUND_IN.search(bug.get("body") or "")
        return (m.group(1).strip().lower() if m else "")

    escaped = [b for b in bugs if "defect:escaped" in labels(b) or found_in(b).startswith(("staging", "production"))]
    prod_bugs = [b for b in bugs if found_in(b).startswith("production")]
    releases = [r for r in data.get("releases", []) if not r.get("isDraft") and r.get("publishedAt")
                and (not since_dt or ts(r["publishedAt"]) >= since_dt)]
    start = since_dt or min((ts(s["createdAt"]) for s in data.get("stories", [])), default=now)
    weeks = max((now - start).days / 7, 1)
    costs = [r["cost_usd"] for r in done if r["cost_usd"]]

    return {
        "window": {"since": start.date().isoformat(), "until": now.date().isoformat(), "weeks": round(weeks, 1)},
        "productivity": {
            "stories_started": len(rows),
            "stories_done": len(done),
            "throughput_per_week": round(len(done) / weeks, 2),
            "median_lead_time_h": median([r["lead_time_h"] for r in done]),
            "median_pr_cycle_time_h": median([r["pr_cycle_h"] for r in done]),
        },
        "quality": {
            "first_pass_yield": round(sum(r["first_pass"] for r in done) / len(done), 2) if done else None,
            "defects_caught_before_merge": sum(r["qa_fails"] + r["review_rejects"] for r in rows),
            "escaped_defects": len(escaped),
            "escaped_defects_per_story": round(len(escaped) / len(done), 2) if done else None,
            "change_failure_rate": round(len(prod_bugs) / len(releases), 2) if releases else None,
        },
        "coordination": {
            "mean_rework_cycles": round(statistics.mean(r["cycles"] for r in done), 2) if done else None,
            "max_rework_cycles": max((r["cycles"] for r in rows), default=0),
            "stories_escalated": sum(1 for r in rows if r["escalations"]),
        },
        "delivery": {"production_releases": len(releases),
                     "releases_per_week": round(len(releases) / weeks, 2)},
        "cost": {"cost_per_done_story_usd": round(statistics.mean(costs), 2) if costs else None,
                 "note": "Only stories whose verdict markers carry cost_usd; use Console/OTel usage for totals."},
        "by_risk": {risk: sum(1 for r in done if r["risk"] == risk) for risk in sorted({r["risk"] for r in done})},
        "stories": rows,
    }


def render(m):
    lines = [f"# Agentic team metrics ({m['window']['since']} → {m['window']['until']}, {m['window']['weeks']} wk)", ""]
    for section in ("productivity", "quality", "coordination", "delivery", "cost"):
        lines += [f"## {section.title()}", "| metric | value |", "|---|---|"]
        lines += [f"| {k.replace('_', ' ')} | {'n/a' if v is None else v} |" for k, v in m[section].items()]
        lines.append("")
    lines += ["## Stories", "| # | risk | done | lead time h | PR cycle h | rework cycles | first pass | escalations |",
              "|---|---|---|---|---|---|---|---|"]
    for r in m["stories"]:
        fmt = lambda v: "n/a" if v is None else (round(v, 1) if isinstance(v, float) else v)
        lines.append(f"| {r['number']} | {r['risk']} | {'✓' if r['done'] else ''} | {fmt(r['lead_time_h'])} | "
                     f"{fmt(r['pr_cycle_h'])} | {r['cycles']} | {'✓' if r['first_pass'] else ''} | {r['escalations']} |")
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--repo")
    p.add_argument("--since", help="YYYY-MM-DD")
    p.add_argument("--fixture", help="read data from a JSON file instead of GitHub")
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    if a.fixture:
        with open(a.fixture, encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = fetch(a.repo)
    m = compute(data, a.since)
    print(json.dumps(m, indent=2, default=str) if a.json else render(m))


if __name__ == "__main__":
    sys.exit(main())
