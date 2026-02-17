"""
Regime Detector
Classifies market regimes for risk adjustment
"""

import numpy as np
from typing import Dict, List, Any
from collections import deque
from dataclasses import dataclass
from enum import Enum


class VolatilityRegime(Enum):
    """Volatility classifications"""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class LiquidityRegime(Enum):
    """Liquidity classifications"""
    DROUGHT = "drought"
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    ABUNDANT = "abundant"


class TrendRegime(Enum):
    """Market trend classifications"""
    STRONG_DOWNTREND = "strong_downtrend"
    DOWNTREND = "downtrend"
    SIDEWAYS = "sideways"
    UPTREND = "uptrend"
    STRONG_UPTREND = "strong_uptrend"


@dataclass
class RegimeState:
    """Current market regime"""
    volatility: VolatilityRegime
    liquidity: LiquidityRegime
    trend: TrendRegime
    volatility_value: float
    liquidity_percentile: float
    trend_strength: float
    confidence: float
    recommendation: str


class AdvancedRegimeDetector:
    """
    Advanced market regime detection
    Uses rolling windows and statistical methods
    """
    
    def __init__(self, 
                 short_window: int = 20,
                 long_window: int = 100,
                 max_history: int = 1000):
        """
        Args:
            short_window: Short-term window for regime detection
            long_window: Long-term window for baseline
            max_history: Maximum history to retain
        """
        self.short_window = short_window
        self.long_window = long_window
        self.max_history = max_history
        
        self.price_history: Dict[str, deque] = {}
        self.volume_history: Dict[str, deque] = {}
        self.spread_history: Dict[str, deque] = {}
    
    def update(self, 
               symbol: str,
               price: float,
               volume: float,
               spread: float = 0.0):
        """Update market data"""
        if symbol not in self.price_history:
            self.price_history[symbol] = deque(maxlen=self.max_history)
            self.volume_history[symbol] = deque(maxlen=self.max_history)
            self.spread_history[symbol] = deque(maxlen=self.max_history)
        
        self.price_history[symbol].append(price)
        self.volume_history[symbol].append(volume)
        self.spread_history[symbol].append(spread)
    
    def detect_regime(self, symbol: str) -> RegimeState:
        """
        Comprehensive regime detection
        
        Returns:
            RegimeState with all classifications
        """
        if symbol not in self.price_history:
            return self._default_regime()
        
        prices = list(self.price_history[symbol])
        volumes = list(self.volume_history[symbol])
        
        if len(prices) < self.short_window:
            return self._default_regime()
        
        # Detect volatility regime
        vol_regime, vol_value = self._detect_volatility(prices)
        
        # Detect liquidity regime
        liq_regime, liq_percentile = self._detect_liquidity(volumes)
        
        # Detect trend regime
        trend_regime, trend_strength = self._detect_trend(prices)
        
        # Calculate confidence
        confidence = min(len(prices) / self.long_window, 1.0)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(vol_regime, liq_regime, trend_regime)
        
        return RegimeState(
            volatility=vol_regime,
            liquidity=liq_regime,
            trend=trend_regime,
            volatility_value=vol_value,
            liquidity_percentile=liq_percentile,
            trend_strength=trend_strength,
            confidence=confidence,
            recommendation=recommendation
        )
    
    def _detect_volatility(self, prices: List[float]) -> tuple:
        """Detect volatility regime"""
        # Calculate returns
        returns = np.diff(prices[-self.short_window:]) / prices[-self.short_window:-1]
        
        # Realized volatility (annualized)
        volatility = np.std(returns) * np.sqrt(365 * 24)  # Assuming hourly data
        
        # Classify
        if volatility < 0.20:
            regime = VolatilityRegime.VERY_LOW
        elif volatility < 0.40:
            regime = VolatilityRegime.LOW
        elif volatility < 0.60:
            regime = VolatilityRegime.MODERATE
        elif volatility < 0.80:
            regime = VolatilityRegime.HIGH
        else:
            regime = VolatilityRegime.VERY_HIGH
        
        return regime, volatility
    
    def _detect_liquidity(self, volumes: List[float]) -> tuple:
        """Detect liquidity regime"""
        if len(volumes) < self.long_window:
            long_window_volumes = volumes
        else:
            long_window_volumes = volumes[-self.long_window:]
        
        recent_avg = np.mean(volumes[-self.short_window:])
        historical_avg = np.mean(long_window_volumes)
        
        # Percentile of recent vs historical
        percentile = (recent_avg / historical_avg) if historical_avg > 0 else 0.5
        
        # Classify
        if percentile < 0.5:
            regime = LiquidityRegime.DROUGHT
        elif percentile < 0.75:
            regime = LiquidityRegime.LOW
        elif percentile < 1.25:
            regime = LiquidityRegime.NORMAL
        elif percentile < 1.5:
            regime = LiquidityRegime.HIGH
        else:
            regime = LiquidityRegime.ABUNDANT
        
        return regime, percentile
    
    def _detect_trend(self, prices: List[float]) -> tuple:
        """Detect trend regime"""
        recent_prices = prices[-self.short_window:]
        
        # Linear regression
        x = np.arange(len(recent_prices))
        coeffs = np.polyfit(x, recent_prices, 1)
        trend_slope = coeffs[0]
        
        # Normalize by price level and volatility
        avg_price = np.mean(recent_prices)
        price_std = np.std(recent_prices)
        
        if price_std > 0:
            normalized_trend = trend_slope / price_std
        else:
            normalized_trend = 0
        
        # R-squared for trend strength
        fitted = np.polyval(coeffs, x)
        ss_res = np.sum((recent_prices - fitted) ** 2)
        ss_tot = np.sum((recent_prices - np.mean(recent_prices)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        # Classify
        if normalized_trend < -0.5:
            regime = TrendRegime.STRONG_DOWNTREND
        elif normalized_trend < -0.2:
            regime = TrendRegime.DOWNTREND
        elif normalized_trend < 0.2:
            regime = TrendRegime.SIDEWAYS
        elif normalized_trend < 0.5:
            regime = TrendRegime.UPTREND
        else:
            regime = TrendRegime.STRONG_UPTREND
        
        return regime, r_squared
    
    def _generate_recommendation(self,
                                vol_regime: VolatilityRegime,
                                liq_regime: LiquidityRegime,
                                trend_regime: TrendRegime) -> str:
        """Generate trading recommendation based on regime"""
        recommendations = []
        
        # Volatility recommendations
        if vol_regime == VolatilityRegime.VERY_HIGH:
            recommendations.append("High volatility - reduce position sizes")
        elif vol_regime == VolatilityRegime.VERY_LOW:
            recommendations.append("Low volatility - favorable for arbitrage")
        
        # Liquidity recommendations
        if liq_regime in [LiquidityRegime.DROUGHT, LiquidityRegime.LOW]:
            recommendations.append("Low liquidity - expect higher slippage")
        elif liq_regime == LiquidityRegime.ABUNDANT:
            recommendations.append("High liquidity - favorable execution conditions")
        
        # Trend recommendations
        if trend_regime in [TrendRegime.STRONG_DOWNTREND, TrendRegime.STRONG_UPTREND]:
            recommendations.append("Strong trend - arbitrage may be challenged")
        elif trend_regime == TrendRegime.SIDEWAYS:
            recommendations.append("Sideways market - ideal for arbitrage")
        
        return "; ".join(recommendations) if recommendations else "Normal conditions"
    
    def _default_regime(self) -> RegimeState:
        """Return default regime when insufficient data"""
        return RegimeState(
            volatility=VolatilityRegime.MODERATE,
            liquidity=LiquidityRegime.NORMAL,
            trend=TrendRegime.SIDEWAYS,
            volatility_value=0.5,
            liquidity_percentile=1.0,
            trend_strength=0.0,
            confidence=0.0,
            recommendation="Insufficient data for regime classification"
        )
