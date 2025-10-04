#!/usr/bin/env python3
"""
Simple script to find YouTube channel ID from channel name or handle
"""

import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

def find_channel_id(search_term, save_to_file=True):
    """Find channel ID from search term"""
    load_dotenv()
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    if not api_key:
        print("Error: YOUTUBE_API_KEY not found in .env file")
        return
    
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    try:
        # Search for channels
        request = youtube.search().list(
            part='snippet',
            q=search_term,
            type='channel',
            maxResults=10
        )
        response = request.execute()
        
        print(f"Search results for '{search_term}':")
        print("=" * 50)
        
        results = []
        for i, item in enumerate(response.get('items', []), 1):
            channel_id = item['snippet']['channelId']
            title = item['snippet']['title']
            description = item['snippet']['description'][:100] + "..." if len(item['snippet']['description']) > 100 else item['snippet']['description']
            
            result = {
                'rank': i,
                'title': title,
                'channel_id': channel_id,
                'description': description,
                'url': f"https://www.youtube.com/channel/{channel_id}"
            }
            results.append(result)
            
            print(f"{i}. Title: {title}")
            print(f"   Channel ID: {channel_id}")
            print(f"   Description: {description}")
            print(f"   URL: https://www.youtube.com/channel/{channel_id}")
            print("-" * 30)
        
        # Save results to file if requested
        if save_to_file and results:
            import json
            from datetime import datetime
            
            # Create result directory
            result_dir = "result"
            os.makedirs(result_dir, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            clean_search = search_term.replace(' ', '_').replace('@', '').replace('/', '_')
            filename = f"{result_dir}/channel_search_{clean_search}_{timestamp}.json"
            
            # Save to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'search_term': search_term,
                    'timestamp': timestamp,
                    'total_results': len(results),
                    'results': results
                }, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Results saved to: {filename}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        search_term = sys.argv[1]
    else:
        search_term = input("Enter channel name or handle to search: ")
    
    find_channel_id(search_term)
