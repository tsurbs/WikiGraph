# from wikipedia2vec import Wikipedia2Vec
import pickle
import numpy as np
from gensim.models.word2vec import Word2Vec
import pandas as pd
import nltk


file = open("data/out.wikipedia_link_en")
file.readline()

init = [[i] for i in range(12467179)]
print("Tok init")
model = Word2Vec(init,      
                 window=1,       
                 min_count=1,     
                 workers=10,
                 ) 
print("Model init")
l = file.readline()
c = 0
while l != '':
    c+=1
    if c%1000 == 0: print(c)
    s = l.split("\t")
    a = s[0]
    b = s[1][:-1]
    model.train([[a, b]], total_examples=1, epochs=1)
    l = file.readline()
print("Constructed model")
model.save("2numgraphModel.model")
print("Saved model")
model_result1 = model.wv.most_similar('1', topn =20) 
print(model_result1)