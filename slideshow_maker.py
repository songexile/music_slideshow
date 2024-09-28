from moviepy.editor import (
    ImageClip,
    VideoFileClip,
    CompositeVideoClip,
    AudioFileClip,
)
import random
import os
import numpy as np
import cv2
from glob import glob
import librosa
import matplotlib.pyplot as plt

# Configuration parameters
BANNER_ON = True       # If the user wants a banner on the slideshow
ZOOM_EFFECT = True     # Enable or disable zoom effect (default is True)
BANNER_IMG = "banner/527.jpeg"  # Banner image
IMAGE_DIR = "thumbnails"        # Directory containing the images
VIDEO_DIR = "videos"            # Directory containing the video clips
OUTPUT_FILENAME = "slideshow.mp4"  # Output video filename
RESOLUTION = (1280, 720)        # 720p resolution exported
AUDIO_PATH = "audio/109_burmacivic_98_lost_rap2_REDOINSTRIMENTALv2.mp3"  # Audio clip
FPS = 24                        # Frames per second for the final video

# Optional: Set a known BPM or None to auto-detect
INPUT_BPM = 109                # Replace with BPM if known

def estimate_bpm(y, sr):
    # Estimate the tempo (BPM)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return tempo

def expected_beat_count(bpm, duration):
    return (bpm / 60) * duration  # Beats per second * duration (seconds)

def tune_delta_by_bpm(detected_onsets, expected_beats):
    tolerance = 0.25
    detected_beat_count = len(detected_onsets)

    if detected_beat_count > expected_beats * (1 + tolerance):
        delta = 0.3  # Too many detected beats, increase delta
    elif detected_beat_count < expected_beats * (1 - tolerance):
        delta = 0.15  # Too few detected beats, lower delta
    else:
        delta = 0.22  # Within tolerance, use default delta

    return delta

def detect_peaks(audio_path, input_bpm=None):
    y, sr = librosa.load(audio_path, sr=None)
    hop_length = 512
    y_harmonic, y_percussive = librosa.effects.hpss(y)
    onset_env = librosa.onset.onset_strength(y=y_percussive, sr=sr, hop_length=hop_length)

    # Use input BPM if provided, otherwise estimate
    if input_bpm is not None:
        bpm = input_bpm
    else:
        bpm = estimate_bpm(y, sr)

    audio_duration = librosa.get_duration(y=y, sr=sr)
    expected_beats = expected_beat_count(bpm, audio_duration)
    print(f"Using BPM: {bpm}, Expected Beats: {expected_beats}")

    # Initial onset detection with moderate delta
    onset_frames = librosa.onset.onset_detect(
        onset_envelope=onset_env,
        sr=sr,
        hop_length=hop_length,
        backtrack=False,
        units='frames',
        delta=0.22,
        wait=0
    )

    onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=hop_length)

    # Dynamically tune delta based on expected and detected beats
    tuned_delta = tune_delta_by_bpm(onset_times, expected_beats)
    print(f"Tuned delta: {tuned_delta}")

    # Re-run onset detection with tuned delta
    onset_frames = librosa.onset.onset_detect(
        onset_envelope=onset_env,
        sr=sr,
        hop_length=hop_length,
        backtrack=False,
        units='frames',
        delta=tuned_delta,
        wait=0
    )

    onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=hop_length)


    return onset_times

def zoom_effect(clip, mode="in", position="center", speed=1):
    if not ZOOM_EFFECT:
        return clip
    duration = clip.duration
    speed_factor = 0.1 * speed

    def apply_zoom(get_frame, t):
        frame = get_frame(t)
        h, w = frame.shape[:2]
        progress = t / duration
        if mode == "out":
            progress = 1 - progress
        zoom_factor = 1 + progress * speed_factor
        new_w, new_h = int(w * zoom_factor), int(h * zoom_factor)
        frame_resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        x1 = (new_w - w) // 2
        y1 = (new_h - h) // 2
        return frame_resized[y1:y1+h, x1:x1+w]

    return clip.fl(apply_zoom, apply_to=['mask'])

