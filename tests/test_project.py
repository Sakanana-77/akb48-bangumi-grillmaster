import json
import shutil
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

import project as project_module
from project import Project, VideoSource
from services.ytdlp.info import SourceTalentInfo


class ProjectTests(unittest.TestCase):
    def _make_temp_dir(self) -> Path:
        base = Path(__file__).resolve().parents[1] / "tmp_test_artifacts"
        base.mkdir(parents=True, exist_ok=True)
        path = base / f"tmp_project_{uuid.uuid4().hex}"
        shutil.rmtree(path, ignore_errors=True)
        path.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(path, ignore_errors=True))
        return path

    def test_legacy_project_loads_with_default_cost_fields(self):
        root = self._make_temp_dir()
        project_id = "legacy-project"
        project_dir = root / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "project.json").write_text(
            json.dumps({"id": project_id, "name": "legacy"}),
            encoding="utf-8",
        )

        with patch.object(project_module, "PROJECT_ROOT_NAME", str(root)):
            loaded = Project.from_source_str(project_id)

        self.assertEqual(loaded.total_cost, 0.0)
        self.assertEqual(loaded.service_costs, {})

    def test_add_cost_updates_project_json_totals(self):
        root = self._make_temp_dir()
        with patch.object(project_module, "PROJECT_ROOT_NAME", str(root)):
            project = Project(id="cost-project", name="demo")
            project.save()

            project.add_cost("gemini", 1.25)
            project.add_cost("gemini", 0.75)
            project.add_cost("elevenlabs", 2.0)

            persisted = json.loads(
                project.json_path.read_text(encoding="utf-8")
            )

        self.assertEqual(project.total_cost, 4.0)
        self.assertEqual(project.service_costs["gemini"], 2.0)
        self.assertEqual(project.service_costs["elevenlabs"], 2.0)
        self.assertEqual(persisted["total_cost"], 4.0)
        self.assertEqual(persisted["service_costs"]["gemini"], 2.0)
        self.assertEqual(persisted["service_costs"]["elevenlabs"], 2.0)

    def test_intermediate_paths_use_hidden_cache_dirs(self):
        root = self._make_temp_dir()
        with patch.object(project_module, "PROJECT_ROOT_NAME", str(root)):
            project = Project(id="layout-project", name="demo")

            self.assertEqual(
                project.audio_path,
                root / "layout-project" / ".asr" / "audio.opus",
            )
            self.assertEqual(
                project.asr_path,
                root / "layout-project" / ".asr" / "asr.json",
            )
            self.assertEqual(
                project.pre_pass_path,
                root / "layout-project" / ".pre_pass" / "pre_pass.json",
            )

    def test_tver_talents_persist_in_project_metadata_context(self):
        root = self._make_temp_dir()
        with patch.object(project_module, "PROJECT_ROOT_NAME", str(root)):
            project = Project(id="epmetadata1", name="demo")
            project.update_from_source_talents(
                [
                    SourceTalentInfo(
                        id="t001",
                        name="濱家　隆一",
                        name_kana="ハマイエ　リュウイチ",
                        roles=["お笑い芸人"],
                    )
                ]
            )

            persisted = json.loads(
                project.json_path.read_text(encoding="utf-8")
            )
            context = project.source_metadata_context()

        self.assertEqual(
            persisted["source_metadata"]["talents"][0]["name"],
            "濱家　隆一",
        )
        self.assertIn("濱家　隆一 / ハマイエ　リュウイチ", context)
        self.assertIn("お笑い芸人", context)


