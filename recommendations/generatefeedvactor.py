__author__ = '4ikist'
import re

import feedparser


def get_words(html):
    #removetags
    txt = re.compile(r'<[^>]+>').sub('', html)
    #choose words
    words = re.compile(r'[^A-Z^a-z]+').split(txt)
    return [word.strip().lower() for word in words if len(word)]


def get_words_count(url):
    """
    return header and word dict with counts
    """
    d = feedparser.parse(url)
    wc = {}
    for e in d.entries:
        if 'summary' in e:
            summary = e.summary
        else:
            summary = e.description

        words = get_words(e.title + ' ' + summary)
        for word in words:
            wc.setdefault(word, 0)
            wc[word] += 1
    return d.feed.title, wc

#prepearing words countsin all feed list
feed_list = open('../feedlist.txt', 'r').readlines()
apcount = {}
wordscount = {}
for feed_url in feed_list:
    title, word_count = get_words_count(feed_url)
    wordscount[title] = word_count
    for word, count in word_count.items():
        apcount.setdefault(word, 0)
        if count > 1:
            apcount[word] += 1

word_list = []

more_bound =0.1
less_bound = 0.5
for w, bc in apcount.items():
    frac = float(bc) / len(feed_list)
    if frac>more_bound and frac<less_bound:word_list.append(w)