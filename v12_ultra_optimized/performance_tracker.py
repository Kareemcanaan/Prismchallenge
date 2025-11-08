"""
Performance Tracker
Tracks and displays performance metrics
"""

from datetime import datetime
from typing import Dict


class PerformanceTracker:
    """Tracks bot performance metrics"""
    
    def __init__(self):
        self.stats = {
            'clients_processed': 0,
            'clients_skipped': 0,
            'skip_reasons': {},
            'strategy_usage': {
                'diversification': 0,
                'preference_weighted': 0,
                'high_conviction': 0
            },
            'solutions_accepted': 0,
            'solutions_rejected': 0,
            'processing_times': [],
            'start_time': datetime.now()
        }
    
    def record_skip(self, reason: str):
        """Record a skipped client with reason"""
        self.stats['clients_skipped'] += 1
        if reason not in self.stats['skip_reasons']:
            self.stats['skip_reasons'][reason] = 0
        self.stats['skip_reasons'][reason] += 1
    
    def record_processed(self, strategy: str):
        """Record a processed client with strategy used"""
        self.stats['clients_processed'] += 1
        if strategy in self.stats['strategy_usage']:
            self.stats['strategy_usage'][strategy] += 1
    
    def record_solution(self, accepted: bool):
        """Record solution result"""
        if accepted:
            self.stats['solutions_accepted'] += 1
        else:
            self.stats['solutions_rejected'] += 1
    
    def record_processing_time(self, seconds: float):
        """Record time taken to process a client"""
        self.stats['processing_times'].append(seconds)
    
    def print_summary(self, api_stats: Dict, cache_stats: Dict):
        """Print comprehensive performance summary"""
        print(f"\n{'='*70}")
        print("PERFORMANCE SUMMARY")
        print(f"{'='*70}")
        
        # Client Processing
        total_clients = self.stats['clients_processed'] + self.stats['clients_skipped']
        print(f"\nClient Processing:")
        print(f"  Total Clients: {total_clients}")
        print(f"  Processed: {self.stats['clients_processed']}")
        print(f"  Skipped: {self.stats['clients_skipped']}")
        
        if total_clients > 0:
            skip_rate = (self.stats['clients_skipped'] / total_clients) * 100
            print(f"  Skip Rate: {skip_rate:.1f}%")
        
        # Skip Reasons
        if self.stats['skip_reasons']:
            print(f"\n  Skip Reasons:")
            for reason, count in sorted(self.stats['skip_reasons'].items(), key=lambda x: -x[1]):
                print(f"    - {reason}: {count}")
        
        # Solution Results
        total_solutions = self.stats['solutions_accepted'] + self.stats['solutions_rejected']
        if total_solutions > 0:
            print(f"\nSolution Results:")
            print(f"  Accepted: {self.stats['solutions_accepted']}")
            print(f"  Rejected: {self.stats['solutions_rejected']}")
            success_rate = (self.stats['solutions_accepted'] / total_solutions) * 100
            print(f"  Success Rate: {success_rate:.1f}%")
        
        # Strategy Usage
        total_strategies = sum(self.stats['strategy_usage'].values())
        if total_strategies > 0:
            print(f"\nStrategy Usage:")
            for strategy, count in self.stats['strategy_usage'].items():
                pct = (count / total_strategies) * 100
                strategy_name = strategy.replace('_', ' ').title()
                print(f"  {strategy_name}: {count} ({pct:.1f}%)")
        
        # API Efficiency
        print(f"\nAPI Efficiency:")
        print(f"  Total API Calls: {api_stats['total_calls']}")
        print(f"  Retries: {api_stats['retries']}")
        print(f"  Failures: {api_stats['failures']}")
        print(f"  Success Rate: {api_stats['success_rate']:.1f}%")
        
        # Cache Performance
        cache_hit_rate = cache_stats['cache_hit_rate']
        total_lookups = cache_stats['cache_hits'] + cache_stats['cache_misses']
        print(f"\nCache Performance:")
        print(f"  Cache Hits: {cache_stats['cache_hits']}")
        print(f"  Cache Misses: {cache_stats['cache_misses']}")
        print(f"  Hit Rate: {cache_hit_rate:.1f}%")
        
        # Processing Speed
        if self.stats['processing_times']:
            avg_time = sum(self.stats['processing_times']) / len(self.stats['processing_times'])
            min_time = min(self.stats['processing_times'])
            max_time = max(self.stats['processing_times'])
            
            print(f"\nProcessing Speed:")
            print(f"  Average Time: {avg_time:.2f}s per client")
            print(f"  Fastest: {min_time:.2f}s")
            print(f"  Slowest: {max_time:.2f}s")
        
        # Total Time
        elapsed = (datetime.now() - self.stats['start_time']).total_seconds()
        print(f"\nTotal Execution Time: {elapsed:.1f}s")
        
        if self.stats['clients_processed'] > 0:
            throughput = self.stats['clients_processed'] / elapsed
            print(f"Throughput: {throughput:.2f} clients/second")
        
        print(f"{'='*70}\n")
    
    def print_quick_stats(self):
        """Print quick one-line stats during processing"""
        total = self.stats['clients_processed'] + self.stats['clients_skipped']
        processed = self.stats['clients_processed']
        skipped = self.stats['clients_skipped']
        accepted = self.stats['solutions_accepted']
        rejected = self.stats['solutions_rejected']
        
        print(f"Stats: {total} total | {processed} processed | {skipped} skipped | {accepted} accepted | {rejected} rejected")
