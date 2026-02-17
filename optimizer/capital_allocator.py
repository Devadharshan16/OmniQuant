"""
Capital Allocation Optimizer
Portfolio-level opportunity ranking and capital allocation
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from scipy.optimize import linprog
import heapq


@dataclass
class AllocationResult:
    """Result of capital allocation"""
    opportunity_id: str
    path: List[str]
    allocated_capital: float
    expected_return: float
    risk_score: float
    confidence: float
    ranking_score: float


@dataclass
class PortfolioAllocation:
    """Complete portfolio allocation"""
    total_capital: float
    capital_allocated: float
    capital_remaining: float
    allocations: List[AllocationResult]
    expected_portfolio_return: float
    portfolio_risk_score: float
    utilization_pct: float
    num_opportunities: int


class CapitalAllocator:
    """
    Institutional-grade capital allocation optimizer
    
    Maximizes: Σ(x_i × r_i × confidence_i / risk_i)
    
    Subject to:
    - Total capital constraint
    - Liquidity constraints per opportunity
    - Risk budget limit
    - Diversification (optional)
    """
    
    def __init__(self,
                 total_capital: float,
                 max_position_pct: float = 0.30,
                 risk_budget: float = 50.0,
                 min_confidence: float = 0.50):
        """
        Args:
            total_capital: Total available capital
            max_position_pct: Maximum % in single opportunity
            risk_budget: Maximum portfolio risk score (0-100)
            min_confidence: Minimum confidence to consider
        """
        self.total_capital = total_capital
        self.max_position_pct = max_position_pct
        self.risk_budget = risk_budget
        self.min_confidence = min_confidence
    
    def allocate_capital(self,
                        opportunities: List[Dict[str, Any]],
                        method: str = 'greedy') -> PortfolioAllocation:
        """
        Allocate capital across opportunities
        
        Args:
            opportunities: List of opportunity dicts containing:
                - id, path, expected_return, risk_score, confidence
                - min_capital, max_capital, liquidity
            method: 'greedy', 'linear_programming', or 'risk_parity'
        
        Returns:
            PortfolioAllocation
        """
        # Filter by minimum confidence
        filtered = [
            opp for opp in opportunities 
            if opp.get('confidence', 0) >= self.min_confidence
        ]
        
        if not filtered:
            return self._empty_allocation()
        
        if method == 'greedy':
            return self._greedy_allocation(filtered)
        elif method == 'linear_programming':
            return self._lp_allocation(filtered)
        elif method == 'risk_parity':
            return self._risk_parity_allocation(filtered)
        else:
            return self._greedy_allocation(filtered)
    
    def _greedy_allocation(self, opportunities: List[Dict[str, Any]]) -> PortfolioAllocation:
        """
        Greedy allocation: rank by score and allocate sequentially
        """
        # Rank opportunities
        ranked = self._rank_opportunities(opportunities)
        
        allocations = []
        remaining_capital = self.total_capital
        cumulative_risk = 0.0
        
        for opp in ranked:
            if remaining_capital <= 0:
                break
            
            # Check risk budget
            if cumulative_risk >= self.risk_budget:
                break
            
            # Calculate max allocation for this opportunity
            max_position = self.total_capital * self.max_position_pct
            max_by_liquidity = opp.get('liquidity', float('inf'))
            max_allocation = min(remaining_capital, max_position, max_by_liquidity)
            
            # Check if adding this would exceed risk budget
            incremental_risk = opp['risk_score'] * (max_allocation / self.total_capital)
            if cumulative_risk + incremental_risk > self.risk_budget:
                # Reduce allocation to stay within risk budget
                scale_factor = (self.risk_budget - cumulative_risk) / incremental_risk
                max_allocation *= scale_factor
            
            if max_allocation < opp.get('min_capital', 0):
                continue
            
            # Allocate
            allocation = AllocationResult(
                opportunity_id=opp['id'],
                path=opp['path'],
                allocated_capital=max_allocation,
                expected_return=opp['expected_return'],
                risk_score=opp['risk_score'],
                confidence=opp['confidence'],
                ranking_score=opp['ranking_score']
            )
            
            allocations.append(allocation)
            remaining_capital -= max_allocation
            cumulative_risk += incremental_risk
        
        return self._build_portfolio(allocations, remaining_capital)
    
    def _lp_allocation(self, opportunities: List[Dict[str, Any]]) -> PortfolioAllocation:
        """
        Linear programming optimization
        
        Maximize: Σ(return_i × confidence_i / risk_i) × x_i
        Subject to: Σx_i ≤ capital, risk constraints, liquidity constraints
        """
        n = len(opportunities)
        
        # Objective: maximize risk-adjusted returns
        # We negate for minimization
        c = [
            -(opp['expected_return'] * opp['confidence'] / max(opp['risk_score'], 1.0))
            for opp in opportunities
        ]
        
        # Inequality constraints: Ax_ub <= b_ub
        A_ub = []
        b_ub = []
        
        # Total capital constraint
        A_ub.append([1.0] * n)
        b_ub.append(self.total_capital)
        
        # Risk budget constraint
        risk_coeffs = [
            opp['risk_score'] / 100.0 for opp in opportunities
        ]
        A_ub.append(risk_coeffs)
        b_ub.append(self.risk_budget / 100.0 * self.total_capital)
        
        # Individual position limits
        bounds = []
        for opp in opportunities:
            lower = opp.get('min_capital', 0)
            upper = min(
                opp.get('liquidity', self.total_capital),
                self.total_capital * self.max_position_pct
            )
            bounds.append((lower, upper))
        
        # Solve
        try:
            result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
            
            if result.success:
                allocations = []
                for i, opp in enumerate(opportunities):
                    if result.x[i] > 0.01:  # Ignore tiny allocations
                        allocation = AllocationResult(
                            opportunity_id=opp['id'],
                            path=opp['path'],
                            allocated_capital=result.x[i],
                            expected_return=opp['expected_return'],
                            risk_score=opp['risk_score'],
                            confidence=opp['confidence'],
                            ranking_score=opp['ranking_score']
                        )
                        allocations.append(allocation)
                
                capital_allocated = sum(a.allocated_capital for a in allocations)
                return self._build_portfolio(allocations, self.total_capital - capital_allocated)
        except Exception:
            pass
        
        # Fallback to greedy if LP fails
        return self._greedy_allocation(opportunities)
    
    def _risk_parity_allocation(self, opportunities: List[Dict[str, Any]]) -> PortfolioAllocation:
        """
        Risk parity: allocate inversely proportional to risk
        """
        # Calculate inverse risk weights
        total_inv_risk = sum(1.0 / max(opp['risk_score'], 1.0) for opp in opportunities)
        
        allocations = []
        for opp in opportunities:
            weight = (1.0 / max(opp['risk_score'], 1.0)) / total_inv_risk
            allocation_amount = self.total_capital * weight
            
            # Apply constraints
            max_position = self.total_capital * self.max_position_pct
            max_by_liquidity = opp.get('liquidity', float('inf'))
            allocation_amount = min(allocation_amount, max_position, max_by_liquidity)
            
            if allocation_amount >= opp.get('min_capital', 0):
                allocation = AllocationResult(
                    opportunity_id=opp['id'],
                    path=opp['path'],
                    allocated_capital=allocation_amount,
                    expected_return=opp['expected_return'],
                    risk_score=opp['risk_score'],
                    confidence=opp['confidence'],
                    ranking_score=opp['ranking_score']
                )
                allocations.append(allocation)
        
        capital_allocated = sum(a.allocated_capital for a in allocations)
        return self._build_portfolio(allocations, self.total_capital - capital_allocated)
    
    def _rank_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank opportunities by composite score
        
        Score = (expected_return × confidence) / risk_score
        """
        for opp in opportunities:
            score = (
                opp['expected_return'] * 
                opp['confidence'] / 
                max(opp['risk_score'], 1.0)
            )
            opp['ranking_score'] = score
        
        # Sort descending by score
        return sorted(opportunities, key=lambda x: x['ranking_score'], reverse=True)
    
    def _build_portfolio(self, 
                        allocations: List[AllocationResult],
                        remaining_capital: float) -> PortfolioAllocation:
        """Build portfolio allocation result"""
        capital_allocated = sum(a.allocated_capital for a in allocations)
        
        # Expected portfolio return (weighted average)
        if capital_allocated > 0:
            expected_return = sum(
                a.allocated_capital * a.expected_return 
                for a in allocations
            ) / capital_allocated
        else:
            expected_return = 0.0
        
        # Portfolio risk (weighted average)
        if capital_allocated > 0:
            portfolio_risk = sum(
                (a.allocated_capital / capital_allocated) * a.risk_score
                for a in allocations
            )
        else:
            portfolio_risk = 0.0
        
        return PortfolioAllocation(
            total_capital=self.total_capital,
            capital_allocated=capital_allocated,
            capital_remaining=remaining_capital,
            allocations=allocations,
            expected_portfolio_return=expected_return,
            portfolio_risk_score=portfolio_risk,
            utilization_pct=(capital_allocated / self.total_capital * 100),
            num_opportunities=len(allocations)
        )
    
    def _empty_allocation(self) -> PortfolioAllocation:
        """Return empty allocation"""
        return PortfolioAllocation(
            total_capital=self.total_capital,
            capital_allocated=0.0,
            capital_remaining=self.total_capital,
            allocations=[],
            expected_portfolio_return=0.0,
            portfolio_risk_score=0.0,
            utilization_pct=0.0,
            num_opportunities=0
        )


