from moviepy.editor import ImageClip, VideoFileClip, CompositeVideoClip, TextClip
from moviepy.video.fx.all import crop
import moviepy.video.compositing.transitions as transitions
import random
import librosa
import os
import numpy as np
import cv2

image_duration = 0.1  # Duration for each image in seconds
video_duration = 5  # Duration for each video clip in seconds

BANNER_ON = True  # If you user wants a banner on the slideshow


BANNER_IMG = "banner/ha.jpg"  # Banner image
IMAGE_DIR = "images"  # Directory containing the images
VIDEO_DIR = "videos"  # Directory containing the video clips
output_filename = "slideshow.mp4"  # Output video filename
resolution = (1280, 720)  # 720p resolution exported
AUDIO_DIR = "audio/127-emo-dubstep-vip-mix.mp3"  # Provide audio clip
audio_duration = librosa.get_duration(filename=AUDIO_DIR)


def Zoom(clip, mode="in", position="center", speed=1):
    fps = clip.fps
    duration = clip.duration
    total_frames = int(duration * fps)

    def main(getframe, t):
        frame = getframe(t)
        h, w = frame.shape[:2]
        i = t * fps
        if mode == "out":
            i = total_frames - i
        zoom = 1 + (i * ((0.1 * speed) / total_frames))
        positions = {
            "center": [(w - (w * zoom)) / 2, (h - (h * zoom)) / 2],
            "left": [0, (h - (h * zoom)) / 2],
            "right": [(w - (w * zoom)), (h - (h * zoom)) / 2],
            "top": [(w - (w * zoom)) / 2, 0],
            "topleft": [0, 0],
            "topright": [(w - (w * zoom)), 0],
            "bottom": [(w - (w * zoom)) / 2, (h - (h * zoom))],
            "bottomleft": [0, (h - (h * zoom))],
            "bottomright": [(w - (w * zoom)), (h - (h * zoom))],
        }
        tx, ty = positions[position]
        M = np.array([[zoom, 0, tx], [0, zoom, ty]])
        frame = cv2.warpAffine(frame, M, (w, h))
        return frame

    return clip.fl(main)


def collect_clips():
    # Create a list to store all the clips (image and video)
    all_clips = []
    # Initialize the cumulative duration to 0
    cumulative_duration = 0
    # Counter for the number of images processed
    image_count = 0

    # Loop through all files in the image directory
    for filename in os.listdir(IMAGE_DIR):
        # Check if the file is an image (jpeg, jpg, or png extension)
        if filename.lower().endswith(('.jpeg', '.jpg', '.png')):
            # Construct the full file path
            file_path = os.path.join(IMAGE_DIR, filename)
            try:
                image = ImageClip(file_path)
                
                # Ensure the image has 3 color channels
                if image.img.ndim == 2:  # If it's a grayscale image
                    image = ImageClip(np.dstack([image.img] * 3))
                
                image = (image
                         .set_duration(image_duration)
                         .resize(resolution)
                         .set_fps(30)
                         .crop(0.5, 0.5))
                
                image = image.set_start(cumulative_duration)

                random_position = random.choice([
                    "center", "left", "right", "top", "topleft", "topright",
                    "bottom", "bottomleft", "bottomright"
                ])
                random_speed = random.uniform(0.2, 1)

                # Uncomment the following lines if you want to use the Zoom effect
                # image = Zoom(
                #     image,
                #     mode="in",
                #     position=random_position,
                #     speed=random_speed,
                # )

                # Add the clip to the list if it doesn't exceed the audio duration
                if cumulative_duration + image_duration <= audio_duration:
                    all_clips.append(image)
                    # Update the cumulative duration
                    cumulative_duration += image_duration
                    image_count += 1
                    
                    # Print information about the processed image
                    print(f"Processed image {image_count}: {filename}")
                    print(f"Image shape: {image.img.shape}")
                    print(f"Image dtype: {image.img.dtype}")
                    print("---")

                    # Break after processing 5 images
                    # if image_count >= 5:
                    #     break
                else:
                    break

            except Exception as e:
                print(f"Error processing image file {filename}: {e}")

    # We're not shuffling the clips for this test
    # random.shuffle(all_clips)
    return all_clips
all_clips = collect_clips()


## Adds a banner if the user wants
if BANNER_ON == True:
    banner_w = resolution[0]
    banner_h = resolution[1] * 0.2
    all_clips.append(
        ImageClip(BANNER_IMG)
        .set_duration(audio_duration - 2)
        .set_start(0)
        .resize(newsize=(banner_w, banner_h))
        .set_position("bottom")
    )

# Create a CompositeVideoClip from the list of clips
final_clip = CompositeVideoClip(all_clips)

# Set the frames per second (fps) of the final clip
final_clip.fps = 24

# Write the final clip to a video file with the specified audio
final_clip.write_videofile(output_filename, audio=AUDIO_DIR, codec="libx264")
