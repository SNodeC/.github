"""Check the retained organization workflow's execution boundary."""
from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]


class OrganizationWorkflowTests(unittest.TestCase):
    def test_control_checks_are_independent_and_read_only(self):
        ci = yaml.load((ROOT / ".github/workflows/validate-organization.yml").read_text(), Loader=yaml.BaseLoader)
        self.assertEqual(ci["on"], ["push", "pull_request", "workflow_dispatch"])
        self.assertEqual(ci["permissions"], {"contents": "read"})
        self.assertEqual(set(ci["jobs"]), {"control"})
        control = ci["jobs"]["control"]
        self.assertNotIn("needs", control)
        self.assertEqual(control["runs-on"], "ubuntu-24.04")
        self.assertEqual(control["timeout-minutes"], "15")
        steps = control["steps"]
        checkout = next(s for s in steps if s.get("uses", "").startswith("actions/checkout@"))
        self.assertEqual(checkout["with"]["ref"], "${{ github.event.pull_request.head.sha || github.sha }}")
        self.assertEqual(checkout["with"]["persist-credentials"], "false")
        catalog = next(s for s in steps if s.get("name") == "Check catalog")
        self.assertEqual(catalog["run"], "python tools/snodec_sync check")
        tests = next(s for s in steps if s.get("name") == "Unit and workflow boundary tests")
        self.assertEqual(tests["if"], "${{ always() && !cancelled() }}")
        self.assertEqual(tests["run"], "python -m unittest discover -s tests -v")
        for step in steps:
            if "uses" in step:
                self.assertRegex(step["uses"], r"^actions/(checkout|setup-python)@v[0-9]+$")
