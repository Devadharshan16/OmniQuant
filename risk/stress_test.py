"""
Stress Testing Module
Market shock simulation and robustness analysis
"""

import numpy as np
from typing import Dict, List, Any, Callable
from dataclasses import dataclass
from enum import Enum


class ShockType(Enum):
    """Types of market shocks"""
    PRICE_SHOCK = "price_shock"
    LIQUIDITY_SHOCK = "liquidity_shock"
    VOLATILITY_SPIKE = "volatility_spike"
    FEE_INCREASE = "fee_increase"
    LATENCY_SPIKE = "latency_spike"
    COMBINED = "combined"


@dataclass
class StressScenario:
    """Defines a stress test scenario"""
    name: str
    shock_type: ShockType
    magnitude: float  # Shock magnitude (e.g., 0.01 = 1%)
    description: str


@dataclass
class StressTestResult:
    """Result of a single stress test"""
    scenario: StressScenario
    base_return: float
    stressed_return: float
    return_change: float
    survives: bool  # True if still profitable after shock
    impact_pct: float


@dataclass
class RobustnessReport:
    """Comprehensive stress test report"""
    scenarios_tested: int
    scenarios_survived: int
    robustness_score: float  # % of scenarios survived
    worst_case_return: float
    best_case_return: float
    stress_results: List[StressTestResult]
    overall_rating: str


