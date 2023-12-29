# from wikipedia2vec import Wikipedia2Vec
import gensim

model = "models/wiki-news-300d-1M.vec"
w2v = gensim.models.KeyedVectors.load_word2vec_format(model)

model_result1 = w2v.most_similar('DFS', topn =20) 
print(model_result1)