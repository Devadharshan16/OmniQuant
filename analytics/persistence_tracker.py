"""
Opportunity Persistence Tracker
Tracks arbitrage opportunities over time
"""

import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import numpy as np


@dataclass
class OpportunitySnapshot:
    """Single snapshot of an opportunity"""
    timestamp: float
    return_pct: float
    risk_score: float
    confidence: float
    liquidity: float


@dataclass
class OpportunityLifecycle:
    """Tracks lifecycle of single opportunity"""
    opportunity_id: str
    path: List[str]
    first_seen: float
    last_seen: float
    snapshots: List[OpportunitySnapshot] = field(default_factory=list)
    peak_return: float = 0.0
    peak_timestamp: float = 0.0
    alive_duration_ms: float = 0.0
    detection_count: int = 0
    
    def add_snapshot(self, snapshot: OpportunitySnapshot):
        """Add new snapshot"""
        self.snapshots.append(snapshot)
        self.last_seen = snapshot.timestamp
        self.detection_count += 1
        
        if snapshot.return_pct > self.peak_return:
            self.peak_return = snapshot.return_pct
            self.peak_timestamp = snapshot.timestamp
        
        self.alive_duration_ms = (self.last_seen - self.first_seen) * 1000
    
    def get_decay_pattern(self) -> str:
        """Analyze how opportunity decayed"""
        if len(self.snapshots) < 2:
            return "insufficient_data"
        
        returns = [s.return_pct for s in self.snapshots]
        
        # Check if monotonically decreasing
        is_decreasing = all(returns[i] >= returns[i+1] for i in range(len(returns)-1))
        is_increasing = all(returns[i] <= returns[i+1] for i in range(len(returns)-1))
        
        if is_decreasing:
            return "monotonic_decay"
        elif is_increasing:
            return "improving"
        else:
            return "oscillating"
    
    def get_persistence_score(self) -> float:
        """
        Calculate persistence score
        Based on:
        - Detection frequency
        - Duration alive
        - Stability of returns
        
        Returns: 0-100
        """
        # Frequency component (0-40 points)
        freq_score = min(self.detection_count * 4, 40)
        
        # Duration component (0-40 points)
        duration_score = min(self.alive_duration_ms / 100, 40)  # 1 point per 100ms
        
        # Stability component (0-20 points)
        if len(self.snapshots) >= 2:
            returns = [s.return_pct for s in self.snapshots]
            stability = 1 / (1 + np.std(returns))
            stability_score = stability * 20
        else:
            stability_score = 10
        
        return min(freq_score + duration_score + stability_score, 100)


@dataclass
class PersistenceMetrics:
    """Aggregate persistence metrics"""
    total_opportunities: int
    avg_lifespan_ms: float
    median_lifespan_ms: float
    avg_detection_count: float
    most_persistent_path: List[str]
    avg_persistence_score: float
    sharpe_ratio: float  # return_mean / return_std


