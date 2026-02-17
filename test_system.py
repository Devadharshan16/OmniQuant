"""
Quick test script to verify OmniQuant setup
"""

import sys
import time

def test_imports():
    """Test if all modules can be imported"""
    print("Testing Python module imports...")
    
    modules = [
        ('simulation.order_book', 'OrderBookSimulator'),
        ('simulation.slippage_model', 'AdvancedSlippageModel'),
        ('simulation.impact_model', 'MarketImpactModel'),
        ('simulation.monte_carlo', 'MonteCarloSimulator'),
        ('risk.risk_engine', 'RiskEngine'),
        ('risk.stress_test', 'StressTestEngine'),
        ('analytics.persistence_tracker', 'PersistenceTracker'),
        ('analytics.regime_detector', 'AdvancedRegimeDetector'),
        ('optimizer.capital_allocator', 'CapitalAllocator'),
    ]
    
    for module_name, class_name in modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"  ✓ {module_name}.{class_name}")
        except Exception as e:
            print(f"  ✗ {module_name}.{class_name}: {e}")
            return False
    
    return True

def test_cpp_engine():
    """Test C++ engine"""
    print("\nTesting C++ engine...")
    try:
        import omniquant_cpp
        
        # Test graph creation
        graph = omniquant_cpp.Graph()
        graph.add_edge("BTC", "ETH", 15.5, 0.001, 10000, "Exchange1")
        graph.add_edge("ETH", "USDT", 2500, 0.001, 50000, "Exchange2")
        graph.add_edge("USDT", "BTC", 0.000025, 0.001, 100000, "Exchange3")
        
        print(f"  ✓ Graph created: {graph.node_count()} nodes, {graph.edge_count()} edges")
        
        # Test cycle detection
        detector = omniquant_cpp.CycleDetector()
        cycles = detector.detect_arbitrage(graph, 10)
        
        print(f"  ✓ Cycle detection works: {len(cycles)} cycles found")
        return True
        
    except ImportError:
        print("  ⚠ C++ engine not available (Python fallback will be used)")
        return True  # Not a critical error
    except Exception as e:
        print(f"  ✗ C++ engine error: {e}")
        return False

def test_monte_carlo():
    """Test Monte Carlo simulation"""
    print("\nTesting Monte Carlo simulator...")
    try:
        from simulation.monte_carlo import MonteCarloSimulator
        
        mc = MonteCarloSimulator(n_simulations=100)
        results = mc.simulate_opportunity(
            base_return=0.005,
            path_length=3,
            liquidities=[10000, 50000, 100000],
            volatilities=[0.01, 0.01, 0.01],
            base_fees=[0.001, 0.001, 0.001],
            capital=1000
        )
        
        print(f"  ✓ Monte Carlo: mean={results.mean_return:.4f}, std={results.std_return:.4f}")
        return True
    except Exception as e:
        print(f"  ✗ Monte Carlo error: {e}")
        return False

def test_risk_engine():
    """Test risk engine"""
    print("\nTesting risk engine...")
    try:
        from risk.risk_engine import RiskEngine
        
        engine = RiskEngine()
        assessment = engine.assess_risk(
            capital=1000,
            liquidities=[10000, 50000, 100000],
            volatilities=[0.01, 0.01, 0.01],
            path_length=3,
            spreads=[10, 10, 10]
        )
        
        print(f"  ✓ Risk assessment: score={assessment.composite_score:.1f}, level={assessment.risk_level.value}")
        return True
    except Exception as e:
        print(f"  ✗ Risk engine error: {e}")
        return False

def test_api():
    """Test API server"""
    print("\nTesting API server...")
    try:
        import requests
        
        # Try to connect to API
        response = requests.get('http://localhost:8000/health', timeout=2)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ API server responding: {data.get('status')}")
            return True
        else:
            print(f"  ✗ API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("  ⚠ API server not running (start with: python api/main.py)")
        return True  # Not a critical error for tests
    except Exception as e:
        print(f"  ✗ API test error: {e}")
        return False

def main():
    print("=" * 60)
    print("OmniQuant v2 - System Test")
    print("=" * 60 + "\n")
    
    results = {
        'Python Modules': test_imports(),
        'C++ Engine': test_cpp_engine(),
        'Monte Carlo': test_monte_carlo(),
        'Risk Engine': test_risk_engine(),
        'API Server': test_api(),
    }
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {test_name:.<40} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All tests passed! OmniQuant is ready.")
        return 0
    else:
        print("\n✗ Some tests failed. Check errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
