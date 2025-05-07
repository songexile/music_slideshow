from PIL import Image
from moviepy.editor import ImageClip, concatenate_videoclips
import numpy as np

class ImageProcessor:
    def __init__(self, file_path, duration, resolution=(1080, 1920)):
        self.file_path = file_path
        self.duration = duration
        self.resolution = resolution

    def load_image(self):
       try:
        # Open image and convert to RGB
            with Image.open(self.file_path) as img: 
                img = img.convert('RGB')
                return img
       except Exception as e:
            print(f"Error processing file {self.file_path}: {e}")
            return None
        
    def resize_image(self, img):
        if img is None:
            raise ValueError("Cannot resize image because the input image is None.")
        
        if (img.width, img.height) != self.resolution:
            img = img.resize(self.resolution, Image.LANCZOS)
        
        return img


def process(self):
    """Process the image file and return a video clip."""
    try:
        img = self.load_image()
        img = self.resize_image(img)
        img_array = np.array(img)
        return ImageClip(img_array).set_duration(self.duration)
    except Exception as e:
        print(f"Failed to process {self.file_path}: {e}")
        return None