"""
Portfolio Validator
Validates portfolio before submission to catch errors early
"""

from typing import Dict, List, Tuple
from config import TARGET_BUDGET_USAGE


class PortfolioValidator:
    """Validates portfolio constraints and optimizes budget usage"""
    
    @staticmethod
    def validate_portfolio(portfolio: List[dict], budget: float, prices: Dict[str, float]) -> Tuple[bool, str]:
        """
        Validate portfolio against budget constraints
        Returns (is_valid: bool, message: str)
        """
        if not portfolio:
            return (False, "Portfolio is empty")
        
        # Calculate total cost
        total_cost = 0
        for inv in portfolio:
            ticker = inv['ticker']
            shares = inv['shares']
            
            if ticker not in prices:
                return (False, f"Missing price for {ticker}")
            
            if shares <= 0:
                return (False, f"Invalid share count for {ticker}: {shares}")
            
            total_cost += shares * prices[ticker]
        
        # Check budget breach (allow 1% tolerance)
        if total_cost > budget * 1.01:
            return (False, f"Budget breach: ${total_cost:.2f} > ${budget:.2f}")
        
        # Warn if too far under budget
        usage_pct = (total_cost / budget) * 100
        if usage_pct < 85:
            return (True, f"WARNING: Low budget usage ({usage_pct:.1f}%)")
        
        return (True, f"Valid portfolio: ${total_cost:.2f} ({usage_pct:.1f}% of budget)")
    
    @staticmethod
    def optimize_budget_usage(portfolio: List[dict], budget: float, prices: Dict[str, float]) -> List[dict]:
        """
        Optimize portfolio to use more of the budget (target 98-99%)
        Adds shares of cheapest stocks to use remaining budget
        """
        if not portfolio:
            return portfolio
        
        # Calculate current cost
        current_cost = sum(inv['shares'] * prices[inv['ticker']] for inv in portfolio)
        remaining = budget * TARGET_BUDGET_USAGE - current_cost
        
        if remaining < 0:
            return portfolio  # Already over target
        
        # Sort portfolio by price (cheapest first)
        sorted_portfolio = sorted(portfolio, key=lambda x: prices[x['ticker']])
        optimized = [inv.copy() for inv in portfolio]
        
        # Add shares to cheapest stocks until we hit target or run out of budget
        for inv in sorted_portfolio:
            ticker = inv['ticker']
            price = prices[ticker]
            
            # How many more shares can we buy?
            additional_shares = int(remaining / price)
            
            if additional_shares > 0:
                # Find this investment in optimized list and update
                for opt_inv in optimized:
                    if opt_inv['ticker'] == ticker:
                        opt_inv['shares'] += additional_shares
                        remaining -= additional_shares * price
                        break
            
            if remaining < min(prices.values()):
                break  # Can't afford any more shares
        
        return optimized
    
    @staticmethod
    def get_portfolio_stats(portfolio: List[dict], prices: Dict[str, float]) -> Dict:
        """
        Get portfolio statistics for analysis
        Returns dict with total_cost, num_stocks, sectors, etc.
        """
        from config import STOCKS
        
        if not portfolio:
            return {}
        
        total_cost = sum(inv['shares'] * prices[inv['ticker']] for inv in portfolio)
        
        # Get sectors
        ticker_to_sector = {s['ticker']: s['sector'] for s in STOCKS}
        sectors = {}
        
        for inv in portfolio:
            ticker = inv['ticker']
            sector = ticker_to_sector.get(ticker, 'Unknown')
            cost = inv['shares'] * prices[ticker]
            
            if sector not in sectors:
                sectors[sector] = {'count': 0, 'cost': 0, 'tickers': []}
            
            sectors[sector]['count'] += 1
            sectors[sector]['cost'] += cost
            sectors[sector]['tickers'].append(ticker)
        
        # Calculate sector percentages
        for sector in sectors:
            sectors[sector]['percentage'] = (sectors[sector]['cost'] / total_cost) * 100
        
        return {
            'total_cost': total_cost,
            'num_stocks': len(portfolio),
            'num_sectors': len(sectors),
            'sectors': sectors,
            'tickers': [inv['ticker'] for inv in portfolio]
        }
