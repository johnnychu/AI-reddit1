#!/usr/bin/env python3
"""
Reddit Stock Symbol Crawler - Demo Version

This is a demo version that simulates the Reddit stock crawler functionality
without requiring actual Reddit API credentials. It shows how the system would work
with sample data.
"""

import re
import time
from collections import Counter
from typing import List, Set

class DemoRedditStockCrawler:
    def __init__(self):
        """Initialize the demo crawler with sample data"""
        # Common stock ticker pattern: 1-5 uppercase letters, often preceded by $
        self.ticker_pattern = re.compile(r'\b(?:\$)?([A-Z]{1,5})\b')
        
        # Filter out common false positives
        self.exclude_words = {
            'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER', 
            'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS', 'HIM', 'HIS', 'HOW',
            'ITS', 'NEW', 'NOW', 'OLD', 'SEE', 'TWO', 'WHO', 'BOY', 'DID', 'ILL',
            'LET', 'OWN', 'SAY', 'SHE', 'TOO', 'USE', 'WAY', 'WHY', 'YOU', 'USD',
            'CEO', 'CFO', 'CTO', 'IPO', 'SEC', 'FDA', 'FBI', 'IRS', 'LLC', 'INC',
            'ETF', 'ATH', 'ATL', 'YTD', 'EOD', 'AH', 'PM', 'DD', 'TA', 'FA',
            'YOLO', 'HODL', 'FOMO', 'FUD', 'WSB', 'LOL', 'OMG', 'WTF', 'TBH',
            'IMO', 'IMHO', 'TLDR', 'ELI', 'AMA', 'TIL', 'PSA', 'EDIT', 'UPDATE',
            'TO', 'IS', 'IT', 'AT', 'ON', 'IN', 'BY', 'UP', 'AS', 'OR', 'IF',
            'MY', 'WE', 'ME', 'HE', 'BE', 'DO', 'GO', 'SO', 'NO', 'OF', 'AN',
            'A', 'I', 'US', 'VS', 'AM', 'PM', 'UK', 'CA', 'EU', 'NY', 'LA'
        }
        
        # Sample Reddit post data (simulated)
        self.sample_posts = [
            "TSLA to the moon! 🚀 Anyone else buying the dip?",
            "Just bought more AAPL shares. Tim Cook is a genius!",
            "GME is still the play. Diamond hands! 💎🙌",
            "SPY looks bullish. Market rally incoming?",
            "NVDA earnings next week. Expecting big things!",
            "AMD vs INTEL - which is the better buy?",
            "Microsoft (MSFT) is undervalued IMO",
            "QQQ calls printing money 💰",
            "PLTR to $50 EOY mark my words",
            "BlackBerry ($BB) is making a comeback",
            "Tesla Model Y sales are through the roof! $TSLA",
            "Apple's new iPhone is amazing. Long $AAPL",
            "GameStop NFT marketplace is revolutionary $GME",
            "S&P 500 ETF $SPY hitting new highs",
            "NVIDIA AI chips demand is insane! $NVDA",
            "AMD Ryzen processors dominating Intel $AMD",
            "Microsoft Azure growth is incredible $MSFT",
            "Invesco QQQ Trust is my favorite ETF $QQQ",
            "Palantir government contracts are huge $PLTR",
            "BlackBerry cybersecurity division growing $BB"
        ]
    
    def extract_tickers(self, text: str) -> Set[str]:
        """Extract potential stock ticker symbols from text"""
        if not text:
            return set()
        
        # Find all potential tickers
        matches = self.ticker_pattern.findall(text.upper())
        
        # Filter out common false positives and ensure reasonable length
        tickers = {
            match for match in matches 
            if match not in self.exclude_words 
            and 1 <= len(match) <= 5
            and not match.isdigit()  # Exclude pure numbers
        }
        
        return tickers
    
    def simulate_crawl(self) -> Counter:
        """Simulate crawling Reddit with sample data"""
        print("🤖 Demo Mode: Simulating Reddit crawl with sample data...")
        ticker_counter = Counter()
        
        subreddits = ['wallstreetbets', 'stocks', 'investing', 'SecurityAnalysis', 'pennystocks']
        
        for subreddit in subreddits:
            print(f"📊 Analyzing r/{subreddit}...")
            
            # Simulate processing posts
            for i, post in enumerate(self.sample_posts):
                tickers = self.extract_tickers(post)
                for ticker in tickers:
                    # Add some randomness to make it more realistic
                    import random
                    mentions = random.randint(1, 3)
                    ticker_counter[ticker] += mentions
                
                # Simulate processing time
                time.sleep(0.05)
            
            print(f"✅ Found mentions in r/{subreddit}")
        
        return ticker_counter
    
    def get_top_stocks(self, num_stocks: int = 10) -> List[tuple]:
        """Get the top N most mentioned stock symbols"""
        total_counter = self.simulate_crawl()
        top_stocks = total_counter.most_common(num_stocks)
        return top_stocks
    
    def display_results(self, top_stocks: List[tuple]):
        """Display the results in a formatted way"""
        print("\n" + "="*50)
        print("🏆 TOP 10 MOST MENTIONED STOCK SYMBOLS (DEMO)")
        print("="*50)
        
        if not top_stocks:
            print("No stock symbols found in the demo data.")
            return
        
        for i, (ticker, count) in enumerate(top_stocks, 1):
            print(f"{i:2d}. ${ticker:<6} - {count:4d} mentions")
        
        print("="*50)
        print(f"📈 Total unique symbols found: {len(top_stocks)}")
        print("🤖 This is demo data. Use the main script with Reddit API for real data.")


def main():
    """Main function to run the demo crawler"""
    print("🚀 Reddit Stock Crawler - Demo Mode")
    print("=" * 40)
    
    crawler = DemoRedditStockCrawler()
    
    try:
        top_stocks = crawler.get_top_stocks(10)
        crawler.display_results(top_stocks)
        
        # Save demo results to file
        with open('demo_top_stocks.txt', 'w') as f:
            f.write("Top 10 Stock Symbols from Reddit (DEMO DATA)\n")
            f.write("=" * 45 + "\n")
            for i, (ticker, count) in enumerate(top_stocks, 1):
                f.write(f"{i:2d}. ${ticker:<6} - {count:4d} mentions\n")
            f.write("\nNote: This is demo data for testing purposes.\n")
        
        print(f"\n💾 Demo results saved to 'demo_top_stocks.txt'")
        
    except Exception as e:
        print(f"❌ An error occurred: {e}")


if __name__ == "__main__":
    main()
