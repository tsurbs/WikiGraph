from gensim.models.word2vec import Word2Vec

model = Word2Vec(corpus_file="data/out.wikipedia_link_en",      
                 window=1,       
                 min_count=1,     
                 workers=10,
                 ) 
print("Constructed model")

model.save("2numgraphModel.model")
print("Saved model")

model_result1 = model.wv.most_similar('1', topn =20) 
print(model_result1)