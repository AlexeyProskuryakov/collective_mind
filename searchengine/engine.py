# coding=utf-8
from collections import defaultdict, Iterable
from urlparse import urljoin, urlparse
from redis.client import StrictRedis
import requests
from bs4 import BeautifulSoup
from pymorphy2 import tokenizers

__author__ = '4ikist'


def is_resident_link(page_url, link):
    try:
        parsed_uri_page = urlparse(page_url)
        domain_page = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri_page)
        parsed_uri_page_link = urlparse(link)
        domain_link = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri_page_link)
        return domain_page == domain_link
    except UnicodeEncodeError as e:
        return False


id = lambda x: hash(x)
word_location = lambda x: 'words_in_url:%s' % x
url_location = lambda x: 'urls_with_word:%s' % x
link = lambda x, y: '%s->%s' % (x, y)

from_ = lambda x: '%s>' % x
_to = lambda x: '>%s' % x

ignore_words = []


class DataBaseHandler(object):
    def __init__(self, truncate=False):
        self.redis = StrictRedis(db=15)
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
        return self.redis.hgetall(url_location(word_id))


class Crawler(object):
    def __init__(self, db):
        self.db = db

    def get_entry_id(self, table, field, value, create_new=True):
        return None

    def add_to_index(self, url, soup):
        if self.is_indexed(url): return
        print "Indexing %s" % url
        text = self.get_text_only(soup)
        words = self.separate_words(text)
        url_id = self.db.add_url(url)
        for i, word in enumerate(words):
            if word not in ignore_words:
                words_id = self.db.add_word(word)
                self.db.set_word_location(url_id, words_id, i)

    def get_text_only(self, soup):
        #todo use some more good renderer like html 2 text
        v = soup.string
        if v is None:
            elements = []
            for el in soup.contents:
                try:
                    soup_element = self.get_text_only(el).encode('utf-8', errors='ignore')
                    elements.append(soup_element)
                except Exception as e:
                    continue
            result_text = '\n'.join(elements)
            return result_text
        return v.strip()

    def separate_words(self, text):
        print text
        return tokenizers.simple_word_tokenize(text)

    def is_indexed(self, url):
        return self.db.is_url_saved(url) and self.db.get_words_locations_in_(url)

    def add_link_ref(self, url_from, url_to, link_text):
        self.db.set_link(url_from, url_to, link_text)

    def crawl(self, pages, depth=2, only_resident=False):
        for i in range(depth):
            new_pages = set()
            for page in pages:
                loaded_page = requests.get(page)
                if loaded_page.status_code != 200:
                    print "some error while loading %s" % page
                    continue
                soup = BeautifulSoup(loaded_page.content)
                self.add_to_index(page, soup)
                links = soup.find_all('a')
                for link in links:
                    if 'href' in dict(link.attrs):
                        url = urljoin(page, link['href'])
                        if url.find("'") != -1: continue
                        url = url.split('#')[0]
                        if url[:4] == 'http' and not self.is_indexed(url):
                            if (only_resident and is_resident_link(page, url)) or not only_resident:
                                new_pages.add(url)
                        link_text = self.get_text_only(link)
                        self.add_link_ref(page, url, link_text)
            pages = new_pages


def _union_dict_values(one, two):
    """
    Объединение двух словарей по значениям
    :param one:
    :param two:
    :return:
    """

    def add(acc, object):
        if isinstance(object, Iterable):
            acc.extend(list(object))
        elif object is not None:
            acc.append(object)

    result = defaultdict(tuple)
    for key in set(one.keys() + two.keys()):
        value = []
        add(value, one.get(key))
        add(value, two.get(key))
        result[key] = value
    return result


class Searcher(object):
    def __init__(self, db):
        self.db = db


    def match_rows(self, q):
        words = q.split()
        result_ids = {}
        for word in words:
            locations = self.db.get_urls_locations_of_(word)
            result_ids = _union_dict_values(result_ids, locations)
        result = {}
        for k, v in result_ids.iteritems():
            result[self.db.get_url(k)] = v
        return result


if __name__ == '__main__':
    crawler = Crawler(DataBaseHandler(truncate=True))
    crawler.crawl(['http://lurkmore.to/'], depth=2, only_resident=True)
    # searcher = Searcher(DataBaseHandler())
    # print searcher.match_rows('привет пока')
