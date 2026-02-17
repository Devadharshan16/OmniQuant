"""
Example usage of OmniQuant components
"""

import sys
sys.path.append('.')

from simulation.order_book import OrderBookSimulator
from simulation.monte_carlo import MonteCarloSimulator
from risk.risk_engine import RiskEngine
from risk.stress_test import StressTestEngine
from optimizer.capital_allocator import CapitalAllocator


def example_monte_carlo():
    """Example: Monte Carlo simulation"""
    print("=" * 60)
    print("Example: Monte Carlo Simulation")
    print("=" * 60)
    
    mc = MonteCarloSimulator(n_simulations=1000)
    
    results = mc.simulate_opportunity(
        base_return=0.0025,  # 0.25% expected return
        path_length=3,
        liquidities=[10000, 50000, 100000],
        volatilities=[0.01, 0.015, 0.012],
        base_fees=[0.001, 0.001, 0.001],
        capital=1000
    )
    
    print(f"\nMonte Carlo Results (n={results.num_simulations}):")
    print(f"  Mean Return:        {results.mean_return * 100:.4f}%")
    print(f"  Std Deviation:      {results.std_return * 100:.4f}%")
    print(f"  Median Return:      {results.median_return * 100:.4f}%")
    print(f"  Worst 5%:           {results.worst_5pct * 100:.4f}%")
    print(f"  Best 5%:            {results.best_5pct * 100:.4f}%")
    print(f"  P(Negative):        {results.probability_negative * 100:.2f}%")
    print(f"  P(Profitable):      {results.probability_profitable * 100:.2f}%")
    print(f"  Sharpe Ratio:       {results.sharpe_ratio:.3f}")


def example_risk_assessment():
    """Example: Risk assessment"""
    print("\n" + "=" * 60)
    print("Example: Risk Assessment")
    print("=" * 60)
    
    engine = RiskEngine()
    
    assessment = engine.assess_risk(
        capital=1000,
        liquidities=[5000, 20000, 50000],
        volatilities=[0.02, 0.015, 0.01],
        path_length=3,
        spreads=[15, 12, 10],
        latency_half_life_ms=75
    )
    
    print(f"\nRisk Assessment:")
    print(f"  Composite Score:    {assessment.composite_score:.1f}/100")
    print(f"  Risk Level:         {assessment.risk_level.value}")
    print(f"  Confidence:         {assessment.confidence:.1f}%")
    print(f"\nRisk Components:")
    print(f"  Liquidity Risk:     {assessment.components.liquidity_risk:.1f}/100")
    print(f"  Complexity Risk:    {assessment.components.complexity_risk:.1f}/100")
    print(f"  Volatility Risk:    {assessment.components.volatility_risk:.1f}/100")
    print(f"  Execution Risk:     {assessment.components.execution_risk:.1f}/100")
    print(f"  Spread Risk:        {assessment.components.spread_risk:.1f}/100")
    
    if assessment.warnings:
        print(f"\nWarnings:")
        for warning in assessment.warnings:
            print(f"  - {warning}")


def example_stress_testing():
    """Example: Stress testing"""
    print("\n" + "=" * 60)
    print("Example: Stress Testing")
    print("=" * 60)
    
    opportunity = {
        'base_return': 0.0030,
        'path_length': 3,
        'liquidities': [10000, 50000, 100000],
        'volatilities': [0.01, 0.01, 0.01],
        'fees': [0.001, 0.001, 0.001]
    }
    
    engine = StressTestEngine()
    report = engine.run_stress_tests(opportunity)
    
    print(f"\nStress Test Report:")
    print(f"  Scenarios Tested:   {report.scenarios_tested}")
    print(f"  Scenarios Survived: {report.scenarios_survived}")
    print(f"  Robustness Score:   {report.robustness_score:.1f}%")
    print(f"  Overall Rating:     {report.overall_rating}")
    print(f"  Worst Case Return:  {report.worst_case_return * 100:.4f}%")
    print(f"  Best Case Return:   {report.best_case_return * 100:.4f}%")
    
    print(f"\nScenario Results:")
    for result in report.stress_results[:3]:  # Show first 3
        print(f"  {result.scenario.name:.<30} {'✓' if result.survives else '✗'} "
              f"{result.stressed_return * 100:.4f}% (impact: {result.impact_pct:.2f}%)")


def example_capital_allocation():
    """Example: Capital allocation"""
    print("\n" + "=" * 60)
    print("Example: Capital Allocation")
    print("=" * 60)
    
    # Mock opportunities
    opportunities = [
        {
            'id': 'opp_1',
            'path': ['BTC', 'ETH', 'USDT', 'BTC'],
            'expected_return': 0.0025,
            'risk_score': 35,
            'confidence': 0.75,
            'liquidity': 50000,
            'min_capital': 100
        },
        {
            'id': 'opp_2',
            'path': ['ETH', 'BNB', 'USDT', 'ETH'],
            'expected_return': 0.0035,
            'risk_score': 55,
            'confidence': 0.65,
            'liquidity': 30000,
            'min_capital': 100
        },
        {
            'id': 'opp_3',
            'path': ['BTC', 'USDT', 'BTC'],
            'expected_return': 0.0015,
            'risk_score': 25,
            'confidence': 0.85,
            'liquidity': 100000,
            'min_capital': 100
        }
    ]
    
    allocator = CapitalAllocator(
        total_capital=10000,
        max_position_pct=0.40,
        risk_budget=50.0
    )
    
    allocation = allocator.allocate_capital(opportunities, method='greedy')
    
    print(f"\nPortfolio Allocation:")
    print(f"  Total Capital:          ${allocation.total_capital:,.2f}")
    print(f"  Capital Allocated:      ${allocation.capital_allocated:,.2f}")
    print(f"  Capital Remaining:      ${allocation.capital_remaining:,.2f}")
    print(f"  Utilization:            {allocation.utilization_pct:.1f}%")
    print(f"  Expected Return:        {allocation.expected_portfolio_return * 100:.4f}%")
    print(f"  Portfolio Risk:         {allocation.portfolio_risk_score:.1f}/100")
    
    print(f"\nAllocations:")
    for alloc in allocation.allocations:
        print(f"  {' → '.join(alloc.path):.<40} ${alloc.allocated_capital:>8,.2f} "
              f"({alloc.expected_return * 100:.3f}%)")


def main():
    print("\n🔷 OmniQuant v2 - Example Usage\n")
    
    try:
        example_monte_carlo()
        example_risk_assessment()
        example_stress_testing()
        example_capital_allocation()
        
        print("\n" + "=" * 60)
        print("✓ All examples completed successfully!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
