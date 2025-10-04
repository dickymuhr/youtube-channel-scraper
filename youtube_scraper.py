#!/usr/bin/env python3
"""
YouTube Channel Video Scraper using Official YouTube Data API v3

This script scrapes all video metadata from a YouTube channel including:
- Video URL, Title, Likes, Comments, Views, Duration, Date, Description, Thumbnail
"""

import os
import time
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from tqdm import tqdm

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from youtube_categories import YouTubeCategories


@dataclass
class VideoMetadata:
    """Data class to store video metadata"""
    video_id: str
    url: str
    title: str
    description: str
    channel_title: str
    published_at: str
    duration: str
    view_count: int
    like_count: int
    comment_count: int
    thumbnail_url: str
    tags: List[str]
    category_id: str
    language: str


class YouTubeChannelScraper:
    """YouTube Channel Scraper using official YouTube Data API v3"""
    
    def __init__(self, api_key: str):
        """
        Initialize the YouTube scraper
        
        Args:
            api_key: YouTube Data API v3 key
        """
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.rate_limit_delay = 0.1  # Delay between requests to respect rate limits
        self.categories = YouTubeCategories(api_key)  # Initialize categories helper
        
    def get_channel_id(self, channel_identifier: str) -> str:
        """
        Get channel ID from username or channel ID
        
        Args:
            channel_identifier: Channel username or channel ID
            
        Returns:
            Channel ID
        """
        try:
            # Try as channel ID first
            if channel_identifier.startswith('UC'):
                request = self.youtube.channels().list(
                    part='id',
                    id=channel_identifier
                )
                response = request.execute()
                if response['items']:
                    return channel_identifier
                    
            # Try as username
            request = self.youtube.channels().list(
                part='id',
                forUsername=channel_identifier
            )
            response = request.execute()
            
            if response.get('items'):
                return response['items'][0]['id']
            else:
                raise ValueError(f"Channel not found: {channel_identifier}")
                
        except HttpError as e:
            raise Exception(f"Error getting channel ID: {e}")
    
    def get_channel_uploads_playlist_id(self, channel_id: str) -> str:
        """
        Get the uploads playlist ID for a channel
        
        Args:
            channel_id: YouTube channel ID
            
        Returns:
            Uploads playlist ID
        """
        try:
            request = self.youtube.channels().list(
                part='contentDetails',
                id=channel_id
            )
            response = request.execute()
            
            if response['items']:
                return response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            else:
                raise ValueError(f"No uploads playlist found for channel: {channel_id}")
                
        except HttpError as e:
            raise Exception(f"Error getting uploads playlist: {e}")
    
    def get_all_video_ids(self, channel_id: str, max_videos: int = None, 
                         published_after: str = None, published_before: str = None) -> List[str]:
        """
        Get all video IDs from a channel (latest first)
        
        Args:
            channel_id: YouTube channel ID
            max_videos: Maximum number of videos to fetch (None for all)
            published_after: ISO 8601 date string (e.g., "2022-01-01T00:00:00Z")
            published_before: ISO 8601 date string (e.g., "2022-12-31T23:59:59Z")
            
        Returns:
            List of video IDs (latest first)
        """
        video_ids = []
        next_page_token = None
        
        print(f"Fetching video IDs from channel (latest first)...")
        if max_videos:
            print(f"Limiting to {max_videos} videos")
        if published_after:
            print(f"Published after: {published_after}")
        if published_before:
            print(f"Published before: {published_before}")
        
        while True:
            try:
                # Build search parameters
                search_params = {
                    'part': 'id',
                    'channelId': channel_id,
                    'type': 'video',
                    'order': 'date',  # Latest first
                    'maxResults': 50,  # Maximum allowed by API
                }
                
                # Add pagination token
                if next_page_token:
                    search_params['pageToken'] = next_page_token
                
                # Add date filters if provided
                if published_after:
                    search_params['publishedAfter'] = published_after
                if published_before:
                    search_params['publishedBefore'] = published_before
                
                request = self.youtube.search().list(**search_params)
                response = request.execute()
                
                if 'items' not in response:
                    print(f"Warning: No 'items' in response")
                    break
                
                # Extract video IDs
                for item in response['items']:
                    video_ids.append(item['id']['videoId'])
                    
                    # Stop if we've reached the limit
                    if max_videos and len(video_ids) >= max_videos:
                        break
                
                # Stop if we've reached the limit
                if max_videos and len(video_ids) >= max_videos:
                    video_ids = video_ids[:max_videos]  # Trim to exact limit
                    break
                
                # Check if there are more pages
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                    
                # Rate limiting
                time.sleep(self.rate_limit_delay)
                
            except HttpError as e:
                if e.resp.status == 403:
                    print("Rate limit exceeded. Waiting 60 seconds...")
                    time.sleep(60)
                    continue
                else:
                    raise Exception(f"Error fetching video IDs: {e}")
        
        print(f"Found {len(video_ids)} videos")
        return video_ids
    
    def get_video_metadata(self, video_ids: List[str]) -> List[VideoMetadata]:
        """
        Get detailed metadata for a list of video IDs
        
        Args:
            video_ids: List of YouTube video IDs
            
        Returns:
            List of VideoMetadata objects
        """
        videos_metadata = []
        
        # Process videos in batches of 50 (API limit)
        batch_size = 50
        
        print("Fetching video metadata...")
        
        for i in tqdm(range(0, len(video_ids), batch_size), desc="Processing videos"):
            batch = video_ids[i:i + batch_size]
            
            try:
                request = self.youtube.videos().list(
                    part='snippet,statistics,contentDetails',
                    id=','.join(batch)
                )
                response = request.execute()
                
                for item in response['items']:
                    video_metadata = self._parse_video_data(item)
                    videos_metadata.append(video_metadata)
                
                # Rate limiting
                time.sleep(self.rate_limit_delay)
                
            except HttpError as e:
                if e.resp.status == 403:
                    print("Rate limit exceeded. Waiting 60 seconds...")
                    time.sleep(60)
                    continue
                else:
                    print(f"Error fetching video metadata: {e}")
                    continue
        
        return videos_metadata
    
    def _parse_video_data(self, video_data: Dict) -> VideoMetadata:
        """
        Parse video data from API response
        
        Args:
            video_data: Video data from YouTube API
            
        Returns:
            VideoMetadata object
        """
        snippet = video_data['snippet']
        statistics = video_data.get('statistics', {})
        content_details = video_data.get('contentDetails', {})
        
        # Parse duration (ISO 8601 format)
        duration = self._parse_duration(content_details.get('duration', ''))
        
        # Get thumbnail URL (highest quality)
        thumbnails = snippet.get('thumbnails', {})
        thumbnail_url = ''
        if 'maxres' in thumbnails:
            thumbnail_url = thumbnails['maxres']['url']
        elif 'high' in thumbnails:
            thumbnail_url = thumbnails['high']['url']
        elif 'medium' in thumbnails:
            thumbnail_url = thumbnails['medium']['url']
        elif 'default' in thumbnails:
            thumbnail_url = thumbnails['default']['url']
        
        return VideoMetadata(
            video_id=video_data['id'],
            url=f"https://www.youtube.com/watch?v={video_data['id']}",
            title=snippet.get('title', ''),
            description=snippet.get('description', ''),
            channel_title=snippet.get('channelTitle', ''),
            published_at=snippet.get('publishedAt', ''),
            duration=duration,
            view_count=int(statistics.get('viewCount', 0)),
            like_count=int(statistics.get('likeCount', 0)),
            comment_count=int(statistics.get('commentCount', 0)),
            thumbnail_url=thumbnail_url,
            tags=snippet.get('tags', []),
            category_id=snippet.get('categoryId', ''),
            language=snippet.get('defaultLanguage', '')
        )
    
    
    def _parse_duration(self, duration: str) -> str:
        """
        Parse ISO 8601 duration to readable format
        
        Args:
            duration: ISO 8601 duration string (e.g., PT4M13S)
            
        Returns:
            Human-readable duration (e.g., 4:13)
        """
        if not duration:
            return '0:00'
        
        # Remove PT prefix
        duration = duration[2:]
        
        hours = 0
        minutes = 0
        seconds = 0
        
        # Parse hours
        if 'H' in duration:
            hours = int(duration.split('H')[0])
            duration = duration.split('H')[1]
        
        # Parse minutes
        if 'M' in duration:
            minutes = int(duration.split('M')[0])
            duration = duration.split('M')[1]
        
        # Parse seconds
        if 'S' in duration:
            seconds = int(duration.split('S')[0])
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    def scrape_channel(self, channel_identifier: str, max_videos: int = None, 
                      published_after: str = None, published_before: str = None, 
                      buffer_days: int = 0) -> List[VideoMetadata]:
        """
        Scrape videos from a YouTube channel (latest first)
        
        Args:
            channel_identifier: Channel username or channel ID
            max_videos: Maximum number of videos to scrape (None for all)
            published_after: ISO 8601 date string (e.g., "2022-01-01T00:00:00Z")
            published_before: ISO 8601 date string (e.g., "2022-12-31T23:59:59Z")
            buffer_days: Number of days to add/subtract from date range (0 for no buffer)
            
        Returns:
            List of VideoMetadata objects (latest first)
        """
        print(f"Starting scrape for channel: {channel_identifier}")
        
        # Apply buffer to dates if provided
        if published_after and buffer_days > 0:
            from datetime import datetime, timedelta
            try:
                # Parse the date and subtract buffer days
                original_date = datetime.fromisoformat(published_after.replace('Z', '+00:00'))
                buffered_date = original_date - timedelta(days=buffer_days)
                published_after = buffered_date.strftime('%Y-%m-%dT%H:%M:%SZ')
                print(f"Applied -{buffer_days} day buffer to start date: {published_after}")
            except ValueError:
                print(f"Warning: Could not parse published_after date: {published_after}")
        
        if published_before and buffer_days > 0:
            from datetime import datetime, timedelta
            try:
                # Parse the date and add buffer days
                original_date = datetime.fromisoformat(published_before.replace('Z', '+00:00'))
                buffered_date = original_date + timedelta(days=buffer_days)
                published_before = buffered_date.strftime('%Y-%m-%dT%H:%M:%SZ')
                print(f"Applied +{buffer_days} day buffer to end date: {published_before}")
            except ValueError:
                print(f"Warning: Could not parse published_before date: {published_before}")
        
        # Get channel ID
        channel_id = self.get_channel_id(channel_identifier)
        print(f"Channel ID: {channel_id}")
        
        # Get video IDs (latest first) with date filtering
        video_ids = self.get_all_video_ids(channel_id, max_videos, published_after, published_before)
        
        if not video_ids:
            print("No videos found in channel")
            return []
        
        # Get video metadata
        videos_metadata = self.get_video_metadata(video_ids)
        
        print(f"Successfully scraped {len(videos_metadata)} videos")
        return videos_metadata
    
    
    def save_to_csv(self, videos: List[VideoMetadata], filename: str = None, 
                   channel_name: str = None, date_range: str = None):
        """
        Save video metadata to CSV file
        
        Args:
            videos: List of VideoMetadata objects
            filename: Output filename (optional)
            channel_name: Channel name for filename
            date_range: Date range for filename
        """
        # Create result directory if it doesn't exist
        result_dir = "result"
        os.makedirs(result_dir, exist_ok=True)
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if channel_name and date_range:
                # Clean channel name for filename
                clean_channel = channel_name.replace(' ', '_').replace('@', '').replace('/', '_')
                filename = f"{clean_channel}_{date_range}_{timestamp}.csv"
            else:
                filename = f"youtube_videos_{timestamp}.csv"
        
        # Add result directory to filename
        filename = os.path.join(result_dir, filename)
        
        # Convert to DataFrame
        data = []
        for video in videos:
            category_name = self.categories.get_category_name(video.category_id)
            data.append({
                'video_id': video.video_id,
                'url': video.url,
                'title': video.title,
                'description': video.description,
                'channel_title': video.channel_title,
                'published_at': video.published_at,
                'duration': video.duration,
                'view_count': video.view_count,
                'like_count': video.like_count,
                'comment_count': video.comment_count,
                'thumbnail_url': video.thumbnail_url,
                'tags': ', '.join(video.tags),
                'category_id': video.category_id,
                'category_name': category_name,
                'language': video.language
            })
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Data saved to {filename}")
    
    def get_category_statistics(self, videos: List[VideoMetadata]):
        """
        Get and print category statistics for videos
        
        Args:
            videos: List of VideoMetadata objects
        """
        if not videos:
            print("No videos to analyze")
            return
        
        # Convert to dictionary format for categories helper
        videos_data = []
        for video in videos:
            videos_data.append({
                'category_id': video.category_id,
                'title': video.title,
                'view_count': video.view_count
            })
        
        # Print category statistics
        self.categories.print_category_stats(videos_data)
    
    def save_to_json(self, videos: List[VideoMetadata], filename: str = None,
                    channel_name: str = None, date_range: str = None):
        """
        Save video metadata to JSON file
        
        Args:
            videos: List of VideoMetadata objects
            filename: Output filename (optional)
            channel_name: Channel name for filename
            date_range: Date range for filename
        """
        # Create result directory if it doesn't exist
        result_dir = "result"
        os.makedirs(result_dir, exist_ok=True)
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if channel_name and date_range:
                # Clean channel name for filename
                clean_channel = channel_name.replace(' ', '_').replace('@', '').replace('/', '_')
                filename = f"{clean_channel}_{date_range}_{timestamp}.json"
            else:
                filename = f"youtube_videos_{timestamp}.json"
        
        # Add result directory to filename
        filename = os.path.join(result_dir, filename)
        
        # Convert to dictionary format
        data = []
        for video in videos:
            category_name = self.categories.get_category_name(video.category_id)
            data.append({
                'video_id': video.video_id,
                'url': video.url,
                'title': video.title,
                'description': video.description,
                'channel_title': video.channel_title,
                'published_at': video.published_at,
                'duration': video.duration,
                'view_count': video.view_count,
                'like_count': video.like_count,
                'comment_count': video.comment_count,
                'thumbnail_url': video.thumbnail_url,
                'tags': video.tags,
                'category_id': video.category_id,
                'category_name': category_name,
                'language': video.language
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Data saved to {filename}")
    


def main():
    """Main function to run the scraper"""
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("Error: YOUTUBE_API_KEY not found in environment variables")
        print("Please set your YouTube API key in a .env file or environment variable")
        return
    
    # Get channel identifier
    channel_id = os.getenv('CHANNEL_ID')
    channel_username = os.getenv('CHANNEL_USERNAME')
    
    if not channel_id and not channel_username:
        print("Please provide either CHANNEL_ID or CHANNEL_USERNAME in your .env file")
        print("Or pass it as an argument to the script")
        return
    
    channel_identifier = channel_id or channel_username
    
    # Get max videos limit (for testing)
    max_videos = os.getenv('MAX_VIDEOS')
    if max_videos:
        try:
            max_videos = int(max_videos)
            print(f"Limiting to {max_videos} videos for testing")
        except ValueError:
            max_videos = None
    else:
        max_videos = None
    
    # Get date range filters
    published_after = os.getenv('PUBLISHED_AFTER')
    published_before = os.getenv('PUBLISHED_BEFORE')
    
    # Add buffer if specified
    buffer_days = os.getenv('BUFFER_DAYS')
    if buffer_days:
        try:
            buffer_days = int(buffer_days)
            print(f"Adding ±{buffer_days} day buffer to date range")
        except ValueError:
            buffer_days = 0
    else:
        buffer_days = 0
    
    try:
        # Initialize scraper
        scraper = YouTubeChannelScraper(api_key)
        
        # Scrape channel with optional date filters and buffer
        videos = scraper.scrape_channel(channel_identifier, max_videos, published_after, published_before, buffer_days)
        
        if videos:
            # Generate filename components
            channel_name = videos[0].channel_title if videos else channel_identifier
            
            # Generate date range string
            if published_after and published_before:
                # Extract year from dates
                start_year = published_after[:4] if published_after else "all"
                end_year = published_before[:4] if published_before else "all"
                if start_year == end_year:
                    date_range = f"{start_year}"
                else:
                    date_range = f"{start_year}-{end_year}"
            else:
                date_range = "all_dates"
            
            # Save to both CSV and JSON with descriptive filenames
            scraper.save_to_csv(videos, channel_name=channel_name, date_range=date_range)
            scraper.save_to_json(videos, channel_name=channel_name, date_range=date_range)
            
            # Print category statistics
            scraper.get_category_statistics(videos)
            
            # Print basic summary
            print(f"\nScraping completed!")
            print(f"Total videos: {len(videos)}")
            print(f"Total views: {sum(v.view_count for v in videos):,}")
            print(f"Total likes: {sum(v.like_count for v in videos):,}")
            print(f"Total comments: {sum(v.comment_count for v in videos):,}")
        else:
            print("No videos found")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()

