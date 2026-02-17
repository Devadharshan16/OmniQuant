#include "graph_engine.h"
#include <cmath>
#include <algorithm>

namespace omniquant {

double Edge::get_weight() const {
    // Log-space transformation: w = -log(rate * (1 - fee))
    // Multiplicative arbitrage becomes additive in log space
    double effective_rate = rate * (1.0 - fee);
    if (effective_rate <= 0) return 1e9;  // Invalid rate
    return -std::log(effective_rate);
}

Graph::Graph() {
    nodes_.reserve(100);
    edges_.reserve(1000);
}

Graph::~Graph() {
    clear();
}

int Graph::add_node(const std::string& token) {
    auto it = node_indices_.find(token);
    if (it != node_indices_.end()) {
        return it->second;  // Already exists
    }
    
    int index = static_cast<int>(nodes_.size());
    nodes_.push_back(token);
    node_indices_[token] = index;
    adj_list_.emplace_back();
    
    return index;
}

void Graph::add_edge(const std::string& from_token, 
                     const std::string& to_token,
                     double rate, 
                     double fee,
                     double liquidity,
                     const std::string& exchange) {
    int from_idx = add_node(from_token);
    int to_idx = add_node(to_token);
    
    Edge edge;
    edge.from = from_idx;
    edge.to = to_idx;
    edge.rate = rate;
    edge.fee = fee;
    edge.liquidity = liquidity;
    edge.exchange = exchange;
    
    int edge_idx = static_cast<int>(edges_.size());
    edges_.push_back(edge);
    adj_list_[from_idx].push_back(edge_idx);
}

int Graph::get_node_index(const std::string& token) const {
    auto it = node_indices_.find(token);
    if (it == node_indices_.end()) return -1;
    return it->second;
}

std::string Graph::get_node_name(int index) const {
    if (index < 0 || index >= static_cast<int>(nodes_.size())) {
        return "";
    }
    return nodes_[index];
}

void Graph::clear() {
    nodes_.clear();
    node_indices_.clear();
    edges_.clear();
    adj_list_.clear();
}

} // namespace omniquant
