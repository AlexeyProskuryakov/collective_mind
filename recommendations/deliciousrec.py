import time
import json
import pydelicious

def initialiseUserDict(tag,count=5):
    user_dict={}
    for p1 in pydelicious.get_popular(tag=tag):
        print p1
        for p2 in pydelicious.get_urlposts(p1['url'])[0:count]:
            print p2
            user = p2['user']
            if len(user):
                user_dict[user]={}
    return user_dict

def fillDict(user_dict):
    all_items = {}
    for user in user_dict:
        print 'fill for user:',user
        for i in range(3):
            try:
                posts= pydelicious.get_userposts(user)
                for post in posts:
                    url =post['url']
                    user_dict[user][url] = 1.0
                    all_items[url] = 1
                break
            except:
                print 'Trying..., error for user:',user
                time.sleep(3)
    for ratings in user_dict.values():
        for item in all_items:
            if item not in ratings:
                ratings[item]=0.0
    return user_dict

def load():
    with open("delicious_users.p",'rb') as f:
        data = json.load(f)
    return data

def save(data):
    with open('delicious_users.p','wb') as f:
        json.dump(data,f)


if __name__ == '__main__':
    user_dict = initialiseUserDict('programming',5)
    user_dict = fillDict(user_dict)
    save(user_dict)