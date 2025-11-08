"""
Cache Manager with Persistent Storage
Handles in-memory and file-based caching for price data
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional, Tuple
from config import CACHE_FILE, CACHE_TTL


class CacheManager:
    """Manages price caching with memory and file persistence"""
    
    def __init__(self):
        self.current_price_cache: Dict[str, Dict] = {}  # {ticker: {'price': float, 'timestamp': datetime}}
        self.historical_price_cache: Dict[Tuple[str, str], float] = {}  # {(ticker, date): price}
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0
        }
        self.load_from_file()
    
    def load_from_file(self):
        """Load historical price cache from file"""
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, 'r') as f:
                    data = json.load(f)
                    # Convert string keys back to tuples
                    for key_str, price in data.get('historical', {}).items():
                        ticker, date = key_str.split('|')
                        self.historical_price_cache[(ticker, date)] = price
                print(f"Loaded {len(self.historical_price_cache)} historical prices from cache file")
            except Exception as e:
                print(f"WARNING: Failed to load cache file: {e}")
    
    def save_to_file(self):
        """Save historical price cache to file"""
        try:
            # Convert tuple keys to strings for JSON
            historical_dict = {
                f"{ticker}|{date}": price
                for (ticker, date), price in self.historical_price_cache.items()
            }
            
            with open(CACHE_FILE, 'w') as f:
                json.dump({
                    'historical': historical_dict,
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            print(f"WARNING: Failed to save cache file: {e}")
    
    def get_current_price(self, ticker: str) -> Optional[float]:
        """Get current price from cache if not expired"""
        if ticker in self.current_price_cache:
            cached = self.current_price_cache[ticker]
            age = (datetime.now() - cached['timestamp']).total_seconds()
            
            if age < CACHE_TTL:
                self.stats['cache_hits'] += 1
                return cached['price']
        
        self.stats['cache_misses'] += 1
        return None
    
    def set_current_price(self, ticker: str, price: float):
        """Store current price in cache"""
        self.current_price_cache[ticker] = {
            'price': price,
            'timestamp': datetime.now()
        }
    
    def get_historical_price(self, ticker: str, date: str) -> Optional[float]:
        """Get historical price from cache"""
        key = (ticker, date)
        if key in self.historical_price_cache:
            self.stats['cache_hits'] += 1
            return self.historical_price_cache[key]
        
        self.stats['cache_misses'] += 1
        return None
    
    def set_historical_price(self, ticker: str, date: str, price: float):
        """Store historical price in cache (permanent)"""
        self.historical_price_cache[(ticker, date)] = price
        # Auto-save every 10 new historical prices
        if len(self.historical_price_cache) % 10 == 0:
            self.save_to_file()
    
    def get_cache_hit_rate(self) -> float:
        """Calculate cache hit rate percentage"""
        total = self.stats['cache_hits'] + self.stats['cache_misses']
        if total == 0:
            return 0.0
        return (self.stats['cache_hits'] / total) * 100
    
    def clear_current_cache(self):
        """Clear expired current price cache"""
        now = datetime.now()
        expired = [
            ticker for ticker, data in self.current_price_cache.items()
            if (now - data['timestamp']).total_seconds() >= CACHE_TTL
        ]
        for ticker in expired:
            del self.current_price_cache[ticker]
    
    def __del__(self):
        """Save cache on cleanup"""
        self.save_to_file()
