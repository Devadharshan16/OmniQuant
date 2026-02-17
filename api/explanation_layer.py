"""
AI Explanation Layer
Converts quantitative analysis into human-readable explanations
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class Explanation:
    """Structured explanation"""
    summary: str
    detailed_analysis: str
    key_metrics: Dict[str, str]
    risk_summary: str
    recommendation: str
    disclaimer: str


class ExplanationEngine:
    """
    Generates human-readable explanations from quantitative data
    
    NOT financial advice - educational translation of mathematical models
    """
    
    def __init__(self, technical_level: str = "moderate"):
        """
        Args:
            technical_level: 'basic', 'moderate', or 'advanced'
        """
        self.technical_level = technical_level
    
    def explain_opportunity(self, opportunity: Dict[str, Any]) -> Explanation:
        """
        Generate comprehensive explanation for arbitrage opportunity
        
        Args:
            opportunity: Complete opportunity dict with:
                - path, expected_return, risk_score, confidence
                - monte_carlo, stress_test results
        
        Returns:
            Explanation object
        """
        # Generate summary
        summary = self._generate_summary(opportunity)
        
        # Detailed analysis
        detailed = self._generate_detailed_analysis(opportunity)
        
        # Key metrics
        metrics = self._format_key_metrics(opportunity)
        
        # Risk summary
        risk_summary = self._generate_risk_summary(opportunity)
        
        # Recommendation
        recommendation = self._generate_recommendation(opportunity)
        
        # Disclaimer
        disclaimer = self._get_disclaimer()
        
        return Explanation(
            summary=summary,
            detailed_analysis=detailed,
            key_metrics=metrics,
            risk_summary=risk_summary,
            recommendation=recommendation,
            disclaimer=disclaimer
        )
    
    def _generate_summary(self, opp: Dict[str, Any]) -> str:
        """Generate plain-English summary"""
        path_str = " → ".join(opp['path'])
        return_pct = opp['expected_return'] * 100
        confidence = opp['confidence']
        risk_level = opp.get('risk_level', 'moderate')
        
        # Build summary based on technical level
        if self.technical_level == 'basic':
            summary = (
                f"OmniQuant detected a potential pricing difference across the path: {path_str}. "
                f"Under simulated conditions, this may generate approximately {return_pct:.3f}% return. "
                f"Risk level: {risk_level}. Confidence: {confidence:.0f}%."
            )
        
        elif self.technical_level == 'advanced':
            mc_info = ""
            if 'monte_carlo' in opp:
                mc = opp['monte_carlo']
                mc_info = (
                    f" Monte Carlo analysis (n={opp.get('mc_simulations', 1000)}) shows "
                    f"mean return of {mc['mean_return']*100:.3f}% with "
                    f"std dev {mc['std_return']*100:.3f}%. "
                    f"95% CI: [{mc.get('confidence_95_lower', 0)*100:.3f}%, "
                    f"{mc.get('confidence_95_upper', 0)*100:.3f}%]."
                )
            
            summary = (
                f"Multi-hop arbitrage cycle detected: {path_str}. "
                f"Theoretical return: {return_pct:.4f}%.{mc_info} "
                f"Risk score: {opp['risk_score']:.1f}/100. "
                f"Confidence: {confidence:.1f}%."
            )
        
        else:  # moderate
            summary = (
                f"OmniQuant identified a temporary pricing imbalance across {len(opp['path'])-1} exchanges. "
                f"Path: {path_str}. "
                f"Expected return: {return_pct:.3f}%. "
                f"Risk assessment: {risk_level} ({opp['risk_score']:.0f}/100). "
                f"Confidence: {confidence:.0f}%."
            )
        
        return summary
    
    def _generate_detailed_analysis(self, opp: Dict[str, Any]) -> str:
        """Generate detailed explanation"""
        sections = []
        
        # 1. Detection methodology
        det_method = (
            "Detection Methodology:\n"
            "OmniQuant uses graph-theoretic negative cycle detection (Bellman-Ford algorithm) "
            "to identify arbitrage opportunities. Exchange rates are converted to log-space weights, "
            "transforming multiplicative arbitrage into additive cycles."
        )
        sections.append(det_method)
        
        # 2. Execution model
        exec_model = (
            "Execution Simulation:\n"
            "The platform models realistic execution conditions including:\n"
            f"- Market impact based on order book depth\n"
            f"- Non-linear slippage proportional to liquidity utilization\n"
            f"- Latency sensitivity (half-life: {opp.get('latency_half_life_ms', 'N/A')} ms)\n"
            f"- Trading fees compounded across {opp['path_length']} hops"
        )
        sections.append(exec_model)
        
        # 3. Monte Carlo results
        if 'monte_carlo' in opp:
            mc = opp['monte_carlo']
            mc_section = (
                "Statistical Validation:\n"
                f"Monte Carlo simulation with {opp.get('mc_simulations', 1000)} iterations shows:\n"
                f"- Mean return: {mc['mean_return']*100:.3f}%\n"
                f"- Standard deviation: {mc['std_return']*100:.3f}%\n"
                f"- 5th percentile (worst case): {mc['worst_5pct']*100:.3f}%\n"
                f"- 95th percentile (best case): {mc['best_5pct']*100:.3f}%\n"
                f"- Probability of profit: {mc['probability_profitable']*100:.1f}%\n"
                f"- Sharpe ratio: {mc['sharpe_ratio']:.2f}"
            )
            sections.append(mc_section)
        
        # 4. Stress test results
        if 'stress_test' in opp:
            st = opp['stress_test']
            st_section = (
                "Stress Testing:\n"
                f"Robustness score: {st['robustness_score']:.0f}% ({st['overall_rating']})\n"
                f"Worst case scenario return: {st['worst_case_return']*100:.3f}%\n"
                "Stress scenarios include: price shocks, liquidity drops, volatility spikes, "
                "fee increases, and combined market stress."
            )
            sections.append(st_section)
        
        return "\n\n".join(sections)
    
    def _format_key_metrics(self, opp: Dict[str, Any]) -> Dict[str, str]:
        """Format key metrics for display"""
        metrics = {
            "Path": " → ".join(opp['path']),
            "Expected Return": f"{opp['expected_return']*100:.3f}%",
            "Risk Score": f"{opp['risk_score']:.1f}/100",
            "Risk Level": opp.get('risk_level', 'N/A'),
            "Confidence": f"{opp['confidence']:.1f}%",
            "Path Length": str(opp['path_length']),
        }
        
        if 'monte_carlo' in opp:
            mc = opp['monte_carlo']
            metrics["Monte Carlo Mean"] = f"{mc['mean_return']*100:.3f}%"
            metrics["Worst 5% Outcome"] = f"{mc['worst_5pct']*100:.3f}%"
            metrics["Prob. Negative"] = f"{mc['probability_negative']*100:.1f}%"
        
        if 'stress_test' in opp:
            st = opp['stress_test']
            metrics["Stress Robustness"] = f"{st['robustness_score']:.0f}%"
        
        if 'latency_half_life_ms' in opp:
            metrics["Latency Half-Life"] = f"{opp['latency_half_life_ms']:.0f} ms"
        
        return metrics
    
    def _generate_risk_summary(self, opp: Dict[str, Any]) -> str:
        """Generate risk summary"""
        risk_level = opp.get('risk_level', 'moderate')
        risk_score = opp['risk_score']
        warnings = opp.get('warnings', [])
        
        summary_parts = [
            f"Overall Risk Assessment: {risk_level.upper()} ({risk_score:.0f}/100)"
        ]
        
        if warnings:
            summary_parts.append("\nRisk Factors:")
            for warning in warnings:
                summary_parts.append(f"  {warning}")
        
        # Add risk components if available
        if 'risk_components' in opp:
            comp = opp['risk_components']
            summary_parts.append("\nRisk Breakdown:")
            summary_parts.append(f"  - Liquidity Risk: {comp.get('liquidity_risk', 0):.0f}/100")
            summary_parts.append(f"  - Complexity Risk: {comp.get('complexity_risk', 0):.0f}/100")
            summary_parts.append(f"  - Volatility Risk: {comp.get('volatility_risk', 0):.0f}/100")
            summary_parts.append(f"  - Execution Risk: {comp.get('execution_risk', 0):.0f}/100")
        
        return "\n".join(summary_parts)
    
    def _generate_recommendation(self, opp: Dict[str, Any]) -> str:
        """Generate recommendation"""
        risk_score = opp['risk_score']
        confidence = opp['confidence']
        recommendations = opp.get('recommendations', [])
        
        rec_parts = []
        
        # Overall guidance
        if risk_score < 30 and confidence > 70:
            rec_parts.append("This opportunity shows favorable risk-return characteristics.")
        elif risk_score < 50 and confidence > 60:
            rec_parts.append("This opportunity has moderate risk with reasonable confidence.")
        elif risk_score < 70:
            rec_parts.append("This opportunity carries elevated risk. Proceed with caution.")
        else:
            rec_parts.append("This opportunity has high risk. Consider avoiding or reducing exposure.")
        
        # Specific recommendations
        if recommendations:
            rec_parts.append("\nSpecific Recommendations:")
            for rec in recommendations:
                rec_parts.append(f"  - {rec}")
        
        # General guidance
        rec_parts.append(
            "\n\nGeneral Guidance:\n"
            "- Always verify opportunities independently\n"
            "- Start with small position sizes\n"
            "- Monitor execution quality\n"
            "- Consider total portfolio risk"
        )
        
        return "\n".join(rec_parts)
    
    def _get_disclaimer(self) -> str:
        """Get mandatory disclaimer"""
        return (
            "⚠️ MANDATORY DISCLAIMER:\n"
            "OmniQuant is a research and educational arbitrage detection simulator. "
            "All opportunities shown are theoretical and generated under simulated market conditions. "
            "No trades are executed. No financial returns are guaranteed. "
            "Users are responsible for independent verification before making financial decisions. "
            "This is NOT financial advice."
        )
    
    def explain_portfolio_allocation(self, allocation: Dict[str, Any]) -> str:
        """Explain portfolio allocation strategy"""
        total = allocation['total_capital']
        allocated = allocation['capital_allocated']
        util_pct = allocation['utilization_pct']
        port_return = allocation['expected_portfolio_return']
        port_risk = allocation['portfolio_risk_score']
        num_opps = allocation['num_opportunities']
        
        explanation = (
            f"Portfolio Allocation Summary:\n\n"
            f"Total Capital: ${total:,.2f}\n"
            f"Allocated: ${allocated:,.2f} ({util_pct:.1f}%)\n"
            f"Number of Opportunities: {num_opps}\n"
            f"Expected Portfolio Return: {port_return*100:.3f}%\n"
            f"Portfolio Risk Score: {port_risk:.1f}/100\n\n"
            
            "Allocation Strategy:\n"
            "The capital allocator uses a risk-adjusted optimization approach, "
            "maximizing expected returns while respecting:\n"
            "- Total capital constraints\n"
            "- Individual position limits (max 30% per opportunity)\n"
            "- Portfolio risk budget\n"
            "- Liquidity constraints\n\n"
            
            "Each opportunity is ranked by its risk-adjusted return score: "
            "(Expected Return × Confidence) / Risk Score\n\n"
            
            f"{self._get_disclaimer()}"
        )
        
        return explanation


def format_for_display(explanation: Explanation, format_type: str = "text") -> str:
    """
    Format explanation for different display types
    
    Args:
        explanation: Explanation object
        format_type: 'text', 'markdown', or 'html'
    
    Returns:
        Formatted string
    """
    if format_type == "markdown":
        return _format_markdown(explanation)
    elif format_type == "html":
        return _format_html(explanation)
    else:
        return _format_text(explanation)


def _format_text(exp: Explanation) -> str:
    """Plain text format"""
    parts = [
        "=" * 80,
        "OMNIQUANT OPPORTUNITY EXPLANATION",
        "=" * 80,
        "",
        exp.summary,
        "",
        "-" * 80,
        "KEY METRICS",
        "-" * 80,
    ]
    
    for key, value in exp.key_metrics.items():
        parts.append(f"{key:.<30} {value}")
    
    parts.extend([
        "",
        "-" * 80,
        "DETAILED ANALYSIS",
        "-" * 80,
        exp.detailed_analysis,
        "",
        "-" * 80,
        "RISK ASSESSMENT",
        "-" * 80,
        exp.risk_summary,
        "",
        "-" * 80,
        "RECOMMENDATION",
        "-" * 80,
        exp.recommendation,
        "",
        "=" * 80,
        exp.disclaimer,
        "=" * 80
    ])
    
    return "\n".join(parts)


def _format_markdown(exp: Explanation) -> str:
    """Markdown format"""
    parts = [
        "# OmniQuant Opportunity Explanation\n",
        "## Summary\n",
        exp.summary + "\n",
        "## Key Metrics\n",
    ]
    
    for key, value in exp.key_metrics.items():
        parts.append(f"- **{key}**: {value}")
    
    parts.extend([
        "\n## Detailed Analysis\n",
        exp.detailed_analysis + "\n",
        "## Risk Assessment\n",
        exp.risk_summary + "\n",
        "## Recommendation\n",
        exp.recommendation + "\n",
        "---\n",
        f"*{exp.disclaimer}*"
    ])
    
    return "\n".join(parts)


def _format_html(exp: Explanation) -> str:
    """HTML format"""
    return f"""
    <div class="omniquant-explanation">
        <h1>OmniQuant Opportunity Explanation</h1>
        
        <section class="summary">
            <h2>Summary</h2>
            <p>{exp.summary}</p>
        </section>
        
        <section class="metrics">
            <h2>Key Metrics</h2>
            <table>
                {"".join(f"<tr><td><strong>{k}</strong></td><td>{v}</td></tr>" for k, v in exp.key_metrics.items())}
            </table>
        </section>
        
        <section class="analysis">
            <h2>Detailed Analysis</h2>
            <pre>{exp.detailed_analysis}</pre>
        </section>
        
        <section class="risk">
            <h2>Risk Assessment</h2>
            <pre>{exp.risk_summary}</pre>
        </section>
        
        <section class="recommendation">
            <h2>Recommendation</h2>
            <pre>{exp.recommendation}</pre>
        </section>
        
        <footer class="disclaimer">
            <p><strong>{exp.disclaimer}</strong></p>
        </footer>
    </div>
    """
