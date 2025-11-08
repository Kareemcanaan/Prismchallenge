#!/usr/bin/env python3
"""
PRISM Challenge V12 - Ultra-Optimized Main Bot
Main orchestrator that coordinates all components
"""

import time
from datetime import datetime
from config import STOCKS
from cache_manager import CacheManager
from api_client import APIClient
from client_filter import ClientFilter
from strategies import PortfolioStrategies
from portfolio_validator import PortfolioValidator
from performance_tracker import PerformanceTracker
from batch_processor import BatchProcessor


def process_challenge(challenge: dict, api_client: APIClient, tracker: PerformanceTracker) -> bool:
    """
    Process a single challenge
    Returns True if processed, False if skipped
    """
    start_time = time.time()
    challenge_id = challenge.get('id', 'unknown')
    
    # Step 1: Smart filtering
    should_skip, skip_reason = ClientFilter.should_skip_client(challenge)
    if should_skip:
        print(f"\nSKIPPED Challenge {challenge_id}: {skip_reason}")
        tracker.record_skip(skip_reason)
        return False
    
    print(f"\n{'='*70}")
    print(f"PROCESSING Challenge {challenge_id}")
    
    # Step 2: Parse context
    context = ClientFilter.parse_client_context(challenge)
    print(f"Budget: ${context['budget']:.2f}")
    print(f"Start Date: {context['start_date']}")
    print(f"Preferred Sectors: {context['preferred_sectors'] or 'None'}")
    print(f"Avoided Sectors: {context['avoided_sectors'] or 'None'}")
    print(f"Preference Strength: {context['preference_strength']}/100")
    
    # Step 3: Select strategy
    strategy = PortfolioStrategies.select_strategy(context)
    print(f"Selected Strategy: {strategy.upper().replace('_', ' ')}")
    tracker.record_processed(strategy)
    
    # Step 4: Get current prices (using cache)
    all_tickers = [s['ticker'] for s in STOCKS]
    current_prices = api_client.get_current_prices(all_tickers)
    
    if not current_prices:
        print("ERROR: Failed to fetch current prices")
        tracker.record_skip("Failed to fetch prices")
        return False
    
    # Step 5: Build portfolio
    portfolio = PortfolioStrategies.build_portfolio(strategy, context, current_prices)
    
    if not portfolio:
        print("ERROR: Failed to build portfolio")
        tracker.record_skip("Failed to build portfolio")
        return False
    
    # Step 6: Validate portfolio
    is_valid, message = PortfolioValidator.validate_portfolio(portfolio, context['budget'], current_prices)
    print(f"Validation: {message}")
    
    if not is_valid:
        print("ERROR: Portfolio validation failed")
        tracker.record_skip("Portfolio validation failed")
        return False
    
    # Step 7: Optimize budget usage
    optimized_portfolio = PortfolioValidator.optimize_budget_usage(portfolio, context['budget'], current_prices)
    
    # Re-validate optimized portfolio
    is_valid, message = PortfolioValidator.validate_portfolio(optimized_portfolio, context['budget'], current_prices)
    print(f"Optimized: {message}")
    
    # Step 8: Display portfolio
    print(f"\nPortfolio ({len(optimized_portfolio)} stocks):")
    for inv in optimized_portfolio:
        cost = inv['shares'] * current_prices[inv['ticker']]
        print(f"  {inv['ticker']}: {inv['shares']} shares @ ${current_prices[inv['ticker']]:.2f} = ${cost:.2f}")
    
    # Step 9: Get historical prices (concurrent)
    portfolio_tickers = [inv['ticker'] for inv in optimized_portfolio]
    historical_prices = api_client.get_historical_prices_concurrent(portfolio_tickers, context['start_date'])
    
    # Step 10: Build investment payload
    investments = []
    for inv in optimized_portfolio:
        hist_price = historical_prices.get(inv['ticker'])
        if hist_price:
            investments.append({
                'ticker': inv['ticker'],
                'shares': inv['shares'],
                'price': hist_price
            })
    
    if not investments:
        print("ERROR: No historical prices available")
        tracker.record_skip("No historical prices")
        return False
    
    print(f"Historical prices fetched: {len(investments)}/{len(optimized_portfolio)}")
    
    # Step 11: Submit solution
    result = api_client.submit_solution(challenge_id, investments)
    
    if result:
        if result.get('status') == 'correct':
            print(f"SUCCESS: {result.get('message', 'Solution accepted')}")
            tracker.record_solution(accepted=True)
        else:
            print(f"FAILED: {result.get('message', 'Solution rejected')}")
            tracker.record_solution(accepted=False)
    
    # Record processing time
    elapsed = time.time() - start_time
    tracker.record_processing_time(elapsed)
    print(f"Processing time: {elapsed:.2f}s")
    
    return True


def main():
    """Main bot loop"""
    print("="*70)
    print("PRISM Challenge Bot - V12 Ultra-Optimized Edition")
    print("="*70)
    print("\nFeatures:")
    print("  - Smart client filtering")
    print("  - Exponential backoff retries")
    print("  - Persistent cache (survives restarts)")
    print("  - Concurrent API calls")
    print("  - Portfolio validation & optimization")
    print("  - 3 auto-selected strategies")
    print("\nInitializing...\n")
    
    # Initialize components
    cache_manager = CacheManager()
    api_client = APIClient(cache_manager)
    tracker = PerformanceTracker()
    batch_processor = BatchProcessor(api_client)
    
    # Pre-warm cache
    print("Pre-warming cache with current prices...")
    all_tickers = [s['ticker'] for s in STOCKS]
    api_client.prewarm_current_prices(all_tickers)
    print("")
    
    # Main loop
    print("Starting main processing loop...\n")
    
    while True:
        # Get next challenge
        challenge = api_client.get_challenge()
        
        if not challenge:
            print("\nNo challenges available or connection error. Stopping.")
            break
        
        if challenge.get('status') == 'finished':
            print("\nAll challenges completed!")
            break
        
        # Process the challenge
        process_challenge(challenge, api_client, tracker)
        
        # Print quick stats every 10 clients
        total = tracker.stats['clients_processed'] + tracker.stats['clients_skipped']
        if total % 10 == 0 and total > 0:
            tracker.print_quick_stats()
        
        # Brief pause to avoid hammering server
        time.sleep(0.3)
    
    # Print final summary
    api_stats = api_client.get_stats()
    cache_stats = {
        'cache_hits': cache_manager.stats['cache_hits'],
        'cache_misses': cache_manager.stats['cache_misses'],
        'cache_hit_rate': cache_manager.get_cache_hit_rate()
    }
    
    tracker.print_summary(api_stats, cache_stats)
    
    # Save cache on exit
    print("Saving cache to disk...")
    cache_manager.save_to_file()
    print("Done!")


if __name__ == "__main__":
    main()
