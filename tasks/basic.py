"""Basic difficulty tasks for trackapp.

Each task is a scenario that handles its own setup and grading.
"""

from env import env, setup_task, make_prompt
from grading import AgentPatchGrader, Grade, ValidateMode


@env.scenario("fix-result-crud")
async def fix_result_crud(hints_enabled: bool = False, validate_mode: ValidateMode | None = None):
    """Fix bugs in result management views (add, edit, delete)."""

    setup_task(
        task_id="fix_result_crud",
        base="fix_result_crud_baseline",
        test="fix_result_crud_test",
        golden="fix_result_crud_golden",
        validate_mode=validate_mode,
    )

    prompt = make_prompt("""Fix the bugs in the result management views (add, edit, delete) in views.py.

After adding or deleting results, the athlete's personal records, rankings,
and milestones are not being updated correctly. Additionally, the edit result
view passes incorrect data to its template context. Compare the behavior of
the different result views and the calculate_result_stats function to
understand the expected behavior.""")

    _ = yield prompt

    grade = Grade.from_subscores([
        AgentPatchGrader.grade(
            weight=1.0,
            problem_id="fix_result_crud",
            test_files=["tests/test_result_crud.py"],
            validate_mode=validate_mode,
            test_command="python manage.py test tests.test_result_crud --verbosity=2",
        )
    ])
    yield grade.score
