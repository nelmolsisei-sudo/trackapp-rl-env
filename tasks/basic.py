"""Basic difficulty tasks for trackapp.

Each task is a scenario that handles its own setup and grading.
Basic tasks involve single-file fixes with isolated, well-scoped bugs.
"""

from env import env, setup_task, make_prompt
from grading import AgentPatchGrader, Grade, ValidateMode

DJANGO_TEST = "python manage.py test {module} --verbosity=2"


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
            test_command=DJANGO_TEST.format(module="tests.test_result_crud"),
        )
    ])
    yield grade.score


@env.scenario("fix-profile-404")
async def fix_profile_404(hints_enabled: bool = False, validate_mode: ValidateMode | None = None):
    """Fix profile view to return 404 for non-existent users."""

    setup_task(
        task_id="fix_profile_404",
        base="fix_profile_404_baseline",
        test="fix_profile_404_test",
        golden="fix_profile_404_golden",
        validate_mode=validate_mode,
    )

    prompt = make_prompt("""Fix the profile view in views.py to handle non-existent users properly.

Currently, visiting the profile page for a user that doesn't exist causes
a server error (500). The view should return a proper 404 Not Found response
instead. Django provides utilities for this pattern.""")

    _ = yield prompt

    grade = Grade.from_subscores([
        AgentPatchGrader.grade(
            weight=1.0,
            problem_id="fix_profile_404",
            test_files=["tests/test_profile_404.py"],
            validate_mode=validate_mode,
            test_command=DJANGO_TEST.format(module="tests.test_profile_404"),
        )
    ])
    yield grade.score


@env.scenario("fix-merge-meet-auth")
async def fix_merge_meet_auth(hints_enabled: bool = False, validate_mode: ValidateMode | None = None):
    """Fix merge_meet view to require authentication."""

    setup_task(
        task_id="fix_merge_meet_auth",
        base="fix_merge_meet_auth_baseline",
        test="fix_merge_meet_auth_test",
        golden="fix_merge_meet_auth_golden",
        validate_mode=validate_mode,
    )

    prompt = make_prompt("""Fix the merge_meet view in views.py to require authentication.

The merge_meet view allows any unauthenticated user to merge meets, which is
a destructive operation that should only be available to logged-in users.
Other similar administrative views in the codebase already enforce this
requirement. Make merge_meet consistent with those views.""")

    _ = yield prompt

    grade = Grade.from_subscores([
        AgentPatchGrader.grade(
            weight=1.0,
            problem_id="fix_merge_meet_auth",
            test_files=["tests/test_merge_meet_auth.py"],
            validate_mode=validate_mode,
            test_command=DJANGO_TEST.format(module="tests.test_merge_meet_auth"),
        )
    ])
    yield grade.score


@env.scenario("fix-register-validation")
async def fix_register_validation(hints_enabled: bool = False, validate_mode: ValidateMode | None = None):
    """Fix register view to validate password length."""

    setup_task(
        task_id="fix_register_validation",
        base="fix_register_validation_baseline",
        test="fix_register_validation_test",
        golden="fix_register_validation_golden",
        validate_mode=validate_mode,
    )

    prompt = make_prompt("""Fix the register view in views.py to validate password length.

The registration form currently accepts passwords of any length, including
empty strings. Add validation to require passwords to be at least 8
characters long. If the password is too short, re-render the registration
page with an appropriate error message, following the same pattern used
for the existing password-mismatch check.""")

    _ = yield prompt

    grade = Grade.from_subscores([
        AgentPatchGrader.grade(
            weight=1.0,
            problem_id="fix_register_validation",
            test_files=["tests/test_register_validation.py"],
            validate_mode=validate_mode,
            test_command=DJANGO_TEST.format(module="tests.test_register_validation"),
        )
    ])
    yield grade.score


@env.scenario("fix-remove-safety")
async def fix_remove_safety(hints_enabled: bool = False, validate_mode: ValidateMode | None = None):
    """Fix remove_coach and remove_athlete views to require POST."""

    setup_task(
        task_id="fix_remove_safety",
        base="fix_remove_safety_baseline",
        test="fix_remove_safety_test",
        golden="fix_remove_safety_golden",
        validate_mode=validate_mode,
    )

    prompt = make_prompt("""Fix the remove_coach and remove_athlete_from_team views in views.py.

Both views currently process their destructive actions (removing a coach or
athlete from a team) on any HTTP request, including GET. This is unsafe
because GET requests should never have side effects. A simple link or
browser prefetch could accidentally trigger removals.

Both views should reject non-POST requests with an appropriate HTTP status
code and only perform the removal when the request method is POST.""")

    _ = yield prompt

    grade = Grade.from_subscores([
        AgentPatchGrader.grade(
            weight=1.0,
            problem_id="fix_remove_safety",
            test_files=["tests/test_remove_safety.py"],
            validate_mode=validate_mode,
            test_command=DJANGO_TEST.format(module="tests.test_remove_safety"),
        )
    ])
    yield grade.score