class OpportunityRanker:
    """
    Ranks opportunities using multiple criteria
    """
    
    @staticmethod
    def rank_by_sharpe(opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank by Sharpe-like ratio"""
        for opp in opportunities:
            if 'monte_carlo_results' in opp:
                sharpe = opp['monte_carlo_results'].sharpe_ratio
            else:
                # Approximate
                sharpe = opp['expected_return'] / (opp['risk_score'] / 100.0)
            opp['sharpe'] = sharpe
        
        return sorted(opportunities, key=lambda x: x.get('sharpe', 0), reverse=True)
    
    @staticmethod
    def rank_by_risk_adjusted_return(opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank by return/risk ratio"""
        for opp in opportunities:
            score = opp['expected_return'] / max(opp['risk_score'], 1.0)
            opp['risk_adj_return'] = score
        
        return sorted(opportunities, key=lambda x: x.get('risk_adj_return', 0), reverse=True)
    
    @staticmethod
    def rank_by_confidence(opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank by confidence level"""
        return sorted(opportunities, key=lambda x: x.get('confidence', 0), reverse=True)
    
    @staticmethod
    def rank_by_composite(opportunities: List[Dict[str, Any]],
                         weights: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
        """
        Rank by weighted composite score
        
        Default weights:
        - return: 0.4
        - confidence: 0.3
        - inverse_risk: 0.3
        """
        if weights is None:
            weights = {'return': 0.4, 'confidence': 0.3, 'inverse_risk': 0.3}
        
        for opp in opportunities:
            score = (
                weights['return'] * opp['expected_return'] * 100 +
                weights['confidence'] * opp['confidence'] * 100 +
                weights['inverse_risk'] * (100 - opp['risk_score'])
            )
            opp['composite_score'] = score
        
        return sorted(opportunities, key=lambda x: x.get('composite_score', 0), reverse=True)
