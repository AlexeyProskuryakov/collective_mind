__author__ = '4ikist'
import recommendations
import deliciousrec

if __name__ == '__main__':
    users = deliciousrec.load()
    print recommendations.getRecommendations(users, 'wgheath', similarity=recommendations.pearson_sim_distance)