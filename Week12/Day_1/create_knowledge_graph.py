import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx

# Load data
movies_data = pd.read_csv('imdb.csv').head(3)

# Initialize a directed graph
G = nx.Graph()

# Add nodes and edges for the graph
for _, row in movies_data.iterrows():
    movie = row['Title']
    director = row['Director']
    genres = row['Genre'].split(',')
    actors = row['Actors'].split(',')
    rating = row['Rating'] if pd.notnull(row['Rating']) else 0
    revenue = row['Revenue (Millions)'] if pd.notnull(row['Revenue (Millions)']) else 0

    # Add movie node
    G.add_node(movie, type='Movie')
    
    # Add director node and edge
    G.add_node(director, type='Director')
    G.add_edge(director, movie, weight=rating + revenue)
    
    # Add genre nodes and edges
    for genre in genres:
        G.add_node(genre, type='Genre')
        G.add_edge(genre, movie, weight=rating + revenue)

    # Add actor nodes and edges
    for actor in actors:
        actor = actor.strip()  # Clean the actor name
        G.add_node(actor, type='Actor')
        G.add_edge(actor, movie, weight=rating + revenue)

# Export graph to GraphML
nx.write_graphml(G, 'movie_kg.graphml')

# Visualize the graph
plt.figure(figsize=(15, 15))
pos = nx.spring_layout(G, seed=42)
node_colors = [
    'lightblue' if data['type'] == 'Movie' else 'lightgreen' if data['type'] == 'Director' 
    else 'lightcoral' if data['type'] == 'Genre' else 'orange'
    for node, data in G.nodes(data=True)
]

nx.draw(G, pos, with_labels=True, node_size=50, node_color=node_colors, font_size=7)
plt.title('IMDB Movie Knowledge Graph')
plt.savefig('imdb_knowledge_graph.png')
plt.show()