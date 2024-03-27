import pandas as pd
import numpy as np
import os
import fasttext
import fasttext.util
from keybert import KeyBERT


def word_embedding(model, keywords_list):
    embeddings = [ np.array(list(map(model.get_word_vector, keywords))) for keywords in keywords_list ]
    return embeddings


def word_list_embedding(model, keywords_list):
    embeddings = word_embedding(model, keywords_list)
    # return np.array([ np.mean(keywords_embedding, axis=0) for keywords_embedding in embeddings])
    return [ np.mean(keywords_embedding, axis=0) for keywords_embedding in embeddings]


def sentence_embedding(model, sentence_list):
    return np.array([ model.get_sentence_vector(' '.join(sentence.split())) for sentence in sentence_list ])


DATA_HOME_DIR = "/lyceum/jhk1c21/msc_project/data"


# load node file
df = pd.read_csv(os.path.join(DATA_HOME_DIR, 'graph', 'full', 'nodes_full.csv'))

title_list = list(df['title'])
keywords_list = list(df['keywords'])
abstract_list = list(df['abstract'])
fos_list = list(df['fos'])


# load pretrained fasttext model
fast_model = fasttext.load_model(os.path.join(DATA_HOME_DIR, 'cc.en.300.bin'))


# keyword and title embeddings
print("[EMBEDDING] keyword embedding start")
keywords_embedding_list = word_list_embedding(fast_model, keywords_list)
print("[EMBEDDING] keyword embedding finish\n")

print("[EMBEDDING] title embedding start")
title_embedding_list = sentence_embedding(fast_model, title_list)
print("[EMBEDDING] title embedding finish\n")


# keyword extraction
print("[KEYWORD EXTRACTION] abstract keyword extraction start")
keywords_from_abstract = []
THRESHOLD = 0.3
KEYWORD_LIMIT = 2
bert_model = KeyBERT()

for idx, abstract in enumerate(abstract_list):
    keywords = bert_model.extract_keywords(abstract, top_n=20, use_mmr=True)

    filtered_keywords = [ keyword[0] for keyword in keywords if keyword[1] > THRESHOLD ]
    if len(filtered_keywords) == 0:
        filtered_keywords = [ keyword[0] for keyword in keywords[:KEYWORD_LIMIT] ]

    keywords_from_abstract.append(filtered_keywords)
    if idx % 1000 == 0:
        print(f"{idx} is done => shape: {filtered_keywords.shape}")
print("[KEYWORD EXTRACTION] abstract keyword extraction finish\n")

# its keyword embedding
print("[EMBEDDING] abstract embedding start")
abstract_embedding_list = word_list_embedding(fast_model, keywords_from_abstract)
print("[EMBEDDING] abstract embedding finish\n")


# search for the uselesses
print("[ELEMINATE] eleminate useless start")
to_eleminate_list = []
original_shape = abstract_embedding_list[0].shape
for idx, embedding in enumerate(abstract_embedding_list):
    if original_shape != embedding.shape:
        to_eleminate_list.append(idx)
        print(idx, len(abstract_list[idx]), abstract_list[idx])

# filter out some uselesses
keywords_embedding = []
title_embedding = []
abstract_embedding = []

filtered_fos = []
filtered_id = []
start = 0

for end in to_eleminate_list:
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
print("[ELEMINATE] eleminate useless finish\n")


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
