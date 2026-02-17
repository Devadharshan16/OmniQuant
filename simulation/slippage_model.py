"""
Slippage Model
Realistic price impact and slippage simulation
"""

import numpy as np
from typing import Dict, Any


class SlippageModel:
    """Models execution slippage based on market conditions"""
    
    def __init__(self, base_slippage: float = 0.001):
        """
        Args:
            base_slippage: Base slippage percentage (0.001 = 0.1%)
        """
        self.base_slippage = base_slippage
    
    def calculate_slippage(self, 
                          volume: float,
                          available_liquidity: float,
                          volatility: float = 0.01) -> float:
        """
        Calculate slippage percentage
        
        Model: slippage = base + volatility_component + liquidity_component
        
        Args:
            volume: Trade volume
            available_liquidity: Available market liquidity
            volatility: Market volatility (std dev)
        
        Returns:
            Slippage as percentage (0.01 = 1%)
        """
        if available_liquidity <= 0:
            return 1.0  # 100% slippage if no liquidity
        
        # Liquidity component - increases with volume/liquidity ratio
        liquidity_ratio = volume / available_liquidity
        liquidity_component = self.base_slippage * liquidity_ratio
        
        # Volatility component
        volatility_component = volatility * np.sqrt(liquidity_ratio)
        
        # Total slippage (capped at 100%)
        total_slippage = min(
            self.base_slippage + liquidity_component + volatility_component,
            1.0
        )
        
        return total_slippage
    
    def apply_slippage(self, rate: float, slippage: float, direction: str = 'buy') -> float:
        """
        Apply slippage to exchange rate
        
        Args:
            rate: Base exchange rate
            slippage: Slippage percentage
            direction: 'buy' or 'sell'
        
        Returns:
            Rate after slippage
        """
        if direction == 'buy':
            # Buying: price increases (worse for buyer)
            return rate * (1 + slippage)
        else:
            # Selling: price decreases (worse for seller)
            return rate * (1 - slippage)
    
    def calculate_effective_rate(self,
                                base_rate: float,
                                volume: float,
                                liquidity: float,
                                volatility: float = 0.01,
                                direction: str = 'buy') -> Dict[str, Any]:
        """
        Calculate effective rate after slippage
        
        Returns:
            Dict with effective_rate, slippage, and metadata
        """
        slippage = self.calculate_slippage(volume, liquidity, volatility)
        effective_rate = self.apply_slippage(base_rate, slippage, direction)
        
        return {
            'base_rate': base_rate,
            'effective_rate': effective_rate,
            'slippage_pct': slippage * 100,
            'volume': volume,
            'liquidity': liquidity,
            'liquidity_utilization': (volume / liquidity * 100) if liquidity > 0 else 100.0
        }


class AdvancedSlippageModel(SlippageModel):
    """Non-linear slippage with convex impact"""
    
    def __init__(self, 
                 base_slippage: float = 0.001,
                 impact_coefficient: float = 0.5,
                 impact_exponent: float = 1.5):
        """
        Args:
            base_slippage: Base slippage
            impact_coefficient: Impact scaling factor (k)
            impact_exponent: Impact exponent (α > 1 for convex impact)
        """
        super().__init__(base_slippage)
        self.k = impact_coefficient
        self.alpha = impact_exponent
    
    def calculate_slippage(self,
                          volume: float,
                          available_liquidity: float,
                          volatility: float = 0.01) -> float:
        """
        Non-linear slippage model
        
        impact = k × (volume/liquidity)^α
        
        This creates convex impact (larger trades have disproportionate impact)
        """
        if available_liquidity <= 0:
            return 1.0
        
        liquidity_ratio = volume / available_liquidity
        
        # Non-linear impact
        impact = self.k * np.power(liquidity_ratio, self.alpha)
        
        # Volatility component
        volatility_component = volatility * np.sqrt(liquidity_ratio)
        
        # Total slippage
        total_slippage = min(
            self.base_slippage + impact + volatility_component,
            1.0
        )
        
        return total_slippage
