# -*- coding: utf-8 -*-
"""SeniorDesignCode_01_20_2023.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/yahya010/DocClustering/blob/Ryan_Working/SeniorDesignCode_01_20_2023.ipynb
"""

# pip install -U sentence-transformers

import pandas as pd
import csv
import numpy as np
import matplotlib
from sentence_transformers import SentenceTransformer
import nltk
import numpy as np
import os
import matplotlib.pyplot as plt
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
nltk.download('punkt')
from nltk.tokenize import sent_tokenize
from seg_algorithm import get_optimal_splits, get_segmented_sentences
from transformers import AutoTokenizer, AutoModel
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import torch
import torch.nn.functional as F
from sklearn.cluster import KMeans
url = "https://raw.githubusercontent.com/yahya010/DocClustering/main/Pres_Speeches/corpus.csv"
dataset = pd.read_csv(url)
p = 0.65 #increase p = no of segments decreases

stop_words = set(stopwords.words('english'))
transcripts = dataset.transcripts
tokenized_transcripts = pd.DataFrame(index=range(44), columns=['Sentences'])

fullTranscripts = []
filteredTranscript = []
originalTranscript_list = [] # contains 44 transcripts
transcript_list = [] #contains 44 transcripts
for transcript in transcripts[0:1]:
    transcript = sent_tokenize(transcript)
    for sentence in transcript:
      fullTranscripts.append(sentence)
# for sentence in transcripts[0:1]:
#      word_tokens = word_tokenize(sentence)
#      filtered_tokens = [w for w in word_tokens if not w.lower() in stop_words]
#      filtered_sentence = [' '.join(filtered_tokens)]
#      filteredTranscript.append(filtered_sentence)
#      print(filtered_sentence)
# filteredTranscript = sent_tokenize(filteredTranscript)
# for sentence in filteredTranscript[]:
#     transcript = sent_tokenize(transcript)
#     for sentence in transcript:
#       fullTranscripts.append(sentence)
# filteredTranscript = pd.DataFrame(filteredTranscript)
# filteredTranscript.to_csv('filteredTranscript.csv')

# Segmentation and Embedding
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v1')
embeddings = model.encode(fullTranscripts)

segmentation  = get_optimal_splits(embeddings, p) # Splits.
segmented_txt = get_segmented_sentences(fullTranscripts, segmentation)
segment_list = []
for segment in segmented_txt:
    segment_list.append('Segment ' + str(segmented_txt.index(segment)) + ': ' + str(segment))

seglistDF = pd.DataFrame(segment_list)
seglistDF.to_csv('fullSegmentationList.csv')

# create directory for data output if not exists
if not os.path.exists('Data_Output'):
  os.mkdir('Data_Output')

def squared_sum(x):
  """ return 3 rounded square rooted value """
  return round(np.sqrt(sum([a*a for a in x])),3)

def cos_similarity(x,y):
  """ return cosine similarity between two lists """
  numerator = sum(a*b for a,b in zip(x,y))
  denominator = squared_sum(x)*squared_sum(y)
  return round(numerator/float(denominator),3)

def filter_Sentences(unfilteredSentences, lengthFilter = -1):
  filteredSentences = unfilteredSentences

  # split sentences and check lengths
  if lengthFilter > 0:
    filteredSentences = [s for s in unfilteredSentences if len(s.split()) > lengthFilter]

    # display removed sentences
    # removedWords = [s for s in unfilteredSentences if s not in filteredSentences]

    # for w in removedWords:
    #    print(w)

def kmeans(reduced_embedding, fullTranscripts):

    # KMeans algorithm
    kmeans_clusters = KMeans(n_clusters=25, init='k-means++', n_init=10, random_state=42, max_iter=300, algorithm='auto',
                             copy_x=True, tol=0.0001, verbose=0)

    label = kmeans_clusters.fit_predict(reduced_embedding)

    cluster_range = range(2, 150)

    cluster_labels = np.unique(label)
    transcript_label_matching = {}

    # plotting the results:
    for i in cluster_labels:
        plt.scatter(reduced_embedding[label == i, 0], reduced_embedding[label == i, 1], label=i)

    plt.xlabel('Dimension 1 Score')
    plt.ylabel('Dimension 2 Score')
    plt.title('KMeans Clustering Visualization')
    plt.legend()
    plt.show()



    # # Comparison of Within Cluster Sum of Squares (wcss) for different cluster sizes
    # wcss = []

    # for i in cluster_range:
    #     kmeans_pca = KMeans(n_clusters=i, init='k-means++', random_state=42, n_init=10)
    #     kmeans_pca.fit(reduced_embedding)
    #     wcss.append(kmeans_pca.inertia_)
    #
    # plt.figure(figsize=(10, 8))
    # plt.plot(cluster_range, wcss, marker='o', linestyle='--')
    # plt.xlabel('Number of Clusters')
    # plt.ylabel('K-means with PCA clustering')
    # plt.show()

    # silhouette score for different cluster sizes
    silhouette_avg = []
    # for i in cluster_range:
    #     silhouette_avg.append(silhouette_score())

    # for i in cluster_range:
    #     kmeans_pca = KMeans(n_clusters=i, init='k-means++', random_state=42, n_init=10)
    #     t_labels = kmeans_pca.fit_predict(reduced_embedding)
    #     silhouette_avg.append(silhouette_score(reduced_embedding, t_labels))
    #
    # plt.plot(cluster_range, silhouette_avg, 'bx-')
    # plt.xlabel('Values of K')
    # plt.ylabel('Silhouette score')
    # plt.title('Silhouette analysis For Optimal k')
    # plt.show()

    for i in label:
        if i not in transcript_label_matching.keys():
            transcript_label_matching[i] = []

    print(len(fullTranscripts))
    print(len(label))
    for i in range(len(fullTranscripts)):
        transcript_label_matching[label[i]].append(fullTranscripts[i])

    with open('Data_Output/KMeansClusters.csv', 'w') as kmeansCSV:
        writer = csv.writer(kmeansCSV)

        for k in transcript_label_matching.keys():
            writer.writerow(transcript_label_matching[k])

