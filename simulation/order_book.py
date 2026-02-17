"""
Order Book Microstructure Simulation
Level-2 order book modeling with bid/ask spread
"""

import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class OrderBookLevel:
    """Single level in order book"""
    price: float
    volume: float


@dataclass
class OrderBook:
    """Level-2 order book representation"""
    symbol: str
    exchange: str
    bids: List[OrderBookLevel]  # Sorted descending by price
    asks: List[OrderBookLevel]  # Sorted ascending by price
    timestamp: float
    
    def get_mid_price(self) -> float:
        """Calculate mid price"""
        if not self.bids or not self.asks:
            return 0.0
        return (self.bids[0].price + self.asks[0].price) / 2.0
    
    def get_spread(self) -> float:
        """Calculate bid-ask spread"""
        if not self.bids or not self.asks:
            return 0.0
        return self.asks[0].price - self.bids[0].price
    
    def get_spread_bps(self) -> float:
        """Spread in basis points"""
        mid = self.get_mid_price()
        if mid == 0:
            return 0.0
        return (self.get_spread() / mid) * 10000
    
    def get_total_bid_liquidity(self) -> float:
        """Total available liquidity on bid side"""
        return sum(level.volume for level in self.bids)
    
    def get_total_ask_liquidity(self) -> float:
        """Total available liquidity on ask side"""
        return sum(level.volume for level in self.asks)


class OrderBookSimulator:
    """Simulates realistic order book depth"""
    
    def __init__(self, depth: int = 5):
        """
        Args:
            depth: Number of price levels to simulate (each side)
        """
        self.depth = depth
    
    def generate_order_book(self, 
                           symbol: str,
                           exchange: str,
                           mid_price: float,
                           base_liquidity: float,
                           spread_bps: float = 10.0,
                           timestamp: float = 0.0) -> OrderBook:
        """
        Generate synthetic order book
        
        Args:
            symbol: Trading pair (e.g., "BTC/USDT")
            exchange: Exchange name
            mid_price: Center price
            base_liquidity: Base liquidity per level
            spread_bps: Spread in basis points
            timestamp: Book timestamp
        
        Returns:
            OrderBook object
        """
        spread = mid_price * (spread_bps / 10000.0)
        
        # Generate bids (descending price)
        bids = []
        for i in range(self.depth):
            price = mid_price - spread / 2 - i * (spread / self.depth)
            # Liquidity decreases with distance from mid
            volume = base_liquidity * np.exp(-0.3 * i) * (1 + np.random.uniform(-0.2, 0.2))
            bids.append(OrderBookLevel(price=price, volume=volume))
        
        # Generate asks (ascending price)
        asks = []
        for i in range(self.depth):
            price = mid_price + spread / 2 + i * (spread / self.depth)
            volume = base_liquidity * np.exp(-0.3 * i) * (1 + np.random.uniform(-0.2, 0.2))
            asks.append(OrderBookLevel(price=price, volume=volume))
        
        return OrderBook(
            symbol=symbol,
            exchange=exchange,
            bids=bids,
            asks=asks,
            timestamp=timestamp
        )
    
    def calculate_execution_price(self, 
                                  order_book: OrderBook,
                                  side: str,
                                  volume: float) -> Tuple[float, float]:
        """
        Calculate effective execution price consuming order book
        
        Args:
            order_book: Order book to execute against
            side: 'buy' or 'sell'
            volume: Volume to execute
        
        Returns:
            (effective_price, executed_volume)
        """
        levels = order_book.asks if side == 'buy' else order_book.bids
        
        remaining_volume = volume
        total_cost = 0.0
        executed_volume = 0.0
        
        for level in levels:
            if remaining_volume <= 0:
                break
            
            executed_at_level = min(remaining_volume, level.volume)
            total_cost += executed_at_level * level.price
            executed_volume += executed_at_level
            remaining_volume -= executed_at_level
        
        if executed_volume == 0:
            return 0.0, 0.0
        
        effective_price = total_cost / executed_volume
        return effective_price, executed_volume
    
    def get_available_liquidity(self, order_book: OrderBook, side: str) -> float:
        """Get total available liquidity on given side"""
        levels = order_book.asks if side == 'buy' else order_book.bids
        return sum(level.volume for level in levels)
