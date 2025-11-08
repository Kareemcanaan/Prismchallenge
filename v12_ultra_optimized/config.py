"""
Configuration and Stock Universe for PRISM Challenge
"""

# API Configuration
PRISM_BASE = "http://www.prism-challenge.com:8082"
LIMEX_BASE = "https://api.limex-data.com"
TIMEOUT = 30

# Cache Configuration
CACHE_TTL = 300  # 5 minutes for current prices
CACHE_FILE = "price_cache.json"

# Retry Configuration
MAX_RETRIES = 3
RETRY_BASE_DELAY = 1  # seconds (exponential: 1s, 2s, 4s)

# Budget Configuration
INITIAL_BUDGET_USAGE = 0.96  # Use 96% initially
TARGET_BUDGET_USAGE = 0.98   # Try to reach 98-99% with optimization

# Strategy Thresholds
STRATEGY_THRESHOLDS = {
    'diversification': (0, 30),      # Preference strength 0-30
    'preference_weighted': (31, 60),  # Preference strength 31-60
    'high_conviction': (61, 100)      # Preference strength 61-100
}

# Concurrent Processing
MAX_WORKERS = 10  # ThreadPoolExecutor worker threads

# Stock Universe (51 stocks, ETFs removed, GOOGL→GOOG)
STOCKS = [
    {"ticker": "AAPL", "sector": "Technology"},
    {"ticker": "MSFT", "sector": "Technology"},
    {"ticker": "GOOG", "sector": "Technology"},
    {"ticker": "AMZN", "sector": "Consumer Cyclical"},
    {"ticker": "NVDA", "sector": "Technology"},
    {"ticker": "META", "sector": "Communication Services"},
    {"ticker": "TSLA", "sector": "Consumer Cyclical"},
    {"ticker": "BRK.B", "sector": "Financial Services"},
    {"ticker": "V", "sector": "Financial Services"},
    {"ticker": "JNJ", "sector": "Healthcare"},
    {"ticker": "WMT", "sector": "Consumer Defensive"},
    {"ticker": "JPM", "sector": "Financial Services"},
    {"ticker": "MA", "sector": "Financial Services"},
    {"ticker": "PG", "sector": "Consumer Defensive"},
    {"ticker": "UNH", "sector": "Healthcare"},
    {"ticker": "HD", "sector": "Consumer Cyclical"},
    {"ticker": "CVX", "sector": "Energy"},
    {"ticker": "MRK", "sector": "Healthcare"},
    {"ticker": "ABBV", "sector": "Healthcare"},
    {"ticker": "KO", "sector": "Consumer Defensive"},
    {"ticker": "PEP", "sector": "Consumer Defensive"},
    {"ticker": "AVGO", "sector": "Technology"},
    {"ticker": "COST", "sector": "Consumer Defensive"},
    {"ticker": "MCD", "sector": "Consumer Cyclical"},
    {"ticker": "TMO", "sector": "Healthcare"},
    {"ticker": "CSCO", "sector": "Technology"},
    {"ticker": "ACN", "sector": "Technology"},
    {"ticker": "DHR", "sector": "Healthcare"},
    {"ticker": "VZ", "sector": "Communication Services"},
    {"ticker": "ADBE", "sector": "Technology"},
    {"ticker": "NFLX", "sector": "Communication Services"},
    {"ticker": "NKE", "sector": "Consumer Cyclical"},
    {"ticker": "CRM", "sector": "Technology"},
    {"ticker": "ORCL", "sector": "Technology"},
    {"ticker": "ABT", "sector": "Healthcare"},
    {"ticker": "PFE", "sector": "Healthcare"},
    {"ticker": "INTC", "sector": "Technology"},
    {"ticker": "DIS", "sector": "Communication Services"},
    {"ticker": "CMCSA", "sector": "Communication Services"},
    {"ticker": "AMD", "sector": "Technology"},
    {"ticker": "T", "sector": "Communication Services"},
    {"ticker": "COP", "sector": "Energy"},
    {"ticker": "NEE", "sector": "Utilities"},
    {"ticker": "UPS", "sector": "Industrials"},
    {"ticker": "IBM", "sector": "Technology"},
    {"ticker": "BA", "sector": "Industrials"},
    {"ticker": "CAT", "sector": "Industrials"},
    {"ticker": "GE", "sector": "Industrials"},
    {"ticker": "HON", "sector": "Industrials"},
    {"ticker": "MMM", "sector": "Industrials"},
    {"ticker": "DE", "sector": "Industrials"}
]

# Sector Keywords for Preference Detection
SECTOR_KEYWORDS = {
    'Technology': ['tech', 'software', 'ai', 'cloud', 'semiconductor', 'computer'],
    'Healthcare': ['health', 'pharma', 'biotech', 'medical', 'drug'],
    'Financial Services': ['bank', 'financial', 'finance', 'payment', 'credit'],
    'Energy': ['energy', 'oil', 'gas', 'petroleum'],
    'Consumer Defensive': ['consumer defensive', 'staple', 'retail', 'food', 'beverage'],
    'Consumer Cyclical': ['consumer cyclical', 'discretionary', 'restaurant', 'travel'],
    'Communication Services': ['communication', 'media', 'telecom', 'entertainment'],
    'Industrials': ['industrial', 'manufacturing', 'aerospace', 'machinery'],
    'Utilities': ['utilit', 'electric', 'water', 'power']
}
