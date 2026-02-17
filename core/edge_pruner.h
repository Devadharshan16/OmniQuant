#ifndef OMNIQUANT_EDGE_PRUNER_H
#define OMNIQUANT_EDGE_PRUNER_H

#include "graph_engine.h"

namespace omniquant {

struct PruningConfig {
    double min_liquidity = 100.0;        // Minimum liquidity threshold
    double max_fee = 0.05;                // Maximum fee (5%)
    double min_rate = 0.0001;             // Minimum exchange rate
    double max_rate = 1000000.0;          // Maximum exchange rate
    bool enable_liquidity_pruning = true;
    bool enable_fee_pruning = true;
    bool enable_rate_pruning = true;
};

class EdgePruner {
public:
    EdgePruner();
    explicit EdgePruner(const PruningConfig& config);
    ~EdgePruner();
    
    // Prune edges from graph based on criteria
    int prune_edges(Graph& graph);
    
    // Get/Set configuration
    void set_config(const PruningConfig& config) { config_ = config; }
    PruningConfig get_config() const { return config_; }
    
    // Statistics
    int get_edges_removed() const { return edges_removed_; }
    
private:
    bool should_prune_edge(const Edge& edge) const;
    
    PruningConfig config_;
    int edges_removed_;
};

} // namespace omniquant

#endif // OMNIQUANT_EDGE_PRUNER_H
