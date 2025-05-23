import yaml
import logging
from src.fetcher.fetcher import Fetcher
from src.clipper.clipper import Clipper
from src.editor.editor import Editor
from src.metadata.metadata import MetadataGenerator
from src.uploader.uploader import Uploader

logging.basicConfig(level=logging.INFO)

class Orchestrator:
    def __init__(self, config_path="configs/config.yaml"):
        cfg = yaml.safe_load(open(config_path))
        self.niche = cfg["niche"]

        self.fetcher = Fetcher(
            cfg["fetcher"]["sources"],
            cfg["fetcher"].get("max_workers", 5)
        )
        self.clipper = Clipper(
            cfg["clipper"]["output_dir"],
            cfg["clipper"].get("processes")
        )
        self.editor = Editor(cfg["editor"]["template"])
        self.meta = MetadataGenerator(
            cfg["openai_key"],
            cfg.get("metadata_rate_limit", 30)
        )
        self.uploader = Uploader(
            cfg["uploader"]["credentials"],
            cfg["uploader"]["token"],
            cfg["uploader"].get("retries", 3)
        )

    def run(self):
        videos = self.fetcher.get_videos()
        for vid in videos:
            try:
                clips = self.clipper.extract_clips(
                    vid,
                    use_scenes=cfg["clipper"].get("scene_detect", True)
                )
                short_path = self.editor.format_short(clips)
                meta_json = self.meta.create_metadata(short_path, self.niche)
                video_id = self.uploader.upload(short_path, meta_json)
                print(f"✅ https://youtu.be/{video_id}")
            except Exception as e:
                logging.error("Pipeline failed for %s: %s", vid, e)

if __name__ == "__main__":
    Orchestrator().run()
