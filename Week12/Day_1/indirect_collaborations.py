import matplotlib.pyplot as plt
import networkx as nx

# Sample data for demonstrations
# Actual data will be fetched using the CSV information
film_data = [
    {"director": "James Gunn", "actors": ["Chris Pratt", "Vin Diesel"]},
    {"director": "Ridley Scott", "actors": ["Michael Fassbender", "Charlize Theron"]},
    {"director": "Jon Favreau", "actors": ["Chris Pratt", "Scarlett Johansson"]},
    {"director": "Christopher Nolan", "actors": ["Matthew McConaughey", "Anne Hathaway"]},
    {"director": "Steven Spielberg", "actors": ["Tom Hanks", "Mark Rylance"]},
    {"director": "Ridley Scott", "actors": ["Matt Damon"]},
    {"director": "Anthony Russo", "actors": ["Scarlett Johansson", "Chris Evans"]},
    {"director": "Joe Russo", "actors": ["Chris Evans"]},
    # More entries can be included
]

# Create a directed graph
G = nx.Graph()

# Add nodes and edges based on movie actor-director relationship
for film in film_data:
    director = film["director"]
    for actor in film["actors"]:
        G.add_node(director, label="director")
        G.add_node(actor, label="actor")
        G.add_edge(director, actor)

# Define a function to find indirect collaborations
def find_indirect_collaborations(graph):
    indirect_connections = []
    for director in list(graph.nodes(data=True)):
        if director[1].get("label") == "director":
            # Find second-degree connections (indirect)
            director_connections = []
            for actor in graph.neighbors(director[0]):
                for d in graph.neighbors(actor):
                    if d != director[0] and graph.nodes[d].get("label") == "director":
                        director_connections.append((director[0], d))
            indirect_connections.extend(director_connections)
    return list(set(indirect_connections))

# Visualize the director-actor network with indirect collaborations
indirect_collaborations = find_indirect_collaborations(G)

plt.figure(figsize=(10, 10))
pos = nx.spring_layout(G)
labels = {node: node for node, data in G.nodes(data=True) if data["label"] == "director"}

nx.draw_networkx_nodes(G, pos, node_color="skyblue", nodelist=[d for d, data in G.nodes(data=True) if data["label"] == "director"], node_size=800)
nx.draw_networkx_nodes(G, pos, node_color="lightgreen", nodelist=[d for d, data in G.nodes(data=True) if data["label"] == "actor"], node_size=500)
nx.draw_networkx_labels(G, pos, labels=labels)
nx.draw_networkx_edges(G, pos, edgelist=G.edges(), edge_color="grey", alpha=0.6)

# Highlight indirect collaborations
for collaboration in indirect_collaborations:
    path = nx.shortest_path(G, source=collaboration[0], target=collaboration[1])
    nx.draw_networkx_edges(G, pos, edgelist=list(zip(path, path[1:])), edge_color="#FF5733", width=2.5)

plt.title("Indirect Collaborations Between Directors")
plt.axis('off')
plt.savefig('indirect_collaborations.png')
plt.show()