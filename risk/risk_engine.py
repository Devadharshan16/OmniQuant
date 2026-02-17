"""
Risk Engine
Comprehensive risk quantification for arbitrage opportunities
"""

import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class RiskLevel(Enum):
    """Risk classification"""
    VERY_LOW = "Very Low"
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    VERY_HIGH = "Very High"


@dataclass
class RiskComponents:
    """Individual risk components"""
    liquidity_risk: float       # 0-100
    complexity_risk: float      # 0-100
    volatility_risk: float      # 0-100
    execution_risk: float       # 0-100
    spread_risk: float          # 0-100
    
    def get_composite_score(self, weights: Optional[Dict[str, float]] = None) -> float:
        """Calculate weighted composite risk score"""
        if weights is None:
            # Default equal weighting
            weights = {
                'liquidity': 0.3,
                'complexity': 0.2,
                'volatility': 0.2,
                'execution': 0.2,
                'spread': 0.1
            }
        
        composite = (
            weights['liquidity'] * self.liquidity_risk +
            weights['complexity'] * self.complexity_risk +
            weights['volatility'] * self.volatility_risk +
            weights['execution'] * self.execution_risk +
            weights['spread'] * self.spread_risk
        )
        
        return min(max(composite, 0), 100)


@dataclass
class RiskAssessment:
    """Complete risk assessment"""
    components: RiskComponents
    composite_score: float
    risk_level: RiskLevel
    confidence: float
    warnings: List[str]
    recommendations: List[str]


