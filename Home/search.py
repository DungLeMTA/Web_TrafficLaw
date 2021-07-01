# model.py

from typing import Tuple, List

from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import pairwise_distances
from elasticsearch import Elasticsearch
import numpy as np
import pandas as pd

import plotly.express as px
import re

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity



class Model(object):
  def __init__(self, model_path):
    super(Model, self).__init__()
    
    self.sbert = SentenceTransformer(model_path)

  def measure_distance(self, sents: Tuple[str, str]):
    # compute embeddings
    corpus_embeddings = self.sbert.encode(sents)

    # compute distance
    distances = (
        pairwise_distances(
        corpus_embeddings[0].reshape(1, -1),
        corpus_embeddings[1].reshape(1, -1),
        metric)[0][0] for metric in ["cosine", "manhattan", "euclidean"]
        )
    return distances

  def fit_kmeans(self, corpus: List[str], n_clusters: int):
    # compute embeddings
    corpus_embeddings = self.sbert.encode(corpus)

    # cluster
    clustering_model = KMeans(n_clusters)
    clustering_model.fit(corpus_embeddings)
    
    # perform PCA
    n_components = int(len(corpus) > 2) + 2
    pca = PCA(n_components)
    X = np.array(corpus_embeddings)
    X_reduced = pca.fit_transform(X)

    # plot corpus in 3d scatter plot
    df = pd.DataFrame({
      'sent': corpus,
      'cluster': clustering_model.labels_.astype(str),
      'x': X_reduced[:, 0],
      'y': X_reduced[:, 1],
      'z': X_reduced[:, 2] if X_reduced.shape[1] > 2 else np.zeros(X_reduced.shape[0])
    })

    fig = px.scatter_3d(df, x='x', y='y', z='z',
              color='cluster', hover_name='sent',
              range_x = [df.x.min()-1, df.x.max()+1],
              range_y = [df.y.min()-1, df.y.max()+1],
              range_z = [df.z.min()-1, df.z.max()+1])

    fig.update_traces(hovertemplate= '<b>%{hovertext}</b>')

    # convert graph to html and replace its id
    graph = fig.to_html(full_html=False, include_plotlyjs=False)

    re_graph = r"Plotly\.newPlot\(\s*'(.*?)',.*?\)"
    groups_html = re.search(re_graph, graph, re.DOTALL)
    result = groups_html[0].replace(groups_html[1], 'plotly')
    
    return result

  def similarity_sentence(self,sents: Tuple[str, str]):
      sentence_embeddings = self.sbert.encode(sents)
      similarites = cosine_similarity(sentence_embeddings)
      similarites_sorted  = similarites.argsort()
      id_1 = []
      id_2 = []
      score  = []
      array = similarites_sorted[0]
      for idx, val in enumerate(array):
          id_1.append(0)
          id_2.append(val)
          score.append(similarites[0][val])
      return sents[0], sents[id_2[-2]], similarites[0][array[-2]]

  def search_elasticsearch(self, s: str):
      sentences = []
      sentences.append(s)
      es = Elasticsearch('http://192.168.43.106:9200')

      es.indices.refresh(index="qaluat")
      res = es.search(index="qaluat", body={"query": {"match": {'question': s}}})
      i = 0
      for hit in res['hits']['hits']:
          sentences.append(hit["_source"]['answer'])
          i += 1
          if (i >= 5): break
      return sentences


model = Model('/content/vn_sbert_deploy/phobert_base_mean_tokens_NLI_STS')

def get_model():
  return model