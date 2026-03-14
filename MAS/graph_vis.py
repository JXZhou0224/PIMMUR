import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle

def load_graph_from_json(json_data):
    """Load graph data from JSON string or dictionary."""
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data
    
    # Create directed graph
    G = nx.DiGraph()
    
    # Add all nodes first
    for node in data.keys():
        G.add_node(node)
    
    # Add edges (connections)
    for node, connections in data.items():
        for connection in connections:
            G.add_edge(node, connection)
    
    return G

def create_centrality_layout(G, k=3, iterations=50):
    """Create a layout that positions high-degree nodes towards the center."""
    # Calculate degree centrality
    degree_centrality = nx.degree_centrality(G)
    
    # Start with spring layout as base
    pos = nx.spring_layout(G, k=k, iterations=iterations, seed=42)
    
    # Calculate attraction to center based on degree centrality
    center = np.array([0, 0])
    
    for node in G.nodes():
        current_pos = np.array(pos[node])
        centrality = degree_centrality[node]
        
        # Pull high-centrality nodes toward center
        # The higher the centrality, the stronger the pull
        attraction_strength = centrality * 0.5
        direction_to_center = center - current_pos
        
        # Apply attraction (but don't move all the way to center)
        pos[node] = current_pos + direction_to_center * attraction_strength
    
    return pos

def visualize_graph(json_file_path=None, json_data=None, figsize=(12, 8)):
    """
    Visualize the graph with nodes positioned by centrality.
    
    Args:
        json_file_path: Path to JSON file (optional)
        json_data: JSON data as string or dict (optional)
        figsize: Figure size tuple
    """
    
    # Load data
    if json_file_path:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
    elif json_data:
        data = json_data
    else:
        # Use the example data if nothing provided
        data = {
            "Kaleek": [],
            "Eleri": ["Kaleek"],
            "Vivi": ["Kaleek", "Eleri"],
            "Marlean": ["Kaleek", "Eleri", "Vivi"],
            "Taniqua": ["Kaleek", "Eleri", "Marlean"],
            "Theodus": ["Kaleek", "Eleri", "Taniqua"],
            "Kera": ["Kaleek", "Eleri", "Theodus"],
            "Carmeshia": ["Taniqua", "Eleri", "Marlean"],
            "Mikailah": ["Eleri", "Theodus", "Kera"],
            "Caryl": ["Marlean", "Vivi", "Taniqua"],
            "Lizett": ["Eleri", "Theodus", "Kera"],
            "Louaine": ["Kaleek", "Taniqua", "Carmeshia"],
            "Wesley": ["Mikailah", "Kera", "Theodus"],
            "Tamesia": ["Kaleek", "Marlean", "Caryl"],
            "Marline": ["Taniqua", "Kera", "Carmeshia"],
            "Lilian": ["Taniqua", "Caryl", "Carmeshia"],
            "Ruthanne": ["Vivi", "Taniqua", "Marline"],
            "Daxon": ["Vivi", "Taniqua", "Ruthanne"],
            "Curtina": ["Kaleek", "Carmeshia", "Lilian"],
            "Angela": ["Kaleek", "Carmeshia", "Ruthanne"]
        }
    
    # Create graph
    G = load_graph_from_json(data)
    
    # Calculate metrics
    degree_centrality = nx.degree_centrality(G)
    in_degree = dict(G.in_degree())
    out_degree = dict(G.out_degree())
    total_degree = {node: in_degree[node] + out_degree[node] for node in G.nodes()}
    
    # Create layout with centrality-based positioning
    pos = create_centrality_layout(G)
    
    # Create the plot
    plt.figure(figsize=figsize)
    
    # Node sizes based on total degree
    max_degree = max(total_degree.values()) if total_degree.values() else 1
    node_sizes = [300 + (total_degree[node] / max_degree) * 1000 for node in G.nodes()]
    
    # Node colors based on degree centrality
    node_colors = [degree_centrality[node] for node in G.nodes()]
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, edge_color='gray', alpha=0.6, 
                          arrows=True, arrowsize=20, arrowstyle='->')
    
    # Draw nodes
    nodes = nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                                  node_size=node_sizes, cmap='viridis',
                                  alpha=0.8)
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold')
    
    # Add colorbar
    plt.colorbar(nodes, label='Degree Centrality', shrink=0.8)
    
    plt.title('Network Graph Visualization\n(Node size and position reflect connectivity)', 
              fontsize=14, fontweight='bold')
    
    # Add statistics text
    stats_text = f"""Network Statistics:
    Nodes: {G.number_of_nodes()}
    Edges: {G.number_of_edges()}
    Most connected: {max(total_degree, key=total_degree.get)} ({max(total_degree.values())} connections)
    """
    
    plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, 
             verticalalignment='top', fontsize=9, 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.axis('off')
    plt.tight_layout()
    plt.show()
    
    # Print detailed node information
    print("\nNode Details (sorted by total connections):")
    print("-" * 50)
    sorted_nodes = sorted(total_degree.items(), key=lambda x: x[1], reverse=True)
    for node, degree in sorted_nodes:
        print(f"{node:12} | In: {in_degree[node]:2} | Out: {out_degree[node]:2} | Total: {degree:2}")

def analyze_graph_properties(json_file_path=None, json_data=None):
    """Analyze and print detailed graph properties."""
    
    # Load data (same logic as visualize_graph)
    if json_file_path:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
    elif json_data:
        data = json_data
    else:
        # Default example data
        data = {
            "Kaleek": [],
            "Eleri": ["Kaleek"],
            "Vivi": ["Kaleek", "Eleri"],
            # ... (same as above)
        }
    
    G = load_graph_from_json(data)
    
    print("=== GRAPH ANALYSIS ===")
    print(f"Number of nodes: {G.number_of_nodes()}")
    print(f"Number of edges: {G.number_of_edges()}")
    print(f"Graph density: {nx.density(G):.3f}")
    
    # Centrality measures
    degree_cent = nx.degree_centrality(G)
    betweenness_cent = nx.betweenness_centrality(G)
    closeness_cent = nx.closeness_centrality(G)
    
    print("\nTop 5 nodes by degree centrality:")
    for node, cent in sorted(degree_cent.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {node}: {cent:.3f}")
    
    print("\nTop 5 nodes by betweenness centrality:")
    for node, cent in sorted(betweenness_cent.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {node}: {cent:.3f}")

# Example usage
if __name__ == "__main__":
    # Visualize with default data
    visualize_graph("friend_graph_log.json")
    
    # Analyze graph properties
    analyze_graph_properties("friend_graph_log.json")
    
    # To use with your own JSON file:
    # visualize_graph(json_file_path='your_graph.json')
    
    # To use with JSON data directly:
    # your_data = {"A": ["B"], "B": ["C"], "C": []}
    # visualize_graph(json_data=your_data)