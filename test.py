from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('/home/dung/PycharmProjects/sentence-transformers-master/output')

corpus = ['Cho biết chương 4 luật giao thông đường bộ',
          'chương 4 luật giao thông đường bộ',
          'chương 5 luật giao thông đường bộ',
          'chương 7 luật giao thông đường bộ',
          'một người muốn thi công một công trình, anh ta muốn hỏi thi công công trình trên đường bộ đang khai thác chỉ được tiến hành khi nào',
          'thời gian thi công công trình như thế nào thì cũng chẳng liên qua tới anh ta',
          'chương 2 luật giao thông đường bộ',
          'Một con khỉ đang diễn xiếc.',
          'Một người đàn ông trong bộ đồ tinh tinh đang làm trò.',
          'Lũ quét đột ngột gây thiệt hại cho ít nhất 3 tỉnh miền núi']

from sklearn.metrics.pairwise import cosine_similarity
def similarity_sentence(sents):
    sbert = SentenceTransformer('/home/dung/PycharmProjects/Web_TrafficLaw/output')
    sentence_embeddings = sbert.encode(sents)
    similarites = cosine_similarity(sentence_embeddings)
    similarites_sorted = similarites.argsort()
    id_1 = []
    id_2 = []
    score = []
    array = similarites_sorted[0]
    for idx, val in enumerate(array):
        id_1.append(0)
        id_2.append(val)
        score.append(similarites[0][val])
    return sents[id_2[-2]], similarites[0][array[-2]]
(sent, score) = similarity_sentence(corpus)
print(sent)
print(score)

corpus_embeddings = model.encode(corpus)
np.array(corpus_embeddings).shape

from sklearn.cluster import KMeans

num_clusters = 5

clustering_model = KMeans(n_clusters=num_clusters)
clustering_model.fit(corpus_embeddings)
cluster_assignment = clustering_model.labels_
print(cluster_assignment)

from sklearn.decomposition import PCA
import numpy as np
import pandas as pd


X = np.array(corpus_embeddings)

pca = PCA(n_components=3)
result = pca.fit_transform(X)

df = pd.DataFrame({
    'sent': corpus,
    'cluster': cluster_assignment.astype(str),
    'x': result[:, 0],
    'y': result[:, 1],
    'z': result[:, 2]
})
print(df)

import plotly.express as px


fig = px.scatter_3d(df, x='x', y='y', z='z',
              color='cluster', hover_name='sent',
              range_x = [df.x.min()-1, df.x.max()+1],
              range_y = [df.y.min()-1, df.y.max()+1],
              range_z = [df.z.min()-1, df.z.max()+1])

fig.update_traces(hovertemplate= '<b>%{hovertext}</b>')
fig.show()