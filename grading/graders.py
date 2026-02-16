"""Graders for evaluating agent solutions."""

import os

from .django_runner import DjangoGradingRunner
from .runner import GradingRunner
from .spec import Grader, ValidateMode


class AgentPatchGrader(Grader):
    """
    Grader that applies test.patch and runs tests.

    Defaults to DjangoGradingRunner (copies repo into a subdirectory matching
    the package name for correct import resolution). Pass runner_class to
    override -- e.g. GradingRunner for non-Django projects like Foundry.

    Usage:
        AgentPatchGrader.grade(
            weight=1.0,
            problem_id="my_task",
            test_files=["test_foo.py"],
        )

    Custom test command:
        AgentPatchGrader.grade(
            weight=1.0,
            problem_id="my_task",
            test_files=["tests/test_foo.py"],
            test_command="python manage.py test tests.test_foo --verbosity=2",
        )

    Non-Django runner (e.g. Foundry smart contracts):
        AgentPatchGrader.grade(
            weight=1.0,
            problem_id="smart_contract_erc20",
            test_files=[],
            test_command="forge test -vvv",
            runner_class=GradingRunner,
        )
    """

    name = "AgentPatchGrader"
    DEFAULT_TEST_COMMAND = "uv run pytest {test_files}"

    @classmethod
    def compute_score(
        cls,
        test_files: list[str],
        problem_id: str | None = None,
        test_command: str | None = None,
        validate_mode: ValidateMode | None = None,
        runner_class: type | None = None,
        **kwargs,
    ) -> tuple[float, dict]:
        """
        Run tests and return score.

        Args:
            test_files: Test files to run
            problem_id: Problem ID for patches (default: PROBLEM_ID env)
            test_command: Test command with {test_files} placeholder
            runner_class: GradingRunner subclass to use (default: DjangoGradingRunner)

        Returns:
            (score, metadata) - score is 1.0 if tests pass, 0.0 otherwise
        """
        pid = problem_id or os.environ.get("PROBLEM_ID")
        if not pid:
            raise ValueError("problem_id required (or set PROBLEM_ID env)")

        cmd = test_command or cls.DEFAULT_TEST_COMMAND

        RunnerClass = runner_class or DjangoGradingRunner
        runner = RunnerClass(
            problem_id=pid,
            test_command=cmd,
            test_files=test_files,
        )

        score = runner.grade()

        # when testing with baseline fail, we want to ensure that the
        # baseline actually fails, so we invert the score
        if validate_mode == "baseline_fail":
            score = 1.0 if score == 0.0 else 0.0

        return (score, {})
