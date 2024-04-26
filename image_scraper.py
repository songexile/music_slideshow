from serpapi import GoogleSearch
import requests
import os

from dotenv import load_dotenv, dotenv_values

# loading variables from .env file
load_dotenv()
api_key = os.getenv("SerpAPI")


if not os.path.exists("thumbnails"):
    os.makedirs("thumbnails")


params = {
    "q": "vertical futurstic  before:2015",
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
    filename = thumbnail_url.split("/")[-1]
    # Construct local file path
    filepath = os.path.join("thumbnails", filename)

    # Download thumbnail
    response = requests.get(thumbnail_url)
    if response.status_code == 200:
        with open(filepath, "wb") as f:
            f.write(response.content)
        print(f"Downloaded: {filename}")
    else:
        print(f"Failed to download: {filename}")
