import logging
import time
import openai

logging.basicConfig(level=logging.INFO)

class MetadataGenerator:
    def __init__(self, api_key, rate_limit=30):
        openai.api_key = api_key
        self.interval = 60 / rate_limit
        self.last = 0

    def create_metadata(self, clip_path, niche):
        # Enforce rate limit between API calls
        wait = self.interval - (time.time() - self.last)
        if wait > 0:
            time.sleep(wait)

        prompt = (
            f"Return JSON with title, description, and hashtags "
            f"for a {niche} YouTube Short: {clip_path}"
        )
        try:
            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a metadata assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            self.last = time.time()
            return resp.choices[0].message.content
        except Exception as e:
            logging.error("Metadata generation failed: %s", e)
            return {}