def collect_clips(peak_times, audio_duration):
    all_files = []
    all_clips = []
    total_peaks = len(peak_times)

    image_extensions = ('*.jpeg', '*.jpg', '*.png', '*.bmp', '*.gif')
    image_files = []
    for ext in image_extensions:
        image_files.extend(glob(os.path.join(IMAGE_DIR, ext)))

    video_extensions = ('*.mp4', '*.mov', '*.avi', '*.mkv')
    video_files = []
    for ext in video_extensions:
        video_files.extend(glob(os.path.join(VIDEO_DIR, ext)))

    all_files = image_files + video_files
    random.shuffle(all_files)

    num_clips = min(len(all_files), total_peaks)
    peak_times = peak_times[:num_clips]
    clip_durations = np.diff(np.append(peak_times, audio_duration))

    # Calculate the duration for every 8 bars
    seconds_per_beat = 60 / INPUT_BPM
    bars_duration = 8 * seconds_per_beat * 4  # Duration of 8 bars assuming 4 beats per bar

    for idx, file_path in enumerate(all_files[:num_clips]):
        try:
            extension = os.path.splitext(file_path)[1].lower()
            duration = clip_durations[idx]
            start_time = peak_times[idx]
            if extension in ['.jpeg', '.jpg', '.png', '.bmp', '.gif']:
                clip = (
                    ImageClip(file_path)
                    .set_duration(duration)
                    .resize(RESOLUTION)
                )
                
                # Apply zoom effect only if the clip falls at the end of an 8-bar segment
                if int(start_time // bars_duration) % 2 == 0:  # Apply zoom every other 8 bars for variety
                    clip = zoom_effect(
                        clip,
                        mode=random.choice(["in", "out"]),
                        position="center",
                        speed=0.5,
                    )

                clip = clip.set_start(start_time)
                clip = clip.set_fps(FPS)
                clip = clip.set_position("center")
            elif extension in ['.mp4', '.mov', '.avi', '.mkv']:
                video = VideoFileClip(file_path).resize(RESOLUTION)
                video_duration = min(video.duration, duration)
                clip = video.subclip(0, video_duration)
                clip = clip.set_duration(duration)
                clip = clip.set_start(start_time)
                clip = clip.set_fps(FPS)
            else:
                continue

            all_clips.append(clip)
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            continue

    return all_clips


def create_banner_clip(duration):
    if BANNER_ON and os.path.exists(BANNER_IMG):
        banner_w = RESOLUTION[0]
        banner_h = int(RESOLUTION[1] * 0.2)
        banner_clip = (
            ImageClip(BANNER_IMG)
            .set_duration(duration)
            .resize(newsize=(banner_w, banner_h))
            .set_position(("center", "bottom"))
        )
        return banner_clip
    else:
        return None

def main():
    try:
        audio_clip = AudioFileClip(AUDIO_PATH)
        audio_duration = audio_clip.duration
    except Exception as e:
        raise Exception(f"Error loading audio file: {e}")

    print("Detecting peaks in the audio...")
    peak_times = detect_peaks(AUDIO_PATH, INPUT_BPM)
    print(peak_times)

    if len(peak_times) == 0:
        raise Exception("No peaks detected in the audio.")

    print("Collecting and processing clips...")
    all_clips = collect_clips(peak_times, audio_duration)

    if not all_clips:
        raise Exception("No clips to process. Please check your IMAGE_DIR and VIDEO_DIR.")

    banner_clip = create_banner_clip(audio_duration)

    print("Compositing final video...")
    if banner_clip:
        final_clip = CompositeVideoClip(all_clips + [banner_clip], size=RESOLUTION)
    else:
        final_clip = CompositeVideoClip(all_clips, size=RESOLUTION)

    final_clip = final_clip.set_duration(audio_duration)
    final_clip = final_clip.set_fps(FPS)

    final_clip = final_clip.set_audio(audio_clip)

    print("Rendering video...")
    final_clip.write_videofile(
        OUTPUT_FILENAME,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="temp-audio.m4a",
        remove_temp=True,
        threads=4,
    )

if __name__ == "__main__":
    main()
