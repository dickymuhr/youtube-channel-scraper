# 🎬 YouTube Channel Scraper

A Python tool to scrape video metadata from YouTube channels using the official YouTube Data API v3.

## ✨ Features

Extracts the following metadata for videos in a YouTube channel:

- 🔗 Video URL
- 📝 Title
- 📄 Description
- 👍 Likes Count
- 💬 Comment Count
- 👀 View Count
- ⏱️ Video Duration
- 📅 Publication Date
- 🖼️ Thumbnail URL
- 📺 Channel Title
- 🏷️ Tags
- 📂 Category ID & Name
- 🌐 Language

## 📋 Prerequisites

1. 🐍 Python 3.7+
2. 🔑 YouTube Data API v3 Key - Get one from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)

## 🚀 Installation

1. **Clone the repository:**
```bash
git clone https://github.com/dickymuhr/youtube-channel-scraper.git
cd youtube-channel-scraper
```

2. **Set up virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure API key:**
```bash
cp env_example.txt .env
# Edit .env and add your YouTube API key
```

## 💻 Usage

### 🎯 Basic Usage
```bash
python youtube_scraper.py
```

### 🔍 Find Channel ID
```bash
python find_channel_id.py "channel_name"
python find_channel_id.py "@handle_name"
```

### 🐍 Programmatic Usage
```python
from youtube_scraper import YouTubeChannelScraper

scraper = YouTubeChannelScraper("your_api_key_here")
videos = scraper.scrape_channel("GoogleDevelopers")

# With date filtering
videos = scraper.scrape_channel(
    "GoogleDevelopers",
    max_videos=10,
    published_after="2022-01-01T00:00:00Z",
    published_before="2022-12-31T23:59:59Z",
    buffer_days=1
)
```

## ⚙️ Configuration

Environment variables in `.env`:

```bash
# Required
YOUTUBE_API_KEY=your_api_key_here

# Optional
CHANNEL_ID=UC_x5XG1OV2P6uZZ5FSM9Ttw
MAX_VIDEOS=10
PUBLISHED_AFTER=2022-01-01T00:00:00Z
PUBLISHED_BEFORE=2022-12-31T23:59:59Z
BUFFER_DAYS=1
```

## 📁 Output

Files are saved to the `result/` folder:

```
result/
├── ChannelName_Year_timestamp.csv
├── ChannelName_Year_timestamp.json
└── channel_search_term_timestamp.json
```

### 📊 CSV Format
```csv
video_id,url,title,description,channel_title,published_at,duration,view_count,like_count,comment_count,thumbnail_url,tags,category_id,language,category_name
```

## 🔧 API Setup

1. 🌐 Go to [Google Cloud Console](https://console.cloud.google.com/)
2. ➕ Create a new project or select existing one
3. 🔌 Enable the YouTube Data API v3
4. 🔑 Create credentials (API Key)
5. 📋 Copy the API key to your `.env` file

### 📈 API Quotas
- 🆓 Free Tier: 10,000 quota units per day
- 📋 Video List Request: 1 unit per request
- 🎥 Video Details Request: 1 unit per video

## 🛠️ Troubleshooting

1. **❌ "API key not valid"**
   - Check your API key in `.env` file
   - Ensure YouTube Data API v3 is enabled

2. **🔍 "Channel not found"**
   - Use `find_channel_id.py` to search for correct channel ID
   - Check if channel is public

3. **⏱️ "Rate limit exceeded"**
   - Scraper handles this automatically
   - Consider reducing `MAX_VIDEOS` for testing

4. **📊 "Quota exceeded"**
   - Wait 24 hours for quota reset
   - Use `MAX_VIDEOS` to limit requests

## 📄 License

MIT License