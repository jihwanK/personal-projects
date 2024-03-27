# import numpy as np
# import torch
# from sklearn.metrics.pairwise import cosine_similarity
# import os

# output_dir = '/lyceum/jhk1c21/msc_project/batch'
# out = torch.load(os.path.join(output_dir, 'result.pt'))

# # n_nodes = out.shape[0]
# n_nodes = 1000

# out_np = out.detach().numpy()
# i_indices, j_indices = np.triu_indices(n_nodes, k=1)
# scores_np = cosine_similarity(out_np[i_indices], out_np[j_indices])
# scores = list(zip(i_indices, j_indices, scores_np))

# print(len(scores))
# print(scores)

# import torch
# import numpy as np
# import os

# # Check if CUDA (GPU) is available


# output_dir = '/lyceum/jhk1c21/msc_project/batch'

# # Load the data and move it to the appropriate device
# out = torch.load(os.path.join(output_dir, 'result.pt')).to(device)

# n_nodes = 1000  # Adjust as necessary

# # Calculate cosine similarity using PyTorch functions on GPU
# norm = torch.norm(out, dim=1).unsqueeze(-1)
# normalized_out = out / norm
# similarity_matrix = torch.mm(normalized_out, normalized_out.transpose(0, 1))

# # Get the upper triangular part of the similarity matrix
# i_indices, j_indices = torch.triu_indices(n_nodes, n_nodes, offset=1, device=device)
# scores = similarity_matrix[i_indices, j_indices]

# # Move scores to CPU to convert them to a Python list
# scores_np = scores.cpu().numpy()
# pairs_and_scores = list(zip(i_indices.cpu().numpy(), j_indices.cpu().numpy(), scores_np))

# print(len(pairs_and_scores))
# print(pairs_and_scores)

import torch
import numpy as np
import pandas as pd
import os

import torch.nn.functional as F


DATA_HOME = "/lyceum/jhk1c21/msc_project/data"
V14_PATH = os.path.join(DATA_HOME, "graph", "v14")
FILTERED_PATH = os.path.join(V14_PATH, "filtered")
output_dir = '/lyceum/jhk1c21/msc_project/batch'


out = torch.load(os.path.join(output_dir, 'result_undirected_100.pt'))
ids = np.load(os.path.join(FILTERED_PATH, "filtered_id.npy"))
edges = np.load(os.path.join(FILTERED_PATH, 'filtered_edge.npy'))


df = pd.DataFrame()
# df['src'] = edges[:, 0]
# df['dst'] = edges[:, 1]
df['src'] = np.concatenate((edges[:,0], edges[:,1]), axis=0)
df['dst'] = np.concatenate((edges[:,1], edges[:,0]), axis=0)

# convert id from str to numbers
id_to_int = {original_id: i for i, original_id in enumerate(ids)}
int_to_id = {i: original_id for original_id, i in id_to_int.items()}

df['src'] = df['src'].apply(lambda x: id_to_int[x])
df['dst'] = df['dst'].apply(lambda x: id_to_int[x])

x, y = out[df.to_numpy()[:, 0]], out[df.to_numpy()[:, 1]]
x, y = torch.tensor(x), torch.tensor(y)
df['sim'] = F.cosine_similarity(x, y, dim=1)
df.to_csv(os.path.join(FILTERED_PATH, 'trained_sim_undirected_100.csv'), index=False)