class RiskEngine:
    """
    Advanced risk quantification engine
    
    Analyzes multiple risk dimensions:
    - Liquidity risk (volume constraints)
    - Path complexity risk (multi-hop fragility)
    - Volatility risk (price variance)
    - Execution risk (latency sensitivity)
    - Spread risk (bid-ask costs)
    """
    
    def __init__(self, 
                 risk_weights: Optional[Dict[str, float]] = None,
                 conservative_mode: bool = False):
        """
        Args:
            risk_weights: Custom risk component weights
            conservative_mode: If True, applies stricter risk scoring
        """
        self.risk_weights = risk_weights or {
            'liquidity': 0.3,
            'complexity': 0.2,
            'volatility': 0.2,
            'execution': 0.2,
            'spread': 0.1
        }
        self.conservative_mode = conservative_mode
        self.conservative_multiplier = 1.3 if conservative_mode else 1.0
    
    def assess_risk(self,
                   capital: float,
                   liquidities: List[float],
                   volatilities: List[float],
                   path_length: int,
                   spreads: List[float],
                   latency_half_life_ms: Optional[float] = None,
                   monte_carlo_results: Optional[Any] = None) -> RiskAssessment:
        """
        Comprehensive risk assessment
        
        Args:
            capital: Trading capital
            liquidities: Available liquidity at each hop
            volatilities: Volatility at each hop
            path_length: Number of hops
            spreads: Bid-ask spreads at each hop
            latency_half_life_ms: Opportunity half-life
            monte_carlo_results: Monte Carlo simulation results
        
        Returns:
            RiskAssessment object
        """
        # Calculate individual risk components
        liquidity_risk = self._calculate_liquidity_risk(capital, liquidities)
        complexity_risk = self._calculate_complexity_risk(path_length)
        volatility_risk = self._calculate_volatility_risk(volatilities)
        execution_risk = self._calculate_execution_risk(latency_half_life_ms, monte_carlo_results)
        spread_risk = self._calculate_spread_risk(spreads)
        
        # Apply conservative multiplier
        components = RiskComponents(
            liquidity_risk=min(liquidity_risk * self.conservative_multiplier, 100),
            complexity_risk=min(complexity_risk * self.conservative_multiplier, 100),
            volatility_risk=min(volatility_risk * self.conservative_multiplier, 100),
            execution_risk=min(execution_risk * self.conservative_multiplier, 100),
            spread_risk=min(spread_risk * self.conservative_multiplier, 100)
        )
        
        # Composite score
        composite_score = components.get_composite_score(self.risk_weights)
        
        # Risk level classification
        risk_level = self._classify_risk_level(composite_score)
        
        # Confidence metric
        confidence = self._calculate_confidence(components, monte_carlo_results)
        
        # Generate warnings and recommendations
        warnings = self._generate_warnings(components, confidence)
        recommendations = self._generate_recommendations(components, risk_level)
        
        return RiskAssessment(
            components=components,
            composite_score=composite_score,
            risk_level=risk_level,
            confidence=confidence,
            warnings=warnings,
            recommendations=recommendations
        )
    
    def _calculate_liquidity_risk(self, capital: float, liquidities: List[float]) -> float:
        """
        Liquidity risk based on capital vs available liquidity
        
        Risk increases when: volume / liquidity ratio is high
        """
        if not liquidities:
            return 100.0
        
        # Calculate average liquidity utilization
        utilizations = [capital / liq for liq in liquidities if liq > 0]
        
        if not utilizations:
            return 100.0
        
        avg_utilization = np.mean(utilizations)
        max_utilization = np.max(utilizations)
        
        # Risk score (0-100)
        # Low risk if utilization < 10%, high risk if > 50%
        risk = (avg_utilization * 0.7 + max_utilization * 0.3) * 200
        
        return min(risk, 100.0)
    
    def _calculate_complexity_risk(self, path_length: int) -> float:
        """
        Path complexity risk
        
        Longer paths = more execution steps = higher risk
        """
        # 2-hop: low risk, 5+ hop: high risk
        if path_length <= 2:
            return 10.0
        elif path_length == 3:
            return 30.0
        elif path_length == 4:
            return 50.0
        elif path_length == 5:
            return 70.0
        else:
            return 90.0
    
    def _calculate_volatility_risk(self, volatilities: List[float]) -> float:
        """
        Volatility risk based on price variance
        
        Higher volatility = more execution uncertainty
        """
        if not volatilities:
            return 50.0
        
        avg_volatility = np.mean(volatilities)
        max_volatility = np.max(volatilities)
        
        # Risk score
        # Low risk if vol < 1%, high risk if vol > 5%
        risk = (avg_volatility * 0.6 + max_volatility * 0.4) * 1000
        
        return min(risk, 100.0)
    
    def _calculate_execution_risk(self, 
                                  latency_half_life_ms: Optional[float],
                                  monte_carlo_results: Optional[Any]) -> float:
        """
        Execution risk based on latency sensitivity and simulation results
        """
        risk = 50.0  # Default moderate risk
        
        # Latency component
        if latency_half_life_ms is not None:
            if latency_half_life_ms < 50:
                risk = 80.0  # Very sensitive to latency
            elif latency_half_life_ms < 100:
                risk = 60.0
            elif latency_half_life_ms < 200:
                risk = 40.0
            else:
                risk = 20.0
        
        # Monte Carlo component
        if monte_carlo_results is not None:
            prob_negative = monte_carlo_results.probability_negative
            risk = max(risk, prob_negative * 100)
        
        return min(risk, 100.0)
    
    def _calculate_spread_risk(self, spreads: List[float]) -> float:
        """
        Spread risk based on bid-ask spreads
        
        Wide spreads = higher execution costs
        """
        if not spreads:
            return 50.0
        
        avg_spread_bps = np.mean(spreads)
        max_spread_bps = np.max(spreads)
        
        # Risk score
        # Low risk if spread < 10 bps, high risk if > 100 bps
        risk = (avg_spread_bps * 0.7 + max_spread_bps * 0.3) / 2
        
        return min(risk, 100.0)
    
    def _classify_risk_level(self, composite_score: float) -> RiskLevel:
        """Classify composite risk score into risk level"""
        if composite_score < 20:
            return RiskLevel.VERY_LOW
        elif composite_score < 40:
            return RiskLevel.LOW
        elif composite_score < 60:
            return RiskLevel.MODERATE
        elif composite_score < 80:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH
    
    def _calculate_confidence(self, 
                             components: RiskComponents,
                             monte_carlo_results: Optional[Any]) -> float:
        """
        Calculate confidence metric
        
        Confidence = 1 - P(negative return | simulations)
        """
        if monte_carlo_results is not None:
            return (1 - monte_carlo_results.probability_negative) * 100
        
        # Heuristic based on risk components
        avg_risk = components.get_composite_score()
        confidence = 100 - avg_risk
        
        return max(min(confidence, 100), 0)
    
    def _generate_warnings(self, components: RiskComponents, confidence: float) -> List[str]:
        """Generate risk warnings"""
        warnings = []
        
        if components.liquidity_risk > 70:
            warnings.append("⚠️ High liquidity risk - capital may exceed available depth")
        
        if components.complexity_risk > 70:
            warnings.append("⚠️ Complex multi-hop path - increased execution fragility")
        
        if components.volatility_risk > 70:
            warnings.append("⚠️ High volatility - prices may move significantly during execution")
        
        if components.execution_risk > 70:
            warnings.append("⚠️ Latency sensitive - opportunity may disappear quickly")
        
        if confidence < 50:
            warnings.append("⚠️ Low confidence - high probability of negative outcome")
        
        return warnings
    
    def _generate_recommendations(self, 
                                 components: RiskComponents, 
                                 risk_level: RiskLevel) -> List[str]:
        """Generate risk mitigation recommendations"""
        recommendations = []
        
        if risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            recommendations.append("Consider reducing position size")
        
        if components.liquidity_risk > 60:
            recommendations.append("Split execution across multiple time periods")
        
        if components.complexity_risk > 60:
            recommendations.append("Look for shorter arbitrage paths")
        
        if components.execution_risk > 60:
            recommendations.append("Use faster execution infrastructure")
        
        if components.volatility_risk > 60:
            recommendations.append("Wait for lower volatility regime")
        
        return recommendations
