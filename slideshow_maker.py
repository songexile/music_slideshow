import os
import random
from typing import List, Tuple
from moviepy.editor import ImageClip, CompositeVideoClip, AudioFileClip
from moviepy.video.fx.all import crop

class SlideshowGenerator:
    def __init__(self, config: dict):
        self.config = config #This reads the config to the class
        self.clips = [] #this is where we will store all clips
        self.cumulative_duration = 0 #NOT SURE
        self.audio = AudioFileClip(self.config['AUDIO_DIR']) #Gets the audio dir
        self.audio_duration = self.audio.duration #Figures out the duration of the audio, this is used for how long the clip is

    def collect_clips(self) -> None: #This function is void because it doens't return anything, loops through all images
        for filename in os.listdir(self.config['IMAGE_DIR']): #Loop through all files in image dir to prep for video
            if filename.lower().endswith(('.jpeg', '.jpg', '.png')):
                self._process_image(filename)
                if self.cumulative_duration >= self.audio_duration: #If the total duration of the images is greater than the audio, break
                    break

    def _process_image(self, filename: str) -> None: #Appends image to clips array
        file_path = os.path.join(self.config['IMAGE_DIR'], filename)
        try:
            image = self._create_image_clip(file_path)
            self.clips.append(image)
            self.cumulative_duration += self.config['image_duration']
            print(f"Processed image: {filename}")
        except Exception as e:
            print(f"Error processing image file {filename}: {e}")

    def _create_image_clip(self, file_path: str) -> ImageClip:
        image = (ImageClip(file_path)
                 .set_duration(self.config['image_duration'])
                 .resize(self.config['resolution'])
                 .set_fps(1)
                 .crop(0.5, 0.5)
                 .set_start(self.cumulative_duration))
        
        if self.config['use_zoom_effect']:
            image = self._apply_zoom_effect(image)
        
        return image

    def _apply_zoom_effect(self, clip: ImageClip) -> ImageClip:
        # Implement the Zoom effect here
        # This is a placeholder for the actual implementation
        return clip

    def add_banner(self) -> None:
        if self.config['BANNER_ON']:
            banner_w, banner_h = self.config['resolution'][0], self.config['resolution'][1] * 0.2
            banner = (ImageClip(self.config['BANNER_IMG'])
                      .set_duration(self.audio_duration - 2)
                      .set_start(0)
                      .resize(newsize=(banner_w, banner_h))
                      .set_position("bottom"))
            self.clips.append(banner)

    def create_final_clip(self) -> CompositeVideoClip:
        return CompositeVideoClip(random.sample(self.clips, len(self.clips)))
        #return CompositeVideoClip(random.shuffle(self.clips))

    def generate_slideshow(self) -> None:
        self.collect_clips()
        self.add_banner()
        final_clip = self.create_final_clip()
        final_clip.write_videofile(
            self.config['output_filename'],
            audio=self.config['AUDIO_DIR'],
            codec="libx264"
        )

# Usage
config = {
    'image_duration': 0.1,
    'video_duration': 5,
    'BANNER_ON': True,
    'BANNER_IMG': "banner/527.jpeg",
    'IMAGE_DIR': "thumbnails",
    'VIDEO_DIR': "videos",
    'output_filename': "slideshow.mp4",
    'resolution': (1280, 720),
    'AUDIO_DIR': "audio/127-emo-dubstep-vip-mix.mp3",
    'use_zoom_effect': False  # Set to True if you want to use the zoom effect
}

slideshow = SlideshowGenerator(config)
slideshow.generate_slideshow()