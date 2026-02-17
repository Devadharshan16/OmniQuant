# 🚀 Quick Start Guide - OmniQuant v2

## Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **CMake 3.15+** (optional, for C++ engine)
- **C++ Compiler** (MSVC on Windows, GCC/Clang on Linux/Mac)

---

## Installation

### Windows

```powershell
# Run build script
.\build.ps1
```

### Linux/Mac

```bash
# Install dependencies
pip install -r requirements.txt

# Build C++ engine (optional)
mkdir build && cd build
cmake ..
cmake --build . --config Release
cd ..

# Setup frontend
cd frontend
npm install
cd ..
```

---

## Running OmniQuant

### Start Backend

```bash
python api/main.py
```

Backend will run on `http://localhost:8000`

### Start Frontend

```bash
cd frontend
npm start
```

Frontend will run on `http://localhost:3000`

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (React)                     │
│               http://localhost:3000                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│                  Backend (FastAPI)                       │
│               http://localhost:8000                      │
│                                                           │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────┐ │
│  │   Arbitrage  │  │   Risk Engine │  │   Monte Carlo│ │
│  │   Detection  │  │               │  │   Simulator  │ │
│  └──────────────┘  └───────────────┘  └──────────────┘ │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│            C++ Core Engine (Bellman-Ford)                │
│          Log-space negative cycle detection              │
└─────────────────────────────────────────────────────────┘
```

---

## API Endpoints

### GET `/`
Health check and version info

### POST `/scan`
Detect arbitrage opportunities

**Request Body:**
```json
{
  "market_data": [
    {
      "from_token": "BTC",
      "to_token": "ETH",
      "rate": 15.5,
      "fee": 0.001,
      "liquidity": 10000,
      "exchange": "Exchange1"
    }
  ],
  "capital": 1000.0,
  "max_cycles": 10,
  "run_monte_carlo": true,
  "mc_simulations": 500
}
```

### GET `/opportunities`
Get all detected opportunities

### GET `/metrics`
System performance metrics

### POST `/allocate`
Optimize capital allocation across opportunities

### GET `/stress-test/{opportunity_id}`
Run stress tests on specific opportunity

---

## Features Implemented

✅ **Graph-theoretic arbitrage detection** (Bellman-Ford)
✅ **Log-space transformation** for multiplicative arbitrage
✅ **Monte Carlo execution simulation** (1000+ runs)
✅ **Advanced risk engine** (liquidity, complexity, volatility)
✅ **Stress testing** (7 scenarios)
✅ **Latency sensitivity analysis** (half-life computation)
✅ **Capital allocation optimizer** (greedy + linear programming)
✅ **Opportunity persistence tracking**
✅ **Market regime detection**
✅ **AI explanation layer** (human-readable summaries)
✅ **Real-time dashboard** (React + Tailwind CSS)

---

## Mathematical Models

### Arbitrage Detection

Exchange rate weights:
```
w = -log(R × (1 - fee))
```

Negative cycle in log space = arbitrage opportunity

### Market Impact

Non-linear slippage:
```
impact = k × (volume/liquidity)^α
```
where α > 1 creates convex impact

### Risk Scoring

Composite risk:
```
Risk = w₁×L + w₂×C + w₃×V
```
- L = Liquidity risk
- C = Complexity risk
- V = Volatility risk

---

## Testing

Run example scan:

```bash
curl -X POST http://localhost:8000/scan \
  -H "Content-Type: application/json" \
  -d '{
    "market_data": [
      {"from_token": "BTC", "to_token": "ETH", "rate": 15.5, "fee": 0.001, "liquidity": 10000, "exchange": "Ex1"},
      {"from_token": "ETH", "to_token": "USDT", "rate": 2500, "fee": 0.001, "liquidity": 50000, "exchange": "Ex2"},
      {"from_token": "USDT", "to_token": "BTC", "rate": 0.000025, "fee": 0.001, "liquidity": 100000, "exchange": "Ex3"}
    ],
    "capital": 1000.0
  }'
```

---

## Project Structure

```
OmniQuant/
├── core/               # C++ arbitrage engine
├── bindings/           # pybind11 bridge
├── simulation/         # Market microstructure
├── risk/               # Risk quantification
├── analytics/          # Persistence tracking
├── optimizer/          # Capital allocation
├── api/                # FastAPI backend
├── frontend/           # React dashboard
├── tests/              # Unit tests
└── README.md
```

---

## Troubleshooting

### C++ Build Fails
- Python fallback is automatically used
- System will work without C++ engine (slightly slower)

### Frontend Won't Start
- Check Node.js version: `node --version`
- Clear node_modules: `rm -rf node_modules && npm install`

### Backend Errors
- Check Python version: `python --version`
- Reinstall dependencies: `pip install -r requirements.txt`

---

## Disclaimer

⚠️ **MANDATORY DISCLAIMER**

OmniQuant is a research and educational arbitrage detection simulator.

- All opportunities shown are theoretical
- No trades are executed
- No financial returns are guaranteed
- Not financial advice
- Users are responsible for independent verification

---

## License

MIT License - See LICENSE file

---

## Contact

For hackathon questions or collaboration:
- Email: your-email@example.com
- GitHub: @yourusername
