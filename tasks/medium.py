"""Medium difficulty tasks.

Each task is a scenario that handles its own setup and grading.
Medium tasks require multi-file understanding, domain-specific reasoning,
or cross-framework knowledge (e.g. Solidity smart contracts).
"""

from env import env, setup_task, make_prompt
from grading import AgentPatchGrader, Grade, GradingRunner, ValidateMode


@env.scenario("fix-erc20-vulnerabilities")
async def fix_erc20_vulnerabilities(hints_enabled: bool = False, validate_mode: ValidateMode | None = None):
    """Fix security vulnerabilities in an ERC-20 token smart contract."""

    setup_task(
        task_id="smart_contract_erc20",
        base="smart_contract_erc20_baseline",
        test="smart_contract_erc20_test",
        golden="smart_contract_erc20_golden",
        validate_mode=validate_mode,
    )

    prompt = make_prompt("""Fix the security vulnerabilities in the ERC-20 token contract at src/Token.sol.

The contract has three categories of critical vulnerabilities:

1. **Access control**: The mint() function can be called by anyone, not just
   the contract owner. This allows arbitrary token inflation.

2. **Balance validation**: The transfer() function does not verify that the
   sender has sufficient balance before transferring, and does not guard
   against transfers to the zero address.

3. **Allowance validation**: The transferFrom() function does not verify that
   the spender has sufficient allowance or that the source has sufficient
   balance, and does not guard against transfers to the zero address.

Add the appropriate require() statements to fix all three categories. Use
descriptive revert messages. The approve() function is already correct.

This is a Foundry project. You can compile with `forge build` and run any
existing tests with `forge test`.""")

    _ = yield prompt

    grade = Grade.from_subscores([
        AgentPatchGrader.grade(
            weight=1.0,
            problem_id="smart_contract_erc20",
            test_files=[],
            test_command="forge test -vvv",
            runner_class=GradingRunner,
            validate_mode=validate_mode,
        )
    ])
    yield grade.score
