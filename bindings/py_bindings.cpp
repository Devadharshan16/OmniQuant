#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include "../core/graph_engine.h"
#include "../core/cycle_detector.h"
#include "../core/edge_pruner.h"

namespace py = pybind11;
using namespace omniquant;

PYBIND11_MODULE(omniquant_cpp, m) {
    m.doc() = "OmniQuant C++ Core - Arbitrage Detection Engine";
    
    // Edge struct
    py::class_<Edge>(m, "Edge")
        .def(py::init<>())
        .def_readwrite("from", &Edge::from)
        .def_readwrite("to", &Edge::to)
        .def_readwrite("rate", &Edge::rate)
        .def_readwrite("fee", &Edge::fee)
        .def_readwrite("liquidity", &Edge::liquidity)
        .def_readwrite("exchange", &Edge::exchange)
        .def("get_weight", &Edge::get_weight);
    
    // Graph class
    py::class_<Graph>(m, "Graph")
        .def(py::init<>())
        .def("add_node", &Graph::add_node)
        .def("add_edge", &Graph::add_edge)
        .def("node_count", &Graph::node_count)
        .def("edge_count", &Graph::edge_count)
        .def("get_node_index", &Graph::get_node_index)
        .def("get_node_name", &Graph::get_node_name)
        .def("get_edges", &Graph::get_edges, py::return_value_policy::reference)
        .def("clear", &Graph::clear);
    
    // ArbitrageCycle struct
    py::class_<ArbitrageCycle>(m, "ArbitrageCycle")
        .def(py::init<>())
        .def_readwrite("path", &ArbitrageCycle::path)
        .def_readwrite("edge_indices", &ArbitrageCycle::edge_indices)
        .def_readwrite("raw_profit", &ArbitrageCycle::raw_profit)
        .def_readwrite("log_profit", &ArbitrageCycle::log_profit)
        .def_readwrite("path_length", &ArbitrageCycle::path_length)
        .def_readwrite("detection_time_ms", &ArbitrageCycle::detection_time_ms);
    
    // DetectionMetrics struct
    py::class_<DetectionMetrics>(m, "DetectionMetrics")
        .def(py::init<>())
        .def_readwrite("graph_nodes", &DetectionMetrics::graph_nodes)
        .def_readwrite("graph_edges", &DetectionMetrics::graph_edges)
        .def_readwrite("detection_time_ms", &DetectionMetrics::detection_time_ms)
        .def_readwrite("cycles_found", &DetectionMetrics::cycles_found);
    
    // CycleDetector class
    py::class_<CycleDetector>(m, "CycleDetector")
        .def(py::init<>())
        .def("detect_arbitrage", &CycleDetector::detect_arbitrage, 
             py::arg("graph"), py::arg("max_cycles") = 10)
        .def("get_metrics", &CycleDetector::get_metrics);
    
    // PruningConfig struct
    py::class_<PruningConfig>(m, "PruningConfig")
        .def(py::init<>())
        .def_readwrite("min_liquidity", &PruningConfig::min_liquidity)
        .def_readwrite("max_fee", &PruningConfig::max_fee)
        .def_readwrite("min_rate", &PruningConfig::min_rate)
        .def_readwrite("max_rate", &PruningConfig::max_rate)
        .def_readwrite("enable_liquidity_pruning", &PruningConfig::enable_liquidity_pruning)
        .def_readwrite("enable_fee_pruning", &PruningConfig::enable_fee_pruning)
        .def_readwrite("enable_rate_pruning", &PruningConfig::enable_rate_pruning);
    
    // EdgePruner class
    py::class_<EdgePruner>(m, "EdgePruner")
        .def(py::init<>())
        .def(py::init<const PruningConfig&>())
        .def("prune_edges", &EdgePruner::prune_edges)
        .def("set_config", &EdgePruner::set_config)
        .def("get_config", &EdgePruner::get_config)
        .def("get_edges_removed", &EdgePruner::get_edges_removed);
}