# PrePCA Cosine Similarity Matrix
heatmap = np.zeros(shape=(len(embeddings), len(embeddings)))
for i in range(len(embeddings)):
    sent = embeddings[i]
    for j in range(len(embeddings)):
        sent2 = embeddings[j]
        cosSim = cos_similarity(sent, sent2)
        heatmap[i,j] = cosSim

# PCA-95 Dimensionality Reduction
embedding = embeddings
pca = PCA(n_components=0.95)
reduced_embedding = pca.fit_transform(embedding)
print(reduced_embedding.shape)

# PostPCA Cosine Similarity Matrix (Sentence Similarity Matrix)
heatmapPost = np.zeros(shape=(len(reduced_embedding), len(reduced_embedding)))
for i in range(len(reduced_embedding)):
    sentPost = reduced_embedding[i]
    for j in range(len(reduced_embedding)):
        sent2Post = reduced_embedding[j]
        cosSimPost = cos_similarity(sentPost, sent2Post)
        heatmapPost[i,j] = cosSimPost

# Remove Diagonal
# heatmapRD = np.delete(heatmap,range(0,heatmap.shape[0]**2,(heatmap.shape[0]+1))).reshape(heatmap.shape[0],(heatmap.shape[1]-1))

# Standardize the Data
print(heatmap)

# ind = np.argpartition(heatmap[0,:], -10)[-10:]
# top4 = heatmap[0,ind]
# print(ind)
# print(top4)
#
# top5 = np.zeros(shape=(y, x))
# ind = np.argpartition(heatmap[0,:], -5)[-5:]
# top4 = heatmap[0,ind]
# print(ind)
# print(top4)
# top4 = pd.DataFrame(top4)
# top4.to_csv('top4.csv')
# for i in range

# Prenormalized Heatmaps

# PrePCA Heatmap
x = 100
y = 100
heatmapPrePCA = np.zeros(shape=(y, x))
for i in range(y):
  for j in range(x):
    heatmapPrePCA[i,j] = heatmap[i,j]
data = heatmapPrePCA
plt.imshow( data , cmap = 'inferno' , interpolation = 'nearest' )
# color schemes that work well (cmap =): cividis, viridis, inferno. Full list: https://matplotlib.org/stable/tutorials/colors/colormaps.html
plt.title( "Transcript 0: PrePCA Heatmap" )
plt.show()

# PostPCA Heatmap
x = 100
y = 100
heatmapPostPCA = np.zeros(shape=(y, x))
for i in range(y):
  for j in range(x):
    heatmapPostPCA[i,j] = heatmapPost[i,j]
data = heatmapPostPCA
plt.imshow( data , cmap = 'inferno' , interpolation = 'nearest' )
# color schemes that work well (cmap =): cividis, viridis, inferno. Full list: https://matplotlib.org/stable/tutorials/colors/colormaps.html
plt.title( "Transcript 0: PostPCA Heatmap" )
plt.show()

# # Standardized

# # Normalize Pre and Post Cosine Similarity Matrixs
# heatmapmax, heatmapmin = heatmap.max(), heatmap.min()
# heatmapPreNorm = (heatmap - heatmapmin)/(heatmapmax - heatmapmin)
# heatmapPostmax, heatmapPostmin = heatmapPost.max(), heatmapPost.min()
# heatmapPostNorm = (heatmapPost - heatmapPostmin)/(heatmapPostmax - heatmapPostmin)

