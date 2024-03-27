import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.metrics.pairwise import cosine_similarity
import dgl
from dgl.nn import GATConv

import os
import pandas as pd
import numpy as np


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# if device == "cpu":
#     print("device CPU")
#     exit(0)


DATA_HOME = "/lyceum/jhk1c21/msc_project/data"
V14_PATH = os.path.join(DATA_HOME, "graph", "v14")
FILTERED_PATH = os.path.join(V14_PATH, "filtered")


# Load the data
nodes = pd.read_csv(os.path.join(V14_PATH, "nodes_v14.csv"), index_col='id')
similarity = pd.read_csv(os.path.join(FILTERED_PATH, "similarity_edges.csv"))

titles = np.load(os.path.join(FILTERED_PATH, 'title_embedding.npy'))
abstracts = np.load(os.path.join(FILTERED_PATH, 'abstract_embedding.npy'))
keywords = np.load(os.path.join(FILTERED_PATH, 'keywords_embedding.npy'))
domains = np.load(os.path.join(FILTERED_PATH, 'domains_embedding.npy'))

ids = np.load(os.path.join(FILTERED_PATH, "filtered_id.npy"))
edges = np.load(os.path.join(FILTERED_PATH, 'filtered_edge.npy'))


df = pd.DataFrame()
df['src'] = edges[:, 0]
df['dst'] = edges[:, 1]

id_to_int = {original_id: i for i, original_id in enumerate(ids)}
int_to_id = {i: original_id for original_id, i in id_to_int.items()}

df['src'] = df['src'].apply(lambda x: id_to_int[x])
df['dst'] = df['dst'].apply(lambda x: id_to_int[x])


# Compute similarity for titles, abstracts, keywords, and domains
def compute_each_similarity(node1, node2):
    title_similarity = cosine_similarity([node1['title']], [node2['title']])[0][0]
    abstract_similarity = cosine_similarity([node1['abstract']], [node2['abstract']])[0][0]
    keyword_similarity = cosine_similarity([node1['keywords']], [node2['keywords']])[0][0]
    domain_dissimilarity = 1 - cosine_similarity([node1['domain']], [node2['domain']])[0][0]

    return title_similarity, abstract_similarity, keyword_similarity, domain_dissimilarity

def compute_similarity(node1, node2):
    title_similarity, abstract_similarity, keyword_similarity, domain_dissimilarity = compute_each_similarity(node1, node2)
    
    return title_similarity + abstract_similarity + keyword_similarity + domain_dissimilarity

def compute_weighted_similarity(node1, node2):
    title_similarity, abstract_similarity, keyword_similarity, domain_dissimilarity = compute_each_similarity(node1, node2)
    w1, w2, w3, w4 = 0.25, 0.15, 0.2, 0.4

    return w1*title_similarity + w2*abstract_similarity + w3*keyword_similarity + w4*domain_dissimilarity

def compute_df_similarity(sim_df, weight=None):
    if weight is None:
        w1, w2, w3, w4 = 0.25, 0.25, 0.25, 0.25
    else:
        w1, w2, w3, w4 = weight

    return w1*sim_df['title'] + w2*sim_df['abstract'] + w3*sim_df['keyword'] + w4*(1-sim_df['domain'])


similarity['weighted_similarity'] = compute_df_similarity(similarity, (0.25, 0.15, 0.2, 0.4))
similarity['similarity'] = compute_df_similarity(similarity)

similarity_list = list(similarity['similarity'])

# Create a DGL graph
citation_network = dgl.graph( (df['src'], df['dst']) )

citation_network.ndata['title'] = torch.FloatTensor(titles)
citation_network.ndata['abstract'] = torch.FloatTensor(abstracts)
citation_network.ndata['keywords'] = torch.FloatTensor(keywords)
citation_network.ndata['domain'] = torch.FloatTensor(domains)
citation_network.edata['weight'] = torch.FloatTensor(similarity_list)


# MODEL STARTS
# GAT Layer
class GATLayer(nn.Module):
    def __init__(self, in_dim, out_dim, num_heads=1):
        super(GATLayer, self).__init__()
        self.gatconv = GATConv(in_dim, out_dim, num_heads, allow_zero_in_degree=True)
        
    def forward(self, g, h):
        h = self.gatconv(g, h)
        return h.squeeze(1)

# GAT Model
class GATModel(nn.Module):
    def __init__(self, in_dim, hidden_dim, out_dim):
        super(GATModel, self).__init__()
        self.layer1 = GATLayer(in_dim, hidden_dim)
        self.layer2 = GATLayer(hidden_dim, out_dim)
        
    def forward(self, g, h):
        h = F.relu(self.layer1(g, h))
        h = self.layer2(g, h)
        return h
    
# Contrastive Loss
class ContrastiveLoss(nn.Module):
    def __init__(self, margin=1.0):
        super(ContrastiveLoss, self).__init__()
        self.margin = margin

    def forward(self, output1, output2, label):
        euclidean_distance = F.pairwise_distance(output1, output2)
        loss_contrastive = torch.mean((1-label) * torch.pow(euclidean_distance, 2) +
                                      (label) * torch.pow(torch.clamp(self.margin - euclidean_distance, min=0.0), 2))
        return loss_contrastive


SIMILARITY_THRESHOLD = 0.5
labels = np.zeros(similarity.shape[0])
labels[list(similarity[similarity['similarity'] <= SIMILARITY_THRESHOLD].index)] = 1

pairs = list(zip(df['src'], df['dst']))

pairs = torch.LongTensor(pairs)
labels = torch.FloatTensor(labels)

# torch.save(pairs, os.path.join(V14_PATH, "result", "pairs.pt"))
# torch.save(labels, os.path.join(V14_PATH, "result", "labels.pt"))
pairs = torch.load(os.path.join(V14_PATH, "result", "pairs.pt"))
labels = torch.load(os.path.join(V14_PATH, "result", "labels.pt"))

# Initialize the model and loss
# INPUT: (Feature Dim, Hidden Dim, Output Dim)
model = GATModel(300, 128, 64)
loss_fn = ContrastiveLoss()

# Define optimizer
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# Training loop
for epoch in range(50):
    model.train()
    
    # Forward pass
    h = torch.FloatTensor(citation_network.ndata['title'])
    output = model(citation_network, h)
    
    # Create output1 and output2 based on pairs
    output1 = output[pairs[:, 0]]
    output2 = output[pairs[:, 1]]
    
    # Compute contrastive loss
    loss = loss_fn(output1, output2, labels)
    
    # Backward pass
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    
    print(f'Epoch {epoch}, Loss: {loss.item()}')

print("TEST strat")



