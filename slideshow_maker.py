import os
import random
import numpy as np
from typing import List, Tuple
from moviepy.editor import ImageClip, CompositeVideoClip, AudioFileClip
from moviepy.video.fx.all import crop
import librosa

class SlideshowGenerator:
    def __init__(self, config: dict):
        self.config = config
        self.clips = []
        self.audio = AudioFileClip(self.config['AUDIO_DIR'])
        self.audio_duration = self.audio.duration
        self.beat_times, self.bpm = self._calculate_beats()
        self.image_files = self._get_image_files()

    def _calculate_beats(self) -> Tuple[np.ndarray, float]:
        if 'BPM' in self.config and self.config['BPM'] is not None:
            # Use the user-specified BPM
            bpm = self.config['BPM']
            beat_duration = 60 / bpm
            num_beats = int(self.audio_duration / beat_duration)
            beat_times = np.arange(0, num_beats) * beat_duration
            beat_times = beat_times[beat_times < self.audio_duration]
            print(f"Using specified BPM: {bpm}")
        else:
            # Calculate BPM using librosa
            y, sr = librosa.load(self.config['AUDIO_DIR'])
            bpm, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
            beat_times = librosa.frames_to_time(beat_frames, sr=sr)
            beat_times = beat_times[beat_times < self.audio_duration]
            print(f"Detected BPM: {bpm}")

        print(f"Number of beats: {len(beat_times)}")
        return beat_times, bpm

    def _get_image_files(self) -> List[str]:
        files = [f for f in os.listdir(self.config['IMAGE_DIR'])
                 if f.lower().endswith(('.jpeg', '.jpg', '.png'))]
        random.shuffle(files)
        return files

    def collect_clips(self) -> None:
        image_index = 0
        for i, start_time in enumerate(self.beat_times):
            if i + 1 < len(self.beat_times):
                end_time = self.beat_times[i + 1]
            else:
                end_time = self.audio_duration

            duration = end_time - start_time

            image_file = self.image_files[image_index % len(self.image_files)]
            self._process_image(image_file, start_time, duration)

            image_index += 1
            if image_index >= len(self.image_files):
                random.shuffle(self.image_files)
                image_index = 0

    def _process_image(self, filename: str, start_time: float, duration: float) -> None:
        file_path = os.path.join(self.config['IMAGE_DIR'], filename)
        try:
            image = self._create_image_clip(file_path, start_time, duration)
            self.clips.append(image)
            print(f"Processed image: {filename} at time {start_time:.2f}, duration {duration:.2f}")
        except Exception as e:
            print(f"Error processing image file {filename}: {e}")

    def _create_image_clip(self, file_path: str, start_time: float, duration: float) -> ImageClip:
        image = (ImageClip(file_path)
                 .set_duration(duration)
                 .resize(self.config['resolution'])
                 .set_start(start_time))
        
        if self.config['use_zoom_effect']:
            image = self._apply_zoom_effect(image)
        
        return image
    
    def _apply_zoom_effect(self, clip: ImageClip) -> ImageClip:
        # Implement the zoom effect here if needed
        return clip

    def add_banner(self) -> None:
        if self.config['BANNER_ON']:
            banner_w, banner_h = self.config['resolution'][0], self.config['resolution'][1] * 0.2
            banner = (ImageClip(self.config['BANNER_IMG'])
                      .set_duration(self.audio_duration)
                      .resize(newsize=(banner_w, banner_h))
                      .set_position("bottom"))
            self.clips.append(banner)

    def create_final_clip(self) -> CompositeVideoClip:
        return CompositeVideoClip(self.clips, size=self.config['resolution'])

    def generate_slideshow(self) -> None:
        self.collect_clips()
        self.add_banner()
        final_clip = self.create_final_clip()
        final_clip.write_videofile(
            self.config['output_filename'],
            audio=self.config['AUDIO_DIR'],
            codec="libx264",
            fps=24  # Set a specific fps for smoother transitions
        )

# Usage with BPM specified
config = {
    'BPM': 127,  # Set this to None or remove it to use automatic BPM detection
    'BANNER_ON': True,
    'BANNER_IMG': "banner/527.jpeg",
    'IMAGE_DIR': "thumbnails",
    'VIDEO_DIR': "videos",
    'output_filename': "exported_videos/slideshow.mp4",
    'resolution': (400, 300),
    'AUDIO_DIR': "audio/127-emo-dubstep-vip-mix.mp3",
    'use_zoom_effect': False  # Set to True if you want to use the zoom effect
}

slideshow = SlideshowGenerator(config)
slideshow.generate_slideshow()