"""
API Client with Exponential Backoff Retries and Caching
Handles all communication with PRISM and LIMEX APIs
"""

import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import PRISM_BASE, LIMEX_BASE, TIMEOUT, MAX_RETRIES, RETRY_BASE_DELAY, MAX_WORKERS
from cache_manager import CacheManager


class APIClient:
    """API client with retry logic, caching, and concurrent processing"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.stats = {
            'total_calls': 0,
            'retries': 0,
            'failures': 0
        }
    
    def _api_call_with_retry(self, func, *args, **kwargs):
        """Execute API call with exponential backoff retry"""
        for attempt in range(MAX_RETRIES):
            try:
                self.stats['total_calls'] += 1
                return func(*args, **kwargs)
            
            except requests.exceptions.Timeout:
                if attempt < MAX_RETRIES - 1:
                    wait = RETRY_BASE_DELAY * (2 ** attempt)  # 1s, 2s, 4s
                    print(f"WARNING: Timeout, retrying in {wait}s (attempt {attempt + 1}/{MAX_RETRIES})")
                    self.stats['retries'] += 1
                    time.sleep(wait)
                else:
                    print(f"ERROR: Request timed out after {MAX_RETRIES} attempts")
                    self.stats['failures'] += 1
                    return None
            
            except requests.exceptions.ConnectionError:
                if attempt < MAX_RETRIES - 1:
                    wait = RETRY_BASE_DELAY * (2 ** attempt)
                    print(f"WARNING: Connection failed, retrying in {wait}s (attempt {attempt + 1}/{MAX_RETRIES})")
                    self.stats['retries'] += 1
                    time.sleep(wait)
                else:
                    print(f"ERROR: Connection failed after {MAX_RETRIES} attempts. Server may be down.")
                    self.stats['failures'] += 1
                    return None
            
            except Exception as e:
                print(f"ERROR: Unexpected error: {str(e)}")
                self.stats['failures'] += 1
                return None
        
        return None
    
    def get_challenge(self):
        """Get next challenge from PRISM"""
        def _get():
            resp = requests.get(f"{PRISM_BASE}/prism", timeout=TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        
        return self._api_call_with_retry(_get)
    
    def submit_solution(self, challenge_id: str, investments: List[Dict]):
        """Submit portfolio solution to PRISM"""
        def _post():
            payload = {
                'id': challenge_id,
                'investments': investments
            }
            resp = requests.post(f"{PRISM_BASE}/prism/solve", json=payload, timeout=TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        
        return self._api_call_with_retry(_post)
    
    def get_current_prices(self, tickers: List[str]) -> Dict[str, float]:
        """
        Get current prices with caching
        Returns dict of {ticker: price}
        """
        prices = {}
        need_fetch = []
        
        # Check cache first
        for ticker in tickers:
            cached_price = self.cache.get_current_price(ticker)
            if cached_price is not None:
                prices[ticker] = cached_price
            else:
                need_fetch.append(ticker)
        
        # Fetch missing prices
        if need_fetch:
            def _fetch():
                resp = requests.post(f"{LIMEX_BASE}/marketdata/quotes", json=need_fetch, timeout=TIMEOUT)
                resp.raise_for_status()
                return resp.json()
            
            data = self._api_call_with_retry(_fetch)
            
            if data:
                for item in data:
                    ticker = item.get('ticker')
                    price = item.get('last')
                    if ticker and price:
                        prices[ticker] = price
                        self.cache.set_current_price(ticker, price)
        
        return prices
    
    def get_historical_price(self, ticker: str, date_str: str) -> Optional[float]:
        """
        Get historical price for a single ticker/date with caching
        """
        # Check cache first
        cached_price = self.cache.get_historical_price(ticker, date_str)
        if cached_price is not None:
            return cached_price
        
        # Fetch from API
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            start = int(dt.timestamp())
            end = int((dt + timedelta(days=1)).timestamp())
            
            def _fetch():
                resp = requests.get(
                    f"{LIMEX_BASE}/marketdata/history",
                    params={'ticker': ticker, 'start': start, 'end': end, 'interval': '1d'},
                    timeout=TIMEOUT
                )
                resp.raise_for_status()
                return resp.json()
            
            data = self._api_call_with_retry(_fetch)
            
            if data and len(data) > 0:
                price = data[0]['open']
                self.cache.set_historical_price(ticker, date_str, price)
                return price
        
        except Exception as e:
            print(f"WARNING: Failed to fetch historical price for {ticker} on {date_str}: {str(e)}")
        
        return None
    
    def get_historical_prices_concurrent(self, tickers: List[str], date_str: str) -> Dict[str, float]:
        """
        Get historical prices for multiple tickers concurrently
        Uses ThreadPoolExecutor for parallel fetching
        Returns dict of {ticker: price}
        """
        prices = {}
        need_fetch = []
        
        # Check cache first
        for ticker in tickers:
            cached_price = self.cache.get_historical_price(ticker, date_str)
            if cached_price is not None:
                prices[ticker] = cached_price
            else:
                need_fetch.append(ticker)
        
        # Fetch missing prices concurrently
        if need_fetch:
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                future_to_ticker = {
                    executor.submit(self.get_historical_price, ticker, date_str): ticker
                    for ticker in need_fetch
                }
                
                for future in as_completed(future_to_ticker):
                    ticker = future_to_ticker[future]
                    try:
                        price = future.result()
                        if price is not None:
                            prices[ticker] = price
                    except Exception as e:
                        print(f"WARNING: Concurrent fetch failed for {ticker}: {str(e)}")
        
        return prices
    
    def prewarm_current_prices(self, tickers: List[str]):
        """
        Pre-fetch all current prices at startup
        Benefits all subsequent clients within cache TTL
        """
        print(f"Pre-warming cache with {len(tickers)} current prices...")
        prices = self.get_current_prices(tickers)
        print(f"Successfully cached {len(prices)} prices")
        return prices
    
    def get_stats(self) -> Dict:
        """Get API call statistics"""
        return {
            **self.stats,
            'success_rate': self._calculate_success_rate()
        }
    
    def _calculate_success_rate(self) -> float:
        """Calculate API call success rate"""
        if self.stats['total_calls'] == 0:
            return 100.0
        failures = self.stats['failures']
        return ((self.stats['total_calls'] - failures) / self.stats['total_calls']) * 100
