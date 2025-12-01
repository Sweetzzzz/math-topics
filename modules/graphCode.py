# Data Setup
import json 
import networkx as nx
import pandas as pd
import os

# Get the path to the JSON file relative to this file's location
json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "wikivital_mathematics.json")
with open(json_path) as f:
    data = json.load(f)
 


# don't ask me why they structured the data backwards
topics = {value: key for key, value in data['node_ids'].items()} 

u, v = data['edges'][0]
w = data['weights'][0]


def bldGraph():
    global G
    G = nx.DiGraph()
    for edge, weight in zip(data['edges'], data['weights']):
        G.add_edge(edge[0], edge[1], weight=weight)
    return G

bldGraph()


weak_components = nx.weakly_connected_components(G)
largest_weak_cc = max(weak_components, key=len)


strong_components = nx.strongly_connected_components(G)
largest_strong_cc = max(strong_components, key=len)



# Knowledge graphs SHOULD be acyclic, so this makes sense


G_viz = G.copy().to_undirected() # For communities, we need undirected
communities = list(nx.algorithms.community.greedy_modularity_communities(G_viz)) # No need to be perfect on visualizations :)

#print(communities)

comm_id = {}
for index, comm in enumerate(communities):
    for v in comm:
        comm_id[v] = index


n_comms = max(comm_id.values()) + 1 if communities else 1

qualitative_maps = [
    "tab10", "Set3", "Accent", "Pastel1", "Dark2",
    "Paired", "tab20", "tab20b", "tab20c"
]


pos = nx.spring_layout(G)



# plt.figure(figsize=(10, 8))



# No labels for large graphs
# nx.draw_networkx_labels(G, pos, font_size=6)

# plt.title(f"Communities in Directed Graph (colored by label, n_comms={n_comms})")
# plt.axis('off')
# plt.tight_layout()
# plt.show()

# What are the big 5?
hubs = []
for comm in communities:
    hub = max(comm, key=lambda x: G.out_degree(x)) # type: ignore
    hubs.append(hub)



# Degree Analysis

# import matplotlib.pyplot as plt
# choose degree type (for DiGraph)

def deg_stats(G):
    in_degrees = [d for _, d in G.in_degree()]
    out_degrees = [d for _, d in G.out_degree()]

    max_deg = max(max(in_degrees, default=0), max(out_degrees, default=0))
    return {
        "in_degrees": in_degrees,
        "out_degrees": out_degrees,
        "max_deg": max_deg
    }


stats = deg_stats(G)


in_degrees = stats["in_degrees"]
out_degrees = stats["out_degrees"]
max_deg = stats["max_deg"]

bins = range(max_deg + 2)

# plt.figure()
# plt.hist(in_degrees, bins=range(max(in_degrees)+2), align='left', rwidth=0.8)
# plt.xlabel('In-degree')
# plt.ylabel('Count')
# plt.title('In-degree distribution')
# plt.show()

# plt.figure()
# plt.hist(out_degrees, bins=range(max(out_degrees)+2), align='left', rwidth=0.8)
# plt.xlabel('Out-degree')
# plt.ylabel('Count')
# plt.title('Out-degree distribution')
# plt.show()

# # plot histograms
# # plot both on the same histogram
# plt.hist(in_degrees, bins=bins, alpha=0.6, label='In-degree', color='tab:blue', rwidth=0.8)
# plt.hist(out_degrees, bins=bins, alpha=0.6, label='Out-degree', color='tab:orange', rwidth=0.8)

# plt.xlabel('Degree')
# plt.ylabel('Count')
# plt.title('In-degree vs Out-degree Distribution')
# plt.legend()
# plt.show()
from typing import Counter

in_deg_counts = Counter(dict(G.in_degree).values())
out_deg_counts = Counter(dict(G.out_degree).values())

in_x, in_y = zip(*sorted(in_deg_counts.items()))
out_x, out_y = zip(*sorted(out_deg_counts.items()))

# plt.figure()
# plt.scatter(in_x, in_y, label='In-degree', color='tab:blue', alpha=0.7)
# plt.scatter(out_x, out_y, label='Out-degree', color='tab:orange', alpha=0.7)

# plt.xscale('log')
# plt.yscale('log')
# plt.xlabel('Degree (log scale)')
# plt.ylabel('Frequency (log scale)')
# plt.title('In-degree vs Out-degree Distribution (Scatter, Log–Log)')
# plt.legend()
# plt.show()
