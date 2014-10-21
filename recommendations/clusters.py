# coding: utf-8
__author__ = '4ikist'

from math import sqrt



def read_file(filename):
    """
    reading file in interested format

    """
    lines = open(filename, 'r').readlines()
    colnames = lines[0].strip().split('\t')[1:]
    rownames = []
    data = []
    for line in lines[1:]:
        p = line.strip().split('\t')
        rownames.append(p[0])
        data.append([float(x) for x in p[1:]])
    return rownames, colnames, data


class BigCluster(object):
    def __init__(self, vec, left=None, right=None, distance=0.0, clust_id=None):
        self.vec = vec
        self.left = left
        self.right = right
        self.distance = distance
        self.clust_id = clust_id


def rotate_matrix(data):
    new_data = []
    for i in range(len(data[0])):
        new_row = [data[j][i] for j in range(len(data))]
        new_data.append(new_row)
    return new_data


def hclust(rows, distance=pearson):
    """
    realise heirarhy clussterisation
    """
    distances = {}
    curr_clust_id = -1
    # at first any cluster is string
    clusters = [BigCluster(rows[i], clust_id=i) for i in range(len(rows))]
    while len(clusters) > 1:
        lowest_pair = (0, 1)
        closest = distance(clusters[0].vec, clusters[1].vec)
        # consider all pairs and search pair with minimal distance
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                if (clusters[i].clust_id, clusters[j].clust_id) not in distances:
                    d = distances[(clusters[i].clust_id, clusters[j].clust_id)] = distance(clusters[i].vec,
                                                                                           clusters[j].vec)
                    if d < closest:
                        closest = d
                        lowest_pair = (i, j)
                        # evaluate middle between pair of clusters
        mergevec = [(clusters[lowest_pair[0]].vec[i] + clusters[lowest_pair[1]].vec[i]) / 2.0 for i in
                    range(len(clusters[0].vec))]
        # create new cluster
        new_cluster = BigCluster(mergevec,
                                 left=clusters[lowest_pair[0]],
                                 right=clusters[lowest_pair[1]],
                                 distance=closest,
                                 clust_id=curr_clust_id)

        #identififcator of new clusters is negative
        curr_clust_id -= 1
        clusters = [clusters[i] for i in range(len(clusters)) if i not in lowest_pair]
        clusters.append(new_cluster)

    return clusters[0]


import random


def get_sums(v):
    s_sum = sum(v)
    sq_sum = sum([pow(el, 2) for el in v])
    return s_sum, sq_sum


def pearson(v1, v2):
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





import pickle

if __name__ == '__main__':
    rownames, colnames, data = read_file('../blogs.txt')
    rdata = rotate_matrix(data)
    pickle.dump(rdata, open('../rdata.dump', 'w'))
    print 'matrix was rotated'
    clust = hclust(rdata)
    pickle.dump(clust, open('../clust.dump', 'w'))
    print 'clustering is end'
    hvis.draw_dendogram(clust, labels=rownames)
    print 'drawing is end'