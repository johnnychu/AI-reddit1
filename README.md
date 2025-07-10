# Reddit Stock Crawler

A Python web crawler that finds the top 10 most mentioned stock symbols on Reddit by analyzing posts and comments from popular finance-related subreddits.

## Features

- Crawls multiple stock-related subreddits (r/wallstreetbets, r/stocks, r/investing, etc.)
- Uses Reddit's official API through PRAW (Python Reddit API Wrapper)
- Extracts stock ticker symbols using intelligent pattern matching
- Filters out common false positives
- Implements proper rate limiting and error handling
- Ranks symbols by frequency of mentions
- Saves results to a text file

## Prerequisites

- Python 3.7 or higher
- Reddit API credentials (free to obtain)

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get Reddit API credentials:**
   - Go to https://www.reddit.com/prefs/apps
   - Click "Create App" or "Create Another App"
   - Choose "script" as the app type
   - Note down your client ID and client secret

3. **Configure environment variables:**
   - Copy `.env.example` to `.env`
   - Fill in your Reddit API credentials:
   ```
   REDDIT_CLIENT_ID=your-client-id
   REDDIT_CLIENT_SECRET=your-client-secret
   REDDIT_USER_AGENT=RedditStockCrawler/1.0
   ```

## Usage

Run the crawler:
```bash
python reddit_stock_crawler.py
```

The script will:
1. Connect to Reddit's API
2. Crawl the specified subreddits
3. Extract and count stock symbol mentions
4. Display the top 10 results
5. Save results to `top_stocks.txt`

## Subreddits Analyzed

- r/wallstreetbets
- r/stocks
- r/investing
- r/SecurityAnalysis
- r/pennystocks

## How It Works

1. **Symbol Extraction**: Uses regex to find potential ticker symbols (1-5 uppercase letters, optionally prefixed with $)
2. **Filtering**: Removes common false positives like "THE", "AND", etc.
3. **Counting**: Tracks mentions across post titles, content, and top comments
4. **Ranking**: Sorts by frequency to find the most discussed symbols

## Rate Limiting

The crawler implements proper rate limiting to respect Reddit's API guidelines:
- 0.1-second delay between requests
- Limits comment analysis to top 10 per post
- Handles API errors gracefully

## Output Example

```
==================================================
TOP 10 MOST MENTIONED STOCK SYMBOLS ON REDDIT
==================================================
 1. $TSLA   -  156 mentions
 2. $AAPL   -  134 mentions
 3. $GME    -  98  mentions
 4. $SPY    -  87  mentions
 5. $NVDA   -  76  mentions
 6. $AMD    -  65  mentions
 7. $MSFT   -  54  mentions
 8. $QQQ    -  43  mentions
 9. $PLTR   -  38  mentions
10. $BB     -  32  mentions
==================================================
```

## Ethical Considerations

- Respects Reddit's API terms of service
- Implements proper rate limiting
- Uses read-only access
- Does not store personal information

## License

This project is for educational purposes. Please ensure compliance with Reddit's API terms and your local regulations when using this tool.
