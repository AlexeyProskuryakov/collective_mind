from redis import StrictRedis

__author__ = '4ikist'

id = lambda x: hash(x)
word_location = lambda x: 'words_in_url:%s' % x
url_location = lambda x: 'urls_with_word:%s' % x
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
        self.redis.hset(word_location(url_id), word_id, location)
        self.redis.hset(url_location(word_id), url_id, location)

    def get_words_locations_in_(self, url):
        url_id = id(url)
        self.redis.hgetall(word_location(url_id))

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
        :returns {url_id:location,...}
        """
        word_id = id(word)
        return dict([(int(k), int(v)) for k, v in self.redis.hgetall(url_location(word_id)).iteritems()])
