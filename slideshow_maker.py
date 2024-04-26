from moviepy.editor import ImageClip, VideoFileClip, concatenate_videoclips
import random

import os

image_duration = 2  # Duration for each image in seconds
video_duration = 5  # Duration for each video clip in seconds

image_dir = "thumbnails"  # Directory containing the images
video_dir = "videos"  # Directory containing the video clips

output_filename = "slideshow.mp4"  # Output video filename

resolution = (1280, 720)  # 720p resolution (width, height)

audio_clip = "audio/rbnation.mp3"

# Create a list to store all the clips (image and video)
all_clips = []

# Loop through all files in the image directory
for filename in os.listdir(image_dir):
    # Check if the file is an image (jpeg, jpg, or png extension)
    if (
        filename.endswith(".jpeg")
        or filename.endswith(".jpg")
        or filename.endswith(".png")
    ):
        # Construct the full file path
        file_path = os.path.join(image_dir, filename)
        try:
            # Create an ImageClip object from the image file
            image = ImageClip(file_path).set_duration(image_duration).resize(resolution)
            # Add the clip to the list
            all_clips.append(image)
        except Exception as e:
            print(f"Error processing image file {filename}: {e}")

# Loop through all files in the video directory
for filename in os.listdir(video_dir):
    # Check if the file is a video (mp4, avi, webm, etc. extension)
    if (
        filename.endswith(".mp4")
        or filename.endswith(".avi")
        or filename.endswith(".webm")
    ):
        # Construct the full file path
        file_path = os.path.join(video_dir, filename)
        try:
            # Create a VideoFileClip object from the video file
            video = VideoFileClip(file_path).resize(resolution)
            # Limit the duration of the video clip to 5 seconds
            video = video.subclip(0, video_duration)
            # Add the clip to the list
            all_clips.append(video)
            print("found video")
        except Exception as e:
            print(f"Error processing video file {filename}: {e}")

random.shuffle(all_clips)

# Concatenate all the clips
final_clip = concatenate_videoclips(all_clips)

# Set the frames per second (fps) of the final clip
final_clip.fps = 30

final_clip.write_videofile(output_filename, audio=audio_clip, codec="libx264")
