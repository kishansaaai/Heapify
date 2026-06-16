# Heapify — Architecture

## Overview

Heapify is an adversarial AI security testing framework built on four layers:

1. **Interception Layer** — Python SDK decorators that sit between an agent's tool calls and real implementations
2. **Reasoning Layer** — Claude/Gemini decision engine that determines whether to mutate a tool result and how
3. **Persistence Layer** — SQLite database tracking sessions, mutations, confirmed bugs, and hypotheses
4. **Reporting Layer** — GitHub issue creation with structured vulnerability output

There are two independent trigger paths: the **Python SDK path** (real-time interception during agent execution) and the **GitHub Script path** (static code analysis triggered manually).

---

## System Diagram

```mermaid
flowchart TD
    subgraph Agent["AI Agent Under Test"]
        T1["search_emails() @query"]
        T2["get_calendar() @query"]
        T3["send_email() @mutation"]
        TN["... more tools"]
    end

    subgraph Intercept["Interception Layer — heapify.py"]
        I["Wraps every decorated tool call\nChecks HEAPIFY_MODE\nExecutes real function\nMaintains world_state coherence"]
    end

    subgraph Reason["Reasoning Layer — Gemini / Claude"]
        direction TB
        RI["Inputs: hypothesis, world_state,\nconfirmed bugs, tool name + args + real result"]
        RO["Output JSON:\n{ mutated, result, description, attack_type }"]
        RI --> RO
    end

    subgraph DB["Persistence Layer — SQLite (heapify.db)"]
        direction LR
        S["sessions\nrun_id · hypothesis\nstart/end · bug_count"]
        M["mutations\nsession_id · tool_name\norig/mutated result\ndescription · attack_type"]
        B["bugs\nsession_id · attack_type\nseverity · hypothesis\ntools_involved"]
        H["hypotheses\nbody · times_tested\ntimes_succeeded"]
    end

    subgraph Report["Reporting Layer — report.py"]
        R["PyGithub\nCreates issue per session\nLabels: heapify, security"]
    end

    T1 & T2 & T3 & TN -- "@query / @mutation\ndecorator intercepts" --> I
    I -- "real result + session context" --> RI
    RO -- "mutated or pass-through result" --> I
    I -- "returns result" --> T1 & T2 & T3 & TN
    I -- "stores mutation" --> M
    M & B --> R
```

---

## Python SDK Path — Execution Flow

The SDK path is used for local development and CI/CD. It performs live interception during a real agent run.

```mermaid
sequenceDiagram
    actor User
    participant SDK as heapify SDK
    participant DB as SQLite
    participant Gemini as Gemini / Claude
    participant Agent as Agent Under Test
    participant GH as GitHub

    User->>SDK: heapify.init()
    SDK->>DB: create schema if absent

    User->>SDK: with heapify.session()
    SDK->>DB: insert session row

    SDK->>DB: read bugs + hypotheses tables
    SDK->>Gemini: generate 3 novel hypotheses
    Gemini-->>SDK: ranked hypotheses
    SDK->>DB: store hypotheses, set session.hypothesis

    SDK->>Gemini: get_input(hypothesis)
    Gemini-->>SDK: task string

    User->>Agent: agent.run(task)

    loop For each tool call
        Agent->>SDK: tool_call() [intercepted by @query/@mutation]
        SDK->>SDK: execute real function → real_result
        SDK->>Gemini: mutate? (hypothesis, world_state, real_result)
        Gemini-->>SDK: { mutated, result, description, attack_type }
        SDK->>DB: insert mutation row
        SDK->>SDK: update world_state
        SDK-->>Agent: return (possibly mutated) result
    end

    SDK->>DB: read all mutations for session
    SDK->>Gemini: evaluate(mutations, agent_output)
    Gemini-->>SDK: confirmed bugs list
    SDK->>DB: insert bug rows

    SDK->>GH: create_issue(session summary + bugs)
    GH-->>User: issue URL
```

---

## Standalone Script Path — Static Analysis

The flow path is triggered via script. It does **not** run the agent or perform live interception — it produces a static analysis report as a comment on an issue.

