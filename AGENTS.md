# Heapify Mocking Agent

## What it does

The Heapify Mocking Agent adversarially tests other AI agents by intercepting their tool calls in real time. For each intercepted call it decides whether to return the genuine result or a subtly crafted fake — designed to expose prompt injection susceptibility, false data trust, state corruption bugs, and privilege escalation paths.

## Agent definition

Defined in `agents/agent.yml`. Registered as an adversarial testing utility.

## How to trigger

### Analysis Mode (GitHub Issues/PRs)

You can run a flow to analyze code and post hypotheses to GitHub:

1. **Analyze** — Reads agent tool implementations from `examples/pa_agent/` using the Code Analyzer agent.
2. **Generate Hypotheses** — Creates top 3 ranked adversarial test scenarios using the Hypothesis Generator agent.
3. **Post Results** — Adds a structured attack surface map with ranked hypotheses as a comment on the specified GitHub issue using the Issue Reporter agent.

**What gets analyzed:**
- All tools decorated with `@heapify.query` (read operations)
- All tools decorated with `@heapify.mutation` (write operations)
- Attack surfaces: prompt injection, false data trust, state corruption, privilege escalation

**Example output:**
- Attack surface map with specific field-level vulnerabilities
- 3 ranked hypotheses (critical → high → medium → low)
- Exact mutations to test each hypothesis
- Commands to run Heapify tests locally

### Standalone Script Mode

Run the analysis manually and post to a specific issue:

```bash
# Using issue number
python scripts/run_flow_analysis.py --issue-number 4

# Using issue URL
python scripts/run_flow_analysis.py --issue-url https://github.com/owner/repo/issues/4
```

**Environment variables required:**
- `GITHUB_TOKEN` — GitHub personal access token with API access
- `GITHUB_REPOSITORY` — GitHub repository (e.g., owner/repo)
- `GEMINI_API_KEY` — Google Gemini API key (optional, uses mock mode if not set)

### CI/CD Execution Mode

Every Pull Request targeting `main` automatically runs the `heapify-test` job (`.github/workflows/heapify-test.yml`). The Python SDK intercepts tool calls in real-time, evaluates agent behavior against adversarial hypotheses, and creates a GitHub issue with the vulnerability report at session end.

**What happens in CI/CD:**
1. Agent runs with `HEAPIFY_MODE=ON`
2. Heapify intercepts each tool call
3. Decides: return genuine result or inject adversarial mutation
4. Tracks agent behavior (COMPROMISED vs SAFE)
5. Creates GitHub issue with full vulnerability report

## Python SDK

Instrument any agent with two decorators:

```python
from heapify import Heapify

heapify = Heapify()

@heapify.query
def get_file_contents(path: str) -> str:
    """Read a file from the repository."""
    ...

@heapify.mutation
def create_pull_request(title: str, branch: str) -> dict:
    """Open a pull request."""
    ...
```

Set `HEAPIFY_MODE=ON` to activate interception. When off, all tools pass through with zero overhead.

## Models used

- **Claude Sonnet 3.5 / Gemini 2.0 Flash** — powers the mocking agent's adversarial reasoning
