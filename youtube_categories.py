#!/usr/bin/env python3
"""
YouTube Categories Helper Module

This module provides category ID to name mapping and utilities
for working with YouTube video categories.
"""

from typing import Dict, Optional
import os
from googleapiclient.discovery import build
from dotenv import load_dotenv


class YouTubeCategories:
    """YouTube Categories helper class"""
    
    # Default category mapping (US region)
    DEFAULT_CATEGORIES = {
        1: "Film & Animation",
        2: "Autos & Vehicles", 
        10: "Music",
        15: "Pets & Animals",
        17: "Sports",
        18: "Short Movies",
        19: "Travel & Events",
        20: "Gaming",
        21: "Videoblogging",
        22: "People & Blogs",
        23: "Comedy",
        24: "Entertainment",
        25: "News & Politics",
        26: "Howto & Style",
        27: "Education",
        28: "Science & Technology",
        29: "Nonprofits & Activism",
        30: "Movies",
        31: "Anime/Animation",
        32: "Action/Adventure",
        33: "Classics",
        34: "Comedy",
        35: "Documentary",
        36: "Drama",
        37: "Family",
        38: "Foreign",
        39: "Horror",
        40: "Sci-Fi/Fantasy",
        41: "Thriller",
        42: "Shorts",
        43: "Shows",
        44: "Trailers"
    }
    
    def __init__(self, api_key: str = None, region_code: str = 'US'):
        """
        Initialize YouTube Categories helper
        
        Args:
            api_key: YouTube API key (optional, will load from .env if not provided)
            region_code: Region code for categories (default: 'US')
        """
        if api_key:
            self.api_key = api_key
        else:
            load_dotenv()
            self.api_key = os.getenv('YOUTUBE_API_KEY')
        
        self.region_code = region_code
        self.youtube = None
        self.categories = self.DEFAULT_CATEGORIES.copy()
        
        if self.api_key:
            try:
                self.youtube = build('youtube', 'v3', developerKey=self.api_key)
                self._load_categories_from_api()
            except Exception as e:
                print(f"Warning: Could not load categories from API: {e}")
                print("Using default category mapping")
    
    def _load_categories_from_api(self):
        """Load categories from YouTube API for the specific region"""
        try:
            request = self.youtube.videoCategories().list(
                part='snippet',
                regionCode=self.region_code
            )
            response = request.execute()
            
            # Update categories with API data
            self.categories = {}
            for item in response.get('items', []):
                category_id = int(item['id'])
                title = item['snippet']['title']
                self.categories[category_id] = title
                
        except Exception as e:
            print(f"Warning: Could not load categories from API: {e}")
    
    def get_category_name(self, category_id: str) -> str:
        """
        Get category name from category ID
        
        Args:
            category_id: Category ID as string
            
        Returns:
            Category name or 'Unknown' if not found
        """
        try:
            cat_id = int(category_id)
            return self.categories.get(cat_id, f"Unknown (ID: {category_id})")
        except (ValueError, TypeError):
            return f"Invalid ID: {category_id}"
    
    def get_all_categories(self) -> Dict[int, str]:
        """
        Get all category mappings
        
        Returns:
            Dictionary mapping category ID to name
        """
        return self.categories.copy()
    
    def print_categories(self):
        """Print all available categories"""
        print(f"YouTube Video Categories (Region: {self.region_code}):")
        print("=" * 50)
        
        for cat_id, name in sorted(self.categories.items()):
            print(f"ID {cat_id:2d}: {name}")
    
    def get_category_stats(self, videos_data: list) -> Dict[str, int]:
        """
        Get category statistics from video data
        
        Args:
            videos_data: List of video metadata dictionaries
            
        Returns:
            Dictionary with category counts
        """
        stats = {}
        
        for video in videos_data:
            category_id = video.get('category_id', '')
            category_name = self.get_category_name(category_id)
            stats[category_name] = stats.get(category_name, 0) + 1
        
        return stats
    
    def print_category_stats(self, videos_data: list):
        """
        Print category statistics for video data
        
        Args:
            videos_data: List of video metadata dictionaries
        """
        stats = self.get_category_stats(videos_data)
        
        if not stats:
            print("No category data available")
            return
        
        print("\n📊 Video Category Statistics:")
        print("=" * 40)
        
        total_videos = sum(stats.values())
        for category, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_videos) * 100
            print(f"{category:25s}: {count:3d} videos ({percentage:5.1f}%)")
        
        print(f"{'Total':25s}: {total_videos:3d} videos")


def main():
    """Test the categories helper"""
    categories = YouTubeCategories()
    categories.print_categories()
    
    # Test with sample data
    sample_videos = [
        {'category_id': '22'},
        {'category_id': '22'},
        {'category_id': '10'},
        {'category_id': '27'},
        {'category_id': '22'}
    ]
    
    print("\n" + "="*50)
    print("Sample Category Statistics:")
    categories.print_category_stats(sample_videos)


if __name__ == "__main__":
    main()
