from moviepy.editor import (
    ImageClip,
    VideoFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
)
from moviepy.video.fx.all import crop
import moviepy.video.compositing.transitions as transitions
import random
import librosa
import os

image_duration = 5  # Duration for each image in seconds
video_duration = 5  # Duration for each video clip in seconds
image_dir = "thumbnails"  # Directory containing the images
video_dir = "videos"  # Directory containing the video clips
output_filename = "slideshow.mp4"  # Output video filename
resolution = (1280, 720)  # 720p resolution (width, height)
audio_clip = "audio/rbnation.mp3"
audio_duration = librosa.get_duration(filename=audio_clip)


def collect_clips():
    # Create a list to store all the clips (image and video)
    all_clips = []

    # Initialize the cumulative duration to 0
    cumulative_duration = 0

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
                image = ImageClip(file_path)
                # Apply the zoom effect
                zoom_factor = 0.9  # Adjust this value to control the zoom amount
                zoomed_image = crop(image, zoom_factor)
                zoomed_image = zoomed_image.set_duration(image_duration)
                # Set the start time for the clip
                zoomed_image = zoomed_image.set_start(cumulative_duration)
                # Add the clip to the list if it doesn't exceed the audio duration
                if cumulative_duration + image_duration <= audio_duration:
                    all_clips.append(zoomed_image)
                    # Update the cumulative duration
                    cumulative_duration += image_duration
                else:
                    break
            except Exception as e:
                print(f"Error processing image file {filename}: {e}")

    # Loop through all files in the video directory
    for filename in os.listdir(video_dir):
        # Check if the file is a video (mp4, mov, or avi extension)
        if (
            filename.endswith(".mp4")
            or filename.endswith(".mov")
            or filename.endswith(".avi")
        ):
            # Construct the full file path
            file_path = os.path.join(video_dir, filename)
            try:
                # Create a VideoFileClip object from the video file
                video = VideoFileClip(file_path)
                # Resize the video clip to match the desired resolution
                video = video.resize(resolution)
                # Set the duration of the video clip
                video = video.set_duration(video_duration)
                # Set the start time for the clip
                video = video.set_start(cumulative_duration)
                # Add the clip to the list if it doesn't exceed the audio duration
                if cumulative_duration + video_duration <= audio_duration:
                    all_clips.append(video)
                    # Update the cumulative duration
                    cumulative_duration += video_duration
                else:
                    break
            except Exception as e:
                print(f"Error processing video file {filename}: {e}")

    return all_clips


all_clips = collect_clips()

# Create a CompositeVideoClip from the list of clips
final_clip = CompositeVideoClip(clips=all_clips)

# Set the frames per second (fps) of the final clip
final_clip.fps = 24

# Write the final clip to a video file with the specified audio
final_clip.write_videofile(output_filename, audio=audio_clip, codec="libx264")
