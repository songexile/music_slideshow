import tkinter as tk
from tkinter import messagebox, filedialog
from serpapi import GoogleSearch
import requests
import os
import re
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional, Any

from image_downloader import ImageDownloader
from image_searcher import ImageSearcher



class ImageDownloaderApp:
    """Main application class"""
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Image Downloader")
        self.root.geometry("400x250")
        
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv("SerpAPI")
        
        # Initialize components
        self.searcher = None
        self.downloader = None
        
        # Create UI elements
        self._create_widgets()
        
    def _create_widgets(self) -> None:
        """Create all UI widgets"""
        # Search query input
        tk.Label(self.root, text="Search Query:").pack(pady=5)
        self.entry_query = tk.Entry(self.root, width=40)
        self.entry_query.pack()
        
        # Pages input
        tk.Label(self.root, text="Pages to Fetch:").pack(pady=5)
        self.entry_pages = tk.Entry(self.root, width=10)
        self.entry_pages.insert(0, "1")
        self.entry_pages.pack()
        
        # Download folder input
        tk.Label(self.root, text="Download Folder:").pack(pady=5)
        self.entry_folder = tk.Entry(self.root, width=40)
        self.entry_folder.insert(0, "images")
        self.entry_folder.pack()
        
        # Folder selection button
        tk.Button(self.root, text="Select Folder", command=self._select_folder).pack(pady=5)
        
        # Download button
        tk.Button(self.root, text="Download Images", command=self._start_download).pack(pady=20)
    
    def _select_folder(self) -> None:
        """Open folder dialog and set the selected folder"""
        folder = filedialog.askdirectory()
        if folder:
            self.entry_folder.delete(0, tk.END)
            self.entry_folder.insert(0, folder)
    
    def _validate_inputs(self) -> Optional[str]:
        """Validate user inputs and return error message if invalid"""
        query = self.entry_query.get()
        if not query:
            return "Query cannot be empty"
            
        try:
            pages = int(self.entry_pages.get())
            if pages <= 0:
                return "Pages must be a positive integer"
        except ValueError:
            return "Pages must be a valid number"
            
        if not self.api_key:
            return "Missing SerpAPI key in .env file"
            
        folder = self.entry_folder.get()
        if not folder:
            return "Download folder cannot be empty"
            
        return None
        
    def _start_download(self) -> None:
        """Start the download process"""
        # Validate inputs
        error = self._validate_inputs()
        if error:
            messagebox.showerror("Error", error)
            return
            
        # Get input values
        query = self.entry_query.get()
        pages = int(self.entry_pages.get())
        folder = self.entry_folder.get()
        
        # Initialize components if needed
        self.searcher = ImageSearcher(self.api_key)
        self.downloader = ImageDownloader(download_folder=folder)
        
        # Perform search and download
        try:
            results = self.searcher.search_multiple_pages(query, max_pages=pages)
            if not results:
                messagebox.showinfo("Done", "No images found.")
                return
                
            download_results = self.downloader.download_images(results)
            successful = sum(1 for r in download_results if r.startswith("Downloaded"))
            messagebox.showinfo("Done", f"Download complete! Successfully downloaded {successful} images.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        

def main():
    """Main entry point for the application"""
    root = tk.Tk()
    app = ImageDownloaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()