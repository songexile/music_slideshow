
import tkinter as tk
from tkinter import messagebox, filedialog
from serpapi import GoogleSearch
import requests
import os
import re
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional, Any

from image_result import ImageResult



class ImageDownloader:
    """Responsible for downloading images to the file system"""
    def __init__(self, download_folder: str = "images", max_filename_length: int = 50, max_workers: int = 5):
        self.download_folder = download_folder
        self.max_filename_length = max_filename_length
        self.max_workers = max_workers
        
        self._ensure_download_folder_exists()
        
    def _ensure_download_folder_exists(self) -> None:
        """Ensure the download folder exists"""
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)
            
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename by removing invalid characters"""
        return re.sub(r'[<>:"/\\|?*]', '', filename)
    
    def download_image(self, image: ImageResult) -> str:
        """Download a single image and return the result message"""
        if not image.is_valid:
            return "No valid image URL"
            
        filename = self._sanitize_filename(image.url.split("/")[-1])[:self.max_filename_length]
        path = os.path.join(self.download_folder, filename)
        
        try:
            r = requests.get(image.url)
            r.raise_for_status()
            with open(path, "wb") as f:
                f.write(r.content)
            return f"Downloaded: {filename}"
        except Exception as e:
            return f"Failed: {e}"
            
    def download_images(self, images: List[ImageResult]) -> List[str]:
        """Download multiple images concurrently and return result messages"""
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.download_image, img) for img in images]
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                print(result)
        return results
