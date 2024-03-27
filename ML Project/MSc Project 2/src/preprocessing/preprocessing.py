import time
import networkx as nx
from pymongo import MongoClient
import matplotlib.pyplot as plt

client = MongoClient('localhost', 27017)
db = client['graph']
citation = db['citation']


print("PREPROCESSING START\n")

##########
# FILTER #
##########
print("FILTER START")

filter_query = { "n_citation": {"$gt": 100}, "references": {"$exists": True}, "fos": {"$exists": True} }
filter_projection = { "_id": True, "fos": True }
filter_result = citation.find(filter_query, filter_projection)

filtered_nodes = [ doc["_id"] for doc in filter_result if len(doc["fos"]) != 0 ]

print("FILTER FINISH")


######################
# Generate Edge List #
######################
print("Generating Edge List START")
BATCH_SIZE = 20_000
num_filtered_nodes = len(filtered_nodes)
n_iter = num_filtered_nodes//BATCH_SIZE
edges_set = set()
idx = 1

for it in range(n_iter+1):
    if it < n_iter:
        batched_filtered_nodes = filtered_nodes[it*BATCH_SIZE:(it+1)*BATCH_SIZE]
    else:
        batched_filtered_nodes = filtered_nodes[it*BATCH_SIZE:]

    edge_result = citation.find({ "_id": {"$in": batched_filtered_nodes} }, { "references": 1 })
    for res_doc in edge_result:
        start = time.time()
        satisfied_references = citation.find({ "_id": {"$in": res_doc["references"]}, "n_citation": {"$gt": 100}, "references": {"$exists": True}, "fos": {"$exists": True} }, { "_id": 1 })

        for reference in satisfied_references:
            edges_set.add((res_doc["_id"], reference["_id"]))

        end = time.time()
        print(f"{idx}/{num_filtered_nodes} [{idx/num_filtered_nodes*100:.2f}%] - time [{end-start:.5f} s/p]")

        idx += 1
edges_list = list(edges_set)
print("Generating Edge List FINISH")





rr = [
    (rec_doc["_id"], reference["_id"]) \
            for reference in citation.find({ "_id": {"$in": res_doc["references"]}, "n_citation": {"$gt": 100}, "references": {"$exists": True}, "fos": {"$exists": True} }, { "_id": 1 }) \
            for rec_doc in citation.find({ "_id": {"$in": filtered_nodes} }, { "references": 1 })
]











##################
# Generate Graph #
##################
# cf. there are some dangling nodes
print("Generate Graph START")
DG = nx.digraph.DiGraph()
DG.add_edges_from(edges_list)

without_dangling_nodes_set = set(DG)




#nx.draw(DG, with_labels=True)
#plt.savefig("citation_network.png")

print("Generate Graph FINISH")




print("PREPROCESSING FINISH\n")

