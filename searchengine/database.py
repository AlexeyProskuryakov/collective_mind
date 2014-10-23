from redis import StrictRedis

__author__ = '4ikist'

id = lambda x: hash(x)
word_location = lambda x: 'words_in_url:%s' % x
url_location = lambda x: 'urls_with_word:%s' % x
url_have_word = lambda url, word: '%s:uw:%s' % (url, word)
link = lambda x, y: '%s->%s' % (x, y)

from_ = lambda x: '%s>' % x
_to = lambda x: '>%s' % x


class DataBaseHandler(object):
    def __init__(self, truncate=False, db_num=15):
        self.redis = StrictRedis(db=db_num)
        if truncate:
            self.redis.flushdb()

    def get_url(self, url_id):
        return self.redis.hget('url_ids', url_id)

    def get_word(self, word_id):
        return self.redis.hget('word_ids', word_id)

    def add_url(self, url):
        url_id = id(url)
        saved = self.redis.hget('url_ids', url_id)
        if not saved:
            self.redis.hset('url_ids', url_id, url)
        return url_id

    def add_word(self, word):
        word_id = id(word)
        saved = self.redis.hget('word_ids', word_id)
        if not saved:
            self.redis.hset('word_ids', word_id, word)
        return word_id

    def set_word_location(self, url_id, word_id, location):
        locations_id = url_have_word(url_id, word_id)
        self.redis.rpush(locations_id, location)
        # url contains words
        self.redis.hset(word_location(url_id), word_id, locations_id)
        # word in urls
        self.redis.hset(url_location(word_id), url_id, locations_id)



    def get_word_location_in_url(self, location_id):
        return [int(el) for el in self.redis.lrange(location_id, 0, -1)]

    def set_link(self, from_url, to_url, via_word):
        from_id = self.add_url(from_url)
        to_id = self.add_url(to_url)
        word_id = self.add_word(via_word)
        self.redis.set(link(from_id, to_id), word_id)
        self.redis.lpush(from_(from_id), to_id)
        self.redis.lpush(_to(to_id), from_id)

    def is_url_saved(self, url):
        return self.redis.get(id(url))

    def get_urls_locations_of_(self, word):
        """
        :returns word_id, {url_id:[locations],...}
        """
        word_id = id(word)
        return word_id, dict([(int(k), self.get_word_location_in_url(v)) \
                              for k, v in self.redis.hgetall(url_location(word_id)).iteritems()])

    def get_words_locations_in_(self, url):
        '''
        :param url:
        :return: url_id, {word_id:[locations]}
        '''
        url_id = id(url)
        return url_id, dict([(int(k), self.get_word_location_in_url(v)) for k, v in
                             self.redis.hgetall(word_location(url_id)).iteritems()])


def test():
    db = DataBaseHandler(truncate=True, db_num=13)

    url = 'http://test/test'
    url_id = db.add_url(url)
    word_id1 = db.add_word('test1')
    word_id2 = db.add_word('test2')
    word_id3 = db.add_word('test3')

    db.set_word_location(url_id, word_id1, 1)
    db.set_word_location(url_id, word_id1, 2)
    db.set_word_location(url_id, word_id1, 3)
    db.set_word_location(url_id, word_id2, 4)
    db.set_word_location(url_id, word_id2, 5)
    db.set_word_location(url_id, word_id2, 6)
    db.set_word_location(url_id, word_id3, 7)
    db.set_word_location(url_id, word_id3, 8)
    db.set_word_location(url_id, word_id3, 9)

    w_id1, url_word_locations1 = db.get_urls_locations_of_('test1')
    w_id2, url_word_locations2 = db.get_urls_locations_of_('test2')
    w_id3, url_word_locations3 = db.get_urls_locations_of_('test3')

    assert w_id1 == word_id1
    assert w_id2 == word_id2
    assert w_id3 == word_id3
    assert url_word_locations1[url_id] == [1, 2, 3]
    assert url_word_locations2[url_id] == [4, 5, 6]
    assert url_word_locations3[url_id] == [7, 8, 9]

    url_id, word_locations = db.get_words_locations_in_(url)


if __name__ == '__main__':
    test()