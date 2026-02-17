#include "cycle_detector.h"
#include <limits>
#include <algorithm>
#include <cmath>
#include <unordered_set>

namespace omniquant {

CycleDetector::CycleDetector() {
    metrics_ = DetectionMetrics{0, 0, 0.0, 0};
}

CycleDetector::~CycleDetector() {}

std::vector<ArbitrageCycle> CycleDetector::detect_arbitrage(const Graph& graph, int max_cycles) {
    auto start_time = std::chrono::high_resolution_clock::now();
    
    std::vector<ArbitrageCycle> cycles;
    metrics_.graph_nodes = graph.node_count();
    metrics_.graph_edges = graph.edge_count();
    
    if (graph.node_count() == 0) {
        return cycles;
    }
    
    std::unordered_set<std::string> found_cycle_keys;
    
    // Try from each node as potential source
    for (int source = 0; source < graph.node_count() && static_cast<int>(cycles.size()) < max_cycles; ++source) {
        std::vector<double> dist(graph.node_count());
        std::vector<int> parent(graph.node_count());
        
        if (bellman_ford(graph, source, dist, parent)) {
            // Negative cycle detected, extract it
            int cycle_node = -1;
            
            // Find node in negative cycle
            const auto& edges = graph.get_edges();
            for (const auto& edge : edges) {
                if (dist[edge.from] + edge.get_weight() < dist[edge.to]) {
                    cycle_node = edge.to;
                    break;
                }
            }
            
            if (cycle_node != -1) {
                ArbitrageCycle cycle = extract_cycle(graph, cycle_node, parent);
                
                // Create unique key for this cycle (sorted path)
                std::vector<std::string> sorted_path = cycle.path;
                std::sort(sorted_path.begin(), sorted_path.end());
                std::string cycle_key;
                for (const auto& token : sorted_path) {
                    cycle_key += token + "|";
                }
                
                // Only add if we haven't seen this cycle before
                if (found_cycle_keys.find(cycle_key) == found_cycle_keys.end()) {
                    cycles.push_back(cycle);
                    found_cycle_keys.insert(cycle_key);
                }
            }
        }
    }
    
    auto end_time = std::chrono::high_resolution_clock::now();
    metrics_.detection_time_ms = std::chrono::duration<double, std::milli>(end_time - start_time).count();
    metrics_.cycles_found = static_cast<int>(cycles.size());
    
    // Set detection time for each cycle
    for (auto& cycle : cycles) {
        cycle.detection_time_ms = metrics_.detection_time_ms / cycles.size();
    }
    
    return cycles;
}

bool CycleDetector::bellman_ford(const Graph& graph, int source, 
                                 std::vector<double>& dist, 
                                 std::vector<int>& parent) {
    int n = graph.node_count();
    const auto& edges = graph.get_edges();
    
    // Initialize distances
    std::fill(dist.begin(), dist.end(), std::numeric_limits<double>::infinity());
    std::fill(parent.begin(), parent.end(), -1);
    dist[source] = 0.0;
    
    // Relax edges |V| - 1 times
    for (int i = 0; i < n - 1; ++i) {
        for (const auto& edge : edges) {
            if (dist[edge.from] != std::numeric_limits<double>::infinity()) {
                double new_dist = dist[edge.from] + edge.get_weight();
                if (new_dist < dist[edge.to]) {
                    dist[edge.to] = new_dist;
                    parent[edge.to] = edge.from;
                }
            }
        }
    }
    
    // Check for negative cycle
    for (const auto& edge : edges) {
        if (dist[edge.from] != std::numeric_limits<double>::infinity()) {
            if (dist[edge.from] + edge.get_weight() < dist[edge.to]) {
                return true;  // Negative cycle exists
            }
        }
    }
    
    return false;  // No negative cycle
}

ArbitrageCycle CycleDetector::extract_cycle(const Graph& graph, int cycle_node, 
                                            const std::vector<int>& parent) {
    ArbitrageCycle cycle;
    
    // Trace back to find cycle start
    std::unordered_set<int> visited;
    int current = cycle_node;
    
    // Move back to ensure we're in the cycle
    for (int i = 0; i < graph.node_count(); ++i) {
        current = parent[current];
    }
    
    // Extract cycle path
    int start = current;
    std::vector<int> node_path;
    
    do {
        node_path.push_back(current);
        current = parent[current];
    } while (current != start && node_path.size() < 100);
    
    node_path.push_back(start);  // Close the cycle
    
    // Reverse to get correct order
    std::reverse(node_path.begin(), node_path.end());
    
    // Convert to token names and find edge indices
    const auto& edges = graph.get_edges();
    for (size_t i = 0; i < node_path.size() - 1; ++i) {
        int from = node_path[i];
        int to = node_path[i + 1];
        
        cycle.path.push_back(graph.get_node_name(from));
        
        // Find edge index
        for (size_t e = 0; e < edges.size(); ++e) {
            if (edges[e].from == from && edges[e].to == to) {
                cycle.edge_indices.push_back(static_cast<int>(e));
                break;
            }
        }
    }
    
    cycle.path.push_back(graph.get_node_name(node_path.back()));
    
    // Calculate profit
    cycle.raw_profit = calculate_profit(graph, cycle.edge_indices);
    cycle.path_length = static_cast<int>(cycle.edge_indices.size());
    
    // Log-space profit (sum of weights should be negative for arbitrage)
    cycle.log_profit = 0.0;
    for (int edge_idx : cycle.edge_indices) {
        cycle.log_profit += edges[edge_idx].get_weight();
    }
    
    return cycle;
}

double CycleDetector::calculate_profit(const Graph& graph, const std::vector<int>& edge_indices) {
    const auto& edges = graph.get_edges();
    double product = 1.0;
    
    for (int edge_idx : edge_indices) {
        const auto& edge = edges[edge_idx];
        double effective_rate = edge.rate * (1.0 - edge.fee);
        product *= effective_rate;
    }
    
    return product - 1.0;  // Return as percentage profit
}

} // namespace omniquant
