import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.request import urlopen

from reliability_monitor.core import (
    ValidationError,
    compare_treatments,
    get_alerts,
    get_overview,
    import_csv,
    insert_run,
)
from reliability_monitor.server import build_server


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "tables" / "mseg_rain_instance_miou_summary.csv"


class ReliabilityMonitorTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.database = Path(self.temp_directory.name) / "monitor.db"

    def tearDown(self):
        self.temp_directory.cleanup()

    def seed(self):
        return import_csv(self.database, RESULTS)

    def test_imports_recorded_results_idempotently(self):
        self.assertEqual(self.seed(), 45)
        self.assertEqual(self.seed(), 45)
        overview = get_overview(self.database)
        self.assertEqual(overview["run_count"], 45)
        self.assertEqual(len(overview["groups"]), 15)
        self.assertEqual(overview["treatments"][0]["treatment"], "idt")

    def test_flags_low_consistency_and_severity_degradation(self):
        self.seed()
        report = get_alerts(
            self.database, minimum_mean=0.70, maximum_severity_drop=0.12
        )
        alert_types = {alert["type"] for alert in report["alerts"]}
        self.assertIn("condition_below_threshold", alert_types)
        self.assertIn("severity_degradation", alert_types)

    def test_compares_candidate_with_baseline(self):
        self.seed()
        comparison = compare_treatments(self.database, "idt", "nerdrain")
        self.assertTrue(comparison["regression"])
        self.assertGreater(comparison["overall_delta"], -0.01)
        heavy = next(
            row for row in comparison["conditions"] if row["severity"] == "heavy"
        )
        self.assertGreater(heavy["delta"], 0)

    def test_rejects_invalid_metric(self):
        invalid = {
            "segmentor": "mseg",
            "treatment": "candidate",
            "severity": "heavy",
            "variant": "v1",
            "sample_count": 50,
            "mean_miou": 1.2,
            "median_miou": 0.6,
            "std_miou": 0.1,
            "min_miou": 0.4,
            "max_miou": 0.8,
        }
        with self.assertRaises(ValidationError):
            insert_run(self.database, invalid)

    def test_rejects_invalid_alert_threshold(self):
        with self.assertRaises(ValidationError):
            get_alerts(self.database, minimum_mean=1.1)

    def test_http_health_and_overview(self):
        self.seed()
        try:
            server = build_server(self.database, port=0)
        except PermissionError:
            self.skipTest("local sandbox does not allow binding a test port")
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            base_url = f"http://127.0.0.1:{server.server_port}"
            with urlopen(f"{base_url}/health", timeout=2) as response:
                self.assertEqual(json.load(response), {"status": "ok"})
            with urlopen(f"{base_url}/api/overview", timeout=2) as response:
                self.assertEqual(json.load(response)["run_count"], 45)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
