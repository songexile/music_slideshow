from typing import List, Dict, Optional, Any


class ImageResult:
    """Class to represent an image result from the search API"""
    def __init__(self, data: Dict[str, Any]):
        self.url = data.get("original", "")
        self.title = data.get("title", "")
        self.source = data.get("source", "")
        self.thumbnail = data.get("thumbnail", "")
        self.position = data.get("position", 0)
        
    @property
    def is_valid(self) -> bool:
        """Check if the image result has a valid URL"""
        return bool(self.url)

