from clusterization.generatefeedvector import process_words
from clusterization.preprocessing import norm
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist
from scipy.cluster import hierarchy

__author__ = '4ikist'

if __name__ == '__main__':
    blog_names, words, data = process_words('feedlist.txt', 'dump\\blog_data.txt', min=0.1, max=0.7)

    print 'words count: %s' % len(words)
    data = norm(data, True)
    # dist_mahalanobis = pdist(data,'mahalanobis')
    dist_euclidean = pdist(data, 'euclidean')
    # dist_chebyshev = pdist(data,'chebyshev')
    # plt.hist(dist_euclidean,500, color='red',alpha=0.5)
    z = hierarchy.linkage(dist_euclidean, method='average')
    plt.figure()
    hierarchy.dendrogram(z, labels=words, color_threshold=.10, leaf_font_size=10, count_sort=True)
    plt.show()
