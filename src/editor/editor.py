import logging
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, AudioFileClip

logging.basicConfig(level=logging.INFO)

class Editor:
    def __init__(self, template):
        self.template = template

    def format_short(self, clip_paths):
        clips = [VideoFileClip(p).resize((1080,1920)) for p in clip_paths]
        full = concatenate_videoclips(clips, method='compose')

        intro = TextClip(self.template['intro_text'], fontsize=60, size=(1080,1920), duration=2)
        outro = TextClip(self.template['outro_text'], fontsize=50, size=(1080,1920), duration=2)
        sequence = [intro, full, outro]

        if self.template.get('music_path'):
            music = AudioFileClip(self.template['music_path']).volumex(self.template.get('music_volume',0.1))
            full = full.set_audio(music.set_duration(full.duration))
            sequence = [intro, full, outro]

        final = concatenate_videoclips(sequence)
        out = self.template.get('output_path', 'short.mp4')
        final.write_videofile(out, fps=self.template.get('fps',24), bitrate=self.template.get('bitrate','3000k'))
        logging.info("Saved short to %s", out)
        return out