# Zpositive = np.ma.masked_less(heatmapPreNorm, .3)
# Znegative = np.ma.masked_greater(heatmapPreNorm, .3)
# # PrePCA Heatmap
# x = 100
# y = 100
# heatmapPrePCAStand = np.zeros(shape=(y, x))
# for i in range(y):
#   for j in range(x):
#     heatmapPrePCAStand[i,j] = heatmapPreNorm[i,j]
# data = Zpositive
# plt.imshow( data , cmap = 'inferno', interpolation = 'nearest' )
# # color schemes that work well (cmap =): cividis, viridis, inferno. Full list: https://matplotlib.org/stable/tutorials/colors/colormaps.html
# plt.title( "Transcript 0: PrePCA Normalized Heatmap" )
# plt.show()
# x = 100
# y = 100
# heatmapPrePCAStand = np.zeros(shape=(y, x))
# for i in range(y):
#   for j in range(x):
#     heatmapPrePCAStand[i,j] = heatmapPreNorm[i,j]
# data = Znegative
# plt.imshow( data , cmap = 'Blues', interpolation = 'nearest' )
# # color schemes that work well (cmap =): cividis, viridis, inferno. Full list: https://matplotlib.org/stable/tutorials/colors/colormaps.html
# plt.title( "Transcript 0: PrePCA Normalized Heatmap" )
# plt.show()

# # PostPCA Heatmap
# x = 100
# y = 100
# heatmapPostPCAStand = np.zeros(shape=(y, x))
# for i in range(y):
#   for j in range(x):
#     heatmapPostPCAStand[i,j] = heatmapPostNorm[i,j]
# data = heatmapPostPCAStand
# plt.imshow( data , cmap = 'inferno' , vmin = -0.6, vmax = 0.8, interpolation = 'nearest' )
# # color schemes that work well (cmap =): cividis, viridis, inferno. Full list: https://matplotlib.org/stable/tutorials/colors/colormaps.html
# plt.title( "Transcript 0: PostPCA Normalized Heatmap" )
# plt.show()

# Normalized Heatmaps

# Normalize Pre and Post Cosine Similarity Matrixs
heatmapmax, heatmapmin = heatmap.max(), heatmap.min()
heatmapPreNorm = (heatmap - heatmapmin)/(heatmapmax - heatmapmin)
heatmapPostmax, heatmapPostmin = heatmapPost.max(), heatmapPost.min()
heatmapPostNorm = (heatmapPost - heatmapPostmin)/(heatmapPostmax - heatmapPostmin)
# PrePCA Heatmap
x = 100
y = 100
heatmapPrePCANorm = np.zeros(shape=(y, x))
for i in range(y):
  for j in range(x):
    heatmapPrePCANorm[i,j] = heatmapPreNorm[i,j]
data = heatmapPrePCANorm
plt.imshow( data , cmap = 'inferno' , vmin = 0.2, vmax = 0.6, interpolation = 'nearest' )
# color schemes that work well (cmap =): cividis, viridis, inferno. Full list: https://matplotlib.org/stable/tutorials/colors/colormaps.html
plt.title( "Transcript 0: PrePCA Normalized Heatmap" )
plt.show()

# PostPCA Heatmap
x = 100
y = 100
heatmapPostPCANorm = np.zeros(shape=(y, x))
for i in range(y):
  for j in range(x):
    heatmapPostPCANorm[i,j] = heatmapPostNorm[i,j]
data = heatmapPostPCANorm
plt.imshow( data , cmap = 'inferno' , vmin = 0.1, vmax = 0.46, interpolation = 'nearest' )
# color schemes that work well (cmap =): cividis, viridis, inferno. Full list: https://matplotlib.org/stable/tutorials/colors/colormaps.html
plt.title( "Transcript 0: PostPCA Normalized Heatmap" )
plt.show()

heatmapdf = pd.DataFrame(data=heatmap)
heatmapdf.to_csv('heatmap.csv')
heatmapPostdf = pd.DataFrame(data=heatmapPost)
heatmapPostdf.to_csv('reduced_heatmap_0.csv')
heatmapPrePCANormdf = pd.DataFrame(data=heatmapPreNorm)
heatmapPrePCANormdf.to_csv('heatmapPreNorm.csv')
heatmapPostPCANormdf = pd.DataFrame(data=heatmapPostNorm)
heatmapPostPCANormdf.to_csv('heatmapPostNorm.csv')

# Test Code
# transcript_list = [] # contains 44 transcripts
# for transcript in transcripts[0:3]:    
#   transcript_list.append(sent_tokenize(transcript))

# Test Code

# fullTranscripts = pd.DataFrame(fullTranscripts)
# fullTranscripts.to_csv('fullTranscripts.csv')

# embedding = pd.DataFrame(embedding)
# embedding.to_csv('embedding.csv')

# reduced_embedding = pd.DataFrame(reduced_embedding)
# reduced_embedding.to_csv('reduced_embedding.csv')

filteredSentences = filter_Sentences(fullTranscripts, 6)

# running KMeans
kmeans(reduced_embedding, fullTranscripts)