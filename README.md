# YouTube Channel Scraper

A comprehensive Python tool to scrape video metadata from YouTube channels using the official YouTube Data API v3. Features automatic result organization, category mapping, and flexible date filtering.

## 🚀 Features

### 📊 Complete Video Metadata
- ✅ **Video URL** - Direct link to the video
- ✅ **Title** - Video title
- ✅ **Description** - Full video description
- ✅ **Likes Count** - Number of likes
- ✅ **Comment Count** - Number of comments
- ✅ **View Count** - Number of views
- ✅ **Video Duration** - Duration in readable format (e.g., "4:13")
- ✅ **Publication Date** - When the video was published
- ✅ **Thumbnail URL** - High-quality thumbnail image
- ✅ **Channel Title** - Name of the channel
- ✅ **Tags** - Video tags
- ✅ **Category ID & Name** - YouTube category with human-readable names
- ✅ **Language** - Video language

### 🎯 Smart Organization
- ✅ **Automatic Result Folder** - All outputs saved to `result/` directory
- ✅ **Descriptive Filenames** - Channel name + date range + timestamp
- ✅ **Category Statistics** - Automatic category breakdown and analysis
- ✅ **Channel Search Tool** - Find channel IDs from usernames/handles

### ⚡ Advanced Filtering
- ✅ **Date Range Filtering** - Filter by publication date with API-level efficiency
- ✅ **Buffer Days** - Add ±N days to date ranges for flexibility
- ✅ **Video Limit** - Test with limited number of videos
- ✅ **Latest First** - Videos ordered newest to oldest by default

## 📁 Project Structure

```
youtube-channel-scraper/
├── youtube_scraper.py          # Main scraper
├── youtube_categories.py       # Categories helper
├── find_channel_id.py          # Channel search utility
├── requirements.txt            # Dependencies
├── env_example.txt            # Environment template
├── README.md                  # This file
├── .env                       # Your configuration
├── venv/                      # Virtual environment
└── result/                    # Output files (auto-created)
    ├── ChannelName_Year_*.csv
    ├── ChannelName_Year_*.json
    └── channel_search_*.json
```

## 🛠️ Prerequisites

1. **Python 3.7+**
2. **YouTube Data API v3 Key** - Get one from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)

## ⚙️ Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd youtube-channel-scraper
```

### 2. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Key
```bash
# Copy environment template
cp env_example.txt .env

# Edit .env and add your YouTube API key
# Get API key from: https://console.cloud.google.com/apis/credentials
```

## 🚀 Quick Start

### 1. Basic Usage
```bash
# Set your API key in .env file, then run:
python youtube_scraper.py
```

### 2. Find Channel ID
```bash
# Search for a channel by name or handle
python find_channel_id.py "channel_name"
python find_channel_id.py "@handle_name"
```

### 3. Programmatic Usage
```python
from youtube_scraper import YouTubeChannelScraper

# Initialize scraper
scraper = YouTubeChannelScraper("your_api_key_here")

# Scrape all videos (latest first)
videos = scraper.scrape_channel("GoogleDevelopers")

# Scrape with limits and date filtering
videos = scraper.scrape_channel(
    "GoogleDevelopers",
    max_videos=10,  # First 10 latest videos
    published_after="2022-01-01T00:00:00Z",
    published_before="2022-12-31T23:59:59Z",
    buffer_days=1  # Add ±1 day buffer
)

# Files automatically saved to result/ folder
# with descriptive names like: GoogleDevelopers_2022_20240101_120000.csv
```

## 📋 Configuration

### Environment Variables (.env)
```bash
# Required
YOUTUBE_API_KEY=your_api_key_here

# Optional: Channel to scrape
CHANNEL_ID=UC_x5XG1OV2P6uZZ5FSM9Ttw
# or
CHANNEL_USERNAME=GoogleDevelopers

# Optional: Testing and limits
MAX_VIDEOS=10                    # Limit for testing

# Optional: Date range filtering (ISO 8601 format)
PUBLISHED_AFTER=2022-01-01T00:00:00Z
PUBLISHED_BEFORE=2022-12-31T23:59:59Z

# Optional: Add buffer days to date range
BUFFER_DAYS=1                    # ±1 day buffer
```

## 🎯 Advanced Features

### 1. Date Range Filtering
```python
# Filter videos from 2022 with ±2 day buffer
videos = scraper.scrape_channel(
    "ChannelName",
    published_after="2022-01-01T00:00:00Z",
    published_before="2022-12-31T23:59:59Z",
    buffer_days=2
)
```

### 2. Category Analysis
```python
# Get category statistics
scraper.get_category_statistics(videos)

