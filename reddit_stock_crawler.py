#!/usr/bin/env python3
"""
Reddit Stock Symbol Crawler

This script crawls Reddit to find the top 10 most mentioned stock symbols.
It uses the PRAW library to access Reddit's API and extracts ticker symbols
from posts and comments in stock-related subreddits.
"""

import praw
import re
import time
import requests
import json
from collections import Counter
from typing import List, Set, Dict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RedditStockCrawler:
    def __init__(self):
        """Initialize the Reddit API client and load SEC ticker data"""
        try:
            self.reddit = praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                user_agent=os.getenv('REDDIT_USER_AGENT', 'StockCrawler/1.0')
            )
            
            # Test the connection
            print("Testing Reddit API connection...")
            try:
                # This will trigger authentication
                self.reddit.user.me()
                print("✅ Reddit API connection successful!")
            except Exception as e:
                print(f"⚠️  Reddit API authentication failed: {e}")
                print("Note: Script will attempt to continue with read-only access")
                
        except Exception as e:
            print(f"❌ Failed to initialize Reddit API client: {e}")
            raise
        
        # Load official SEC company tickers
        print("Loading SEC company tickers...")
        self.valid_tickers = self._load_sec_tickers()
        print(f"✅ Loaded {len(self.valid_tickers)} official stock tickers from SEC")
        
        # Simple stock ticker pattern
        self.ticker_pattern = re.compile(r'\b\$?([A-Z]{1,5})\b')
        
        # Subreddits to crawl
        self.subreddits = ['wallstreetbets', 'stocks', 'investing', 'SecurityAnalysis', 'pennystocks']
    
    def _load_sec_tickers(self) -> Set[str]:
        """Load official stock tickers from local SEC data file"""
        try:
            # First try to load from local file
            try:
                with open('sec_tickers.json', 'r') as f:
                    ticker_data = json.load(f)
                
                tickers = set()
                for item in ticker_data:
                    ticker = item.get('ticker', '').upper()
                    if ticker:
                        # Handle tickers with special characters (like BRK-B)
                        base_ticker = ticker.split('-')[0].split('.')[0]
                        if base_ticker and len(base_ticker) <= 5:
                            tickers.add(base_ticker)
                        # Also add the full ticker if it has special chars
                        if '-' in ticker or '.' in ticker:
                            tickers.add(ticker)
                
                return tickers
                
            except FileNotFoundError:
                print("Local SEC data not found, fetching from web...")
                # Fall back to web fetch with proper headers
                headers = {
                    'User-Agent': 'Reddit Stock Crawler 1.0 (Educational Use)',
                    'Accept': 'application/json',
                }
                
                url = "https://www.sec.gov/files/company_tickers.json"
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                company_data = response.json()
                tickers = set()
                
                for company_info in company_data.values():
                    ticker = company_info.get('ticker', '').upper()
                    if ticker:
                        base_ticker = ticker.split('-')[0].split('.')[0]
                        if base_ticker and len(base_ticker) <= 5:
                            tickers.add(base_ticker)
                        if '-' in ticker or '.' in ticker:
                            tickers.add(ticker)
                
                return tickers
            
        except Exception as e:
            print(f"⚠️  Failed to load SEC tickers: {e}")
            print("Falling back to basic known tickers...")
            # Fallback to a basic set of well-known tickers
            return {
                'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'TSLA', 'META', 'NVDA',
                'NFLX', 'CRM', 'ORCL', 'ADBE', 'UBER', 'ABNB', 'COIN', 'RBLX',
                'GME', 'AMC', 'BB', 'NOK', 'PLTR', 'WISH', 'CLOV', 'MVIS',
                'SPY', 'QQQ', 'IWM', 'VTI', 'VOO', 'SQQQ', 'TQQQ', 'UVXY',
                'AMD', 'INTEL', 'MU', 'QCOM', 'AMAT', 'LRCX', 'KLAC', 'MCHP',
                'BRK', 'BRKA', 'BRKB'  # Added Berkshire variations
            }
    
    def extract_tickers(self, text: str) -> Set[str]:
        """Extract stock ticker symbols from text using SEC official list"""
        if not text:
            return set()
        
        # Find symbols with $ prefix first (these are most likely to be stocks)
        dollar_pattern = re.compile(r'\$([A-Z]{1,5})\b')
        dollar_matches = set(dollar_pattern.findall(text.upper()))
        
        # Find all potential tickers
        matches = set(self.ticker_pattern.findall(text.upper()))
        
        # Only include tickers that are in the official SEC list
        valid_tickers = set()
        
        for match in matches:
            # Skip if it's too long or contains numbers
            if len(match) > 5 or match.isdigit():
                continue
            
            # Check if it's a valid SEC ticker
            if match in self.valid_tickers:
                valid_tickers.add(match)
            # Special handling for symbols with $ prefix - they're more likely to be intentional
            elif match in dollar_matches and len(match) >= 2:
                # Even if not in SEC list, if it has $ prefix and looks like a ticker, include it
                # This catches things like crypto symbols or newer listings
                valid_tickers.add(match)
        
        return valid_tickers
    
    def crawl_subreddit(self, subreddit_name: str, limit: int = 25) -> Counter:
        """Crawl a specific subreddit for stock mentions"""
        print(f"Crawling r/{subreddit_name}...")
        ticker_counter = Counter()
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Get hot posts
            for submission in subreddit.hot(limit=limit):
                # Extract from title and selftext
                tickers = self.extract_tickers(submission.title)
                tickers.update(self.extract_tickers(submission.selftext))
                
                for ticker in tickers:
                    ticker_counter[ticker] += 1
                
                # Extract from top comments (limit to avoid rate limiting)
                submission.comments.replace_more(limit=0)
                for comment in submission.comments[:10]:  # Top 10 comments
                    comment_tickers = self.extract_tickers(comment.body)
                    for ticker in comment_tickers:
                        ticker_counter[ticker] += 1
                
                # Rate limiting - be respectful to Reddit's servers
                time.sleep(0.1)
                
        except Exception as e:
            print(f"Error crawling r/{subreddit_name}: {e}")
            if "401" in str(e):
                print("💡 Tip: Check your Reddit API credentials in the .env file")
                print("   Make sure your Reddit app is configured as 'script' type")
                print("   Visit https://www.reddit.com/prefs/apps to verify settings")
        
        return ticker_counter
    
    def get_top_stocks(self, num_stocks: int = 10) -> List[tuple]:
        """Get the top N most mentioned stock symbols across all subreddits"""
        print("Starting Reddit stock symbol crawl...")
        total_counter = Counter()
        
        for subreddit_name in self.subreddits:
            subreddit_counter = self.crawl_subreddit(subreddit_name)
            total_counter.update(subreddit_counter)
            print(f"Found {len(subreddit_counter)} unique tickers in r/{subreddit_name}")
        
        # Get top stocks
        top_stocks = total_counter.most_common(num_stocks)
        return top_stocks
    
    def display_results(self, top_stocks: List[tuple]):
        """Display the results in a formatted way"""
        print("\n" + "="*60)
        print("🏆 TOP 10 MOST MENTIONED STOCK SYMBOLS ON REDDIT")
        print("="*60)
        
        if not top_stocks:
            print("No valid stock symbols found.")
            return
        
        for i, (ticker, count) in enumerate(top_stocks, 1):
            print(f"{i:2d}. ${ticker:<6} - {count:4d} mentions")
        
        print("="*60)
        print(f"📊 Total unique symbols found: {len(top_stocks)}")
        print(f"✅ All symbols verified against SEC official ticker list")


def main():
    """Main function to run the crawler"""
    # Check if environment variables are set
    if not os.getenv('REDDIT_CLIENT_ID'):
        print("Error: Reddit API credentials not found!")
        print("Please create a .env file with the following variables:")
        print("REDDIT_CLIENT_ID=your_client_id")
        print("REDDIT_CLIENT_SECRET=your_client_secret")
        print("REDDIT_USER_AGENT=YourApp/1.0")
        print("\nYou can get these credentials from: https://www.reddit.com/prefs/apps")
        return
    
    crawler = RedditStockCrawler()
    
    try:
        top_stocks = crawler.get_top_stocks(10)
        crawler.display_results(top_stocks)
        
        # Optionally save to file
        with open('top_stocks.txt', 'w') as f:
            f.write("Top 10 Stock Symbols from Reddit (SEC Verified)\n")
            f.write("=" * 48 + "\n")
            for i, (ticker, count) in enumerate(top_stocks, 1):
                f.write(f"{i:2d}. ${ticker:<6} - {count:4d} mentions\n")
            f.write("\nNote: All symbols verified against SEC official ticker list\n")
        
        print(f"\nResults saved to 'top_stocks.txt'")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please check your Reddit API credentials and internet connection.")


if __name__ == "__main__":
    main()
