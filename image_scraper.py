import tkinter as tk
from tkinter import messagebox, filedialog
from serpapi import GoogleSearch
import requests
import os
import re
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()

class ImageDownloader:
    def __init__(self, query, api_key, download_folder="images", max_filename_length=50, max_workers=5):
        self.query = query
        self.api_key = api_key
        self.download_folder = download_folder
        self.max_filename_length = max_filename_length
        self.max_workers = max_workers

        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)

    def get_images(self, page=0):
        try:
            params = {
                "q": self.query,
                "engine": "google_images",
                "ijn": str(page),
                "api_key": self.api_key,
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            return results.get("images_results", [])
        except Exception as e:
            print(f"Error fetching: {e}")
            return []

    def get_images_multiple_pages(self, max_pages=1):
        all_images = []
        for page in range(max_pages):
            print(f"Fetching page {page}...")
            images = self.get_images(page=page)
            if not images:
                break
            all_images.extend(images)
        return all_images

    def sanitize_filename(self, filename):
        return re.sub(r'[<>:"/\\|?*]', '', filename)

    def download_image(self, result):
        url = result.get("original")
        if not url:
            return "No valid image URL"
        filename = self.sanitize_filename(url.split("/")[-1])[:self.max_filename_length]
        path = os.path.join(self.download_folder, filename)
        try:
            r = requests.get(url)
            r.raise_for_status()
            with open(path, "wb") as f:
                f.write(r.content)
            return f"Downloaded: {filename}"
        except Exception as e:
            return f"Failed: {e}"

    def download_images_concurrently(self, results):
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.download_image, r) for r in results]
            for future in as_completed(futures):
                print(future.result())


# GUI with Tkinter
def start_download():
    query = entry_query.get()
    try:
        pages = int(entry_pages.get())
        if pages <= 0:
            raise ValueError("Pages must be a positive integer.")
    except ValueError:
        messagebox.showerror("Error", "Pages must be a positive number")
        return

    if not query:
        messagebox.showerror("Error", "Query cannot be empty")
        return

    api_key = os.getenv("SerpAPI")
    if not api_key:
        messagebox.showerror("Error", "Missing SerpAPI key in .env")
        return

    download_folder = entry_folder.get()
    if not download_folder:
        messagebox.showerror("Error", "Download folder cannot be empty")
        return

    # Set the download folder path
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    downloader = ImageDownloader(query=query, api_key=api_key, download_folder=download_folder)
    results = downloader.get_images_multiple_pages(max_pages=pages)
    if not results:
        messagebox.showinfo("Done", "No images found.")
        return
    downloader.download_images_concurrently(results)
    messagebox.showinfo("Done", "Download complete!")

# Open folder dialog
def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        entry_folder.delete(0, tk.END)
        entry_folder.insert(0, folder)


# Tkinter setup
root = tk.Tk()
root.title("Image Downloader")
root.geometry("400x250")

tk.Label(root, text="Search Query:").pack(pady=5)
entry_query = tk.Entry(root, width=40)
entry_query.pack()

tk.Label(root, text="Pages to Fetch:").pack(pady=5)
entry_pages = tk.Entry(root, width=10)
entry_pages.insert(0, "1")
entry_pages.pack()

tk.Label(root, text="Download Folder:").pack(pady=5)
entry_folder = tk.Entry(root, width=40)
entry_folder.pack()

tk.Button(root, text="Select Folder", command=select_folder).pack(pady=5)

tk.Button(root, text="Download Images", command=start_download).pack(pady=20)

root.mainloop()