class StressTestEngine:
    """
    Stress testing for arbitrage opportunities
    
    Tests robustness under various market shocks:
    - Price movements (±1-5%)
    - Liquidity drops (30-50%)
    - Volatility spikes (2-5x)
    - Fee increases
    - Latency spikes
    """
    
    def __init__(self, profitability_threshold: float = 0.0):
        """
        Args:
            profitability_threshold: Minimum return to consider "survived"
        """
        self.threshold = profitability_threshold
    
    def run_stress_tests(self,
                        opportunity: Dict[str, Any],
                        scenarios: List[StressScenario] = None) -> RobustnessReport:
        """
        Run comprehensive stress tests
        
        Args:
            opportunity: Arbitrage opportunity dict with:
                - base_return
                - liquidities
                - volatilities
                - fees
                - path_length
            scenarios: Custom scenarios (uses defaults if None)
        
        Returns:
            RobustnessReport
        """
        if scenarios is None:
            scenarios = self._get_default_scenarios()
        
        stress_results = []
        base_return = opportunity['base_return']
        
        for scenario in scenarios:
            result = self._run_single_stress_test(opportunity, scenario)
            stress_results.append(result)
        
        # Aggregate results
        scenarios_survived = sum(1 for r in stress_results if r.survives)
        robustness_score = (scenarios_survived / len(scenarios)) * 100
        
        worst_case = min(r.stressed_return for r in stress_results)
        best_case = max(r.stressed_return for r in stress_results)
        
        # Overall rating
        if robustness_score >= 80:
            rating = "Excellent"
        elif robustness_score >= 60:
            rating = "Good"
        elif robustness_score >= 40:
            rating = "Moderate"
        elif robustness_score >= 20:
            rating = "Weak"
        else:
            rating = "Very Weak"
        
        return RobustnessReport(
            scenarios_tested=len(scenarios),
            scenarios_survived=scenarios_survived,
            robustness_score=robustness_score,
            worst_case_return=worst_case,
            best_case_return=best_case,
            stress_results=stress_results,
            overall_rating=rating
        )
    
    def _run_single_stress_test(self,
                                opportunity: Dict[str, Any],
                                scenario: StressScenario) -> StressTestResult:
        """Run single stress test scenario"""
        base_return = opportunity['base_return']
        
        # Apply shock based on type
        if scenario.shock_type == ShockType.PRICE_SHOCK:
            stressed_return = self._apply_price_shock(opportunity, scenario.magnitude)
        
        elif scenario.shock_type == ShockType.LIQUIDITY_SHOCK:
            stressed_return = self._apply_liquidity_shock(opportunity, scenario.magnitude)
        
        elif scenario.shock_type == ShockType.VOLATILITY_SPIKE:
            stressed_return = self._apply_volatility_spike(opportunity, scenario.magnitude)
        
        elif scenario.shock_type == ShockType.FEE_INCREASE:
            stressed_return = self._apply_fee_increase(opportunity, scenario.magnitude)
        
        elif scenario.shock_type == ShockType.LATENCY_SPIKE:
            stressed_return = self._apply_latency_spike(opportunity, scenario.magnitude)
        
        elif scenario.shock_type == ShockType.COMBINED:
            stressed_return = self._apply_combined_shock(opportunity, scenario.magnitude)
        
        else:
            stressed_return = base_return
        
        return_change = stressed_return - base_return
        survives = stressed_return > self.threshold
        impact_pct = (return_change / base_return * 100) if base_return != 0 else -100
        
        return StressTestResult(
            scenario=scenario,
            base_return=base_return,
            stressed_return=stressed_return,
            return_change=return_change,
            survives=survives,
            impact_pct=impact_pct
        )
    
    def _apply_price_shock(self, opp: Dict[str, Any], magnitude: float) -> float:
        """Simulate uniform price movement"""
        # Price shock reduces return approximately by the shock magnitude
        # For a cycle, if all prices move by x%, return changes by roughly -x% per hop
        path_length = opp['path_length']
        base_return = opp['base_return']
        
        # Each hop hit by price movement
        return_multiplier = (1 - magnitude) ** path_length
        stressed_return = (1 + base_return) * return_multiplier - 1
        
        return stressed_return
    
    def _apply_liquidity_shock(self, opp: Dict[str, Any], magnitude: float) -> float:
        """Simulate liquidity drop"""
        # Liquidity drops by magnitude %
        # This increases slippage
        base_return = opp['base_return']
        
        # Increased slippage eats into return
        # Rough model: slippage proportional to (1/liquidity)
        liquidity_impact = magnitude * 0.005  # 30% liq drop ≈ 0.15% return loss
        
        stressed_return = base_return - liquidity_impact
        return stressed_return
    
    def _apply_volatility_spike(self, opp: Dict[str, Any], magnitude: float) -> float:
        """Simulate volatility increase"""
        base_return = opp['base_return']
        volatilities = opp.get('volatilities', [0.01] * opp['path_length'])
        
        # Increased volatility adds execution uncertainty
        # Model: random walk impact proportional to vol
        avg_vol = np.mean(volatilities)
        volatility_impact = avg_vol * magnitude * np.random.normal(0, 1)
        
        stressed_return = base_return + volatility_impact
        return stressed_return
    
    def _apply_fee_increase(self, opp: Dict[str, Any], magnitude: float) -> float:
        """Simulate fee increase"""
        base_return = opp['base_return']
        fees = opp.get('fees', [0.001] * opp['path_length'])
        
        # Fee increase directly reduces return
        additional_fees = sum(fees) * magnitude
        
        stressed_return = base_return - additional_fees
        return stressed_return
    
    def _apply_latency_spike(self, opp: Dict[str, Any], magnitude: float) -> float:
        """Simulate latency increase"""
        base_return = opp['base_return']
        
        # Latency causes price decay
        # Model: return decays by ~0.1% per 100ms additional latency
        latency_impact = magnitude * 0.001
        
        stressed_return = base_return - latency_impact
        return stressed_return
    
    def _apply_combined_shock(self, opp: Dict[str, Any], magnitude: float) -> float:
        """Simulate combined market stress"""
        # Apply multiple shocks simultaneously (reduced magnitude)
        base_return = opp['base_return']
        
        stressed_return = base_return
        stressed_return = self._apply_price_shock(
            {**opp, 'base_return': stressed_return}, magnitude * 0.5
        )
        stressed_return = self._apply_liquidity_shock(
            {**opp, 'base_return': stressed_return}, magnitude * 0.5
        )
        stressed_return = self._apply_fee_increase(
            {**opp, 'base_return': stressed_return}, magnitude * 0.3
        )
        
        return stressed_return
    
    def _get_default_scenarios(self) -> List[StressScenario]:
        """Get default stress test scenarios"""
        return [
            StressScenario(
                name="Price +1%",
                shock_type=ShockType.PRICE_SHOCK,
                magnitude=0.01,
                description="Uniform 1% price increase"
            ),
            StressScenario(
                name="Price -1%",
                shock_type=ShockType.PRICE_SHOCK,
                magnitude=0.01,
                description="Uniform 1% price decrease"
            ),
            StressScenario(
                name="Liquidity -30%",
                shock_type=ShockType.LIQUIDITY_SHOCK,
                magnitude=0.30,
                description="30% liquidity reduction"
            ),
            StressScenario(
                name="Volatility 2x",
                shock_type=ShockType.VOLATILITY_SPIKE,
                magnitude=2.0,
                description="Volatility doubles"
            ),
            StressScenario(
                name="Fee +50%",
                shock_type=ShockType.FEE_INCREASE,
                magnitude=0.50,
                description="50% increase in trading fees"
            ),
            StressScenario(
                name="Latency +100ms",
                shock_type=ShockType.LATENCY_SPIKE,
                magnitude=100.0,
                description="100ms additional latency"
            ),
            StressScenario(
                name="Combined Stress",
                shock_type=ShockType.COMBINED,
                magnitude=0.50,
                description="Multiple simultaneous shocks"
            ),
        ]


def calculate_breakeven_shock(opportunity: Dict[str, Any], 
                              shock_type: ShockType,
                              max_iterations: int = 100) -> float:
    """
    Calculate shock magnitude that brings return to zero (breakeven)
    
    Uses binary search to find breakeven point
    
    Returns:
        Shock magnitude at breakeven
    """
    engine = StressTestEngine()
    
    low, high = 0.0, 1.0
    tolerance = 0.001
    
    for _ in range(max_iterations):
        mid = (low + high) / 2
        scenario = StressScenario("test", shock_type, mid, "")
        result = engine._run_single_stress_test(opportunity, scenario)
        
        if abs(result.stressed_return) < tolerance:
            return mid
        
        if result.stressed_return > 0:
            low = mid
        else:
            high = mid
    
    return (low + high) / 2
