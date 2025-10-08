import networkx as nx
import matplotlib.pyplot as plt

# Load the graph
G = nx.read_graphml('director_collaborations.graphml')

# Set the size of the figure
plt.figure(figsize=(15, 15))

# Draw the graph
pos = nx.spring_layout(G, seed=42)  # positions for all nodes
nx.draw(G, pos, with_labels=True, node_size=50, font_size=8, node_color='skyblue', edge_color='gray')

# Calculate the shortest path length
path_lengths = dict(nx.all_pairs_shortest_path_length(G, cutoff=2))  # only to 2-hops

# Highlight nodes with indirect relationships
for node, paths in path_lengths.items():
    for connected_node, length in paths.items():
        if length == 2:
            nx.draw_networkx_edges(G, pos, edgelist=[(node, connected_node)], edge_color='red')

# Save the visualization
plt.title('Indirect Collaborations Among Directors')
plt.savefig('director_collaboration_network.png')
plt.show()