class PersistenceTracker:
    """
    Tracks arbitrage opportunities over time
    Measures:
    - Opportunity lifespan
    - Detection frequency
    - Return stability
    - Decay patterns
    """
    
    def __init__(self, opportunity_timeout_ms: float = 10000):
        """
        Args:
            opportunity_timeout_ms: Consider opportunity dead after this time
        """
        self.opportunities: Dict[str, OpportunityLifecycle] = {}
        self.timeout_ms = opportunity_timeout_ms
        self.start_time = time.time()
    
    def track_opportunity(self,
                         path: List[str],
                         return_pct: float,
                         risk_score: float,
                         confidence: float,
                         liquidity: float) -> str:
        """
        Track new or existing opportunity
        
        Returns:
            Opportunity ID
        """
        # Generate opportunity ID from path
        opp_id = self._generate_id(path)
        
        current_time = time.time()
        
        # Create snapshot
        snapshot = OpportunitySnapshot(
            timestamp=current_time,
            return_pct=return_pct,
            risk_score=risk_score,
            confidence=confidence,
            liquidity=liquidity
        )
        
        if opp_id not in self.opportunities:
            # New opportunity
            lifecycle = OpportunityLifecycle(
                opportunity_id=opp_id,
                path=path,
                first_seen=current_time,
                last_seen=current_time,
                snapshots=[snapshot],
                peak_return=return_pct,
                peak_timestamp=current_time,
                detection_count=1
            )
            self.opportunities[opp_id] = lifecycle
        else:
            # Existing opportunity
            self.opportunities[opp_id].add_snapshot(snapshot)
        
        # Clean up stale opportunities
        self._cleanup_stale()
        
        return opp_id
    
    def get_lifecycle(self, opportunity_id: str) -> Optional[OpportunityLifecycle]:
        """Get lifecycle for specific opportunity"""
        return self.opportunities.get(opportunity_id)
    
    def get_active_opportunities(self) -> List[OpportunityLifecycle]:
        """Get currently active opportunities"""
        current_time = time.time()
        active = []
        
        for lifecycle in self.opportunities.values():
            age_ms = (current_time - lifecycle.last_seen) * 1000
            if age_ms < self.timeout_ms:
                active.append(lifecycle)
        
        return active
    
    def get_persistence_metrics(self) -> PersistenceMetrics:
        """Calculate aggregate persistence metrics"""
        if not self.opportunities:
            return PersistenceMetrics(
                total_opportunities=0,
                avg_lifespan_ms=0,
                median_lifespan_ms=0,
                avg_detection_count=0,
                most_persistent_path=[],
                avg_persistence_score=0,
                sharpe_ratio=0
            )
        
        lifecycles = list(self.opportunities.values())
        
        # Lifespan stats
        lifespans = [lc.alive_duration_ms for lc in lifecycles]
        avg_lifespan = np.mean(lifespans)
        median_lifespan = np.median(lifespans)
        
        # Detection count
        avg_detection_count = np.mean([lc.detection_count for lc in lifecycles])
        
        # Most persistent
        persistence_scores = [(lc.get_persistence_score(), lc.path) for lc in lifecycles]
        most_persistent = max(persistence_scores, key=lambda x: x[0])[1] if persistence_scores else []
        
        # Average persistence score
        avg_persistence = np.mean([lc.get_persistence_score() for lc in lifecycles])
        
        # Sharpe-like ratio
        all_returns = []
        for lc in lifecycles:
            all_returns.extend([s.return_pct for s in lc.snapshots])
        
        if all_returns:
            sharpe = np.mean(all_returns) / np.std(all_returns) if np.std(all_returns) > 0 else 0
        else:
            sharpe = 0
        
        return PersistenceMetrics(
            total_opportunities=len(self.opportunities),
            avg_lifespan_ms=avg_lifespan,
            median_lifespan_ms=median_lifespan,
            avg_detection_count=avg_detection_count,
            most_persistent_path=most_persistent,
            avg_persistence_score=avg_persistence,
            sharpe_ratio=sharpe
        )
    
    def _generate_id(self, path: List[str]) -> str:
        """Generate unique ID from path"""
        # Sort path to handle equivalent cycles
        sorted_path = sorted(path[:-1])  # Exclude closing token
        return "|".join(sorted_path)
    
    def _cleanup_stale(self):
        """Remove stale opportunities"""
        current_time = time.time()
        stale_ids = []
        
        for opp_id, lifecycle in self.opportunities.items():
            age_ms = (current_time - lifecycle.last_seen) * 1000
            if age_ms > self.timeout_ms * 2:  # 2x timeout before deletion
                stale_ids.append(opp_id)
        
        for opp_id in stale_ids:
            del self.opportunities[opp_id]
    
    def calculate_half_life(self, opportunity_id: str) -> Optional[float]:
        """
        Calculate half-life: time until return drops to 50% of peak
        
        Returns:
            Half-life in milliseconds, or None if not applicable
        """
        lifecycle = self.get_lifecycle(opportunity_id)
        if not lifecycle or len(lifecycle.snapshots) < 2:
            return None
        
        peak_return = lifecycle.peak_return
        target_return = peak_return * 0.5
        
        # Find first time return drops below target
        for snapshot in lifecycle.snapshots:
            if snapshot.timestamp > lifecycle.peak_timestamp:
                if snapshot.return_pct <= target_return:
                    half_life_ms = (snapshot.timestamp - lifecycle.peak_timestamp) * 1000
                    return half_life_ms
        
        return None  # Still above half-life


class RegimeDetector:
    """
    Detects market regime
    - High volatility vs low volatility
    - High liquidity vs low liquidity
    - Trending vs mean-reverting
    """
    
    def __init__(self, window_size: int = 100):
        """
        Args:
            window_size: Number of samples for regime classification
        """
        self.window_size = window_size
        self.price_history = defaultdict(list)
        self.volume_history = defaultdict(list)
    
    def add_observation(self, symbol: str, price: float, volume: float):
        """Add market observation"""
        self.price_history[symbol].append(price)
        self.volume_history[symbol].append(volume)
        
        # Keep only recent window
        if len(self.price_history[symbol]) > self.window_size:
            self.price_history[symbol] = self.price_history[symbol][-self.window_size:]
            self.volume_history[symbol] = self.volume_history[symbol][-self.window_size:]
    
    def detect_regime(self, symbol: str) -> Dict[str, Any]:
        """
        Detect current market regime
        
        Returns:
            Dict with regime classification
        """
        prices = self.price_history.get(symbol, [])
        volumes = self.volume_history.get(symbol, [])
        
        if len(prices) < 20:
            return {
                'volatility_regime': 'unknown',
                'liquidity_regime': 'unknown',
                'trend_regime': 'unknown'
            }
        
        # Volatility classification
        returns = np.diff(prices) / prices[:-1]
        volatility = np.std(returns)
        
        if volatility < 0.01:
            vol_regime = 'low'
        elif volatility < 0.03:
            vol_regime = 'moderate'
        else:
            vol_regime = 'high'
        
        # Liquidity classification
        avg_volume = np.mean(volumes)
        recent_volume = np.mean(volumes[-10:])
        
        if recent_volume < avg_volume * 0.7:
            liq_regime = 'low'
        elif recent_volume < avg_volume * 1.3:
            liq_regime = 'normal'
        else:
            liq_regime = 'high'
        
        # Trend classification (simple)
        trend = np.polyfit(range(len(prices)), prices, 1)[0]
        
        if abs(trend) < np.std(prices) * 0.1:
            trend_regime = 'mean_reverting'
        else:
            trend_regime = 'trending'
        
        return {
            'volatility_regime': vol_regime,
            'volatility_value': volatility,
            'liquidity_regime': liq_regime,
            'trend_regime': trend_regime,
            'confidence': min(len(prices) / self.window_size, 1.0)
        }
