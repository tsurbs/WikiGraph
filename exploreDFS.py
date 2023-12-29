import math
import requests
import networkx as nx
import matplotlib.pyplot as plt
from functools import reduce
import sys

#idea: wordToVec as heuristic for wikigame
sys.setrecursionlimit(20000)

printd = lambda *a: print(a) if debug else None
debug = False

headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}

startUrl = "Depth-first_search"
depthLimit = 5
count = 0
countLimit = 100 # number of unique sites to explore
maxSinglePage = 10
edges = []
nodes = []

# r = requests.post("https://en.wikipedia.org/wiki/"+startUrl, headers=headers)
session = requests.Session()



def isIgnorePage(page : str):
    return (page.startswith("Portal:") or
            page.startswith("Help:") or
            page.startswith("File:") or
            page.startswith("Talk:") or
            page.startswith("User_Talk:") or
            page.startswith("Wikipedia:") or
            page.startswith("Template:") or
            page.startswith("Special:") or
            page.startswith("Category:"))

def DFS(prevPage, curPage, d):
    global count
    printd(count)

    if curPage in nodes or isIgnorePage(curPage): return "ignore"
    nodes.append(curPage)

    if prevPage is not None: 
        edges.append((prevPage, curPage)) #add edge
        count += 1
    r = session.post("https://en.wikipedia.org/wiki/"+curPage, headers=headers)
    text = r.text
    li = text.find("href=\"/wiki/")
    thisPageCount = 0
    while li != -1 and thisPageCount < maxSinglePage:
        thisPageCount+=1
        printd(prevPage, curPage, thisPageCount)
        text = text[li+len("href=/wiki/"):] # Slice so we dont research this one
        lj = text.find("\"") # Find end of tag
        if count<countLimit and d<depthLimit:
            if DFS(curPage, text[1:lj], d+1) == "ignore": #recurse
                thisPageCount -= 1
        li = text.find("href=\"/wiki/") #continue at this level

DFS(None, startUrl, 0)
print(edges)
colors = [i+1 for i in range(20)]
options = {
    "edge_color": "Red",
    "with_labels": True,
}

G = nx.Graph()
printd(1)
G.add_nodes_from(nodes)
G.add_edges_from(edges)
printd(2)
d = dict(G.degree)
printd(3)

pos = nx.spring_layout(G, seed=3113794652, iterations=20)  # Seed for reproducible layout
printd(4)

nx.draw_networkx_nodes(
    G, 
    pos, 
    nodes,
    node_size=[v for v in d.values()]
)
printd(5)

nx.draw_networkx_edges(
    G, 
    pos, 
    edges,
    edge_color="#FF0000",
    alpha=.5
)
printd(6, [(v) for k,v in d.items()])
nx.draw(G, pos, node_size=[(math.log(v,2)+1)*100 for v in d.values()], **options)
printd(7)

plt.show()
