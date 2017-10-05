# -*- coding: utf-8 -*-
from pyvi.pyvi import ViTokenizer, ViPosTagger
from HTMLParser import HTMLParser
import json
import csv

def parse_html_string(text):
    class MyHTMLParser(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self)
            self.data = ''

        def handle_data(self, data):
            self.data = '%s %s'% (self.data, data)

    parser = MyHTMLParser()
    parser.feed(text)
    return parser.data

def remove_special_character(text):
    import re
    myre = re.compile(u'[0-9-!@#$></.,:()\"\']+', re.I)
    return myre.sub(u'', text)

def compress_sentence(sentence):
    t = ViPosTagger.postagging(ViTokenizer.tokenize(sentence))
    compression_words = []
    previous_topic_word = ''
    max_likelihood_word = ''
    max_likelihood_word_prob = 0
    for index, item in enumerate(t[0]):
        print t[1][index][0]
        if t[1][index][0] in 'NMP':
            compression_words.append(max_likelihood_word)
            compression_words.append(item)
            previous_topic_word = item
            max_likelihood_word = ''
            max_likelihood_word_prob = 0
        else:
            likelihood_word_prob = compute_2_N_grams_prob(previous_topic_word, item)
            if likelihood_word_prob > max_likelihood_word_prob:
                max_likelihood_word = item
                max_likelihood_word_prob = likelihood_word_prob
        if index + 1 == len(t[0]):
            compression_words.append(item)
    return compression_words

def compute_2_N_grams_prob(word_1, word_2):
    return 1

def update_2_grams(word_1, word_2, dictionary=dict()):
    if word_1 in dictionary:
        if word_2 in dict(dictionary[word_1]):
            dictionary[word_1][word_2] += 1
        else:
            dictionary[word_1][word_2] = 1
    else:
        dictionary[word_1] = dict()

dictionary = {}

with open('a1.csv') as csvfile:
    csvreader = csv.DictReader(csvfile, delimiter=',')
    index = 0
    for index, row in enumerate(csvreader):
        content = u''
        try:
            json_body = json.loads(row['body'])
            for item in json_body:
                try:
                    if item and item['type'] == 'text':
                        parsed_text = parse_html_string(item['content'])
                        clean_text = remove_special_character(parsed_text)
                        content = u'{0} {1}'.format(content, clean_text)
                except:
                    pass
        except:
            continue
        tokens, post_tags = ViPosTagger.postagging(ViTokenizer.tokenize(content))
        for index, item in enumerate(tokens):
            if index == 0:
                continue
            update_2_grams(tokens[index-1], item, dictionary)
        if index > 5:
            break
for k, v in dictionary.items():
    print '%s - %s' % (k,v)
