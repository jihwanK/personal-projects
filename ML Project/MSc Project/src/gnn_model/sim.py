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
