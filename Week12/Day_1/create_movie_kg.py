import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Data (corrections to special characters)
actor_genre_data = [
    {'actors': 'Eddie Redmayne, Katherine Waterston, Alison Sudol, Dan Fogler', 'genres': ['Adventure', 'Family', 'Fantasy']},
    {'actors': 'Charlize Theron', 'genres': ['Drama']},
    {'actors': 'Jennifer Aniston', 'genres': ['Comedy', 'Drama']},
    {'actors': 'Keanu Reeves', 'genres': ['Action', 'Crime', 'Thriller']},
    {'actors': 'Colin Firth', 'genres': ['Action', 'Adventure', 'Comedy']},
    {'actors': 'Robert Downey Jr.', 'genres': ['Action', 'Adventure', 'Sci-Fi']},
    {'actors': 'Alison Sudol', 'genres': ['Adventure', 'Family', 'Fantasy']},
    {'actors': 'Will Ferrell', 'genres': ['Animation', 'Adventure', 'Comedy']}
]

# Create Graph
G = nx.Graph()

# Add edges and nodes
for data in actor_genre_data:
    actors = data['actors'].split(', ')
    genres = data['genres']
    # Add nodes for genres
    for genre in genres:
        G.add_node(genre, type='genre')
    # Create edges for each actor
    for i in range(len(genres)):
        for j in range(i + 1, len(genres)):
            for actor in actors:
                G.add_edge(genres[i], genres[j], label=actor)

# Create positions
pos = nx.spring_layout(G)

# Draw graph
plt.figure(figsize=(12, 8))
colors = ['skyblue' for _ in G.nodes()]
nx.draw(G, pos, node_color=colors, with_labels=True, node_size=3000, font_size=10, font_weight='bold', edge_color='gray', alpha=0.7)
edge_labels = {(u, v): d['label'] for u, v, d in G.edges(data=True)}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
plt.title('Movie Genre Connectivity through Actors')
plt.savefig('movie_kg.png')
plt.show()

# Save graph to file
nx.write_graphml(G, 'movie_kg.graphml')