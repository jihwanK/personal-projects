import os
import pandas as pd
import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.metrics.pairwise import cosine_similarity
import dgl
from dgl.nn import GATConv


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)

DATA_HOME = "/lyceum/jhk1c21/msc_project/data"
FILTERED_PATH = os.path.join(DATA_HOME, "graph", "filtered")

# Load the data
titles = np.load(os.path.join(FILTERED_PATH, 'filtered_title.npy'))
abstracts = np.load(os.path.join(FILTERED_PATH, 'filtered_abstract.npy'))
keywords = np.load(os.path.join(FILTERED_PATH, 'filtered_keyword.npy'))
domains = np.load(os.path.join(FILTERED_PATH, 'filtered_domain.npy'))

ids = np.load(os.path.join(FILTERED_PATH, "filtered_id.npy"))
edges = np.load(os.path.join(FILTERED_PATH, 'filtered_edges.npy'))

df = pd.DataFrame()
df['src'] = edges[:, 0]
df['des'] = edges[:, 1]

# convert id from str to numbers
id_to_int = {original_id: i for i, original_id in enumerate(ids)}
int_to_id = {i: original_id for original_id, i in id_to_int.items()}

df['src'] = df['src'].apply(lambda x: id_to_int[x])
df['des'] = df['des'].apply(lambda x: id_to_int[x])


# Create a DGL graph
citation_network = dgl.graph( (df['src'], df['des']) )

citation_network.ndata['title'] = torch.FloatTensor(titles)
citation_network.ndata['abstract'] = torch.FloatTensor(abstracts)
citation_network.ndata['keywords'] = torch.FloatTensor(keywords)
citation_network.ndata['domain'] = torch.FloatTensor(domains)



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

# Compute similarity for titles, abstracts, keywords, and domains
def compute_similarity(node1, node2):
    title_similarity = cosine_similarity([node1['title']], [node2['title']])[0][0]
    abstract_similarity = cosine_similarity([node1['abstract']], [node2['abstract']])[0][0]
    keyword_similarity = cosine_similarity([node1['keywords']], [node2['keywords']])[0][0]
    domain_dissimilarity = 1 - cosine_similarity([node1['domain']], [node2['domain']])[0][0]

    w1, w2, w3, w4 = 0.2, 0.1, 0.2, 0.5

    # return title_similarity + abstract_similarity + keyword_similarity - domain_dissimilarity
    return w1*title_similarity + w2*abstract_similarity + w3*keyword_similarity - w4*domain_dissimilarity



###################

# Initialize lists to hold pairs and labels
pairs = []
labels = []

# Loop over edges in the graph to create pairs and labels
for u, v in zip(list(df['src']), list(df['des'])):
    node1 = {'title': titles[u], 'abstract': abstracts[u], 'keywords': keywords[u], 'domain': domains[u]}
    node2 = {'title': titles[v], 'abstract': abstracts[v], 'keywords': keywords[v], 'domain': domains[v]}
    
    similarity = compute_similarity(node1, node2)
    
    if similarity > 0.5:
        labels.append(0)
    else:
        labels.append(1)
        
    pairs.append((u, v))

# Convert pairs and labels to tensors
pairs = torch.LongTensor(pairs)
labels = torch.FloatTensor(labels)


# pairs = torch.load(os.path.join(FILTERED_PATH, "gat", "pairs.pt"))
# labels = torch.load(os.path.join(FILTERED_PATH, "gat", "labels.pt"))
###################

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
    

print("VALIDATION START")

