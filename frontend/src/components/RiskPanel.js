import React from 'react';

function RiskPanel({ opportunities }) {
  if (!opportunities || opportunities.length === 0) {
    return (
      <div className="card">
        <h3 className="text-xl font-bold text-cyan-400 mb-4">Risk Overview</h3>
        <p className="text-gray-400 text-sm">No opportunities to analyze</p>
      </div>
    );
  }

  // Calculate aggregate risk metrics
  const avgRiskScore = opportunities.reduce((sum, opp) => sum + opp.risk_score, 0) / opportunities.length;
  const avgConfidence = opportunities.reduce((sum, opp) => sum + opp.confidence, 0) / opportunities.length;
  
  const riskDistribution = {
    'Very Low': 0,
    'Low': 0,
    'Moderate': 0,
    'High': 0,
    'Very High': 0
  };
  
  opportunities.forEach(opp => {
    const level = opp.risk_level || 'Moderate';
    if (riskDistribution.hasOwnProperty(level)) {
      riskDistribution[level]++;
    }
  });

  return (
    <div className="card">
      <h3 className="text-xl font-bold text-cyan-400 mb-4">Risk Overview</h3>
      
      <div className="space-y-4">
        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-gray-400">Portfolio Risk Score</span>
            <span className="font-bold">{avgRiskScore.toFixed(1)}/100</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-green-500 via-yellow-500 to-red-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${avgRiskScore}%` }}
            ></div>
          </div>
        </div>

        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-gray-400">Avg Confidence</span>
            <span className="font-bold text-cyan-400">{avgConfidence.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div 
              className="bg-cyan-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${avgConfidence}%` }}
            ></div>
          </div>
        </div>

        <div className="pt-4 border-t border-gray-700">
          <div className="text-sm text-gray-400 mb-3">Risk Distribution</div>
          <div className="space-y-2">
            {Object.entries(riskDistribution).map(([level, count]) => (
              count > 0 && (
                <div key={level} className="flex justify-between items-center text-sm">
                  <span className={`badge ${getRiskColorClass(level)}`}>
                    {level}
                  </span>
                  <span className="text-gray-400">{count} opp{count !== 1 ? 's' : ''}</span>
                </div>
              )
            ))}
          </div>
        </div>

        <div className="pt-4 border-t border-gray-700">
          <div className="text-sm text-gray-400 mb-2">Risk Factors</div>
          <div className="space-y-2 text-xs">
            <RiskFactor 
              label="Liquidity"
              level={calculateAvgComponentRisk(opportunities, 'liquidity')}
            />
            <RiskFactor 
              label="Complexity"
              level={calculatePathComplexity(opportunities)}
            />
            <RiskFactor 
              label="Volatility"
              level={calculateAvgComponentRisk(opportunities, 'volatility')}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function RiskFactor({ label, level }) {
  const getColorClass = () => {
    if (level < 30) return 'bg-green-500';
    if (level < 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div>
      <div className="flex justify-between mb-1">
        <span className="text-gray-400">{label}</span>
        <span className="text-gray-300">{level.toFixed(0)}%</span>
      </div>
      <div className="w-full bg-gray-700 rounded-full h-1.5">
        <div 
          className={`${getColorClass()} h-1.5 rounded-full transition-all duration-300`}
          style={{ width: `${level}%` }}
        ></div>
      </div>
    </div>
  );
}

function getRiskColorClass(level) {
  return `risk-${level.toLowerCase().replace(' ', '-')}`;
}

function calculateAvgComponentRisk(opportunities, component) {
  // Placeholder - would extract from risk_components if available
  return Math.random() * 100;
}

function calculatePathComplexity(opportunities) {
  const avgPathLength = opportunities.reduce((sum, opp) => sum + opp.path_length, 0) / opportunities.length;
  // Map path length to risk: 2-hop = low, 5+ hop = high
  return Math.min((avgPathLength - 2) * 25, 100);
}

export default RiskPanel;
