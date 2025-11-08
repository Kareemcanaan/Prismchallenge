"""
Quick Start Guide for PRISM Challenge V12 Ultra-Optimized
"""

# OPTION 1: Run as Python Script (Recommended for Production)
# =============================================================

# Navigate to the directory
cd v12_ultra_optimized

# Run the bot
python main.py

# The bot will:
# 1. Load cache from previous runs (if exists)
# 2. Pre-warm all current prices
# 3. Process all challenges with smart filtering
# 4. Print performance statistics at the end
# 5. Save cache for next run


# OPTION 2: Run in Jupyter Notebook (Recommended for Development)
# ================================================================

# Open the notebook
# File: v12_ultra_optimized/ultra_optimized_notebook.ipynb

# Run all cells in order:
# 1. Import modules
# 2. Initialize components
# 3. Pre-warm cache
# 4. Define processing function
# 5. Run main loop
# 6. View performance summary


# OPTION 3: Import as Library (For Custom Scripts)
# =================================================

from v12_ultra_optimized.cache_manager import CacheManager
from v12_ultra_optimized.api_client import APIClient
from v12_ultra_optimized.client_filter import ClientFilter
from v12_ultra_optimized.strategies import PortfolioStrategies
from v12_ultra_optimized.portfolio_validator import PortfolioValidator

# Initialize
cache = CacheManager()
api = APIClient(cache)

# Use individual components as needed
# ...


# CONFIGURATION
# =============

# Edit config.py to customize:
# - API timeouts
# - Cache TTL
# - Retry parameters
# - Strategy thresholds
# - Budget allocation percentages


# PERFORMANCE MONITORING
# ======================

# The bot automatically tracks:
# - API call count vs cache hits
# - Clients processed vs skipped
# - Strategy usage breakdown
# - Average processing time
# - Success rate

# Statistics are printed at the end of each run


# TROUBLESHOOTING
# ===============

# If you see "Connection refused":
# - Check if PRISM server is running
# - Bot will retry 3 times with exponential backoff

# If you see "No historical prices":
# - Check your internet connection
# - Historical API may be temporarily down
# - Bot will skip client and continue

# If cache is not persisting:
# - Check file permissions for price_cache.json
# - Ensure __del__ method runs (cache saves on cleanup)

# To clear cache:
# rm price_cache.json


# TESTING
# =======

# Test individual components:

# Test client filtering
from client_filter import ClientFilter
challenge = {'message': 'Invest $500', 'start_date': '2020-01-01'}
should_skip, reason = ClientFilter.should_skip_client(challenge)
print(f"Skip: {should_skip}, Reason: {reason}")

# Test strategy selection
context = {'preference_strength': 75}
from strategies import PortfolioStrategies
strategy = PortfolioStrategies.select_strategy(context)
print(f"Selected: {strategy}")

# Test portfolio validation
from portfolio_validator import PortfolioValidator
portfolio = [{'ticker': 'AAPL', 'shares': 10}]
prices = {'AAPL': 150.0}
is_valid, msg = PortfolioValidator.validate_portfolio(portfolio, 2000, prices)
print(f"Valid: {is_valid}, Message: {msg}")


# EXPECTED PERFORMANCE
# ====================

# Baseline (V10): ~500 API calls for 100 clients
# V11 Optimized: ~250 API calls (50% reduction)
# V12 Ultra: ~100 API calls (80% reduction)

# Processing speed:
# - First client: ~2-3 seconds (includes pre-warming)
# - Subsequent clients: ~0.5-1 second (cached prices)
# - 100 clients: ~2-3 minutes total

# Cache hit rate:
# - After 10 clients: 30-40%
# - After 50 clients: 60-70%
# - After 100 clients: 70-80%


print("Ready to run! Choose an option above.")
