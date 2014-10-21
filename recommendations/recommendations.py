# coding=utf-8
from math import sqrt

__author__ = '4ikist'
# todo comment each method

critics = {'Lisa Rose': {'Lady in the Water': 2.5,
                         'Snakes оn а Plane': 3.5,
                         'Just My Luck': 3.0,
                         'Superman Returns': 3.5,
                         'You, Ме and Dupree': 2.5},

           'Gene Seymour': {'Lady in the Water': 3.0,
                            'Snakes оn а Plane': 3.5,
                            'Just My Luck': 1.5,
                            'Superman Returns': 5.0,
                            'You, Ме and Dupree': 3.5},

           'Michael Philips': {'Lady in the Water': 2.5,
                               'Snakes оn а Plane': 3.0,
                               'The Night Listener': 4.0,
                               'Superman Returns': 3.5},

           'Claudia Puig': {'Snakes оn а Plane': 3.5,
                            'Just My Luck': 3.0,
                            'Superman Returns': 4.0,
                            'You, Ме and Dupree': 2.5,
                            'The Night Listener': 4.5},

           'Mick LaSalle': {'Lady in the Water': 3.0,
                            'Snakes оn а Plane': 4.0,
                            'Just My Luck': 2.0,
                            'Superman Returns': 3.0,
                            'You, Ме and Dupree': 2.0,
                            'The Night Listener': 3.0},

           'Jack Matthews': {'Lady in the Water': 3.0,
                             'Snakes оn а Plane': 4.0,
                             'Just Mu Luck': 3.0,
                             'Superman Returns': 5.0,
                             'You, Ме and Dupree': 3.5,
                             'The Night Listener': 3.0},

           'Toby': {'Snakes оn а Plane': 4.5,
                    'Superman Returns': 4.0,
                    'You, Ме and Dupree': 1.0}
}


# evklid distance
def evklid_sim_distance(prefs, person1, person2):
    """
    return evklid distance between two objects in pref
    :param prefs - preferences like {person1:{pref_name:value of this pref, ...}, person2:{...}}
    :param person1, person2 -  names of persons in prefs
    """
    sim = {}
    for item in prefs[person1].iterkeys():
        if item in prefs[person2]:
            sim[item] = 1
    if not len(sim): return 0

    sum_of_squares = sum(
        [pow(prefs[person1][item] - prefs[person2][item], 2) for item in prefs[person1] if item in prefs[person2]])

    return 1 / (1 + sum_of_squares)


#pearson distance
def pearson_sim_distance(prefs, person1, person2):
    """
    Вычисляет коэффииент корреляции Пирсона для двух персон.
    Коэффициент корреляции - то насколько близко к прямой находятся оцененые объектаами субъекты
    returning value in [-1;1]
    """
    #список предметов оцененных обоими
    si = dict([(item, 1) for item in prefs[person1].iterkeys() if item in prefs[person2]])
    #длина этого списка и если она равна 0, воввращаем 0
    n = len(si)
    if not n:
        return 0

    sum1, sum2, sumSq1, sumSq2, sumP = 0, 0, 0, 0, 0
    for it in si:
        attr_val_1 = prefs[person1][it]
        attr_val_2 = prefs[person2][it]
        #сумма всех предпочтений для разных обхектов
        sum1 += attr_val_1
        sum2 += attr_val_2
        #квадраты сумм
        sumSq1 += pow(attr_val_1, 2)
        sumSq2 += pow(attr_val_2, 2)
        #произведение сумм
        sumP += attr_val_1 * attr_val_2

    num = sumP - (sum1 * sum2 / n)
    den = sqrt((sumSq1 - pow(sum1, 2)) * (sumSq2 - pow(sum2, 2)))
    if den == 0: return 0

    return float(num) / den


def jakkar_sim_distance(prefs, person1, person2):
    """
    Возвращает коэффициент Жаккара между думя персонами
    """
    a = len(prefs[person1])
    b = len(prefs[person2])
    c = len(set(prefs[person1].keys()).intersection(set(prefs[person2].keys())))
    return float(c) / (a + b - c)

def manhattan_sim_distance(prefs, person1, person2):
    """
    Возвращает манхэттенское расстояние между двумя объектами
    """
    result = 0
    for k,v in prefs[person1].iteritems():
        if k in prefs[person2]:
            result+=abs(v-prefs[person2][k])
    return float(result)

def topMatches(prefs, person, n=5, similarity=evklid_sim_distance):
    """
    evaluating n maximum similarity to person in prefs. Using similarity engine
    """
    scores = [similarity(prefs, person, other) for other in prefs if other != person]
    scores.sort()
    scores.reverse()
    return scores[0:n]


def getRecommendations(prefs, person, similarity=evklid_sim_distance):
    """
    evaluating recommendations of prefs objects to person. using similarity
    """
    totals = {}
    simSums = {}
    for other in prefs:
        if other == person: continue

        sim = similarity(prefs, other, person)
        if sim <= 0: continue

        for item in prefs[other]:
            if item not in prefs[person] or prefs[person][item] == 0:
                #the coefficient of similarity * rating
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item] * sim

                simSums.setdefault(item, 0)
                simSums[item] += sim
    rankings = [(total / simSums[item], item) for item, total in totals.items()]
    rankings.sort()
    rankings.reverse()
    return rankings


def transformPrefs(prefs):
    """
    transforming preferences -> persons become objects, objects become persons
    """
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})
            result[item][person] = prefs[person][item]
    return result


#
def calculateSimilarItems(prefs, n=10, similarity=evklid_sim_distance):
    """
    calculating similarity for objects/ for any object in prefs on similarity function calculating n top matches
    """
    result = {}
    itemPrefs = transformPrefs(prefs)

    for item in itemPrefs:
        scores = topMatches(itemPrefs, item, n=n, similarity=similarity)
        result[item] = scores
    return result


def getRecommendationsItems(prefs, itemMatch, user):
    """
    calculating recommendations for items
    """
    userRatings = prefs[user]
    scores = {}
    totalSim = {}
    #for items in objects which ratings of user
    for (item, rating) in userRatings.items():
        #for items which sim this item
        for (similarity, sim_item) in itemMatch[item]:
            if sim_item in userRatings: continue
            scores.setdefault(sim_item, 0)
            scores[sim_item] += similarity * rating

            totalSim.setdefault(sim_item, 0)
            totalSim[sim_item] += similarity

    rankings = [(score / totalSim[item], item) for item, score in scores.items()]
    rankings.sort()
    rankings.reverse()
    return rankings


if __name__ == '__main__':
    print evklid_sim_distance(critics, 'Lisa Rose', 'Gene Seymour')
    print pearson_sim_distance(critics, 'Lisa Rose', 'Gene Seymour')
    print jakkar_sim_distance(critics, 'Lisa Rose', 'Gene Seymour')
    print manhattan_sim_distance(critics, 'Lisa Rose', 'Gene Seymour')
    print getRecommendations(critics, 'Lisa Rose', similarity=evklid_sim_distance)
    print getRecommendations(critics, 'Lisa Rose', similarity=pearson_sim_distance)
    print getRecommendations(critics, 'Lisa Rose', similarity=jakkar_sim_distance)
    print getRecommendations(critics, 'Lisa Rose', similarity=manhattan_sim_distance)

