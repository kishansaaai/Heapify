import os

from github import Github


def create_vulnerability_report(session_id: str, bugs: list, stats: dict) -> str:
    """Create a GitHub issue with the full vulnerability report. Returns the issue URL."""
    token = os.environ.get("GITHUB_TOKEN")
    repo_name = os.environ.get("GITHUB_REPOSITORY")

    if not token or not repo_name:
        raise RuntimeError(
            "GITHUB_TOKEN and GITHUB_REPOSITORY must be set to create issue reports"
        )

    g = Github(token)
    repo = g.get_repo(repo_name)

    short_id = session_id[:8]

    if not bugs:
        body = (
            f"## Heapify Report: Session `{short_id}`\n\n"
            f"✅ **No vulnerabilities found.**\n\n"
            f"**Stats:** {stats['tool_calls_total']} tool calls tested, "
            f"{stats['adversarial_calls']} adversarial injections applied."
        )
    else:
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_bugs = sorted(bugs, key=lambda b: severity_order.get(b.get("severity", "low"), 3))

        lines = [
            f"## Heapify Report: Session `{short_id}`\n",
            f"⚠️ **{len(bugs)} vulnerabilit{'y' if len(bugs) == 1 else 'ies'} found** "
            f"across {stats['tool_calls_total']} tool calls "
            f"({stats['adversarial_calls']} adversarial).\n",
        ]
        for b in sorted_bugs:
            severity = b.get("severity", "medium").upper()
            attack = b.get("attack_type", "unknown").replace("_", " ").title()
            lines.append(f"### {attack} — Severity: {severity}")
            lines.append(f"- **Tool:** `{b.get('tools_involved', 'unknown')}`")
            lines.append(f"- **Hypothesis:** {b.get('hypothesis', '')}")
            lines.append(f"- **What happened:** {b.get('bug_description', '')}")
            lines.append(f"- **Assumption violated:** {b.get('assumption_violated', '')}\n")

        body = "\n".join(lines)

    # Note: GitHub requires the labels to exist on the repository beforehand if using create_issue,
    # or it will automatically try to create them or succeed. If labels do not exist, PyGithub handles it fine.
    issue = repo.create_issue(
        title=f"Heapify Report: {short_id}",
        body=body,
        labels=["heapify", "security"]
    )
    return issue.html_url
