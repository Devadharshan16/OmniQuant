#ifndef OMNIQUANT_GRAPH_ENGINE_H
#define OMNIQUANT_GRAPH_ENGINE_H

#include <vector>
#include <string>
#include <unordered_map>
#include <memory>

namespace omniquant {

struct Edge {
    int from;
    int to;
    double rate;           // Exchange rate
    double fee;            // Fee percentage (0.001 = 0.1%)
    double liquidity;      // Available liquidity
    std::string exchange;  // Exchange name
    
    double get_weight() const;  // Returns -log(rate * (1 - fee))
};

class Graph {
public:
    Graph();
    ~Graph();
    
    // Add node (token)
    int add_node(const std::string& token);
    
    // Add edge (exchange pair)
    void add_edge(const std::string& from_token, 
                  const std::string& to_token,
                  double rate, 
                  double fee,
                  double liquidity,
                  const std::string& exchange);
    
    // Get graph properties
    int node_count() const { return nodes_.size(); }
    int edge_count() const { return edges_.size(); }
    
    // Get node index by token symbol
    int get_node_index(const std::string& token) const;
    std::string get_node_name(int index) const;
    
    // Get edges
    const std::vector<Edge>& get_edges() const { return edges_; }
    const std::vector<std::vector<int>>& get_adjacency_list() const { return adj_list_; }
    
    // Clear graph
    void clear();
    
private:
    std::vector<std::string> nodes_;                          // Token names
    std::unordered_map<std::string, int> node_indices_;       // Token -> index
    std::vector<Edge> edges_;                                  // All edges
    std::vector<std::vector<int>> adj_list_;                  // Adjacency list (node -> edge indices)
};

} // namespace omniquant

#endif // OMNIQUANT_GRAPH_ENGINE_H
