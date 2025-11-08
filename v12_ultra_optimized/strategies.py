"""
Portfolio Strategies
Three strategies that auto-select based on client preference strength
"""

from typing import Dict, List
from config import STOCKS, STRATEGY_THRESHOLDS, INITIAL_BUDGET_USAGE


class PortfolioStrategies:
    """Portfolio building strategies"""
    
    @staticmethod
    def select_strategy(context: dict) -> str:
        """
        Auto-select strategy based on client preference strength.
        
        Returns:
        - 'diversification': No clear preferences (strength 0-30)
        - 'preference_weighted': Moderate preferences (strength 31-60)
        - 'high_conviction': Strong preferences (strength 61-100)
        """
        strength = context['preference_strength']
        
        for strategy, (min_val, max_val) in STRATEGY_THRESHOLDS.items():
            if min_val <= strength <= max_val:
                return strategy
        
        return 'diversification'  # Default fallback
    
    @staticmethod
    def build_portfolio(strategy: str, context: dict, prices: Dict[str, float]) -> List[dict]:
        """
        Build portfolio using selected strategy
        Returns list of {'ticker': str, 'shares': int}
        """
        if strategy == 'diversification':
            return PortfolioStrategies._diversification(context, prices)
        elif strategy == 'preference_weighted':
            return PortfolioStrategies._preference_weighted(context, prices)
        elif strategy == 'high_conviction':
            return PortfolioStrategies._high_conviction(context, prices)
        else:
            return PortfolioStrategies._diversification(context, prices)
    
    @staticmethod
    def _diversification(context: dict, prices: Dict[str, float]) -> List[dict]:
        """
        Strategy 1: Pure Diversification
        - Equal weighting across multiple sectors
        - Max 40% per sector
        - 3-7 stocks based on budget
        """
        budget = context['budget']
        avoided = set(context['avoided_sectors'])
        safe_budget = budget * INITIAL_BUDGET_USAGE
        
        # Filter candidates
        candidates = [
            {**stock, 'price': prices.get(stock['ticker'], float('inf'))}
            for stock in STOCKS
            if stock['sector'] not in avoided and stock['ticker'] in prices
        ]
        candidates.sort(key=lambda x: x['price'])
        
        # Determine target stocks
        if budget < 100:
            target_stocks = 3
        elif budget < 500:
            target_stocks = 5
        else:
            target_stocks = 7
        
        # Select stocks with sector diversity
        selected = []
        sector_counts = {}
        max_per_sector = max(2, target_stocks // 2)
        
        for stock in candidates:
            if len(selected) >= target_stocks:
                break
            
            sector = stock['sector']
            if sector_counts.get(sector, 0) < max_per_sector:
                selected.append(stock)
                sector_counts[sector] = sector_counts.get(sector, 0) + 1
        
        # Equal allocation
        if not selected:
            return []
        
        per_stock_budget = safe_budget / len(selected)
        portfolio = []
        
        for stock in selected:
            shares = int(per_stock_budget / stock['price'])
            if shares > 0:
                portfolio.append({
                    'ticker': stock['ticker'],
                    'shares': shares
                })
        
        return portfolio
    
    @staticmethod
    def _preference_weighted(context: dict, prices: Dict[str, float]) -> List[dict]:
        """
        Strategy 2: Preference-Weighted (60% preferred / 40% diversified)
        - 60% budget to preferred sectors
        - 40% budget to other sectors for diversification
        - 4-6 stocks total
        """
        budget = context['budget']
        preferred = set(context['preferred_sectors'])
        avoided = set(context['avoided_sectors'])
        
        preferred_budget = budget * 0.60
        other_budget = budget * 0.36  # 96% total usage
        
        # Separate candidates
        preferred_stocks = []
        other_stocks = []
        
        for stock in STOCKS:
            if stock['sector'] in avoided or stock['ticker'] not in prices:
                continue
            
            stock_with_price = {**stock, 'price': prices[stock['ticker']]}
            
            if stock['sector'] in preferred:
                preferred_stocks.append(stock_with_price)
            else:
                other_stocks.append(stock_with_price)
        
        preferred_stocks.sort(key=lambda x: x['price'])
        other_stocks.sort(key=lambda x: x['price'])
        
        # Select 2-3 from preferred
        preferred_selected = []
        if preferred_stocks:
            target_preferred = min(3, len(preferred_stocks))
            per_preferred = preferred_budget / target_preferred
            
            for i in range(target_preferred):
                stock = preferred_stocks[i]
                shares = int(per_preferred / stock['price'])
                if shares > 0:
                    preferred_selected.append({
                        'ticker': stock['ticker'],
                        'shares': shares
                    })
        
        # Select 2-3 from others
        other_selected = []
        if other_stocks:
            target_other = min(3, len(other_stocks))
            per_other = other_budget / target_other
            
            sector_counts = {}
            for stock in other_stocks:
                if len(other_selected) >= target_other:
                    break
                
                sector = stock['sector']
                if sector_counts.get(sector, 0) < 1:  # Max 1 per sector in "other"
                    shares = int(per_other / stock['price'])
                    if shares > 0:
                        other_selected.append({
                            'ticker': stock['ticker'],
                            'shares': shares
                        })
                        sector_counts[sector] = 1
        
        return preferred_selected + other_selected
    
    @staticmethod
    def _high_conviction(context: dict, prices: Dict[str, float]) -> List[dict]:
        """
        Strategy 3: High Conviction (80% preferred / 20% diversified)
        - 80% budget to preferred sectors
        - 20% budget to best diversification pick
        - 3-5 stocks total
        """
        budget = context['budget']
        preferred = set(context['preferred_sectors'])
        avoided = set(context['avoided_sectors'])
        
        preferred_budget = budget * 0.80
        other_budget = budget * 0.16  # 96% total usage
        
        # Separate candidates
        preferred_stocks = []
        other_stocks = []
        
        for stock in STOCKS:
            if stock['sector'] in avoided or stock['ticker'] not in prices:
                continue
            
            stock_with_price = {**stock, 'price': prices[stock['ticker']]}
            
            if stock['sector'] in preferred:
                preferred_stocks.append(stock_with_price)
            else:
                other_stocks.append(stock_with_price)
        
        preferred_stocks.sort(key=lambda x: x['price'])
        other_stocks.sort(key=lambda x: x['price'])
        
        # Select 3-4 from preferred
        preferred_selected = []
        if preferred_stocks:
            target_preferred = min(4, len(preferred_stocks))
            per_preferred = preferred_budget / target_preferred
            
            for i in range(target_preferred):
                stock = preferred_stocks[i]
                shares = int(per_preferred / stock['price'])
                if shares > 0:
                    preferred_selected.append({
                        'ticker': stock['ticker'],
                        'shares': shares
                    })
        
        # Select 1 from others (best diversification)
        other_selected = []
        if other_stocks and other_budget > 0:
            stock = other_stocks[0]  # Cheapest from other sectors
            shares = int(other_budget / stock['price'])
            if shares > 0:
                other_selected.append({
                    'ticker': stock['ticker'],
                    'shares': shares
                })
        
        return preferred_selected + other_selected
