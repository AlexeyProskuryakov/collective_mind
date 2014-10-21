# coding=utf-8
import json

__author__ = '4ikist'

import feedparser
import re


brackets = re.compile(r'<[^>]+>')
non_word = re.compile(r'[^a-zA-Zа-яА-Я]')


def __get_words(html):
    txt = brackets.sub('', html)
    words = non_word.split(txt)
    return [word.lower() for word in words if word.strip() != '']


import os
import sys


def get_words_count(url):
    file_path = os.path.join(os.curdir, 'dump', '%s.json' % hash(url))
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            object = json.load(f)
            return object['title'], object['data']
    else:
        data = feedparser.parse(url)
        wc = {}
        for entry in data.entries:
            summary = entry.summary if 'summary' in entry else entry.description
            words = __get_words('%s %s' % (entry.title, summary))
            for word in words:
                wc.setdefault(word, 0)
                wc[word] += 1

        title = data.feed.title if 'title' in data.feed else url
        data = wc
        with open(file_path, 'w') as f:
            json.dump({'title': title, 'data': data}, f)
        return title, data


def process_words(feed_list_filename, out_file_name, min=0.1, max=0.5):
    """
    Read each feed from url and process count of words
    After saving matrix with feed and each word and count
    :param feed_list_filename: file with feed url
    :param out_file_name:
    :param min:
    :param max:
    :return:
    """
    words_count = {}
    words_per_blog = {}
    feed_list_count = 0
    with open(feed_list_filename, 'r') as f:
        for feed_url in f.xreadlines():
            print 'processing url %s' % feed_url
            feed_list_count += 1
            title, blog_words_count = get_words_count(feed_url)
            words_count[title] = blog_words_count
            for word, count in blog_words_count.iteritems():
                words_per_blog.setdefault(word, 0)
                if count > 1:
                    words_per_blog[word] += 1
    word_list = []
    for word, bc in words_per_blog.iteritems():
        frac = float(bc) / feed_list_count
        if frac > min and frac < max: word_list.append(word)

    blog_names = []
    data = []

    with open(out_file_name, 'w') as out:
        out.write('Blog')
        for word in word_list:
            to_write = '\t%s' % word.encode('utf8', errors='ignore')
            out.write(to_write)
        out.write('\n')
        for blog, wc in words_count.iteritems():
            out.write(blog.encode('utf8', errors='ignore'))
            data_el = []
            for word in word_list:
                to_write = '\t%s' % wc.get(word, 0)
                data_el.append(wc.get(word, 0))
                out.write(to_write)

            out.write('\n')
            data.append(data_el)
            blog_names.append(blog)

    return blog_names, word_list, data


if __name__ == '__main__':
    # get_words_count('http://blogs.abcnews.com/theblotter/index.rdf')
    pass