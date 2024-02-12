import os
from time import process_time
import pandas as pd
import numpy as np
import fasttext
import fasttext.util
from keybert import KeyBERT
import multiprocessing


def word_embedding(model, keyword_list):
    embeddings = [ np.array(list(map(model.get_word_vector, keywords))) for keywords in keyword_list ]
    return embeddings

def word_list_embedding(model, keyword_list):
    embeddings = word_embedding(model, keyword_list)
    # return np.array([ np.mean(keywords_embedding, axis=0) for keywords_embedding in embeddings])
    return [ np.mean(keywords_embedding, axis=0) for keywords_embedding in embeddings]

def sentence_embedding(model, sentence_list):
    return np.array([ model.get_sentence_vector(' '.join(str(sentence).split())) for sentence in sentence_list ])

def extract_keywords_from_abstract(abstracts):
    bert_model = KeyBERT()
    keywords_from_abstract_chunk = []
    to_eleminate_idx_list_chunk = []

    for idx, abstract in enumerate(abstracts):
        if len(str(abstract).split()) == 1:
            to_eleminate_idx_list_chunk.append(idx)
            continue

        keywords = bert_model.extract_keywords(str(abstract), top_n=10, use_mmr=True)

        filtered_keywords = [keyword[0] for keyword in keywords if keyword[1] > THRESHOLD]
        if len(filtered_keywords) == 0:
            filtered_keywords = [keyword[0] for keyword in keywords[:KEYWORD_LIMIT]]

        keywords_from_abstract_chunk.append(filtered_keywords)

    return keywords_from_abstract_chunk, to_eleminate_idx_list_chunk



DATA_HOME_DIR = "/lyceum/jhk1c21/msc_project/data"


# load node file
print("[LOADING] load csv starts")
t_start = process_time()
df = pd.read_csv(os.path.join(DATA_HOME_DIR, 'graph', 'full', 'nodes_full.csv'))
print(df.shape[0])
t_finish = process_time()
print("[LOADING] load csv finishes")
print(f"[LOADING] {t_finish - t_start} seconds\n")


title_list = list(df['title'])
keywords_list = list(df['keywords'])
abstract_list = list(df['abstract'])
fos_list = list(df['fos'])


# load pretrained fasttext model
print("[LOADING] load fasttext data starts")
t_start = process_time()
fast_model = fasttext.load_model(os.path.join(DATA_HOME_DIR, 'cc.en.300.bin'))
t_finish = process_time()
print("[LOADING] load fasttext data finishes")
print(f"[LOADING] {t_finish - t_start} seconds\n")


# keyword and title embeddings
print("[EMBEDDING] keyword embedding start")
t_start = process_time()
keywords_embedding_list = word_list_embedding(fast_model, keywords_list)
t_finish = process_time()
print("[EMBEDDING] keyword embedding finish")
print(f"[EMBEDDING] {t_finish - t_start} seconds\n")


print("[EMBEDDING] title embedding start")
t_start = process_time()
title_embedding_list = sentence_embedding(fast_model, title_list)
t_finish = process_time()
print("[EMBEDDING] title embedding finish")
print(f"[EMBEDDING] {t_finish - t_start} seconds\n")


# keyword extraction
t_start = process_time()
print("[KEYWORD EXTRACTION] abstract keyword extraction start")

keywords_from_abstract = []
to_eleminate_idx_list = []
THRESHOLD = 0.3
KEYWORD_LIMIT = 2

# Splitting abstract_list into chunks for parallel processing
num_cores = multiprocessing.cpu_count()
chunks = [abstract_list[i::num_cores] for i in range(num_cores)]

with multiprocessing.Pool(num_cores) as pool:
    results = pool.map(extract_keywords_from_abstract, chunks)

# Merging results from all processors
for result in results:
    keywords_from_abstract_chunk, to_eleminate_idx_list_chunk = result
    keywords_from_abstract.extend(keywords_from_abstract_chunk)
    to_eleminate_idx_list.extend(to_eleminate_idx_list_chunk)

t_finish = process_time()
print("[KEYWORD EXTRACTION] abstract keyword extraction finish")
print(f"[KEYWORD EXTRACTION] {t_finish - t_start} seconds\n")


# its keyword embedding
t_start = process_time()
print("[EMBEDDING] abstract embedding start")
abstract_embedding_list = word_list_embedding(fast_model, keywords_from_abstract)
t_finish = process_time()
print("[EMBEDDING] abstract embedding finish")
print(f"[EMBEDDING] {t_finish - t_start} seconds\n")


# search for the uselesses
t_start = process_time()
print("[ELEMINATE] eleminate useless start")
original_shape = abstract_embedding_list[0].shape
for idx, embedding in enumerate(abstract_embedding_list):
    if original_shape != embedding.shape:
        to_eleminate_idx_list.append(idx)
        print(idx, len(abstract_list[idx]), abstract_list[idx])

# filter out some uselesses
keywords_embedding = []
title_embedding = []
abstract_embedding = []

filtered_fos = []
filtered_id = []
start = 0

for end in to_eleminate_idx_list:
    keywords_embedding.extend(keywords_embedding_list[start:end])
    title_embedding.extend(title_embedding_list[start:end])
    abstract_embedding.extend(abstract_embedding_list[start:end])

    filtered_fos.extend(list(df['fos'].iloc[:][start:end]))
    filtered_id.extend(list(df['_id'].iloc[:][start:end]))
    start = end + 1

keywords_embedding.extend(keywords_embedding_list[start:])
title_embedding.extend(title_embedding_list[start:])
abstract_embedding.extend(abstract_embedding_list[start:])

filtered_fos.extend(list(df['fos'].iloc[:][start:]))
filtered_id.extend(list(df['_id'].iloc[:][start:]))

t_finish = process_time()
print("[ELEMINATE] eleminate useless finish")
print(f"[EMBEDDING] {t_finish - t_start} seconds\n")


print("[SAVE] save files")
keywords_embedding = np.array(keywords_embedding)
title_embedding = np.array(title_embedding)
abstract_embedding = np.array(abstract_embedding)
filtered_id = np.array(filtered_id)
filtered_fos = np.array(filtered_fos, dtype='object')

np.save(os.path.join(DATA_HOME_DIR, 'graph', 'full', 'new_title_embedding.npy'), title_embedding)
np.save(os.path.join(DATA_HOME_DIR, 'graph', 'full', 'new_keywords_embedding.npy'), keywords_embedding)
np.save(os.path.join(DATA_HOME_DIR, 'graph', 'full', 'new_abstract_embedding.npy'), abstract_embedding)
np.save(os.path.join(DATA_HOME_DIR, 'graph', 'full', 'new_id.npy'), filtered_id)
np.save(os.path.join(DATA_HOME_DIR, 'graph', 'full', 'new_fos.npy'), filtered_fos)
