# 🔷 OmniQuant v2

## Quantitative Market Inefficiency Research Platform

⚠️ **MANDATORY LEGAL & ETHICAL DISCLAIMER**

> **OmniQuant is a research and educational arbitrage detection simulator.**
> 
> - All opportunities shown are theoretical and generated under simulated market conditions
> - No trades are executed. No financial returns are guaranteed
> - Users are responsible for independent verification before making financial decisions
> - This is NOT financial advice

---

## 🎯 Overview

OmniQuant v2 is a **graph-theoretic arbitrage detection and execution-simulation research engine** with statistical validation and microstructure modeling.

### Key Features

- 📊 **Multi-hop Arbitrage Detection** - Graph-based negative cycle detection using Bellman-Ford algorithm
- 🧮 **Market Microstructure Simulation** - Level-2 order book modeling with realistic slippage
- 🎲 **Monte Carlo Execution Simulator** - 1000+ simulations per opportunity
- 🛡️ **Advanced Risk Engine** - Liquidity, complexity, and volatility risk scoring
- ⚡ **Latency Sensitivity Analysis** - Half-life computation for opportunity decay
- 💼 **Capital Allocation Optimizer** - Portfolio-level opportunity ranking
- 🧠 **AI Explanation Layer** - Human-readable summaries of complex quant models
- 📈 **Stress Testing Module** - Robustness analysis under market shocks

---

## 🏗️ Architecture

```
Market Data (API/Simulated)
           ↓
   C++ Arbitrage Core
    (Bellman-Ford)
           ↓
   Python Bridge (pybind11)
           ↓
  Profit & Risk Simulator
           ↓
  AI Explanation Layer
           ↓
Web Dashboard (FastAPI + React)
```

---

## 📐 Mathematical Model

### Log-Space Arbitrage Detection

Exchange rates are converted to additive space for cycle detection:

```
w = -log(R × (1 - fee))
```

Where:
- `R` = exchange rate
- `fee` = exchange fee percentage

Multiplicative arbitrage becomes additive in log space, enabling Bellman-Ford negative cycle detection.

### Market Impact Function

Nonlinear slippage modeling:

```
impact = k × (volume/liquidity)^α
```

Where `α > 1` creates convex impact (institutional-grade modeling).

### Risk Scoring

```
Risk = w₁L + w₂C + w₃V
```

- `L` = Liquidity risk
- `C` = Complexity risk (path length)
- `V` = Volatility exposure

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- C++17 compiler (MSVC/GCC/Clang)
- CMake 3.15+
- Node.js 16+ (for frontend)

### Installation

```powershell
# Clone repository
git clone https://github.com/yourusername/OmniQuant.git
cd OmniQuant

# Build C++ core
mkdir build
cd build
cmake ..
cmake --build . --config Release

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
```

### Running

```powershell
# Start backend API
python api/main.py

# Start frontend (separate terminal)
cd frontend
npm run dev
```

Access dashboard at `http://localhost:3000`

---

## 📁 Project Structure

```
OmniQuant/
│
├── core/               # C++ arbitrage detection engine
│   ├── graph_engine.cpp
│   ├── cycle_detector.cpp
│   └── edge_pruner.cpp
│
├── bindings/           # pybind11 Python-C++ bridge
│   └── py_bindings.cpp
│
├── simulation/         # Market microstructure modeling
│   ├── order_book.py
│   ├── slippage_model.py
│   ├── impact_model.py
│   └── monte_carlo.py
│
├── risk/               # Risk quantification
│   ├── risk_engine.py
│   └── stress_test.py
│
├── optimizer/          # Capital allocation
│   └── capital_allocator.py
│
├── analytics/          # Tracking and metrics
│   ├── persistence_tracker.py
│   └── regime_detector.py
│
├── api/                # FastAPI backend
│   └── main.py
│
├── frontend/           # React dashboard
│   ├── src/
│   └── public/
│
└── tests/              # Unit tests
```

---

## 🔬 Simulation Assumptions

1. **Order Book Depth**: Top 5 bid/ask levels simulated
2. **Latency**: 0-200ms delay scenarios tested
3. **Slippage**: Nonlinear impact based on liquidity depth
4. **Fees**: Exchange-specific trading and withdrawal fees
5. **Capital Constraints**: Liquidity-limited execution

---

## 📊 Risk Methodology

### Risk Components

1. **Liquidity Risk** - Volume consumed vs. available depth
2. **Complexity Risk** - Path length penalty (longer = riskier)
3. **Volatility Risk** - Short-window price variance
4. **Execution Uncertainty** - Latency sensitivity

### Confidence Metric

```
Confidence = 1 - P(negative return | Monte Carlo)
```

Based on 1000+ execution simulations.

---

## 🧪 Stress Testing

Simulated market shocks:
- ±1% uniform price movement
- 30% liquidity reduction
- Fee increases
- Latency spikes

**Robustness Score**: % of opportunities surviving stress scenarios

---

## ⚠️ Known Limitations

1. Order book data is simulated or delayed (public APIs)
2. Does not account for:
   - Withdrawal processing time
   - Network congestion
   - Exchange KYC/limits
   - Regulatory constraints
3. Assumes atomic multi-hop execution (unrealistic)
4. No real capital deployment capability

---

## 🔮 Future Work

1. **Real-time WebSocket Integration**
   - Live order book streaming
   - Sub-millisecond latency tracking

2. **Machine Learning Layer**
   - Opportunity persistence prediction
   - Regime classification improvements

3. **Blockchain Integration**
   - DEX arbitrage detection
   - MEV opportunity tracking

4. **Execution Interface** (Research Only)
   - Paper trading simulation
   - Historical backtest framework

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

---

## 🏆 Built For

**MIT/IIT Hackathon - Quantitative Finance Track**

This project demonstrates:
- Advanced graph algorithms
- Financial mathematics
- Systems engineering
- Full-stack development
- Statistical rigor

---

## 👥 Team

[Your Team Name]
- [Member 1] - C++ Core Engine
- [Member 2] - Python Simulation Layer
- [Member 3] - Frontend & API
- [Member 4] - Risk & Analytics

---

## 📞 Contact

For questions or research collaboration:
- Email: your-email@example.com
- GitHub: [@yourusername](https://github.com/yourusername)

---

**Remember: This is a research and educational tool. Always perform independent verification before making financial decisions.**
