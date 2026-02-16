# trackapp-rl-env

**A reinforcement learning environment for evaluating AI agents on real-world Django application bug-fixing.**

Built on [HUD](https://hud.ai) infrastructure. Targets [trackapp-target](https://github.com/nelmolsisei-sudo/trackapp-target).

---

## Why RL Environments Matter

The next phase of AI capability isn't about larger context windows or cheaper inference. It's about closing the loop between model output and real-world consequence. Reinforcement learning environments are the mechanism that closes it.

Every frontier lab has converged on the same conclusion: post-training on agentic trajectories produces models that don't just predict code, they *reason about systems*. They navigate ambiguity, recover from dead ends, and verify their own work. But the quality ceiling of these models is entirely determined by the quality of the environments they train against.

The environments that exist today are overwhelmingly synthetic. Contrived puzzles, isolated function completions, toy codebases designed to be solvable rather than realistic. They've been sufficient for climbing benchmarks, but they produce agents that are brittle in exactly the ways real-world software is not brittle: agents that hallucinate APIs, misunderstand data flow across modules, and cannot reason about the second-order effects of a change.

The environments that will define the next generation of capable models are those grounded in real applications with real architectural decisions, real accumulated technical debt, and real domain complexity. They are environments where the "right answer" requires the same kind of holistic system understanding that a human engineer develops over months of working in a codebase.

This repository is one such environment.

## Smart Contract Security: The Highest-Stakes Frontier

Of all the domains where autonomous coding agents will operate, smart contract development may be the one where capability gaps are most consequential and RL environments are most urgently needed.

Smart contracts are immutable. Once deployed to an EVM-compatible chain -- Ethereum, Monad, Arbitrum, Base -- there is no hotfix, no rollback, no patch Tuesday. A single missing `require` statement can drain millions. The history of on-chain exploits makes this concrete: the DAO hack ($60M, 2016), Wormhole ($320M, 2022), Ronin Bridge ($625M, 2022), and dozens of others -- each traceable to a vulnerability that a competent auditor would have caught in review. The total value lost to smart contract bugs exceeds $5 billion.

This creates a unique alignment between AI capability and economic value. An agent that can reliably identify and fix access control violations, reentrancy risks, integer overflow patterns, and validation gaps in Solidity contracts is not solving an academic exercise -- it is performing work that currently costs $50,000-$500,000 per audit engagement and still misses critical bugs.

But building agents that are *actually reliable* at this requires RL environments that test the right things: not toy contracts with a single planted bug, but realistic token implementations with the same categories of vulnerability that appear in production DeFi protocols. The ERC-20 standard alone -- the most basic building block of on-chain finance -- has been the source of hundreds of exploits when implemented without proper guards.

This environment includes Solidity smart contract tasks graded via Foundry's `forge test`, targeting EVM-compatible chains. Because Monad, Ethereum, and all major L2s share the same EVM execution model, agents trained on these tasks generalize across the entire EVM ecosystem. The near-term roadmap includes ERC-721 (NFT) implementations, DeFi protocol interactions, and multi-contract security auditing tasks.

## What This Environment Does

`trackapp-rl-env` presents AI agents with a real Django web application -- a track and field performance management system used for recording athlete results, managing teams, tracking personal records, computing milestones, and coordinating qualifying standards across seasons. The application has real models with foreign key relationships, real views with authentication requirements, real business logic for statistical computation, and real bugs.

Each task places the agent inside a Docker container with the full application codebase, a bash shell, and a file editor. The agent receives a natural language description of a problem. It must explore the codebase, understand the architecture, identify the root cause, and implement a correct fix. Its solution is then graded against a hidden test suite that was never visible to the agent.

This is not prompt engineering. This is not completion. This is autonomous software engineering under uncertainty, the exact capability that determines whether AI agents can be trusted with real work.

### Current Task Inventory

**Basic (5 tasks)** -- single-file Django fixes, isolated bugs, well-scoped:

| Task | Bug | Domain |
|------|-----|--------|
| `fix-result-crud` | Missing stat recalculation on add/delete; incorrect template context on edit | Data integrity, view logic |
| `fix-profile-404` | Server crash (500) on non-existent user profile instead of 404 | Error handling |
| `fix-merge-meet-auth` | Destructive merge operation accessible without authentication | Security, authorization |
| `fix-register-validation` | User registration accepts empty/trivially short passwords | Input validation |
| `fix-remove-safety` | Destructive team membership changes processed on GET requests | HTTP method safety |

**Medium (1 task)** -- cross-domain, multi-vulnerability, requires Solidity/EVM knowledge:

| Task | Bug | Domain |
|------|-----|--------|
| `fix-erc20-vulnerabilities` | Missing access control on mint, no balance/allowance validation on transfers, no zero-address guards | Smart contract security, ERC-20, Solidity |

**Hard tasks are in active development**, targeting multi-contract interactions, DeFi protocol logic, and architectural smart contract patterns.

### Validation Results

All tasks pass the dual-validation invariant:
- **baseline_fail**: the buggy codebase correctly fails the hidden tests (reward = 1.0 inverted)
- **golden_pass**: the reference solution correctly passes all hidden tests (reward = 1.0)

On initial agent evaluation (Claude, 20 steps max), all 5 basic tasks achieved **reward = 1.0**. This confirms the tasks are well-formed and solvable, while establishing a performance baseline for comparison against other models and architectures.

## Architecture

```
trackapp-rl-env/          # This repo: environment definition
  Dockerfile.hud          # Container image (Ubuntu 24.04 + Django + Foundry + HUD MCP server)
  env.py                  # Tool definitions (bash, editor) and scenario helpers
  tasks/
    basic.py              # Basic difficulty scenarios (Django bug-fixes)
    medium.py             # Medium difficulty scenarios (Solidity smart contracts)
    hard.py               # Hard difficulty scenarios (in progress)
  grading/
    django_runner.py      # Django-specific test runner with correct sys.path handling
    graders.py            # AgentPatchGrader: pluggable runner (Django or Foundry)
  imagectl4.py            # CLI for build, validate, run, push

trackapp-target/          # Target repo (github.com/nelmolsisei-sudo/trackapp-target)
  Django branches:
    views.py, models.py   # Django application source
    {task}_baseline        # Contains the bug
    {task}_golden          # Contains the reference fix
    {task}_test            # Contains the hidden test suite
  Solidity branches (orphan -- separate file tree):
    src/Token.sol          # ERC-20 token contract (Foundry project)
    foundry.toml           # Foundry configuration
    {task}_baseline        # Contains the vulnerable contract
    {task}_golden          # Contains the secure implementation
    {task}_test            # Contains the Forge test suite
```

At runtime, the environment:
1. Clones `trackapp-target` into the container as `/home/ubuntu/trackapp`
2. Checks out the baseline branch (buggy code -- Django or Solidity depending on task)
3. Generates diff patches between branches for grading
4. Presents the agent with tools and a task prompt
5. After the agent finishes, applies the hidden test patch to a copy of the agent's modified repo
6. Runs the appropriate test framework (`python manage.py test` for Django, `forge test` for Solidity) and returns a binary score

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

This environment now spans two distinct domains -- Django application maintenance and Solidity smart contract security -- with a shared evaluation infrastructure. The near-term roadmap includes:

- **Smart contract expansion**: ERC-721 (NFT) token implementations, DeFi protocol interactions (lending, AMM), multi-contract upgrade patterns, and gas optimization tasks targeting Monad and other high-performance EVM chains
- **Hard difficulty tasks**: multi-contract security audits, reentrancy and flash-loan attack prevention, proxy upgrade patterns, and cross-contract state consistency
- **Django expansion**: multi-file fixes requiring understanding of model-view-template relationships, queryset optimization, and cross-component data flow
- **Domain convergence**: tasks that bridge web2 and web3 -- e.g., fixing a Django backend that serves as an oracle or indexer for on-chain data
- **Evaluation infrastructure**: comparative benchmarking across model families, step-efficiency analysis, and failure mode taxonomy

The long-term vision is a comprehensive evaluation suite that measures not just whether an agent can fix a bug, but whether it can operate as a reliable contributor across the full stack of modern software -- from web applications to immutable on-chain protocols where mistakes are permanent and consequences are measured in millions.

## License

MIT
