from moviepy.editor import ImageClip, concatenate_videoclips
import os

image_duration = 2  # Duration for each image in seconds
image_dir = "thumbnails"  # Directory containing the images
output_filename = "slideshow.mp4"  # Output video filename
resolution = (1280, 720)  # 720p resolution (width, height)
audio_clip = "audio/rbnation.mp3"

# Create a list to store all the image clips
image_clips = []

# Loop through all files in the image directory
for filename in os.listdir(image_dir):
    # Check if the file is an image (jpeg or jpg extension)
    if (
        filename.endswith(".jpeg")
        or filename.endswith(".jpg")
        or filename.endswith(".png")
    ):
        # Construct the full file path
        file_path = os.path.join(image_dir, filename)

        try:
            # Create an ImageClip object from the image file
            image = (
                ImageClip(file_path).set_duration(image_duration).resize(resolution)
            )  # Resize the clip to 720p

            # Add the clip to the list
            image_clips.append(image)
        except Exception as e:
            print(f"Error processing file {filename}: {e}")

# Concatenate all the image clips
final_clip = concatenate_videoclips(image_clips)

# Set the frames per second (fps) of the final clip
final_clip.fps = 30

final_clip.write_videofile(
    output_filename,
    audio=audio_clip,
)
