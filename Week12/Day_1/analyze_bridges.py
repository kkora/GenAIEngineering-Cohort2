import networkx as nx
import matplotlib.pyplot as plt

# Load the graph
G = nx.read_graphml('imdb_graph.graphml')

# Analyze bridges - finding actors/directors connecting unrelated genres
bridge_actors_directors = []

# For each actor or director, check the genres they connect
for node in G.nodes:
    if G.nodes[node]['type'] in ['actor', 'director']:
        connected_genres = set()
        for neighbor in G.neighbors(node):
            if G.nodes[neighbor]['type'] == 'movie':
                for movie_neighbor in G.neighbors(neighbor):
                    if G.nodes[movie_neighbor]['type'] == 'genre':
                        connected_genres.add(movie_neighbor)
        
        # If the actor/director connects multiple distinct genres
        if len(connected_genres) > 1:
            bridge_actors_directors.append((node, list(connected_genres)))

# Visualize using a small subset for clarity
shortest_paths_images = []
for actor_director, genres in bridge_actors_directors[:3]:  # limit to 3 for visualization
    # Find and plot shortest paths between genres
    for i in range(len(genres)):
        for j in range(i + 1, len(genres)):
            path = nx.shortest_path(G, source=genres[i], target=genres[j])
            plt.figure(figsize=(10, 5))
            subgraph = G.subgraph(path)
            pos = nx.spring_layout(subgraph)
            nx.draw(subgraph, pos, with_labels=True, node_color='lightblue', edge_color='grey')
            file_name = f'{actor_director}_path_{genres[i]}_{genres[j]}.png'
            plt.savefig(file_name)
            plt.close()
            shortest_paths_images.append(file_name)

shortest_paths_images