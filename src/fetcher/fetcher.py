import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import feedparser
from pytube import YouTube

logging.basicConfig(level=logging.INFO)

class Fetcher:
    def __init__(self, sources, max_workers=5):
        self.sources = sources
        self.max_workers = max_workers

    def _from_rss(self, url):
        feed = feedparser.parse(url)
        return [e.link for e in feed.entries]

    def _from_folder(self, path):
        import os
        return [os.path.join(path, f)
                for f in os.listdir(path)
                if f.lower().endswith(('.mp4','.mov','.mkv'))]

    def _from_youtube(self, channel_url, max_videos=3):
        yt = YouTube(channel_url)
        streams = yt.streams.filter(file_extension='mp4').order_by('resolution').desc()
        return [s.url for s in streams[:max_videos]]

    def get_videos(self):
        videos = []
        with ThreadPoolExecutor(self.max_workers) as exe:
            futures = []
            for s in self.sources:
                t = s['type']
                if t=='rss':    futures.append(exe.submit(self._from_rss, s['url']))
                if t=='folder': futures.append(exe.submit(self._from_folder, s['path']))
                if t=='youtube_channel':
                    futures.append(exe.submit(self._from_youtube, s['channel_url'], s.get('max_videos',3)))
            for f in as_completed(futures):
                try: videos.extend(f.result())
                except Exception as e: logging.error("Fetch failed: %s", e)
        logging.info("Fetched %d videos", len(videos))
        return videos