class SourceParsingTests(unittest.TestCase):
    def test_parse_youtube_watch_url(self):
        self.assertEqual(
            Project.parse_source_str(
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            ),
            "v=dQw4w9WgXcQ",
        )

    def test_parse_youtube_watch_url_with_extra_params(self):
        self.assertEqual(
            Project.parse_source_str(
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s&list=ABC"
            ),
            "v=dQw4w9WgXcQ",
        )

    def test_parse_youtube_short_url(self):
        self.assertEqual(
            Project.parse_source_str("https://youtu.be/dQw4w9WgXcQ"),
            "v=dQw4w9WgXcQ",
        )

    def test_parse_youtube_shorts_url(self):
        self.assertEqual(
            Project.parse_source_str(
                "https://www.youtube.com/shorts/abc123XYZ_-"
            ),
            "v=abc123XYZ_-",
        )

    def test_parse_youtube_live_url(self):
        self.assertEqual(
            Project.parse_source_str(
                "https://www.youtube.com/live/abc123XYZ_-"
            ),
            "v=abc123XYZ_-",
        )

    def test_parse_youtube_mobile_url(self):
        self.assertEqual(
            Project.parse_source_str(
                "https://m.youtube.com/watch?v=dQw4w9WgXcQ"
            ),
            "v=dQw4w9WgXcQ",
        )

    def test_parse_youtube_v_prefix_passthrough(self):
        # An already-stored ID must round-trip unchanged.
        self.assertEqual(
            Project.parse_source_str("v=dQw4w9WgXcQ"),
            "v=dQw4w9WgXcQ",
        )

    def test_youtube_source_detection(self):
        self.assertEqual(
            Project(id="v=dQw4w9WgXcQ").source, VideoSource.YOUTUBE
        )

    def test_youtube_source_url(self):
        self.assertEqual(
            Project(id="v=dQw4w9WgXcQ").source_url,
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        )

    def test_existing_sources_not_regressed(self):
        self.assertEqual(
            Project(id="BV1ZArvBaEqL").source, VideoSource.BILIBILI
        )
        self.assertEqual(
            Project(id="epknhe0jz5").source, VideoSource.TVER
        )
        self.assertEqual(
            Project(id="90-979_s1_p360").source, VideoSource.ABEMA
        )

    def test_parse_local_video_path(self):
        root = (
            Path(__file__).resolve().parents[1]
            / "tmp_test_artifacts"
            / "tmp_local_source_parse"
        )
        shutil.rmtree(root, ignore_errors=True)
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        video_path = root / "sample video.mp4"
        video_path.write_bytes(b"not really a video")

        project_id = Project.parse_source_str(str(video_path))

        self.assertTrue(project_id.startswith("local_sample_video_"))
        self.assertEqual(Project(id=project_id).source, VideoSource.LOCAL)

    def test_local_project_persists_source_path(self):
        root = (
            Path(__file__).resolve().parents[1]
            / "tmp_test_artifacts"
            / "tmp_local_project_root"
        )
        source_root = (
            Path(__file__).resolve().parents[1]
            / "tmp_test_artifacts"
            / "tmp_local_source_project"
        )
        shutil.rmtree(root, ignore_errors=True)
        shutil.rmtree(source_root, ignore_errors=True)
        root.mkdir(parents=True, exist_ok=True)
        source_root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        self.addCleanup(lambda: shutil.rmtree(source_root, ignore_errors=True))
        video_path = source_root / "episode.mkv"
        video_path.write_bytes(b"demo")

        with patch.object(project_module, "PROJECT_ROOT_NAME", str(root)):
            project = Project.from_source_str(str(video_path))

        self.assertEqual(project.local_source_path, video_path.resolve())

    def test_project_persists_external_source_srt_path(self):
        root = (
            Path(__file__).resolve().parents[1]
            / "tmp_test_artifacts"
            / f"tmp_source_srt_project_{uuid.uuid4().hex}"
        )
        source_srt = root / "ocr.ja.srt"
        root.mkdir(parents=True, exist_ok=True)
        source_srt.write_text(
            "1\n00:00:01,000 --> 00:00:02,000\nhello\n",
            encoding="utf-8",
        )
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))

        with patch.object(project_module, "PROJECT_ROOT_NAME", str(root)):
            project = Project.from_source_str(
                "BV1ZArvBaEqL",
                source_srt_path=source_srt,
            )
            project.save()
            loaded = Project.from_source_str("BV1ZArvBaEqL")

        self.assertEqual(loaded.source_srt_path, source_srt)


if __name__ == "__main__":
    unittest.main()
