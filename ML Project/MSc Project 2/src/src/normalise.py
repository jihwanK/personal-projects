from sklearn.metrics.pairwise import cosine_similarity
import os
import pandas as pd
import numpy as np


# Compute similarity for titles, abstracts, keywords, and domains
def compute_similarity(node1, node2):
    title_similarity = cosine_similarity([node1['title']], [node2['title']])[0][0]
    abstract_similarity = cosine_similarity([node1['abstract']], [node2['abstract']])[0][0]
    keyword_similarity = cosine_similarity([node1['keywords']], [node2['keywords']])[0][0]
    domain_dissimilarity = 1 - cosine_similarity([node1['domain']], [node2['domain']])[0][0]

    return title_similarity, abstract_similarity, keyword_similarity, domain_dissimilarity


# Compute similarity for titles, abstracts, keywords, and domains
def compute_hetro_similarity(node1, node2):
    title_similarity, abstract_similarity, keyword_similarity, domain_dissimilarity = compute_similarity(node1, node2)
    w1, w2, w3, w4 = 0.25, 0.15, 0.2, 0.4

    # return title_similarity + abstract_similarity + keyword_similarity - domain_dissimilarity
    return w1*title_similarity + w2*abstract_similarity + w3*keyword_similarity - w4*domain_dissimilarity


# Compute similarity for titles, abstracts, keywords
def compute_homo_similarity(node1, node2):
    title_similarity, abstract_similarity, keyword_similarity, domain_dissimilarity = compute_similarity(node1, node2)
    w1, w2, w3 = 0.4, 0.3, 0.35

    return w1*title_similarity + w2*abstract_similarity + w3*keyword_similarity


# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

DATA_HOME = "/lyceum/jhk1c21/msc_project/data"
V14_PATH = os.path.join(DATA_HOME, "graph", "v14")
# TMP_PATH = os.path.join(DATA_HOME, "embedding", "tmp", "v14")

# Load the data
# nodes = pd.read_csv(os.path.join(FILTERED_PATH, "filtered_nodes.csv"), index_col='_id')

titles = np.load(os.path.join(V14_PATH, "filtered", 'title_embedding.npy'))
abstracts = np.load(os.path.join(V14_PATH, "filtered", 'abstract_embedding.npy'))
keywords = np.load(os.path.join(V14_PATH, "filtered", 'keywords_embedding.npy'))
domains = np.load(os.path.join(V14_PATH, "filtered", 'domains_embedding.npy'))

ids = np.load(os.path.join(V14_PATH, "filtered", "filtered_id.npy"))
edges = np.load(os.path.join(V14_PATH, "filtered", 'filtered_edge.npy'))

df = pd.DataFrame()
df['src'] = edges[:, 0]
df['dst'] = edges[:, 1]

# convert id from str to numbers
id_to_int = {original_id: i for i, original_id in enumerate(ids)}
int_to_id = {i: original_id for original_id, i in id_to_int.items()}

df['src'] = df['src'].apply(lambda x: id_to_int[x])
df['dst'] = df['dst'].apply(lambda x: id_to_int[x])

# mean_for_normalise = pd.read_csv(os.path.join(V14_PATH, "filtered", "mean.csv"))
# std_for_normalise = pd.read_csv(os.path.join(V14_PATH, "filtered", "std.csv"))

mean_for_normalise = {}
std_for_normalise = {}

title_similarity_list = []
abstract_similarity_list = []
keyword_similarity_list = []
domain_similarity_list = []

# normalise only in terms of edges
src_list, dst_list = list(df['src']), list(df['dst'])
for idx, (src, dst) in enumerate(zip(src_list, dst_list)):
    node1 = {'title': titles[src], 'abstract': abstracts[src], 'keywords': keywords[src], 'domain': domains[src]}
    node2 = {'title': titles[dst], 'abstract': abstracts[dst], 'keywords': keywords[dst], 'domain': domains[dst]}

    title_similarity, abstract_similarity, keyword_similarity, domain_dissimilarity = compute_similarity(node1, node2)
    title_similarity_list.append(title_similarity)
    abstract_similarity_list.append(abstract_similarity)
    keyword_similarity_list.append(keyword_similarity)
    domain_similarity_list.append(1 - domain_dissimilarity)

    if idx % 10000 == 0:
        print(idx)

res_df = pd.DataFrame()
res_df['title'] = title_similarity_list
res_df['abstract'] = abstract_similarity_list
res_df['keyword'] = keyword_similarity_list
res_df['domain'] = domain_similarity_list

res_df.to_csv(os.path.join(V14_PATH, "filtered", "similarity.csv"), index=False)

mean_for_normalise['title'] = np.mean(np.array(title_similarity_list))
mean_for_normalise['abstract'] = np.mean(np.array(abstract_similarity_list))
mean_for_normalise['keyword'] = np.mean(np.array(keyword_similarity_list))
mean_for_normalise['domain'] = np.mean(np.array(domain_similarity_list))

std_for_normalise['title'] = np.std(np.array(title_similarity_list))
std_for_normalise['abstract'] = np.std(np.array(abstract_similarity_list))
std_for_normalise['keyword'] = np.std(np.array(keyword_similarity_list))
std_for_normalise['domain'] = np.std(np.array(domain_similarity_list))

pd.Series(mean_for_normalise).to_csv(os.path.join(V14_PATH, "filtered", "mean.csv"))
pd.Series(std_for_normalise).to_csv(os.path.join(V14_PATH, "filtered", "std.csv"))

    # normalised_title_similarity = (title_similarity - mean_for_normalise.loc['title']) / std_for_normalise.loc['title']
    # normalised_abstract_similarity = (abstract_similarity - mean_for_normalise.loc['abstract']) / std_for_normalise.loc['abstract']
    # normalised_keyword_similarity = (keyword_similarity - mean_for_normalise.loc['keyword']) / std_for_normalise.loc['keyword']
    # normalised_domain_similarity = (domain_similarity - mean_for_normalise.loc['domain']) / std_for_normalise.loc['domain']