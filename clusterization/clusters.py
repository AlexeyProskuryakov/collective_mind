from math import sqrt
import random
import numpy
from scipy.spatial.distance import cdist


__author__ = '4ikist'


def read_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    colnames = lines[0].strip().split('\t')[1:]
    rownames = []
    data = []
    for line in lines[1:]:
        p = line.strip().split('\t')
        rownames.append(p[0])
        data.append([float(x) for x in p[1:]])
    return rownames, colnames, data


def get_sums(v):
    s_sum = sum(v)
    sq_sum = sum([pow(el, 2) for el in v])
    return s_sum, sq_sum


def sim_pearson(v1, v2):
    """
    evaluate pearson factor
    v1 and v2 must be arrays of some values with equals length
    if less than v1 and v2 faithful
    """
    n = len(v1)
    s1, sq1 = get_sums(v1)
    s2, sq2 = get_sums(v2)
    psum = sum([v1[i] * v2[i] for i in range(n)])
    num = psum - (s1 * s2 / n)
    den = sqrt((sq1 - pow(s1, 2) / n) * (sq2 - pow(s2, 2) / n))
    if den == 0: return 0
    return 1.0 - num / den


class BiCluster(object):
    def __init__(self, vec, left=None, right=None, distance=0.0, id=None):
        self.left = left
        self.right = right
        self.vec = vec
        self.id = id
        self.distance = distance


def heirarchy_clustering(rows, similarity=sim_pearson):
    distances = {}
    current_cluster_id = -1
    clusters = [BiCluster(el, id=i) for i, el in enumerate(rows)]
    cluster_vec_sequence = range(len(clusters[0].vec))
    while len(clusters) > 1:
        print "clusters count: %s" % len(clusters)
        lowest_pair = (0, 1)
        closest = similarity(clusters[0].vec, clusters[1].vec)

        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                if (clusters[i].id, clusters[j].id) not in distances:
                    distances[(clusters[i].id, clusters[j].id)] = similarity(clusters[i].vec, clusters[j].vec)
                d = distances[(clusters[i].id, clusters[j].id)]
                if d < closest:
                    closest = d
                    lowest_pair = (i, j)

        merge_vec = [(clusters[lowest_pair[0]].vec[i] + clusters[lowest_pair[1]].vec[i]) / 2.0 for i in
                     cluster_vec_sequence]
        new_cluster = BiCluster(merge_vec, left=clusters[lowest_pair[0]], right=clusters[lowest_pair[1]],
                                distance=closest, id=current_cluster_id)
        current_cluster_id -= 1
        clusters = [clusters[i] for i in range(len(clusters)) if i not in lowest_pair]
        clusters.append(new_cluster)
    return clusters[0]


def klust(rows, distance=sim_pearson, k=4, iters=100):
    # evaluate min and max values for any point
    ranges = [(min([row[i] for row in rows]), max([row[i] for row in rows])) for i in range(len(rows[0]))]
    # create k random disposition centroids
    clusters = [[random.random() * (ranges[i][1] - ranges[i][0]) + ranges[i][0] for i in range(len(rows[0]))] for j in
                range(k)]
    lastmathces = None
    for t in range(iters):
        print 'iteration %s' % t
        bestmatches = [[] for i in range(k)]
        for j in range(len(rows)):
            row = rows[j]
            bestmatch = 0
            for i in range(k):
                d = distance(clusters[i], row)
                if d < distance(clusters[bestmatch], row): bestmatch = i
                bestmatches[bestmatch].append(j)

        if bestmatches == lastmathces: break
        lastmathces = bestmatches

        # replacing any centroid in center of him elements
        for i in range(k):
            avgs = [0.0] * len(rows[0])
            if len(bestmatches[i]) > 0:
                for rowid in bestmatches[i]:
                    for m in range(len(rows[rowid])):
                        avgs[m] += rows[rowid][m]
                for j in range(len(avgs)):
                    avgs[j] /= len(bestmatches[i])
                clusters[i] = avgs

    return clusters


def kmeans_export(centroids, data, labels):
    """Export kmeans result"""

    res = [[] for i in xrange(len(centroids))]
    d = cdist(numpy.array(data), centroids, 'euclidean')
    for i, l in enumerate(d):
        res[l.tolist().index(l.min())].append((labels[i], data[i]))

    return res