```mermaid
flowchart LR
    T(["run_flow_analysis.py"])

    subgraph Pipeline["Adversarial Analysis Flow"]
        S1["Step 1 · Code Analyzer\nMap attack surfaces\nper tool and field"]
        S2["Step 2 · Hypothesis Generator\nRank top 3 hypotheses\nby severity"]
        S3["Step 3 · Issue Commenter\nPost full analysis\nas comment"]
        S1 --> S2 --> S3
    end

    GH[("GitHub Issue")]

    T --> Pipeline
    S3 --> GH
```

---

## Module Reference

### `heapify/heapify.py` — Core Interception Engine

| Symbol | Type | Role |
|--------|------|------|
| `Heapify` | class | Main SDK class; holds session reference and world state |
| `Heapify.query` | decorator | Wraps read-only tools; signals that injection into text fields is in scope |
| `Heapify.mutation` | decorator | Wraps write tools; signals that state corruption and privilege escalation are in scope |
| `Heapify.hypothesize()` | method | Generates and selects the test hypothesis for this session |
| `Heapify.get_input()` | method | Produces a task prompt that exercises the hypothesis |
| `Heapify.evaluate()` | method | Post-run analysis; identifies confirmed bugs from mutation log |

### `heapify/session.py` — Session Management

| Symbol | Type | Role |
|--------|------|------|
| `Session` | class | Holds `run_id`, `hypothesis`, `world_state` dict, and db connection |
| `session.world_state` | dict | Grows throughout the run; passed to Gemini/Claude on every call for consistency |
| `heapify.session()` | context manager | Creates session row on enter, writes end_time + bug_count on exit |

### `heapify/indices.py` — SQLite Schema

| Table | Key Columns | Purpose |
|-------|-------------|---------|
| `sessions` | `run_id`, `hypothesis`, `start_time`, `end_time`, `bug_count` | One row per test run |
| `mutations` | `session_id`, `tool_name`, `original_result`, `mutated_result`, `description`, `attack_type` | One row per intercepted tool call that was mutated |
| `bugs` | `session_id`, `attack_type`, `severity`, `hypothesis`, `tools_involved` | Confirmed vulnerabilities written during `evaluate()` |
| `hypotheses` | `body`, `times_tested`, `times_succeeded` | Corpus of discovered hypotheses; grows across sessions |

### `heapify/report.py` — GitHub Issue Creator

Uses `PyGithub` to authenticate via `GITHUB_TOKEN` and open an issue on `GITHUB_REPOSITORY`. Issue body is templated from the `bugs` and `sessions` tables for the completed run.

### `heapify/config.py` — Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `HEAPIFY_MODE` | No | Set to `ON` to activate interception; any other value is pass-through |
| `GITHUB_TOKEN` | Yes (reporting) | GitHub personal access token for issue creation |
| `GITHUB_REPOSITORY` | Yes (reporting) | Target repository (e.g. `owner/repo`) |
| `GEMINI_API_KEY` | Optional | Google Gemini API key; used for decision making |

---

## CI/CD Integration

```mermaid
flowchart LR
    PR["PR opened\ntargeting main"] --> CI["GitHub Actions\nheapify-test.yml"]
    CI --> Install["pip install -e ."]
    Install --> Run["python -m examples.pa_agent.main\nHEAPIFY_MODE=ON"]
    Run --> SDK["Full SDK path\ninterception → evaluation"]
    SDK --> Issue["GitHub issue created\nwith vulnerability report"]
    SDK --> Artifact["heapify.db artifact\n7-day retention"]
```

---

## Key Design Decisions

**World state coherence**: Every mutation is stored in `session.world_state` and passed to Gemini/Claude on subsequent calls. This ensures that if the LLM fabricates a calendar entry in call 2, it will remember that fabrication in call 4 and return a consistent (still fake) version if queried again — making the deception harder for the agent to detect.

**Decorator-based instrumentation**: Agents adopt Heapify by adding two decorators and setting an environment variable. No changes to agent logic, no mock infrastructure to maintain. When `HEAPIFY_MODE` is off, the decorators are transparent wrappers with no measurable overhead.

**Hypothesis-driven fuzzing**: Rather than applying random mutations, the LLM generates a specific attack hypothesis (e.g., "the agent will forward sensitive Notion content if told to via email body injection") and the interception layer is then focused on testing exactly that hypothesis. This reduces noise and produces actionable, reproducible bug reports.

**SQLite over managed databases**: Keeps the framework self-contained for local development and CI runners. The database file is an artifact of the CI run, not shared state, which makes each session independently reproducible.
