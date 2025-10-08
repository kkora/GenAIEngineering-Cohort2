import pandas as pd
import networkx as nx

# Read the IMDb CSV file
data = pd.read_csv('imdb.csv')

# Create a graph
G = nx.Graph()

# Iterate through the rows of the dataframe to add nodes and edges
for _, row in data.iterrows():
    genres = row['Genre'].split(',')
    director = row['Director'].strip()
    actors = [actor.strip() for actor in row['Actors'].split(',')]
    movie = row['Title'].strip()
    
    # Add movie node
    G.add_node(movie, type='movie')
    
    # Add genre nodes and movie-genre edges
    for genre in genres:
        G.add_node(genre, type='genre')
        G.add_edge(movie, genre)
    
    # Add director node and movie-director edge
    G.add_node(director, type='director')
    G.add_edge(movie, director)
    
    # Add actor nodes and movie-actor edges
    for actor in actors:
        G.add_node(actor, type='actor')
        G.add_edge(movie, actor)

# Save the graph as a GraphML file
nx.write_graphml(G, 'imdb_graph.graphml')