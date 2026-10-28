"""Regression checks for public source archives and optional viewer isolation."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from package_delivery import package_project
from sync_report_viewer import sync_source


class DeliveryContracts(unittest.TestCase):
    def test_package_ignores_thesis_and_untracked_local_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            (root / "README.md").write_text("tracked source", encoding="utf-8")
            (root / ".gitignore").write_text("thesis_source/\n", encoding="utf-8")
            (root / "thesis_source").mkdir()
            (root / "thesis_source/page.txt").write_text("local document", encoding="utf-8")
            (root / "untracked.txt").write_text("not approved for export", encoding="utf-8")
            subprocess.run(["git", "add", "README.md", ".gitignore"], cwd=root, check=True)
            target = root / "output.zip"
            package_project(root, target)
            with ZipFile(target) as archive:
                self.assertEqual(set(archive.namelist()), {"README.md", ".gitignore", "DELIVERY_MANIFEST.json"})
                self.assertEqual(archive.read("README.md"), b"tracked source")

    def test_viewer_sync_preserves_identity_without_editing_compiled_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "report-app/src/data.json"
            dist = root / "report-app/dist/index.html"
            report = root / "reports/reviewed_snapshot.json"
            for path in (source, dist, report):
                path.parent.mkdir(parents=True, exist_ok=True)
            source.write_text('{"id":"stable-id"}', encoding="utf-8")
            dist.write_text("compiled bundle", encoding="utf-8")
            report.write_text('{"title":"updated", "buildStatus":"creating"}', encoding="utf-8")
            sync_source(root)
            result = json.loads(source.read_text(encoding="utf-8"))
            self.assertEqual(result, {"title": "updated", "id": "stable-id"})
            self.assertEqual(dist.read_text(), "compiled bundle")


if __name__ == "__main__":
    unittest.main()
