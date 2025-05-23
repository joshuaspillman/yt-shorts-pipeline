import logging, subprocess
from pathlib import Path
from multiprocessing import Pool, cpu_count
from scenedetect import ContentDetector, SceneManager, detect

logging.basicConfig(level=logging.INFO)

class Clipper:
    def __init__(self, out_dir, processes=None):
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.processes = processes or cpu_count()

    def _run_ffmpeg(self, args):
        video, start, end, idx = args
        out = self.out_dir / f"clip_{idx}.mp4"
        cmd = ['ffmpeg','-y','-ss',str(start),'-to',str(end),'-i',video,'-c','copy',str(out)]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return str(out)

    def detect_scenes(self, video_path):
        mgr = SceneManager(); mgr.add_detector(ContentDetector(threshold=30.0))
        scenes = detect(video_path, mgr)
        times = [(s[0].get_seconds(), s[1].get_seconds()) for s in scenes]
        logging.info("Detected %d scenes", len(times))
        return times

    def extract_clips(self, video_path, use_scenes=True, timestamps=None):
        if use_scenes:
            timestamps = self.detect_scenes(video_path)
        args = [(video_path, s, e, i) for i,(s,e) in enumerate(timestamps)]
        with Pool(self.processes) as p:
            clips = p.map(self._run_ffmpeg, args)
        logging.info("Extracted %d clips", len(clips))
        return clips
