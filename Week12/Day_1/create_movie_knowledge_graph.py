import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Load the data
imdb_data = pd.read_csv('imdb.csv')

# Limit to 200 records
imdb_data = imdb_data.head(200)

# Create a graph
g = nx.Graph()

# Add nodes and edges to the graph
def add_movie_knowledge_graph(imdb_data):
    for index, row in imdb_data.iterrows():
        movie_title = row['Title']
        directors = row['Director'].split(',')
        genres = row['Genre'].split(',')
        actors = row['Actors'].split(',')
        rating = float(row['Rating'])

        # Add the movie node
        g.add_node(movie_title, type='movie')

        # Add director nodes and edges
        for director in directors:
            director = director.strip()
            g.add_node(director, type='director')
            g.add_edge(director, movie_title, weight=rating)

        # Add genre nodes and edges
        for genre in genres:
            genre = genre.strip()
            g.add_node(genre, type='genre')
            g.add_edge(movie_title, genre, weight=rating)

        # Add actor nodes and edges
        for actor in actors:
            actor = actor.strip()
            g.add_node(actor, type='actor')
            g.add_edge(actor, movie_title, weight=rating)

    return g

# Generate the knowledge graph
g = add_movie_knowledge_graph(imdb_data)

# Save the graph as GraphML
output_file_path = 'movie_kg.graphml'
nx.write_graphml(g, output_file_path)

# Plotting the graph
pos = nx.spring_layout(g, k=0.15, iterations=20)
plt.figure(figsize=(15, 15))
options = {
    'node_color': 'skyblue',
    'node_size': 1000,
    'linewidths': 0.5,
    'width': 0.5,
    'with_labels': False,
}
nx.draw(g, pos, **options)
plt.title("IMDB Movies Knowledge Graph")
visual_path = 'movie_knowledge_graph.png'
plt.savefig(visual_path)
plt.close()

# Calculate centrality and most connected nodes
degree_centrality = nx.degree_centrality(g)
most_connected_nodes = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:10]

# Print results to file
with open('results.log', 'w') as f:
    f.write(f'Visualization saved to: {visual_path}\n')
    f.write('Most Connected Nodes:\n')
    for node, centrality in most_connected_nodes:
        f.write(f'{node}: {centrality}\n')

# Output result
'Visualization saved to: {visual_path}', most_connected_nodes