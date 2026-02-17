"""
Market Impact Model
Institutional-grade price impact modeling
"""

import numpy as np
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class ImpactResult:
    """Result of market impact calculation"""
    base_price: float
    impacted_price: float
    impact_bps: float
    volume: float
    liquidity: float
    temporary_impact: float
    permanent_impact: float


class MarketImpactModel:
    """
    Models market impact on prices
    Based on institutional trading models
    """
    
    def __init__(self,
                 temporary_impact_coef: float = 0.5,
                 permanent_impact_coef: float = 0.1,
                 liquidity_exponent: float = 0.6):
        """
        Args:
            temporary_impact_coef: Temporary impact coefficient
            permanent_impact_coef: Permanent impact coefficient  
            liquidity_exponent: Exponent for liquidity impact (typically 0.5-0.7)
        """
        self.temp_coef = temporary_impact_coef
        self.perm_coef = permanent_impact_coef
        self.beta = liquidity_exponent
    
    def calculate_impact(self,
                        price: float,
                        volume: float,
                        daily_volume: float,
                        volatility: float = 0.01) -> ImpactResult:
        """
        Calculate market impact using square-root law
        
        Common model: impact ∝ σ × √(volume/daily_volume)
        
        Args:
            price: Current price
            volume: Trade volume
            daily_volume: Average daily volume (proxy for liquidity)
            volatility: Price volatility
        
        Returns:
            ImpactResult object
        """
        if daily_volume <= 0:
            # No liquidity - maximum impact
            return ImpactResult(
                base_price=price,
                impacted_price=price * 1.1,  # 10% impact
                impact_bps=1000,
                volume=volume,
                liquidity=daily_volume,
                temporary_impact=0.1,
                permanent_impact=0.0
            )
        
        # Participation rate
        participation = volume / daily_volume
        
        # Temporary impact (mean-reverting)
        # I_temp = σ × temp_coef × (volume/daily_volume)^β
        temp_impact = volatility * self.temp_coef * np.power(participation, self.beta)
        
        # Permanent impact (information-based)
        # I_perm = σ × perm_coef × (volume/daily_volume)
        perm_impact = volatility * self.perm_coef * participation
        
        # Total impact
        total_impact = temp_impact + perm_impact
        
        # Apply to price
        impacted_price = price * (1 + total_impact)
        
        # Convert to basis points
        impact_bps = total_impact * 10000
        
        return ImpactResult(
            base_price=price,
            impacted_price=impacted_price,
            impact_bps=impact_bps,
            volume=volume,
            liquidity=daily_volume,
            temporary_impact=temp_impact,
            permanent_impact=perm_impact
        )
    
    def calculate_multihop_impact(self,
                                  prices: List[float],
                                  volumes: List[float],
                                  liquidities: List[float],
                                  volatilities: List[float]) -> Dict[str, Any]:
        """
        Calculate compounded impact across multiple hops
        
        Args:
            prices: Price at each hop
            volumes: Volume at each hop
            liquidities: Liquidity at each hop
            volatilities: Volatility at each hop
        
        Returns:
            Dict with total impact and hop-by-hop breakdown
        """
        hop_impacts = []
        cumulative_price = 1.0
        
        for price, vol, liq, vola in zip(prices, volumes, liquidities, volatilities):
            impact = self.calculate_impact(price, vol, liq, vola)
            hop_impacts.append(impact)
            
            # Compound the impact
            price_multiplier = impact.impacted_price / impact.base_price
            cumulative_price *= price_multiplier
        
        return {
            'hop_impacts': hop_impacts,
            'cumulative_price_impact': cumulative_price - 1.0,
            'total_impact_bps': (cumulative_price - 1.0) * 10000,
            'num_hops': len(prices)
        }


class AlmgrenChrissModel:
    """
    Advanced Almgren-Chriss optimal execution model
    Used in institutional trading
    """
    
    def __init__(self, 
                 risk_aversion: float = 1e-6,
                 permanent_impact: float = 0.1,
                 temporary_impact: float = 0.5):
        """
        Args:
            risk_aversion: Risk aversion parameter (λ)
            permanent_impact: Permanent impact coefficient
            temporary_impact: Temporary impact coefficient
        """
        self.lambd = risk_aversion
        self.eta = permanent_impact
        self.epsilon = temporary_impact
    
    def calculate_optimal_strategy(self,
                                   total_volume: float,
                                   time_horizon: int,
                                   volatility: float,
                                   liquidity: float) -> Dict[str, Any]:
        """
        Calculate optimal execution strategy
        
        Returns optimal trade schedule to minimize:
        - Execution cost
        - Market impact
        - Price risk
        
        This is simplified - full model requires dynamic programming
        """
        # Simplified: uniform VWAP strategy with adjustments
        volume_per_period = total_volume / time_horizon
        
        # Adjust for liquidity constraints
        max_participation = 0.1  # 10% daily volume
        adjusted_volume = min(volume_per_period, liquidity * max_participation)
        
        # Calculate expected cost
        impact_cost = self.eta * (total_volume / liquidity)
        risk_cost = self.lambd * volatility**2 * total_volume**2 / time_horizon
        
        total_cost = impact_cost + risk_cost
        
        return {
            'volume_per_period': adjusted_volume,
            'periods': time_horizon,
            'expected_impact_cost': impact_cost,
            'expected_risk_cost': risk_cost,
            'total_expected_cost': total_cost,
            'strategy': 'vwap_adjusted'
        }
