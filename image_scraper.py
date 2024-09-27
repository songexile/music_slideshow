from serpapi import GoogleSearch
import requests
import os
import re
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load variables from .env file
load_dotenv()

class ImageDownloader:
    def __init__(self, query, api_key, download_folder="thumbnails", max_filename_length=50, max_workers=5):
        self.query = query
        self.api_key = api_key
        self.download_folder = download_folder
        self.max_filename_length = max_filename_length
        self.max_workers = max_workers
        
        # Ensure download folder exists
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)

    def get_images(self):
        """Fetches image URLs from the SerpAPI with error handling."""
        try:
            params = {
                "q": self.query,
                "engine": "google_images",
                "ijn": "0",
                "api_key": self.api_key,
            }
            search = GoogleSearch(params)
            results = search.get_dict()

            if "images_results" not in results:
                raise ValueError("No image results found in API response")

            return results["images_results"]

        except requests.exceptions.RequestException as e:
            print(f"Error fetching results from SerpAPI: {e}")
            return []


    def sanitize_filename(self, filename):
        """Sanitizes filenames to remove invalid characters."""
        return re.sub(r'[<>:"/\\|?*]', '', filename)

    def download_image(self, result):
        """Downloads a single image from the URL."""
        thumbnail_url = result.get("original")
        
        if not thumbnail_url:
            return f"No valid thumbnail URL found"
        
        filename = self.sanitize_filename(thumbnail_url.split("/")[-1])

        if len(filename) > self.max_filename_length:
            filename = filename[:self.max_filename_length]

        filepath = os.path.join(self.download_folder, filename)

        try:
            response = requests.get(thumbnail_url)
            response.raise_for_status()
            with open(filepath, "wb") as f:
                f.write(response.content)
            return f"Downloaded: {filename}"
        except requests.exceptions.RequestException as e:
            return f"Failed to download {filename}: {e}"

    def download_images_concurrently(self, images_results):
        """Downloads images concurrently using ThreadPoolExecutor."""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_image = {executor.submit(self.download_image, result): result for result in images_results}
            for future in as_completed(future_to_image):
                try:
                    print(future.result())
                except Exception as exc:
                    print(f"Generated an exception: {exc}")
        print("All downloads are complete!")

# Example usage:
if __name__ == "__main__":
    api_key = os.getenv("SerpAPI")
    if not api_key:
        raise ValueError("SerpAPI key not found in environment variables")

    downloader = ImageDownloader(query="chongqing before:2011", api_key=api_key)
    
    images_results = downloader.get_images()
    downloader.download_images_concurrently(images_results)
