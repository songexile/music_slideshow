from moviepy.editor import ImageClip, concatenate_videoclips
import os
import argparse
from glob import glob
import numpy as np
from PIL import Image
from tqdm import tqdm
import multiprocessing
from functools import partial
import concurrent.futures

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Create a video from a series of images.')
    parser.add_argument('--image_dir', default='ibiza', help='Directory containing the images')
    parser.add_argument('--output', default='ibiza.mp4', help='Output video filename')
    parser.add_argument('--width', type=int, default=1080, help='Output video width')
    parser.add_argument('--height', type=int, default=1920, help='Output video height')
    parser.add_argument('--fps', type=int, default=24, help='Frames per second')
    parser.add_argument('--duration', type=float, default=0.1, help='Duration for each image (seconds)')
    parser.add_argument('--batch_size', type=int, default=100, help='Number of images to process in each batch')
    parser.add_argument('--threads', type=int, default=multiprocessing.cpu_count(), help='Number of processing threads')
    return parser.parse_args()

def find_image_files(directory):
    """Find all image files in the specified directory."""
    image_extensions = ('*.jpeg', '*.jpg', '*.png', '*.bmp', '*.gif')
    image_files = []
    for ext in image_extensions:
        image_files.extend(glob(os.path.join(directory, ext)))
    
    return sorted(image_files)

def process_image(file_path, resolution, duration):
    """Process a single image file and return a clip."""
    try:
        # Open image and convert to RGB
        with Image.open(file_path) as img:
            img = img.convert('RGB')
            
            # Check if resizing is needed to avoid unnecessary operations
            if (img.width, img.height) != resolution:
                img = img.resize(resolution, Image.LANCZOS)
            
            # Convert to numpy array
            img_array = np.array(img)
            
            # Create the clip
            clip = ImageClip(img_array).set_duration(duration)
            return clip
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return None

def process_image_batch(image_files, resolution, duration, threads):
    """Process a batch of images in parallel."""
    processor = partial(process_image, resolution=resolution, duration=duration)
    
    clips = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        for clip in tqdm(
            executor.map(processor, image_files),
            total=len(image_files),
            desc="Processing images"
        ):
            if clip is not None:
                clips.append(clip)
    
    return clips

def main():
    args = parse_arguments()
    
    # Create resolution tuple from width and height
    resolution = (args.width, args.height)
    
    print(f"Looking for images in {args.image_dir}...")
    image_files = find_image_files(args.image_dir)
    
    if not image_files:
        raise Exception(f"No image files found in the directory: {args.image_dir}")
    
    print(f"Found {len(image_files)} images")
    
    # Process images in batches to avoid memory issues
    all_clips = []
    total_batches = (len(image_files) + args.batch_size - 1) // args.batch_size
    
    for i in range(0, len(image_files), args.batch_size):
        print(f"Processing batch {(i//args.batch_size)+1} of {total_batches}")
        batch = image_files[i:i + args.batch_size]
        batch_clips = process_image_batch(batch, resolution, args.duration, args.threads)
        all_clips.extend(batch_clips)
    
    if not all_clips:
        raise Exception("No clips were successfully processed. Please check your images.")
    
    print("Concatenating clips and creating video...")
    final_clip = concatenate_videoclips(all_clips, method="compose")
    final_clip = final_clip.set_fps(args.fps)
    
    print(f"Rendering video to {args.output}...")
    final_clip.write_videofile(
        args.output,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="temp-audio.m4a",
        remove_temp=True,
        threads=args.threads,
        logger="bar"  # Show progress bar
    )
    
    print(f"Video successfully created: {args.output}")

if __name__ == "__main__":
    main()