"""
Django-specific grading runner.

Handles the Django project structure where manage.py adds its parent
directory to sys.path. The repo must be copied into a subdirectory
named after the Django package (e.g. /tmp/grading_<uuid>/trackapp/)
so that 'import trackapp' resolves correctly.
"""

import logging
import os
import subprocess
import uuid

from .runner import GradingRunner

logger = logging.getLogger(__name__)


class DjangoGradingRunner(GradingRunner):
    """Grading runner for Django projects.

    Overrides the grade() method to copy the repo into a subdirectory
    matching the Django package name (FOLDER_NAME), so that manage.py's
    sys.path manipulation resolves correctly.

    Usage:
        runner = DjangoGradingRunner(
            problem_id="fix_result_crud",
            test_command="python manage.py test tests.test_result_crud --verbosity=2",
            test_files=["tests/test_result_crud.py"],
        )
        score = runner.grade()
    """

    def grade(self) -> float:
        """Run grading with Django-compatible directory structure.

        Returns:
            1.0 if tests pass, 0.0 otherwise
        """
        folder_name = os.environ.get("FOLDER_NAME", "trackapp")

        # Create base directory and copy repo into a subdirectory named
        # after the Django package, so manage.py's sys.path.insert(0, '..')
        # makes the package importable.
        base_dir = f"/tmp/grading_{uuid.uuid4()}"
        self.working_dir = os.path.join(base_dir, folder_name)
        os.makedirs(base_dir, exist_ok=True)

        logger.info(f"Copying repo to {self.working_dir}")
        subprocess.run(
            ["cp", "-rT", self.repo_path, self.working_dir],
            check=True,
        )

        # Apply test patch (adds test files)
        logger.info(f"Applying test patch: {self.test_patch}")
        with open(self.test_patch) as f:
            patch_content = f.read()

        if patch_content.strip():
            subprocess.run(
                ["git", "apply"],
                cwd=self.working_dir,
                input=patch_content.encode(),
                check=True,
            )

        # Run tests
        success, metadata = self.run_tests()

        return 1.0 if success else 0.0
