#ifndef OMNIQUANT_CYCLE_DETECTOR_H
#define OMNIQUANT_CYCLE_DETECTOR_H

#include "graph_engine.h"
#include <vector>
#include <string>
#include <chrono>

namespace omniquant {

struct ArbitrageCycle {
    std::vector<std::string> path;      // Token path (e.g., ["BTC", "ETH", "USDT", "BTC"])
    std::vector<int> edge_indices;      // Edge indices used
    double raw_profit;                   // Raw theoretical profit (multiplicative)
    double log_profit;                   // Log-space profit
    int path_length;                     // Number of hops
    double detection_time_ms;            // Detection time in milliseconds
};

struct DetectionMetrics {
    int graph_nodes;
    int graph_edges;
    double detection_time_ms;
    int cycles_found;
};

class CycleDetector {
public:
    CycleDetector();
    ~CycleDetector();
    
    // Main detection function using Bellman-Ford
    std::vector<ArbitrageCycle> detect_arbitrage(const Graph& graph, int max_cycles = 10);
    
    // Get performance metrics
    DetectionMetrics get_metrics() const { return metrics_; }
    
private:
    // Bellman-Ford with negative cycle detection
    bool bellman_ford(const Graph& graph, int source, std::vector<double>& dist, std::vector<int>& parent);
    
    // Extract cycle from parent array
    ArbitrageCycle extract_cycle(const Graph& graph, int cycle_node, const std::vector<int>& parent);
    
    // Calculate actual profit from cycle
    double calculate_profit(const Graph& graph, const std::vector<int>& edge_indices);
    
    DetectionMetrics metrics_;
};

} // namespace omniquant

#endif // OMNIQUANT_CYCLE_DETECTOR_H
