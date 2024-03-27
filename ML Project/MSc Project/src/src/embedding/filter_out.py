import os
from time import time
import pandas as pd
import numpy as np


DATA_HOME_DIR = "/lyceum/jhk1c21/msc_project/data"
V14_DIR = os.path.join(DATA_HOME_DIR, "graph", "v14")
FILTERED_DIR = os.path.join(DATA_HOME_DIR, "graph", "v14", "filtered")
TMP_DIR = os.path.join(DATA_HOME_DIR, 'embedding', 'tmp', 'v14')


# load node file
print("[FILTER][LOADING] load csv starts")
t_start = time()
df = pd.read_csv(os.path.join(V14_DIR, 'nodes_v14.csv'))
# print(df.shape[0])
t_finish = time()
print("[FILTER][LOADING] load csv finishes")
print(f"[FILTER][LOADING] {t_finish - t_start} seconds\n")


abstract_list = list(df['abstract'])

title_embedding_list = np.load(os.path.join(TMP_DIR, 'tmp_title_embedding.npy'))
keywords_embedding_list = np.load(os.path.join(TMP_DIR, 'tmp_keywords_embedding.npy'))
abstract_embedding_list = np.load(os.path.join(TMP_DIR, 'tmp_abstract_embedding.npy'))
domain_embedding_list = np.load(os.path.join(TMP_DIR, 'tmp_domains_embedding.npy'))
to_eleminate_idx_list = np.load(os.path.join(TMP_DIR, 'eleminated_idx.npy'))

# to_eleminate_idx_list = []

# search for the uselesses
t_start = time()
print("[FILTER][ELEMINATE] eleminate useless start")

# filter out some uselesses
keywords_embedding = []
title_embedding = []
# abstract_embedding = [] # has been done while embedding the abstract earlier
filtered_fos = []

filtered_id = []
start = 0

for end in to_eleminate_idx_list:
    keywords_embedding.extend(keywords_embedding_list[start:end])
    title_embedding.extend(title_embedding_list[start:end])
    # abstract_embedding.extend(abstract_embedding_list[start:end])
    filtered_fos.extend(list(domain_embedding_list[start:end]))

    filtered_id.extend(list(df['id'].iloc[:][start:end]))
    start = end + 1

keywords_embedding.extend(keywords_embedding_list[start:])
title_embedding.extend(title_embedding_list[start:])
# abstract_embedding.extend(abstract_embedding_list[start:])
filtered_fos.extend(list(domain_embedding_list[start:]))

filtered_id.extend(list(df['id'].iloc[:][start:]))

t_finish = time()
print("[FILTER][ELEMINATE] eleminate useless finish")
print(f"[FILTER] {t_finish - t_start} seconds\n")


t_start = time()
print("[FILTER][EDGE] filter out edges")

filtered_edge = []
edges = np.load(os.path.join(V14_DIR, "edge_list_v14.npy"))

for src, des in edges:
    if src in filtered_id and des in filtered_id:
        filtered_edge.append( (src, des) )

t_finish = time()
print("[FILTER][EDGE] filter out edges")
print(f"[FILTER] {t_finish - t_start} seconds\n")


print("[FILTER][SAVE] save files")
keywords_embedding = np.array(keywords_embedding)
title_embedding = np.array(title_embedding)
# abstract_embedding = np.array(abstract_embedding)
filtered_id = np.array(filtered_id)
filtered_fos = np.array(filtered_fos)
filtered_edge = np.array(filtered_edge)



np.save(os.path.join(FILTERED_DIR, 'title_embedding.npy'), title_embedding)
np.save(os.path.join(FILTERED_DIR, 'keywords_embedding.npy'), keywords_embedding)
np.save(os.path.join(FILTERED_DIR, 'abstract_embedding.npy'), abstract_embedding_list)
np.save(os.path.join(FILTERED_DIR, 'domains_embedding.npy'), filtered_fos)
np.save(os.path.join(FILTERED_DIR, 'filtered_edge.npy'), filtered_edge)
np.save(os.path.join(FILTERED_DIR, 'filtered_id.npy'), filtered_id)
