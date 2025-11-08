"""
Smart Client Filtering
Determines if clients have sufficient information for processing
"""

import re
from datetime import datetime
from typing import Tuple


class ClientFilter:
    """Filters out clients with insufficient information"""
    
    @staticmethod
    def should_skip_client(challenge: dict) -> Tuple[bool, str]:
        """
        Determine if client should be skipped due to insufficient information.
        Returns (should_skip: bool, reason: str)
        """
        msg = challenge.get('message', '')
        
        # Check 1: No budget information
        budget_match = re.search(r'\$?([\d,]+)', msg)
        if not budget_match:
            return (True, "No budget information found")
        
        try:
            budget = float(budget_match.group(1).replace(',', ''))
            if budget <= 0:
                return (True, "Budget is zero or negative")
        except ValueError:
            return (True, "Invalid budget format")
        
        # Check 2: No valid date
        start_date = challenge.get('start_date')
        if not start_date:
            return (True, "No start_date provided")
        
        if not ClientFilter._is_valid_date(start_date):
            return (True, "Invalid date format")
        
        # Check 3: No preferences (no risk terms, no sector mentions, no avoid terms)
        msg_lower = msg.lower()
        
        # Risk indicators
        has_risk_info = any(term in msg_lower for term in [
            'aggressive', 'moderate', 'conservative', 'risk', 'volatile', 'stable',
            'growth', 'value', 'safe', 'speculative', 'balanced'
        ])
        
        # Sector indicators
        sectors = ['technology', 'tech', 'healthcare', 'health', 'financial', 'bank',
                   'energy', 'oil', 'consumer', 'industrial', 'communication', 'media',
                   'utilities', 'defensive', 'cyclical']
        has_sector_info = any(sector in msg_lower for sector in sectors)
        
        # Avoid indicators
        has_avoid_info = 'avoid' in msg_lower or 'not' in msg_lower or 'no ' in msg_lower
        
        if not has_risk_info and not has_sector_info and not has_avoid_info:
            return (True, "No investment preferences found (no risk/sector/avoid terms)")
        
        # Client has sufficient information
        return (False, "")
    
    @staticmethod
    def _is_valid_date(date_str: str) -> bool:
        """Validate date format"""
        try:
            # Try ISO format first
            if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                datetime.strptime(date_str, '%Y-%m-%d')
                return True
            
            # Try written format
            month_map = {
                'january': '01', 'february': '02', 'march': '03', 'april': '04',
                'may': '05', 'june': '06', 'july': '07', 'august': '08',
                'september': '09', 'october': '10', 'november': '11', 'december': '12'
            }
            match = re.search(r'(\w+)\s+(\d+)(?:st|nd|rd|th)?,?\s+(\d{4})', date_str.lower())
            if match:
                month_name, day, year = match.groups()
                if month_name in month_map:
                    return True
            
            return False
        
        except ValueError:
            return False
    
    @staticmethod
    def parse_client_context(challenge: dict) -> dict:
        """
        Parse client context with enhanced preference detection
        Returns dict with budget, date, preferences, and strength score
        """
        from config import SECTOR_KEYWORDS
        
        msg = challenge.get('message', '')
        msg_lower = msg.lower()
        
        # Extract budget
        budget_match = re.search(r'\$?([\d,]+)', msg)
        budget = float(budget_match.group(1).replace(',', '')) if budget_match else 100000
        
        # Extract and normalize date
        start_date = challenge.get('start_date', '2020-01-01')
        start_date = ClientFilter._normalize_date(start_date)
        
        # Detect preferred sectors
        preferred_sectors = []
        for sector, keywords in SECTOR_KEYWORDS.items():
            if any(kw in msg_lower for kw in keywords):
                preferred_sectors.append(sector)
        
        # Detect avoided sectors
        avoid_pattern = r'avoid\s+([^\.,]+)'
        avoided_sectors = []
        for match in re.finditer(avoid_pattern, msg_lower):
            avoided_text = match.group(1).strip()
            for sector, keywords in SECTOR_KEYWORDS.items():
                if any(kw in avoided_text for kw in keywords):
                    avoided_sectors.append(sector)
        
        # Calculate preference strength (0-100)
        strength = ClientFilter._calculate_preference_strength(
            len(preferred_sectors),
            len(avoided_sectors)
        )
        
        return {
            'budget': budget,
            'start_date': start_date,
            'preferred_sectors': preferred_sectors,
            'avoided_sectors': avoided_sectors,
            'preference_strength': strength
        }
    
    @staticmethod
    def _normalize_date(date_str: str) -> str:
        """Normalize date to YYYY-MM-DD format"""
        # Already in ISO format
        if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
            return date_str
        
        # Convert written format
        month_map = {
            'january': '01', 'february': '02', 'march': '03', 'april': '04',
            'may': '05', 'june': '06', 'july': '07', 'august': '08',
            'september': '09', 'october': '10', 'november': '11', 'december': '12'
        }
        match = re.search(r'(\w+)\s+(\d+)(?:st|nd|rd|th)?,?\s+(\d{4})', date_str.lower())
        if match:
            month_name, day, year = match.groups()
            month = month_map.get(month_name, '01')
            return f"{year}-{month}-{day.zfill(2)}"
        
        return date_str
    
    @staticmethod
    def _calculate_preference_strength(num_preferred: int, num_avoided: int) -> int:
        """
        Calculate preference strength score (0-100)
        Higher score = stronger, more specific preferences
        """
        strength = 0
        
        if num_preferred == 1:
            strength = 80  # Strong single sector preference
        elif num_preferred == 2:
            strength = 60  # Moderate dual sector preference
        elif num_preferred >= 3:
            strength = 40  # Weak multi-sector preference
        
        if num_avoided > 0:
            strength += 20  # Clear avoidance = stronger overall preference
        
        return min(strength, 100)
