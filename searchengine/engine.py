# coding=utf-8
from collections import defaultdict, Iterable
from urlparse import urljoin, urlparse
import html2text
import requests
from bs4 import BeautifulSoup
from pymorphy2 import tokenizers

from searchengine.database import DataBaseHandler

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


def to_unicode(data):
    if isinstance(data, unicode):
        return data
    elif isinstance(data, str):
        return data.decode('utf8')


ignore_words = []


class Crawler(object):
    def __init__(self, db):
        self.db = db
        self.html2text = html2text.HTML2Text()
        self.html2text.ignore_links = True

    def add_to_index(self, url, soup):
        if self.is_indexed(url): return
        print "Indexing %s" % url
        text = self.get_text_only(soup)
        if text is None: return
        words = self.separate_words(text)
        url_id = self.db.add_url(url)
        for i, word in enumerate(words):
            if word not in ignore_words:
                words_id = self.db.add_word(word)
                self.db.set_word_location(url_id, words_id, i)

    def get_text_only(self, html):
        try:
            text = self.html2text.handle(to_unicode(html))
            return text
        except Exception as e:
            return None

    def separate_words(self, text):
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
                self.add_to_index(page, loaded_page.content)
                links = soup.find_all('a')
                for link in links:
                    if 'href' in dict(link.attrs):
                        url = urljoin(page, link['href'])
                        if url.find("'") != -1: continue
                        url = url.split('#')[0]
                        if url[:4] == 'http' and not self.is_indexed(url):
                            if (only_resident and is_resident_link(page, url)) or not only_resident:
                                new_pages.add(url)
                        link_text = self.get_text_only(link.string)
                        if link_text is not None:
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
        url_and_words = {}
        word_ids = []
        for word in words:
            word_id, locations = self.db.get_urls_locations_of_(word)
            url_and_words = _union_dict_values(url_and_words, locations)
            word_ids.append(word_id)
        return url_and_words, word_ids

    def get_scored_list(self, urls_words, word_ids):
        '''

        :param urls_words:
        :param word_ids:
        :return: {url_id:weight, ...}
        '''
        total_scores = dict([(url_id, 0) for url_id, _ in urls_words.iteritems()])
        weights = [(1.0, Scores.frequency_scores(urls_words))]
        for (weight, scores) in weights:
            for url in total_scores:
                total_scores[url] += weight * scores[url]
        return total_scores

    def query(self, q):
        urls_words, words_ids = self.match_rows(q)
        scores = self.get_scored_list(urls_words, words_ids)
        ranked_scores = sorted([(score, self.db.get_url(url_id)) for url_id, score in scores.iteritems()], reverse=1)
        return ranked_scores


class Scores(object):
    @staticmethod
    def normalize_scores(scores, small_is_better=False):
        small = 0.000001
        if small_is_better:
            min_score = min(scores.values())
            return dict([(url_id, float(min_score) / max(small, l)) for url_id, l in scores.iteritems()])
        else:
            max_score = max(scores.values())
            if max_score == 0: max_score = small
            return dict([(url_id, float(score) / max_score) for url_id, score in scores.iteritems()])

    @staticmethod
    def frequency_scores(rows):
        total_scores = dict([(url_id, len(words_ids)) for url_id, words_ids in rows.iteritems()])
        return Scores.normalize_scores(total_scores)


if __name__ == '__main__':

    searcher = Searcher(DataBaseHandler())
    result = searcher.query(u'привет пока')
    for (score, url_name) in result:
        print score, '\t', url_name

