from serpapi import GoogleSearch
import requests
import os

from dotenv import load_dotenv, dotenv_values

# loading variables from .env file
load_dotenv()
api_key = os.getenv("SerpAPI")


if not os.path.exists("images"):
    os.makedirs("images")


params = {
    "q": "rainy night snow anime    before:2013",
    "engine": "google_images",
    "ijn": "0",
    "api_key": api_key,
}

search = GoogleSearch(params)
results = search.get_dict()
images_results = results["images_results"]
print(images_results)


for result in images_results:
    thumbnail_url = result["original"]
    # Extract filename from URL
    max_filename_length = 50  # Set your desired maximum filename length

    filename = thumbnail_url.split("/")[-1]

    # Check if the filename is too long
    if len(filename) > max_filename_length:
        # If the filename is too long, truncate it
        filename = filename[:max_filename_length]

# Now you can use the 'filename' variable

    # Construct local file path
    filepath = os.path.join("images", filename)

    # Download thumbnail
    response = requests.get(thumbnail_url)
    if response.status_code == 200:
        with open(filepath, "wb") as f:
            f.write(response.content)
        print(f"Downloaded: {filename}")
    else:
        print(f"Failed to download: {filename}")
