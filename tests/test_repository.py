import json
import py_compile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RepositoryValidationTests(unittest.TestCase):
    def test_notebooks_are_valid_and_have_no_saved_outputs(self):
        notebooks = sorted((ROOT / "notebooks").glob("*.ipynb"))
        self.assertGreater(len(notebooks), 0)

        for notebook_path in notebooks:
            with self.subTest(notebook=notebook_path.name):
                notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
                for cell in notebook.get("cells", []):
                    if cell.get("cell_type") == "code":
                        self.assertEqual(cell.get("outputs", []), [])
                        self.assertIsNone(cell.get("execution_count"))

    def test_python_scripts_compile(self):
        scripts = sorted((ROOT / "scripts").glob("*.py"))
        self.assertGreater(len(scripts), 0)

        for script_path in scripts:
            with self.subTest(script=script_path.name):
                py_compile.compile(str(script_path), doraise=True)

    def test_no_public_file_exceeds_github_limit(self):
        limit = 100 * 1024 * 1024
        oversized = [
            path.relative_to(ROOT)
            for path in ROOT.rglob("*")
            if path.is_file() and ".git" not in path.parts and path.stat().st_size >= limit
        ]
        self.assertEqual(oversized, [])


if __name__ == "__main__":
    unittest.main()
