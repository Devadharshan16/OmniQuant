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

# Import OmniQuant modules
import sys
sys.path.append('..')

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
    mc_simulations: int = 500


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
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        self.monte_carlo = MonteCarloSimulator(n_simulations=500)
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
    # Simplified: just create mock opportunities for demo
    opportunities = []
    
    # Example: BTC -> ETH -> USDT -> BTC
    if len(request.market_data) >= 3:
        opportunities.append({
            'id': f"opp_{int(time.time()*1000)}_0",
            'path': ['BTC', 'ETH', 'USDT', 'BTC'],
            'raw_profit': 0.0025,
            'expected_return': 0.0025,
            'path_length': 3,
            'detection_time_ms': 15.5
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
