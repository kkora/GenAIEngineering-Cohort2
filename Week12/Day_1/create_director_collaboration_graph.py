import networkx as nx
import pandas as pd

# Load data from the CSV file
movies = pd.read_csv('imdb.csv')

# Create a Graph
G = nx.Graph()

# Dictionary to hold actors and their directors
actor_director_map = {}

# Iterate through the movies row
for _, row in movies.iterrows():
    director = row['Director'].strip()
    actors = row['Actors'].split(',')
    
    # Add directors as nodes
    if director not in G:
        G.add_node(director)
    
    for actor in actors:
        actor = actor.strip()
        # Record which director this actor has worked with
        if actor not in actor_director_map:
            actor_director_map[actor] = set()
        actor_director_map[actor].add(director)

# Add edges based on shared actors
for actor, directors in actor_director_map.items():
    director_list = list(directors)
    for i in range(len(director_list)):
        for j in range(i+1, len(director_list)):
            if not G.has_edge(director_list[i], director_list[j]):
                G.add_edge(director_list[i], director_list[j])

# Save the constructed graph
nx.write_graphml(G, 'director_collaborations.graphml')

# Print the number of connected components
num_components = nx.number_connected_components(G)
num_components