# trackapp-rl-env

**A reinforcement learning environment for evaluating AI agents on real-world Django application bug-fixing.**

Built on [HUD](https://hud.ai) infrastructure. Targets [trackapp-target](https://github.com/jackdeterman/trackapp-target).

---

## Why RL Environments Matter

The next phase of AI capability isn't about larger context windows or cheaper inference. It's about closing the loop between model output and real-world consequence. Reinforcement learning environments are the mechanism that closes it.

Every frontier lab has converged on the same conclusion: post-training on agentic trajectories produces models that don't just predict code, they *reason about systems*. They navigate ambiguity, recover from dead ends, and verify their own work. But the quality ceiling of these models is entirely determined by the quality of the environments they train against.

The environments that exist today are overwhelmingly synthetic. Contrived puzzles, isolated function completions, toy codebases designed to be solvable rather than realistic. They've been sufficient for climbing benchmarks, but they produce agents that are brittle in exactly the ways real-world software is not brittle: agents that hallucinate APIs, misunderstand data flow across modules, and cannot reason about the second-order effects of a change.

The environments that will define the next generation of capable models are those grounded in real applications with real architectural decisions, real accumulated technical debt, and real domain complexity. They are environments where the "right answer" requires the same kind of holistic system understanding that a human engineer develops over months of working in a codebase.

This repository is one such environment.

## What This Environment Does

`trackapp-rl-env` presents AI agents with a real Django web application -- a track and field performance management system used for recording athlete results, managing teams, tracking personal records, computing milestones, and coordinating qualifying standards across seasons. The application has real models with foreign key relationships, real views with authentication requirements, real business logic for statistical computation, and real bugs.

Each task places the agent inside a Docker container with the full application codebase, a bash shell, and a file editor. The agent receives a natural language description of a problem. It must explore the codebase, understand the architecture, identify the root cause, and implement a correct fix. Its solution is then graded against a hidden test suite that was never visible to the agent.

This is not prompt engineering. This is not completion. This is autonomous software engineering under uncertainty, the exact capability that determines whether AI agents can be trusted with real work.

### Current Task Inventory

**Basic (5 tasks)** -- single-file fixes, isolated bugs, well-scoped:

| Task | Bug | Domain |
|------|-----|--------|
| `fix-result-crud` | Missing stat recalculation on add/delete; incorrect template context on edit | Data integrity, view logic |
| `fix-profile-404` | Server crash (500) on non-existent user profile instead of 404 | Error handling |
| `fix-merge-meet-auth` | Destructive merge operation accessible without authentication | Security, authorization |
| `fix-register-validation` | User registration accepts empty/trivially short passwords | Input validation |
| `fix-remove-safety` | Destructive team membership changes processed on GET requests | HTTP method safety |

**Medium and Hard tasks are in active development**, targeting multi-file bugs, cross-model logic errors, and domain-specific calculation issues.

### Validation Results

All tasks pass the dual-validation invariant:
- **baseline_fail**: the buggy codebase correctly fails the hidden tests (reward = 1.0 inverted)
- **golden_pass**: the reference solution correctly passes all hidden tests (reward = 1.0)

On initial agent evaluation (Claude, 20 steps max), all 5 basic tasks achieved **reward = 1.0**. This confirms the tasks are well-formed and solvable, while establishing a performance baseline for comparison against other models and architectures.

## Architecture

```
trackapp-rl-env/          # This repo: environment definition
  Dockerfile.hud          # Container image (Ubuntu 24.04 + Django + HUD MCP server)
  env.py                  # Tool definitions (bash, editor) and scenario helpers
  tasks/
    basic.py              # Basic difficulty scenarios
    medium.py             # Medium difficulty scenarios (in progress)
    hard.py               # Hard difficulty scenarios (in progress)
  grading/
    django_runner.py      # Django-specific test runner with correct sys.path handling
    graders.py            # AgentPatchGrader: applies hidden tests, runs Django test suite
  imagectl4.py            # CLI for build, validate, run, push

trackapp-target/          # Target repo (github.com/jackdeterman/trackapp-target)
  views.py, models.py     # Django application source
  3 branches per task:
    {task}_baseline        # Contains the bug
    {task}_golden          # Contains the reference fix
    {task}_test            # Contains the hidden test suite
```

At runtime, the environment:
1. Clones `trackapp-target` into the container as `/home/ubuntu/trackapp`
2. Checks out the baseline branch (buggy code)
3. Generates diff patches between branches for grading
4. Presents the agent with tools and a task prompt
5. After the agent finishes, applies the hidden test patch to a copy of the agent's modified repo
6. Runs `python manage.py test` and returns a binary score

## Quick Start

```bash
# Build the Docker image
uv run python imagectl4.py -b

# Validate all scenarios (baseline fails, golden passes)
uv run python imagectl4.py -v

# Run an agent against all scenarios
uv run python imagectl4.py -r

# Run a single scenario
uv run python imagectl4.py -r --ids fix-result-crud

# Build fresh (no Docker cache) and validate
uv run python imagectl4.py -bv --no-cache
```

## Roadmap

This environment currently captures a narrow but representative slice of Django application maintenance: bug identification and repair across views, models, forms, authentication, and data integrity logic. The near-term roadmap includes:

- **Medium difficulty tasks**: multi-file fixes requiring understanding of model-view-template relationships, queryset optimization, and cross-component data flow
- **Hard difficulty tasks**: architectural refactoring, complex business logic errors in statistical computation, and template/URL resolution debugging
- **Domain expansion**: extending beyond bug-fixing into feature implementation, migration authoring, and test writing
- **Evaluation infrastructure**: comparative benchmarking across model families, step-efficiency analysis, and failure mode taxonomy

The long-term vision is a comprehensive evaluation suite that measures not just whether an agent can fix a bug, but whether it can operate as a reliable contributor to a living codebase.

## License

MIT
