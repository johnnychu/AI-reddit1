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
from collections import Counter
from typing import List, Set, Dict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RedditStockCrawler:
    def __init__(self):
        """Initialize the Reddit API client"""
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
        
        # Common stock ticker pattern: 1-5 uppercase letters, often preceded by $
        self.ticker_pattern = re.compile(r'\b(?:\$)?([A-Z]{1,5})\b')
        
        # Filter out common false positives
        self.exclude_words = {
            # Common English words
            'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER', 
            'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS', 'HIM', 'HIS', 'HOW',
            'ITS', 'NEW', 'NOW', 'OLD', 'SEE', 'TWO', 'WHO', 'BOY', 'DID', 'ILL',
            'LET', 'OWN', 'SAY', 'SHE', 'TOO', 'USE', 'WAY', 'WHY', 'YOU', 'USD',
            'TO', 'IS', 'IT', 'AT', 'ON', 'IN', 'BY', 'UP', 'AS', 'OR', 'IF',
            'MY', 'WE', 'ME', 'HE', 'BE', 'DO', 'GO', 'SO', 'NO', 'OF', 'AN',
            'A', 'I', 'US', 'VS', 'AM', 'PM', 'UK', 'CA', 'EU', 'NY', 'LA',
            'THAT', 'THIS', 'HAVE', 'WITH', 'WILL', 'FROM', 'THEY', 'BEEN',
            'WERE', 'SAID', 'EACH', 'WHICH', 'THEIR', 'TIME', 'THAN', 'MANY',
            'SOME', 'WHAT', 'WOULD', 'MAKE', 'LIKE', 'INTO', 'OVER', 'THINK',
            'ALSO', 'BACK', 'AFTER', 'FIRST', 'WELL', 'WORK', 'LIFE', 'ONLY',
            'YEAR', 'YEARS', 'LAST', 'MUCH', 'WHERE', 'THOSE', 'COME', 'CAME',
            'RIGHT', 'USED', 'EACH', 'MADE', 'MOST', 'OVER', 'SAID', 'SOME',
            'VERY', 'WHAT', 'WITH', 'HAVE', 'FROM', 'THEY', 'KNOW', 'WANT',
            'BEEN', 'GOOD', 'MUCH', 'COME', 'COULD', 'WOULD', 'SHOULD', 'JUST',
            'HTTPS', 'HTTP', 'WWW', 'COM', 'ORG', 'NET', 'GOV', 'EDU',
            # Financial/Business terms that aren't tickers
            'CEO', 'CFO', 'CTO', 'IPO', 'SEC', 'FDA', 'FBI', 'IRS', 'LLC', 'INC',
            'ETF', 'ATH', 'ATL', 'YTD', 'EOD', 'AH', 'PM', 'DD', 'TA', 'FA',
            'YOLO', 'HODL', 'FOMO', 'FUD', 'WSB', 'LOL', 'OMG', 'WTF', 'TBH',
            'IMO', 'IMHO', 'TLDR', 'ELI', 'AMA', 'TIL', 'PSA', 'EDIT', 'UPDATE',
            'BULL', 'BEAR', 'MOON', 'DIP', 'RIP', 'BUY', 'SELL', 'HOLD'
        }
        
        # Common legitimate stock symbols that should be included
        self.known_stocks = {
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'TSLA', 'META', 'NVDA',
            'NFLX', 'CRM', 'ORCL', 'ADBE', 'UBER', 'ABNB', 'COIN', 'RBLX',
            'GME', 'AMC', 'BB', 'NOK', 'PLTR', 'WISH', 'CLOV', 'MVIS',
            'SPY', 'QQQ', 'IWM', 'VTI', 'VOO', 'SQQQ', 'TQQQ', 'UVXY',
            'AMD', 'INTEL', 'MU', 'QCOM', 'AMAT', 'LRCX', 'KLAC', 'MCHP'
        }
        
        # Subreddits to crawl
        # self.subreddits = ['wallstreetbets', 'stocks', 'investing', 'SecurityAnalysis', 'pennystocks']
        self.subreddits = ['wallstreetbets']
    
    def extract_tickers(self, text: str) -> Set[str]:
        """Extract potential stock ticker symbols from text"""
        if not text:
            return set()
        
        # Find all potential tickers
        matches = self.ticker_pattern.findall(text.upper())
        
        # Filter out common false positives and ensure reasonable length
        tickers = set()
        for match in matches:
            # Skip if it's in our exclude list
            if match in self.exclude_words:
                continue
            
            # Skip if it's too short or too long
            if not (1 <= len(match) <= 5):
                continue
                
            # Skip if it's pure numbers
            if match.isdigit():
                continue
            
            # Prefer known stock symbols
            if match in self.known_stocks:
                tickers.add(match)
                continue
            
            # For unknown symbols, apply stricter filtering
            # Must be 2-5 characters for unknown symbols
            if 2 <= len(match) <= 5:
                # Skip common words that might slip through
                if match not in {'NULL', 'TRUE', 'FALSE', 'NONE', 'NULL'}:
                    tickers.add(match)
        
        return tickers
    
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
        print("\n" + "="*50)
        print("TOP 10 MOST MENTIONED STOCK SYMBOLS ON REDDIT")
        print("="*50)
        
        for i, (ticker, count) in enumerate(top_stocks, 1):
            print(f"{i:2d}. ${ticker:<6} - {count:4d} mentions")
        
        print("="*50)
        print(f"Total unique symbols found: {len(top_stocks)}")


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
            f.write("Top 10 Stock Symbols from Reddit\n")
            f.write("=" * 35 + "\n")
            for i, (ticker, count) in enumerate(top_stocks, 1):
                f.write(f"{i:2d}. ${ticker:<6} - {count:4d} mentions\n")
        
        print(f"\nResults saved to 'top_stocks.txt'")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please check your Reddit API credentials and internet connection.")


if __name__ == "__main__":
    main()
