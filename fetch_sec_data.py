#!/usr/bin/env python3
"""
SEC Ticker Data Loader

This script fetches the latest SEC company tickers and saves them locally
for use by the Reddit stock crawler.
"""

import requests
import json
import time

def fetch_sec_tickers():
    """Fetch SEC company tickers and save to local file"""
    try:
        print("Fetching SEC company tickers...")
        
        # Add headers to avoid 403 error
        headers = {
            'User-Agent': 'Reddit Stock Crawler 1.0 (Contact: your-email@example.com)',
            'Accept': 'application/json',
        }
        
        url = "https://www.sec.gov/files/company_tickers.json"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        company_data = response.json()
        tickers = []
        
        for company_info in company_data.values():
            ticker = company_info.get('ticker', '').upper()
            title = company_info.get('title', '')
            if ticker:
                tickers.append({
                    'ticker': ticker,
                    'title': title
                })
        
        # Save to local file
        with open('sec_tickers.json', 'w') as f:
            json.dump(tickers, f, indent=2)
        
        print(f"✅ Successfully fetched and saved {len(tickers)} tickers to sec_tickers.json")
        return tickers
        
    except Exception as e:
        print(f"❌ Failed to fetch SEC tickers: {e}")
        return None

if __name__ == "__main__":
    # Add a small delay to be respectful to SEC servers
    time.sleep(1)
    fetch_sec_tickers()
