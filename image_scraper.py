from serpapi import GoogleSearch
import requests
import os
from dotenv import load_dotenv
import urllib3

# Disable SSL warnings (use with caution)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Loading variables from .env file
load_dotenv()
api_key = os.getenv("SerpAPI")

if not os.path.exists("images1"):
    os.makedirs("images1")

params = {
    "q": "Bangkok Rama IX bridge illuminated night before:2012",
    "engine": "google_images",
    "ijn": "0",
    "api_key": api_key,
}

search = GoogleSearch(params)
results = search.get_dict()
images_results = results["images_results"]
print(f"Total images found: {len(images_results)}")

successful_downloads = 0
failed_downloads = 0

for index, result in enumerate(images_results, start=1):
    thumbnail_url = result["original"]
    
    # Extract filename from URL
    max_filename_length = 50  # Set your desired maximum filename length
    filename = thumbnail_url.split("/")[-1]
    
    # Check if the filename is too long
    if len(filename) > max_filename_length:
        # If the filename is too long, truncate it
        filename = filename[:max_filename_length]
    
    # Construct local file path
    filepath = os.path.join("images1", filename)
    
    # Download thumbnail with error handling
    try:
        response = requests.get(thumbnail_url, verify=False, timeout=10)
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
        
        with open(filepath, "wb") as f:
            f.write(response.content)
        print(f"Downloaded ({index}/{len(images_results)}): {filename}")
        successful_downloads += 1
    
    except requests.exceptions.SSLError as ssl_err:
        print(f"SSL Error when downloading {filename}: {ssl_err}")
        failed_downloads += 1
    except requests.exceptions.RequestException as req_err:
        print(f"Error downloading {filename}: {req_err}")
        failed_downloads += 1
    except IOError as io_err:
        print(f"IO Error when saving {filename}: {io_err}")
        failed_downloads += 1
    except Exception as e:
        print(f"Unexpected error when processing {filename}: {e}")
        failed_downloads += 1

# Print summary
print("\nDownload Summary:")
print(f"Total images: {len(images_results)}")
print(f"Successfully downloaded: {successful_downloads}")
print(f"Failed downloads: {failed_downloads}")