#include "edge_pruner.h"
#include <algorithm>

namespace omniquant {

EdgePruner::EdgePruner() : edges_removed_(0) {
    config_ = PruningConfig();
}

EdgePruner::EdgePruner(const PruningConfig& config) : config_(config), edges_removed_(0) {}

EdgePruner::~EdgePruner() {}

int EdgePruner::prune_edges(Graph& graph) {
    edges_removed_ = 0;
    
    // This is a simplified version - in production, we'd rebuild the graph
    // For now, we'll just count how many edges would be removed
    // Actual implementation would reconstruct the graph without pruned edges
    
    const auto& edges = graph.get_edges();
    int edges_to_remove = 0;
    
    for (const auto& edge : edges) {
        if (should_prune_edge(edge)) {
            edges_to_remove++;
        }
    }
    
    edges_removed_ = edges_to_remove;
    return edges_removed_;
}

bool EdgePruner::should_prune_edge(const Edge& edge) const {
    // Check liquidity
    if (config_.enable_liquidity_pruning && edge.liquidity < config_.min_liquidity) {
        return true;
    }
    
    // Check fee
    if (config_.enable_fee_pruning && edge.fee > config_.max_fee) {
        return true;
    }
    
    // Check rate bounds
    if (config_.enable_rate_pruning) {
        if (edge.rate < config_.min_rate || edge.rate > config_.max_rate) {
            return true;
        }
    }
    
    return false;
}

} // namespace omniquant
