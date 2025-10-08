import networkx as nx
import matplotlib.pyplot as plt

# Graph initialization
G = nx.Graph()

# Sample movie data
data = [
    {"Title": "Guardians of the Galaxy", "Genre": "Action,Adventure,Sci-Fi", "Director": "James Gunn", "Actors": ["Chris Pratt", "Vin Diesel", "Bradley Cooper", "Zoe Saldana"], "Rating": 8.1},
    {"Title": "Prometheus", "Genre": "Adventure,Mystery,Sci-Fi", "Director": "Ridley Scott", "Actors": ["Noomi Rapace", "Logan Marshall-Green", "Michael Fassbender", "Charlize Theron"], "Rating": 7.0},
    {"Title": "Split", "Genre": "Horror,Thriller", "Director": "M. Night Shyamalan", "Actors": ["James McAvoy", "Anya Taylor-Joy", "Haley Lu Richardson", "Jessica Sula"], "Rating": 7.3},
    {"Title": "Sing", "Genre": "Animation,Comedy,Family", "Director": "Christophe Lourdelet", "Actors": ["Matthew McConaughey", "Reese Witherspoon", "Seth MacFarlane", "Scarlett Johansson"], "Rating": 7.2},
    {"Title": "Suicide Squad", "Genre": "Action,Adventure,Fantasy", "Director": "David Ayer", "Actors": ["Will Smith", "Jared Leto", "Margot Robbie", "Viola Davis"], "Rating": 6.2},
    {"Title": "The Great Wall", "Genre": "Action,Adventure,Fantasy", "Director": "Yimou Zhang", "Actors": ["Matt Damon", "Tian Jing", "Willem Dafoe", "Andy Lau"], "Rating": 6.1},
    {"Title": "La La Land", "Genre": "Comedy,Drama,Music", "Director": "Damien Chazelle", "Actors": ["Ryan Gosling", "Emma Stone", "Rosemarie DeWitt", "J.K. Simmons"], "Rating": 8.3},
    {"Title": "Mindhorn", "Genre": "Comedy", "Director": "Sean Foley", "Actors": ["Essie Davis", "Andrea Riseborough", "Julian Barratt", "Kenneth Branagh"], "Rating": 6.4},
    {"Title": "The Lost City of Z", "Genre": "Action,Adventure,Biography", "Director": "James Gray", "Actors": ["Charlie Hunnam", "Robert Pattinson", "Sienna Miller", "Tom Holland"], "Rating": 7.1},
    {"Title": "Passengers", "Genre": "Adventure,Drama,Romance", "Director": "Morten Tyldum", "Actors": ["Jennifer Lawrence", "Chris Pratt", "Michael Sheen", "Laurence Fishburne"], "Rating": 7.0}
]

# Add nodes and edges
for movie in data:
    # Add movie node
    G.add_node(movie['Title'], type='movie')
    
    # Add director node and edge
    G.add_node(movie['Director'], type='director')
    G.add_edge(movie['Title'], movie['Director'], weight=movie['Rating'])
    
    # Add genre nodes and edges
    genres = movie['Genre'].split(",")
    for genre in genres:
        G.add_node(genre.strip(), type='genre')
        G.add_edge(movie['Title'], genre.strip(), weight=movie['Rating'])
        
    # Add actor nodes and edges
    for actor in movie['Actors']:
        G.add_node(actor, type='actor')
        G.add_edge(movie['Title'], actor, weight=movie['Rating'])

# Draw the graph
plt.figure(figsize=(14, 10))
layout = nx.spring_layout(G, k=0.15, iterations=20)

# Colors for different types of nodes
colors = {'movie': 'lightblue', 'director': 'lightgreen', 'actor': 'lightcoral', 'genre': 'lightyellow'}

# Draw nodes with colors
nx.draw_networkx_nodes(G, layout, node_color=[colors[G.nodes[node]['type']] for node in G.nodes], node_size=500)

# Draw edges
edges = nx.draw_networkx_edges(G, layout, width=0.5, alpha=0.7, edge_color="gray")

# Draw labels
nx.draw_networkx_labels(G, layout, font_size=8, font_family="sans-serif")
plt.title('IMDB Movie Knowledge Graph')
plt.axis('off')

# Save the graph
plt.savefig("imdb_knowledge_graph.png")
plt.show()