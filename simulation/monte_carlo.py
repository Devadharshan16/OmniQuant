"""
Monte Carlo Execution Simulator
Statistical validation via simulation
"""

import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import concurrent.futures


@dataclass
class SimulationResult:
    """Single simulation run result"""
    final_return: float
    execution_prices: List[float]
    slippage_realized: List[float]
    latency_ms: float
    success: bool


@dataclass
class MonteCarloResults:
    """Aggregated Monte Carlo results"""
    mean_return: float
    std_return: float
    median_return: float
    worst_5pct: float
    best_5pct: float
    probability_negative: float
    probability_profitable: float
    sharpe_ratio: float
    num_simulations: int
    all_returns: List[float]
    confidence_95_lower: float
    confidence_95_upper: float


class MonteCarloSimulator:
    """
    Monte Carlo simulation for arbitrage execution
    Runs thousands of scenarios with randomized:
    - Latency
    - Slippage
    - Volatility noise
    - Liquidity variance
    """
    
    def __init__(self, n_simulations: int = 1000, random_seed: Optional[int] = None):
        """
        Args:
            n_simulations: Number of simulation runs
            random_seed: Random seed for reproducibility
        """
        self.n_simulations = n_simulations
        if random_seed is not None:
            np.random.seed(random_seed)
    
    def simulate_opportunity(self,
                            base_return: float,
                            path_length: int,
                            liquidities: List[float],
                            volatilities: List[float],
                            base_fees: List[float],
                            capital: float = 1000.0) -> MonteCarloResults:
        """
        Run Monte Carlo simulation on arbitrage opportunity
        
        Args:
            base_return: Theoretical return without noise
            path_length: Number of hops
            liquidities: Liquidity at each hop
            volatilities: Volatility at each hop
            base_fees: Fees at each hop
            capital: Trading capital
        
        Returns:
            MonteCarloResults with statistical summary
        """
        returns = []
        
        for _ in range(self.n_simulations):
            result = self._run_single_simulation(
                base_return,
                path_length,
                liquidities,
                volatilities,
                base_fees,
                capital
            )
            returns.append(result.final_return)
        
        return self._aggregate_results(returns)
    
    def _run_single_simulation(self,
                               base_return: float,
                               path_length: int,
                               liquidities: List[float],
                               volatilities: List[float],
                               base_fees: List[float],
                               capital: float) -> SimulationResult:
        """Run single simulation with randomization"""
        
        # Randomize latency (0-200ms)
        latency_ms = np.random.exponential(50)
        
        # Price decay due to latency (assume 0.1% per 100ms)
        latency_decay = 1 - (latency_ms / 100) * 0.001
        
        # Simulate each hop
        cumulative_return = 1.0
        execution_prices = []
        slippages = []
        
        for i in range(path_length):
            # Randomize liquidity (±30%)
            actual_liquidity = liquidities[i] * np.random.uniform(0.7, 1.3)
            
            # Randomize volatility (±50%)
            actual_volatility = volatilities[i] * np.random.uniform(0.5, 1.5)
            
            # Calculate slippage based on capital and liquidity
            liquidity_ratio = capital / actual_liquidity if actual_liquidity > 0 else 1.0
            slippage = min(0.01 * liquidity_ratio ** 0.6, 0.1)  # Capped at 10%
            
            # Volatility noise
            volatility_noise = np.random.normal(0, actual_volatility)
            
            # Effective return for this hop
            hop_multiplier = (1 - base_fees[i]) * (1 - slippage) * (1 + volatility_noise)
            cumulative_return *= hop_multiplier
            
            execution_prices.append(hop_multiplier)
            slippages.append(slippage)
        
        # Apply latency decay
        cumulative_return *= latency_decay
        
        # Final return
        final_return = cumulative_return - 1.0
        
        return SimulationResult(
            final_return=final_return,
            execution_prices=execution_prices,
            slippage_realized=slippages,
            latency_ms=latency_ms,
            success=final_return > 0
        )
    
    def _aggregate_results(self, returns: List[float]) -> MonteCarloResults:
        """Aggregate simulation results into statistics"""
        returns_array = np.array(returns)
        
        mean_return = np.mean(returns_array)
        std_return = np.std(returns_array)
        median_return = np.median(returns_array)
        
        # Percentiles
        worst_5pct = np.percentile(returns_array, 5)
        best_5pct = np.percentile(returns_array, 95)
        
        # Confidence intervals
        conf_95_lower = np.percentile(returns_array, 2.5)
        conf_95_upper = np.percentile(returns_array, 97.5)
        
        # Probabilities
        prob_negative = np.mean(returns_array < 0)
        prob_profitable = np.mean(returns_array > 0)
        
        # Sharpe ratio (annualized, assuming daily opportunities)
        risk_free_rate = 0.0
        sharpe = (mean_return - risk_free_rate) / std_return if std_return > 0 else 0
        sharpe_annualized = sharpe * np.sqrt(365)
        
        return MonteCarloResults(
            mean_return=mean_return,
            std_return=std_return,
            median_return=median_return,
            worst_5pct=worst_5pct,
            best_5pct=best_5pct,
            probability_negative=prob_negative,
            probability_profitable=prob_profitable,
            sharpe_ratio=sharpe_annualized,
            num_simulations=self.n_simulations,
            all_returns=returns,
            confidence_95_lower=conf_95_lower,
            confidence_95_upper=conf_95_upper
        )
    
    def simulate_parallel(self,
                         opportunities: List[Dict[str, Any]],
                         max_workers: int = 4) -> List[MonteCarloResults]:
        """
        Run Monte Carlo simulations in parallel for multiple opportunities
        
        Args:
            opportunities: List of opportunity dicts
            max_workers: Number of parallel workers
        
        Returns:
            List of MonteCarloResults
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for opp in opportunities:
                future = executor.submit(
                    self.simulate_opportunity,
                    opp['base_return'],
                    opp['path_length'],
                    opp['liquidities'],
                    opp['volatilities'],
                    opp['fees'],
                    opp.get('capital', 1000.0)
                )
                futures.append(future)
            
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        return results


def calculate_value_at_risk(returns: List[float], confidence: float = 0.95) -> float:
    """
    Calculate Value at Risk (VaR)
    
    Args:
        returns: List of simulated returns
        confidence: Confidence level (0.95 = 95%)
    
    Returns:
        VaR value
    """
    return np.percentile(returns, (1 - confidence) * 100)


def calculate_expected_shortfall(returns: List[float], confidence: float = 0.95) -> float:
    """
    Calculate Expected Shortfall (CVaR)
    Average loss beyond VaR
    
    Args:
        returns: List of simulated returns
        confidence: Confidence level
    
    Returns:
        Expected shortfall
    """
    var = calculate_value_at_risk(returns, confidence)
    tail_returns = [r for r in returns if r <= var]
    return np.mean(tail_returns) if tail_returns else var
