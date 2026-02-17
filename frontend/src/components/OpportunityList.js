import React from 'react';

function OpportunityList({ opportunities, loading }) {
  if (loading) {
    return (
      <div className="card">
        <div className="flex justify-center items-center py-12">
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  if (!opportunities || opportunities.length === 0) {
    return (
      <div className="card text-center py-16">
        <div className="text-4xl mb-3 opacity-60">📡</div>
        <p className="text-gray-500 text-sm">No opportunities detected. Click <span className="text-cyan-400 font-semibold">"Scan Markets"</span> to start.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl sm:text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400 mb-4">
        Detected Opportunities ({opportunities.length})
      </h2>
      
      {/* Summary */}
      {(() => {
        const profitable = opportunities.filter(o => o.is_profitable || o.expected_return > 0).length;
        const nearProf = opportunities.length - profitable;
        return (
          <div className="flex gap-4 text-sm mb-2">
            {profitable > 0 && (
              <span className="bg-green-900/40 text-green-400 px-3 py-1 rounded-full">
                {profitable} Profitable
              </span>
            )}
            {nearProf > 0 && (
              <span className="bg-yellow-900/40 text-yellow-400 px-3 py-1 rounded-full">
                {nearProf} Near-Profitable
              </span>
            )}
          </div>
        );
      })()}
      
      {opportunities.map((opp, index) => (
        <OpportunityCard key={opp.id || index} opportunity={opp} rank={index + 1} />
      ))}
    </div>
  );
}

function OpportunityCard({ opportunity, rank }) {
  const getRiskColorClass = (riskLevel) => {
    const level = (riskLevel || '').toLowerCase().replace(' ', '-');
    return `risk-${level}`;
  };

  const isProfitable = opportunity.is_profitable || opportunity.expected_return > 0;
  const returnPct = (opportunity.expected_return * 100).toFixed(3);
  const returnColor = isProfitable ? 'text-green-400' : 'text-yellow-400';
  const borderColor = isProfitable ? 'border-green-500/30' : 'border-yellow-500/20';

  return (
    <div className={`opportunity-card ${borderColor}`}>
      <div className="flex justify-between items-start mb-3">
        <div className="flex items-center space-x-3">
          <div className={`${isProfitable ? 'bg-gradient-to-br from-emerald-500 to-green-600' : 'bg-gradient-to-br from-amber-500 to-yellow-600'} text-white rounded-full w-8 h-8 flex items-center justify-center font-bold text-sm shadow-lg`}>
            {rank}
          </div>
          <div>
            <div className="path-display font-mono">
              {opportunity.path.join(' → ')}
            </div>
            <div className="text-xs text-gray-400 mt-1">
              {opportunity.path_length} hops •{' '}
              <span className={isProfitable ? 'text-green-400' : 'text-yellow-400'}>
                {isProfitable ? 'Profitable' : 'Near-Profitable'}
              </span>
            </div>
          </div>
        </div>
        <div className="text-right">
          <div className={`text-2xl font-bold ${returnColor}`}>
            {returnPct}%
          </div>
          <div className="text-xs text-gray-400">Expected Return</div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
        <MetricItem label="Confidence" value={`${opportunity.confidence.toFixed(1)}%`} />
        <MetricItem label="Risk Score" value={`${opportunity.risk_score.toFixed(1)}/100`} />
        <MetricItem 
          label="Risk Level" 
          value={opportunity.risk_level}
          className={getRiskColorClass(opportunity.risk_level)}
          isPill
        />
        {opportunity.monte_carlo && (
          <MetricItem 
            label="MC Worst 5%" 
            value={`${(opportunity.monte_carlo.worst_5pct * 100).toFixed(3)}%`} 
          />
        )}
      </div>

      {opportunity.warnings && opportunity.warnings.length > 0 && (
        <div className="bg-yellow-900/20 border border-yellow-600/50 rounded p-2 mt-3">
          <div className="text-xs text-yellow-400">
            {opportunity.warnings.join(' • ')}
          </div>
        </div>
      )}

      {opportunity.monte_carlo && (
        <div className="mt-3 pt-3 border-t border-gray-700/50">
          <div className="text-xs text-gray-500 mb-2 uppercase tracking-wider font-medium">Monte Carlo Results</div>
          <div className="grid grid-cols-3 gap-2 text-xs">
            <div className="bg-gray-800/60 p-2.5 rounded-lg border border-gray-700/40">
              <div className="text-gray-500 text-[0.65rem] uppercase">Mean</div>
              <div className="text-cyan-400 font-semibold mt-0.5">
                {(opportunity.monte_carlo.mean_return * 100).toFixed(3)}%
              </div>
            </div>
            <div className="bg-gray-800/60 p-2.5 rounded-lg border border-gray-700/40">
              <div className="text-gray-500 text-[0.65rem] uppercase">Std Dev</div>
              <div className="text-cyan-400 font-semibold mt-0.5">
                {(opportunity.monte_carlo.std_return * 100).toFixed(3)}%
              </div>
            </div>
            <div className="bg-gray-800/60 p-2.5 rounded-lg border border-gray-700/40">
              <div className="text-gray-500 text-[0.65rem] uppercase">Sharpe</div>
              <div className="text-cyan-400 font-semibold mt-0.5">
                {opportunity.monte_carlo.sharpe_ratio.toFixed(2)}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function MetricItem({ label, value, className = '', isPill = false }) {
  return (
    <div>
      <div className="text-xs text-gray-400">{label}</div>
      {isPill ? (
        <span className={`risk-pill ${className} mt-1`}>{value}</span>
      ) : (
        <div className={`font-semibold ${className}`}>{value}</div>
      )}
    </div>
  );
}

export default OpportunityList;
