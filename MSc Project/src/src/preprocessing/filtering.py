import pandas as pd
import numpy as np
import os
import re

DATA_HOME = "/lyceum/jhk1c21/msc_project/data"
FILTERED_DIR = os.path.join(DATA_HOME, "graph", "filtered", "n_citation")

df = pd.read_csv(os.path.join(FILTERED_DIR, 'node_50.csv'))

titles = np.load(os.path.join(FILTERED_DIR, 'title.npy'))
abstracts = np.load(os.path.join(FILTERED_DIR, 'abstract.npy'))
keywords = np.load(os.path.join(FILTERED_DIR, 'keywords.npy'))
domains = np.load(os.path.join(FILTERED_DIR, 'domain_embedding.npy'))
ids = np.load(os.path.join(FILTERED_DIR, "id.npy"))

edges = np.load(os.path.join(FILTERED_DIR, "n_citation", 'edge_list_50.npy'))

filtered_df = df[df['_id'].isin(ids)].reset_index()
keywords_list = list(map(eval, df['keywords']))

def find_index_of_matching_lists_optimized(data, pattern):
    matching_indices = []
    pattern_re = re.compile(pattern)

    for i, sublist in enumerate(data):
        if all(pattern_re.search(element) for element in sublist):
            matching_indices.append(i)
            # print(sublist)
    return matching_indices

updated_pattern = r'^[A-Z][0-9]{1,2}$'
matching_indices_optimized = find_index_of_matching_lists_optimized(keywords_list, updated_pattern)

mask = np.ones(titles.shape[0], dtype=bool)
mask[matching_indices_optimized] = False

excluded_titles = titles[mask]
excluded_abstracts = abstracts[mask]
excluded_keywords = keywords[mask]
excluded_domains = domains[mask]
excluded_ids = ids[mask]

np.save(os.path.join(FILTERED_DIR, "filtered_title.npy"), excluded_titles)
np.save(os.path.join(FILTERED_DIR, "filtered_abstract.npy"), excluded_abstracts)
np.save(os.path.join(FILTERED_DIR, "filtered_keyword.npy"), excluded_keywords)
np.save(os.path.join(FILTERED_DIR, "filtered_domain.npy"), excluded_domains)
np.save(os.path.join(FILTERED_DIR, "filtered_id.npy"), excluded_ids)


edges_id_a = set( [ id for id, _ in edges ] )
edges_id_b = set( [ id for _, id in edges ] )
union_edges = edges_id_a.union(edges_id_b)
exc_id_set = set(excluded_ids)

edges = list(union_edges.intersection(exc_id_set))
excluded_edges = [ (src, des) for src, des in edges if (src in excluded_ids) and (des in excluded_ids) ]
np.save(os.path.join(FILTERED_DIR, "filtered_edges.npy"), excluded_edges)