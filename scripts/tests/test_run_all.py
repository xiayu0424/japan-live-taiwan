import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.crawlers import run_all


class RunAllIntegrationTest(unittest.TestCase):
    def test_main_splits_duplicates_into_change_requests(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            data_dir = root / "public" / "data"
            config_path = root / "scripts" / "configs" / "crawler_sources.yaml"
            data_dir.mkdir(parents=True)
            config_path.parent.mkdir(parents=True)

            (data_dir / "artists.json").write_text(
                json.dumps(
                    [
                        {"id": "lisa", "name": "LiSA", "aliases": ["LiSA"]},
                        {"id": "hikari-loop", "name": "Hikari Loop", "aliases": ["Hikari Loop"]},
                        {"id": "yuta-orisaka", "name": "折坂悠太", "aliases": ["折坂悠太", "Yuta Orisaka"]},
                    ],
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            (data_dir / "events.json").write_text(
                json.dumps(
                    [
                        {
                            "id": "lisa-live-is-smile-always-15-2026-taipei",
                            "title": "LiSA LiVE is Smile Always～15～ in Taipei",
                            "artist_ids": ["lisa"],
                            "status": "sale_soon",
                            "shows": [{"date": "2026-06-19", "venue_name": "台北小巨蛋"}],
                            "ticket_sales": [],
                            "prices": [],
                            "organizers": ["Mock Source"],
                        }
                    ],
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            config_path.write_text(
                "\n".join(
                    [
                        "sources:",
                        "  - id: mock",
                        "    name: Mock crawler",
                        "    enabled: true",
                        "    crawler: mock",
                        '    base_url: "https://example.org"',
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            with patch.object(run_all, "CONFIG_PATH", config_path), patch.object(run_all, "DATA_DIR", data_dir), patch.object(
                run_all, "CANDIDATES_PATH", data_dir / "candidates.json"
            ), patch.object(run_all, "CHANGE_REQUESTS_PATH", data_dir / "change_requests.json"), patch.object(
                run_all, "CRAWLER_REPORT_PATH", data_dir / "crawler_report.json"
            ):
                run_all.main()

            candidates = json.loads((data_dir / "candidates.json").read_text(encoding="utf-8"))
            change_requests = json.loads((data_dir / "change_requests.json").read_text(encoding="utf-8"))
            report = json.loads((data_dir / "crawler_report.json").read_text(encoding="utf-8"))

            self.assertEqual(len(candidates), 2)
            self.assertEqual(len(change_requests), 1)
            self.assertEqual(change_requests[0]["existing_event_id"], "lisa-live-is-smile-always-15-2026-taipei")
            self.assertEqual(change_requests[0]["detected_changes"]["match_type"], "possible_update")
            self.assertEqual(report["summary"]["total_candidates"], 2)
            self.assertEqual(report["summary"]["change_requests"], 1)
            self.assertEqual(report["sources"][0]["candidate_count"], 2)
            self.assertEqual(report["sources"][0]["change_request_count"], 1)


if __name__ == "__main__":
    unittest.main()