# Output example:
# 📊 Video Category Statistics:
# ========================================
# Education           :  45 videos (55.6%)
# Science & Technology:  20 videos (24.7%)
# Entertainment       :  16 videos (19.7%)
# Total               :  81 videos
```

### 3. Channel Discovery
```python
# Find channel ID from username or handle
from find_channel_id import find_channel_id

# Search by name
find_channel_id("pmi_tv")

# Search by handle
find_channel_id("@roteskreuz_de")
```

### 4. Custom Processing
```python
# Filter high-engagement videos
high_engagement = [v for v in videos if v.like_count > 1000]

# Sort by view count
top_videos = sorted(videos, key=lambda x: x.view_count, reverse=True)

# Get recent videos
recent_videos = [v for v in videos if v.published_at > "2023-01-01"]
```

## 📊 Output Files

### Automatic Organization
All files are saved to the `result/` folder with descriptive names:

```
result/
├── GoogleDevelopers_2022_20240101_120000.csv
├── GoogleDevelopers_2022_20240101_120000.json
├── PMI_TV_2022_20240101_130000.csv
├── PMI_TV_2022_20240101_130000.json
└── channel_search_pmi_tv_20240101_140000.json
```

### CSV Format
```csv
video_id,url,title,description,channel_title,published_at,duration,view_count,like_count,comment_count,thumbnail_url,tags,category_id,language,category_name
dQw4w9WgXcQ,https://www.youtube.com/watch?v=dQw4w9WgXcQ,Example Video,This is an example...,Example Channel,2023-01-01T00:00:00Z,3:32,1000000,50000,1000,https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg,"music,example",10,en,Music
```

### JSON Format
Structured JSON with the same data fields plus metadata about the scraping session.

## 🔧 API Setup

### 1. Google Cloud Console
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the YouTube Data API v3
4. Go to "Credentials" → "Create Credentials" → "API Key"
5. Copy the API key to your `.env` file

### 2. API Quotas
- **Free Tier**: 10,000 quota units per day
- **Video List Request**: 1 unit per request
- **Video Details Request**: 1 unit per video
- **Typical 1000-video channel**: ~1000-2000 quota units

## ⚡ Performance & Rate Limiting

- **Built-in Rate Limiting**: 0.1 second delay between requests
- **Automatic Retry**: Handles rate limit errors gracefully
- **Batch Processing**: Efficient API usage
- **Progress Tracking**: Real-time progress bars for long operations

## 🛠️ Troubleshooting

### Common Issues

1. **"API key not valid"**
   - Check your API key in `.env` file
   - Ensure YouTube Data API v3 is enabled
   - Verify API key has proper permissions

2. **"Channel not found"**
   - Use `find_channel_id.py` to search for correct channel ID
   - Check if channel is public and accessible
   - Verify channel username or ID format

3. **"Rate limit exceeded"**
   - Scraper handles this automatically with retries
   - Consider reducing `MAX_VIDEOS` for testing
   - Wait and retry if persistent

4. **"Quota exceeded"**
   - Wait 24 hours for quota reset
   - Upgrade to paid plan for higher limits
   - Use `MAX_VIDEOS` to limit requests

### Debug Mode
```python
# Enable debug output
scraper = YouTubeChannelScraper("your_api_key")
scraper.debug = True  # Shows detailed API responses
```

## 📈 Use Cases

- **Content Analysis**: Analyze video performance and engagement
- **Competitor Research**: Track competitor channel activity
- **Data Mining**: Extract video metadata for research
- **Archive Management**: Backup channel video information
- **Trend Analysis**: Study video publishing patterns

## ⚖️ Legal & Compliance

- ✅ **Official API**: Uses YouTube Data API v3 (compliant)
- ✅ **Terms of Service**: Follows YouTube's ToS
- ✅ **Rate Limited**: Respects API quotas and limits
- ✅ **Public Data Only**: Only accesses public video metadata
- ✅ **No Scraping**: Uses official API endpoints only

## 🤝 Contributing

Feel free to submit issues, feature requests, and pull requests!

## 📄 License

This project is open source and available under the MIT License.

---

**Happy Scraping! 🎬📊**