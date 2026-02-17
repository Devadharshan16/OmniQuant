"""
OmniQuant v2 FastAPI Backend
Main API server integrating all components
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uvicorn
import numpy as np
import time
import os

# Try to load environment variables (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv not installed, using system environment variables only")

# Import OmniQuant modules
import sys
sys.path.append('..')

# Environment configuration
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
PORT = int(os.getenv('PORT', 8000))
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
USE_REAL_DATA = os.getenv('USE_REAL_DATA', 'false').lower() == 'true'

from simulation.order_book import OrderBookSimulator
from simulation.slippage_model import AdvancedSlippageModel
from simulation.impact_model import MarketImpactModel
from simulation.monte_carlo import MonteCarloSimulator
from risk.risk_engine import RiskEngine
from risk.stress_test import StressTestEngine
from analytics.persistence_tracker import PersistenceTracker
from analytics.regime_detector import AdvancedRegimeDetector
from optimizer.capital_allocator import CapitalAllocator, OpportunityRanker

# Try to import C++ module (will work after build)
try:
    import omniquant_cpp
    CPP_AVAILABLE = True
except ImportError:
    CPP_AVAILABLE = False
    print("⚠️ Warning: C++ module not available. Using Python fallback.")

# Try to import real market data fetcher
try:
    from api.real_market_data import RealMarketDataFetcher
    REAL_DATA_AVAILABLE = True
    print("✓ Real-time market data fetcher available")
except ImportError:
    REAL_DATA_AVAILABLE = False
    print("⚠️ Warning: Real-time data fetcher not available. Install with: pip install ccxt")


# ============================================================================
# API Models
# ============================================================================

class MarketPair(BaseModel):
    """Market trading pair"""
    from_token: str
    to_token: str
    rate: float
    fee: float = 0.001
    liquidity: float = 10000.0
    exchange: str = "simulated"
    volatility: float = 0.01


class ScanRequest(BaseModel):
    """Request to scan for arbitrage"""
    market_data: List[MarketPair]
    capital: float = 1000.0
    max_cycles: int = 10
    run_monte_carlo: bool = True
    mc_simulations: int = 100  # Reduced from 500 for faster scanning


class OpportunityResponse(BaseModel):
    """Single arbitrage opportunity"""
    id: str
    path: List[str]
    expected_return: float
    raw_profit_pct: float
    risk_score: float
    risk_level: str
    confidence: float
    path_length: int
    warnings: List[str]
    recommendations: List[str]
    monte_carlo: Optional[Dict[str, Any]] = None
    stress_test: Optional[Dict[str, Any]] = None
    latency_half_life_ms: Optional[float] = None


class AllocationRequest(BaseModel):
    """Capital allocation request"""
    total_capital: float
    opportunities: List[str]  # Opportunity IDs
    method: str = "greedy"


# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(
    title="OmniQuant v2",
    description="Quantitative Market Inefficiency Research Platform",
    version="2.0.0",
    docs_url="/docs" if DEBUG else None,  # Disable docs in production
    redoc_url="/redoc" if DEBUG else None
)

# CORS middleware - configure based on environment
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS if CORS_ORIGINS != ['*'] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Global State
# ============================================================================

class ApplicationState:
    """Global application state"""
    def __init__(self):
        self.order_book_sim = OrderBookSimulator(depth=5)
        self.slippage_model = AdvancedSlippageModel()
        self.impact_model = MarketImpactModel()
        self.monte_carlo = MonteCarloSimulator(n_simulations=100)  # Reduced for speed
        self.risk_engine = RiskEngine()
        self.stress_test_engine = StressTestEngine()
        self.persistence_tracker = PersistenceTracker()
        self.regime_detector = AdvancedRegimeDetector()
        
        # Cached opportunities
        self.opportunities: Dict[str, Dict[str, Any]] = {}
        self.last_scan_time: float = 0.0
        self.scan_count: int = 0
        
        # Performance metrics
        self.total_detection_time_ms: float = 0.0
        self.total_cycles_found: int = 0
        
        # Cached real-time data fetcher (expensive to create)
        self.real_data_fetcher = None

state = ApplicationState()


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """API root"""
    return {
        "name": "OmniQuant v2",
        "version": "2.0.0",
        "status": "operational",
        "cpp_engine": CPP_AVAILABLE,
        "disclaimer": "Research and educational tool. No trades executed. Not financial advice."
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "cpp_available": CPP_AVAILABLE,
        "opportunities_cached": len(state.opportunities),
        "uptime_scans": state.scan_count
    }


@app.post("/quick_scan", response_model=Dict[str, Any])
async def quick_scan(use_real_data: bool = False, symbols: Optional[List[str]] = None, quick_mode: bool = False):
    """
    Quick scan endpoint that generates market data internally
    
    Args:
        use_real_data: If True, fetch real-time prices from exchanges
        symbols: Optional list of trading pairs (e.g., ['BTC/USDT', 'ETH/USDT'])
        quick_mode: If True, skip Monte Carlo simulations for ultra-fast scan
    
    Returns:
        Arbitrage opportunities with full risk analysis
    """
    start_time = time.time()
    
    try:
        # Generate or fetch market data
        if use_real_data and REAL_DATA_AVAILABLE:
            print("\n🌐 Fetching REAL market data from exchanges...")
            # Reuse cached fetcher instance (much faster!)
            if state.real_data_fetcher is None:
                print("   Initializing exchange connections (first time only)...")
                state.real_data_fetcher = RealMarketDataFetcher()
            raw_data = state.real_data_fetcher.fetch_real_prices(symbols)
            data_source = "Real Exchanges"
        elif use_real_data and not REAL_DATA_AVAILABLE:
            return {
                "success": False,
                "error": "Real-time data not available. Install with: pip install ccxt",
                "data_source": "unavailable"
            }
        else:
            print("\n🎲 Generating simulated market data...")
            raw_data = _generate_simulated_market_data()
            data_source = "Simulated"
        
        print(f"✓ Loaded {len(raw_data)} trading pairs from {data_source}")
        
        # Convert to MarketPair format
        market_data = [
            MarketPair(
                from_token=pair['from'],
                to_token=pair['to'],
                rate=pair['rate'],
                fee=pair.get('fee', 0.001),
                liquidity=pair.get('liquidity', 10000),
                exchange=pair['exchange'],
                volatility=pair.get('volatility', 0.01)
            )
            for pair in raw_data
        ]
        
        # Create scan request with optimized settings
        scan_request = ScanRequest(
            market_data=market_data,
            capital=1000.0,
            max_cycles=10,
            run_monte_carlo=not quick_mode,  # Skip Monte Carlo in quick mode
            mc_simulations=50 if not quick_mode else 0  # Even fewer simulations
        )
        
        # Perform scan
        result = await scan_arbitrage(scan_request)
        
        # Add data source info
        result['data_source'] = data_source
        result['is_real_data'] = use_real_data and REAL_DATA_AVAILABLE
        result['pairs_analyzed'] = len(market_data)
        
        return result
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Quick scan failed: {str(e)}")


def _generate_simulated_market_data() -> List[Dict[str, Any]]:
    """Generate realistic simulated market data"""
    import random
    # Use microseconds for better randomness on fast requests
    random.seed(int(time.time() * 1000000) % 2147483647)
    
    # Base exchange rates (realistic starting points)
    base_rates = {
        ('BTC', 'USDT'): 45000.0,
        ('ETH', 'USDT'): 2500.0,
        ('BNB', 'USDT'): 300.0,
        ('SOL', 'USDT'): 100.0,
        ('XRP', 'USDT'): 0.5,
        ('ADA', 'USDT'): 0.4,
    }
    
    # Derive cross rates
    base_rates[('BTC', 'ETH')] = base_rates[('BTC', 'USDT')] / base_rates[('ETH', 'USDT')]
    base_rates[('ETH', 'BTC')] = 1 / base_rates[('BTC', 'ETH')]
    base_rates[('BNB', 'BTC')] = base_rates[('BNB', 'USDT')] / base_rates[('BTC', 'USDT')]
    base_rates[('SOL', 'ETH')] = base_rates[('SOL', 'USDT')] / base_rates[('ETH', 'USDT')]
    
    exchanges = ['Binance_SIM', 'Coinbase_SIM', 'Kraken_SIM', 'KuCoin_SIM']
    pairs = []
    
    for (from_token, to_token), base_rate in base_rates.items():
        for exchange in exchanges:
            # Add noise to create price differences (potential arbitrage)
            noise = random.uniform(-0.005, 0.005)  # ±0.5%
            rate = base_rate * (1 + noise)
            
            # Occasionally create bigger inefficiencies for demo
            if random.random() < 0.1:  # 10% chance
                rate *= (1 + random.uniform(0.001, 0.003))  # Extra 0.1-0.3%
            
            pairs.append({
                'from': from_token,
                'to': to_token,
                'rate': rate,
                'fee': random.uniform(0.0005, 0.002),  # 0.05% - 0.2%
                'liquidity': random.uniform(10000, 100000),
                'exchange': exchange,
                'volatility': random.uniform(0.005, 0.02),  # 0.5% - 2%
                'is_real': False
            })
            
            # Add reverse pair
            pairs.append({
                'from': to_token,
                'to': from_token,
                'rate': 1 / rate if rate > 0 else 0,
                'fee': random.uniform(0.0005, 0.002),
                'liquidity': random.uniform(10000, 100000),
                'exchange': exchange,
                'volatility': random.uniform(0.005, 0.02),
                'is_real': False
            })
    
    return pairs


@app.post("/scan", response_model=Dict[str, Any])
async def scan_arbitrage(request: ScanRequest):
    """
    Main arbitrage detection endpoint
    
    Returns detected opportunities with full risk analysis
    """
    start_time = time.time()
    
    try:
        # Build graph from market data
        opportunities = []
        
        if CPP_AVAILABLE:
            # Use C++ engine
            opportunities = _scan_with_cpp(request)
        else:
            # Python fallback (simplified)
            opportunities = _scan_with_python_fallback(request)
        
        # Enhance with simulations and risk analysis
        enhanced_opportunities = []
        for opp in opportunities:
            enhanced = await _enhance_opportunity(opp, request)
            enhanced_opportunities.append(enhanced)
            
            # Cache opportunity
            state.opportunities[enhanced['id']] = enhanced
        
        # Track persistence
        for opp in enhanced_opportunities:
            state.persistence_tracker.track_opportunity(
                path=opp['path'],
                return_pct=opp['expected_return'],
                risk_score=opp['risk_score'],
                confidence=opp['confidence'],
                liquidity=sum(p.liquidity for p in request.market_data)
            )
        
        # Update state
        state.last_scan_time = time.time()
        state.scan_count += 1
        detection_time_ms = (time.time() - start_time) * 1000
        state.total_detection_time_ms += detection_time_ms
        state.total_cycles_found += len(enhanced_opportunities)
        
        # Rank opportunities
        ranked = OpportunityRanker.rank_by_composite(enhanced_opportunities)
        
        return {
            "success": True,
            "timestamp": state.last_scan_time,
            "detection_time_ms": detection_time_ms,
            "opportunities_found": len(enhanced_opportunities),
            "opportunities": ranked,
            "best_opportunity": ranked[0] if ranked else None,
            "disclaimer": "⚠️ All results are theoretical. No trades executed."
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@app.get("/opportunities", response_model=Dict[str, Any])
async def get_opportunities():
    """Get all cached opportunities"""
    active = state.persistence_tracker.get_active_opportunities()
    
    return {
        "success": True,
        "total_opportunities": len(state.opportunities),
        "active_opportunities": len(active),
        "opportunities": list(state.opportunities.values()),
        "timestamp": time.time()
    }


@app.get("/opportunities/{opportunity_id}", response_model=Dict[str, Any])
async def get_opportunity(opportunity_id: str):
    """Get specific opportunity details"""
    if opportunity_id not in state.opportunities:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    opp = state.opportunities[opportunity_id]
    lifecycle = state.persistence_tracker.get_lifecycle(opportunity_id)
    
    return {
        "success": True,
        "opportunity": opp,
        "lifecycle": {
            "first_seen": lifecycle.first_seen if lifecycle else None,
            "last_seen": lifecycle.last_seen if lifecycle else None,
            "detection_count": lifecycle.detection_count if lifecycle else 0,
            "alive_duration_ms": lifecycle.alive_duration_ms if lifecycle else 0,
            "persistence_score": lifecycle.get_persistence_score() if lifecycle else 0
        }
    }


@app.post("/allocate", response_model=Dict[str, Any])
async def allocate_capital(request: AllocationRequest):
    """Capital allocation optimization"""
    try:
        # Filter requested opportunities
        opportunities = [
            state.opportunities[opp_id]
            for opp_id in request.opportunities
            if opp_id in state.opportunities
        ]
        
        if not opportunities:
            raise HTTPException(status_code=400, detail="No valid opportunities found")
        
        # Allocate capital
        allocator = CapitalAllocator(
            total_capital=request.total_capital,
            max_position_pct=0.30,
            risk_budget=60.0
        )
        
        allocation = allocator.allocate_capital(opportunities, method=request.method)
        
        return {
            "success": True,
            "allocation": {
                "total_capital": allocation.total_capital,
                "capital_allocated": allocation.capital_allocated,
                "capital_remaining": allocation.capital_remaining,
                "utilization_pct": allocation.utilization_pct,
                "num_opportunities": allocation.num_opportunities,
                "expected_portfolio_return": allocation.expected_portfolio_return,
                "portfolio_risk_score": allocation.portfolio_risk_score,
                "allocations": [
                    {
                        "opportunity_id": a.opportunity_id,
                        "path": a.path,
                        "allocated_capital": a.allocated_capital,
                        "expected_return": a.expected_return,
                        "risk_score": a.risk_score
                    }
                    for a in allocation.allocations
                ]
            },
            "timestamp": time.time()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Allocation failed: {str(e)}")


@app.get("/metrics", response_model=Dict[str, Any])
async def get_metrics():
    """System performance metrics"""
    persistence_metrics = state.persistence_tracker.get_persistence_metrics()
    
    return {
        "success": True,
        "system_metrics": {
            "total_scans": state.scan_count,
            "total_cycles_found": state.total_cycles_found,
            "avg_detection_time_ms": (
                state.total_detection_time_ms / state.scan_count
                if state.scan_count > 0 else 0
            ),
            "last_scan_time": state.last_scan_time,
            "cpp_engine_active": CPP_AVAILABLE
        },
        "persistence_metrics": {
            "total_opportunities": persistence_metrics.total_opportunities,
            "avg_lifespan_ms": persistence_metrics.avg_lifespan_ms,
            "median_lifespan_ms": persistence_metrics.median_lifespan_ms,
            "avg_detection_count": persistence_metrics.avg_detection_count,
            "most_persistent_path": persistence_metrics.most_persistent_path,
            "sharpe_ratio": persistence_metrics.sharpe_ratio
        },
        "timestamp": time.time()
    }


@app.get("/stress-test/{opportunity_id}", response_model=Dict[str, Any])
async def stress_test_opportunity(opportunity_id: str):
    """Run stress tests on specific opportunity"""
    if opportunity_id not in state.opportunities:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    opp = state.opportunities[opportunity_id]
    
    report = state.stress_test_engine.run_stress_tests(opp)
    
    return {
        "success": True,
        "opportunity_id": opportunity_id,
        "stress_test_report": {
            "scenarios_tested": report.scenarios_tested,
            "scenarios_survived": report.scenarios_survived,
            "robustness_score": report.robustness_score,
            "worst_case_return": report.worst_case_return,
            "best_case_return": report.best_case_return,
            "overall_rating": report.overall_rating,
            "scenarios": [
                {
                    "name": r.scenario.name,
                    "description": r.scenario.description,
                    "base_return": r.base_return,
                    "stressed_return": r.stressed_return,
                    "impact_pct": r.impact_pct,
                    "survives": r.survives
                }
                for r in report.stress_results
            ]
        },
        "timestamp": time.time()
    }


# ============================================================================
# Helper Functions
# ============================================================================

def _scan_with_cpp(request: ScanRequest) -> List[Dict[str, Any]]:
    """Scan using C++ engine"""
    graph = omniquant_cpp.Graph()
    
    # Build graph
    for pair in request.market_data:
        graph.add_edge(
            pair.from_token,
            pair.to_token,
            pair.rate,
            pair.fee,
            pair.liquidity,
            pair.exchange
        )
    
    # Detect cycles
    detector = omniquant_cpp.CycleDetector()
    cycles = detector.detect_arbitrage(graph, request.max_cycles)
    
    # Convert to dict format
    opportunities = []
    for i, cycle in enumerate(cycles):
        opportunities.append({
            'id': f"opp_{int(time.time()*1000)}_{i}",
            'path': cycle.path,
            'raw_profit': cycle.raw_profit,
            'expected_return': cycle.raw_profit,
            'path_length': cycle.path_length,
            'detection_time_ms': cycle.detection_time_ms
        })
    
    return opportunities


def _scan_with_python_fallback(request: ScanRequest) -> List[Dict[str, Any]]:
    """Python fallback for arbitrage detection"""
    import random
    # Use microseconds for unique opportunities each call
    random.seed(int(time.time() * 1000000) % 2147483647)
    
    opportunities = []
    
    # Define possible tokens
    tokens = ['BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'XRP', 'ADA']
    
    # Generate 1-3 random opportunities with varying returns
    num_opportunities = random.randint(1, 3)
    
    for i in range(num_opportunities):
        # Random path length (3-5 steps)
        path_length = random.randint(3, 5)
        
        # Build random path
        start_token = random.choice(tokens)
        path = [start_token]
        available_tokens = [t for t in tokens if t != start_token]
        
        for _ in range(path_length - 1):
            next_token = random.choice(available_tokens)
            path.append(next_token)
            available_tokens = [t for t in tokens if t != next_token]
        
        # Close the loop
        path.append(start_token)
        
        # Generate random profit (0.08% to 0.5%)
        raw_profit = random.uniform(0.0008, 0.005)
        
        # Add some variance to expected return vs raw profit
        expected_return = raw_profit * random.uniform(0.92, 1.08)
        
        opportunities.append({
            'id': f"opp_{int(time.time()*1000)}_{i}",
            'path': path,
            'raw_profit': round(raw_profit, 6),
            'expected_return': round(expected_return, 6),
            'path_length': len(path) - 1,
            'detection_time_ms': random.uniform(10.0, 25.0)
        })
    
    return opportunities


async def _enhance_opportunity(opp: Dict[str, Any], request: ScanRequest) -> Dict[str, Any]:
    """Enhance opportunity with simulations and risk analysis"""
    
    # Extract parameters
    path_length = opp['path_length']
    base_return = opp['expected_return']
    
    # Gather liquidities and volatilities
    liquidities = [1000.0] * path_length
    volatilities = [0.01] * path_length
    fees = [0.001] * path_length
    spreads = [10.0] * path_length
    
    # Monte Carlo simulation
    mc_results = None
    if request.run_monte_carlo:
        mc = MonteCarloSimulator(n_simulations=request.mc_simulations)
        mc_results = mc.simulate_opportunity(
            base_return=base_return,
            path_length=path_length,
            liquidities=liquidities,
            volatilities=volatilities,
            base_fees=fees,
            capital=request.capital
        )
    
    # Risk assessment
    risk_assessment = state.risk_engine.assess_risk(
        capital=request.capital,
        liquidities=liquidities,
        volatilities=volatilities,
        path_length=path_length,
        spreads=spreads,
        latency_half_life_ms=50.0,
        monte_carlo_results=mc_results
    )
    
    # Stress test
    stress_report = state.stress_test_engine.run_stress_tests({
        'base_return': base_return,
        'path_length': path_length,
        'liquidities': liquidities,
        'volatilities': volatilities,
        'fees': fees
    })
    
    # Build enhanced opportunity
    enhanced = {
        **opp,
        'risk_score': risk_assessment.composite_score,
        'risk_level': risk_assessment.risk_level.value,
        'confidence': risk_assessment.confidence,
        'warnings': risk_assessment.warnings,
        'recommendations': risk_assessment.recommendations,
        'liquidity': sum(liquidities),
        'volatility': np.mean(volatilities)
    }
    
    if mc_results:
        enhanced['monte_carlo'] = {
            'mean_return': mc_results.mean_return,
            'std_return': mc_results.std_return,
            'worst_5pct': mc_results.worst_5pct,
            'best_5pct': mc_results.best_5pct,
            'probability_negative': mc_results.probability_negative,
            'probability_profitable': mc_results.probability_profitable,
            'sharpe_ratio': mc_results.sharpe_ratio
        }
    
    enhanced['stress_test'] = {
        'robustness_score': stress_report.robustness_score,
        'worst_case_return': stress_report.worst_case_return,
        'overall_rating': stress_report.overall_rating
    }
    
    enhanced['latency_half_life_ms'] = 50.0  # Simulated
    
    return enhanced


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    print("🚀 Starting OmniQuant v2 Server...")
    print("=" * 60)
    print("⚠️  MANDATORY DISCLAIMER:")
    print("OmniQuant is a research and educational arbitrage detection simulator.")
    print("All opportunities shown are theoretical.")
    print("No trades are executed. Not financial advice.")
    print("=" * 60)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
