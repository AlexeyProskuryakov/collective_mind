# coding=utf-8
from collections import Counter
import requests
from searchengine.database import DataBaseHandler
from searchengine.engine import Crawler, Searcher

__author__ = '4ikist'


def test_crawl():
    crawler = Crawler(DataBaseHandler(truncate=True))
    crawler.crawl(['http://lurkmore.to/'], depth=10, only_resident=True)


def test_search():
    searcher = Searcher(DataBaseHandler())
    result = searcher.query(u'привет пока')
    for (score, url_name) in result:
        print score, '\t', url_name


if __name__ == '__main__':
    test_crawl()