import math
import requests
import networkx as nx
import matplotlib.pyplot as plt
from functools import reduce
import sys
from threading import Thread, local, active_count
from queue import Queue
import time

#idea: wordToVec as heuristic for wikigame
sys.setrecursionlimit(20000)

printd = lambda *a: print(a) if debug else None
debug = True

headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}

startUrl = "Depth-first_search"
depthLimit = 3
count = 0
countLimit = 1000 # number of unique sites to explore
maxSinglePage = 15
edges = []
nodes = []
cedges = []
cnodes = []
num_TP_threads = 20
# r = requests.post("https://en.wikipedia.org/wiki/"+startUrl, headers=headers)
session = requests.Session()
thread_local = local()


def isIgnorePage(page : str):
    return (page.startswith("Portal:") or
            page.startswith("Help:") or
            page.startswith("File:") or
            page.startswith("Talk:") or
            page.startswith("User_Talk:") or
            page.startswith("Wikipedia:") or
            page.startswith("Template:") or
            page.startswith("Template_Talk:") or
            page.startswith("Special:") or
            page.startswith("Category:"))

def getAllOutlinks(text):
    outlinks = []
    li = text.find("href=\"/wiki/")
    while li != -1: 
        text = text[li+len("href=/wiki/"):] # Slice so we dont re-search this one
        lj = text.find("\"") # Find end of tag
        outlinks.append(text[1:lj])
        li = text.find("href=\"/wiki/") #continue at this level
    return outlinks

def getSession():
    if not hasattr(thread_local,'session'):
        thread_local.session = requests.Session()
    return thread_local.session



def BFS(TP:Queue): 
    global count
    a = TP.get()
    count += 1
    if a is None: 
        TP.task_done()
        count -= 1
        return
    (prevPage, text, d) = a
    print(prevPage, d)
    
    if d>=depthLimit: 
        TP.task_done()
        count -= 1
        return
    
    LP = Queue(maxsize=0)
    outlinks = getAllOutlinks(text)


    def filterNeighbors(neighs):
        ignoreIf = lambda title: not(title in nodes) and not(isIgnorePage(title))
        Ngp = list(filter(ignoreIf, outlinks))
        shortList = Ngp[:maxSinglePage]
        return shortList

    for title in outlinks:
        cedges.append((prevPage, title))
        cnodes.append(title)
        

    nextExp = filterNeighbors(outlinks)
    for title in nextExp:
        edges.append((prevPage, title))
        nodes.append(title)
        LP.put("https://en.wikipedia.org/wiki/"+title)
    textList = []

    def downloadOneLink():
        while True:
            url = LP.get()
            with session.post(url, headers=headers) as r:
                textList.append((url[len("https://en.wikipedia.org/wiki/"):], r.text))
                LP.task_done()

            
    for i in range(10):
        worker = Thread(target=downloadOneLink)
        worker.start()
    
    LP.join()

    if d<depthLimit:
        for (prevPage, text) in textList:
            TP.put((prevPage, text, d+1))

    TP.task_done()
    count -= 1
    
    for i in range(num_TP_threads-active_count()):
        print("starting new thread", active_count())
        worker = Thread(target=BFS, args=[TP])
        worker.start()

    BFS(TP)




r = requests.post("https://en.wikipedia.org/wiki/"+startUrl, headers=headers)

text_pool = Queue(maxsize=0)
text_pool.put((startUrl, r.text, 0))

BFS(text_pool)


while count != 0: 
    time.sleep(1)
    print(count)

print(cnodes, cedges)

colors = [i+1 for i in range(20)]
options = {
    "edge_color": "Red",
    "with_labels": True,
}

G = nx.Graph()
printd(1)
G.add_nodes_from(cnodes)
G.add_edges_from(cedges)
printd(2)
outDegrees = dict(G.degree)
printd(3)

pos = nx.spring_layout(G, seed=3113794652, iterations=20)  # Seed for reproducible layout
printd(4)

nx.draw_networkx_nodes(
    G, 
    pos, 
    cnodes
)
printd(5)

nx.draw_networkx_edges(
    G, 
    pos, 
    cedges,
    edge_color="#FF0000",
    alpha=.5
)
printd(6, [(v) for k,v in outDegrees.items()])
nx.draw(G, pos, node_size=[(math.log(v,2)+1)*100 for v in outDegrees.values()], **options)
printd(7)

plt.show()
