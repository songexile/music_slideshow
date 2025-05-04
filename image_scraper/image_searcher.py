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


class ImageSearcher:
    """Responsible for searching images using the SerpAPI"""
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    def search(self, query: str, page: int = 0) -> List[ImageResult]:
        """Search for images with the given query and page number"""
        try:
            params = {
                "q": query,
                "engine": "google_images",
                "ijn": str(page),
                "api_key": self.api_key,
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            return [ImageResult(img) for img in results.get("images_results", [])]
        except Exception as e:
            print(f"Error fetching: {e}")
            return []
            
    def search_multiple_pages(self, query: str, max_pages: int = 1) -> List[ImageResult]:
        """Search for images across multiple pages"""
        all_images = []
        for page in range(max_pages):
            print(f"Fetching page {page}...")
            images = self.search(query, page=page)
            if not images:
                break
            all_images.extend(images)
        return all_images