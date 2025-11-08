"""
Batch Processor
Groups clients by date for efficient batch processing
"""

from typing import List, Dict
from collections import defaultdict


class BatchProcessor:
    """Handles batch grouping and processing of clients by date"""
    
    def __init__(self, api_client):
        self.api_client = api_client
        self.date_groups = defaultdict(list)  # {date: [client1, client2, ...]}
    
    def add_client(self, client_id: str, date: str):
        """Add client to date group"""
        self.date_groups[date].append(client_id)
    
    def get_dates(self) -> List[str]:
        """Get all unique dates"""
        return list(self.date_groups.keys())
    
    def get_clients_for_date(self, date: str) -> List[str]:
        """Get all clients for a specific date"""
        return self.date_groups[date]
    
    def fetch_historical_prices_batch(self, tickers: List[str], date: str) -> Dict[str, float]:
        """
        Fetch historical prices for all tickers at once for a given date
        Uses concurrent processing for maximum speed
        """
        return self.api_client.get_historical_prices_concurrent(tickers, date)
    
    def clear(self):
        """Clear all date groups"""
        self.date_groups.clear()
    
    def get_stats(self) -> Dict:
        """Get batch processing statistics"""
        total_clients = sum(len(clients) for clients in self.date_groups.values())
        
        return {
            'unique_dates': len(self.date_groups),
            'total_clients': total_clients,
            'avg_clients_per_date': total_clients / len(self.date_groups) if self.date_groups else 0,
            'date_distribution': {
                date: len(clients) for date, clients in sorted(self.date_groups.items())
            }
        }
    
    def print_batch_info(self):
        """Print batch grouping information"""
        stats = self.get_stats()
        
        print(f"\nBatch Processing Info:")
        print(f"  Unique Dates: {stats['unique_dates']}")
        print(f"  Total Clients: {stats['total_clients']}")
        print(f"  Avg Clients/Date: {stats['avg_clients_per_date']:.1f}")
        
        if stats['unique_dates'] <= 10:
            print(f"\n  Date Distribution:")
            for date, count in stats['date_distribution'].items():
                print(f"    {date}: {count} clients")
