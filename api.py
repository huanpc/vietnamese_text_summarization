import os

from flask import Flask, request,redirect,jsonify,send_from_directory, abort, request, make_response, url_for
import json

from pyvi.pyvi import ViTokenizer, ViPosTagger
from sqlalchemy import create_engine

MYSQL_DATABASE = {
    'drivername': 'mysql',
    'host': '127.0.0.1',
    'port': '3307',
    'username': 'admin',
    'password': 'qwer4321',
    'database': 'dataset',
    'query': {'charset': 'utf8'}
}
_engine = create_engine('sqlite:///cache')

app = Flask(__name__)


def get_word_from_db(word):
    conn = _engine.connect()
    try:
        result = conn.execute(u"""SELECT * FROM dictionary WHERE word='{word}';""".format(word=word))
        if result.rowcount == 0:
            return None
        result = result.fetchone()
        if result:
            temp = json.loads(result['2_grams'])
            return temp
    except Exception as e:
        print e
        print '%s' % word
    finally:
        conn.close()


def compute_2_N_grams_prob(word_1, word_2):
    word_1_dict = get_word_from_db(word_1)
    if word_1_dict:
        if word_2 in word_1_dict:
            return word_1_dict[word_2]
    return -1


def remove_special_character(text):
    import re
    myre = re.compile(u'[0-9-!@#$></.,:()\"\'\n]+', re.I)
    return myre.sub(u'', text)


def compress_sentence(_sentence):
    t = ViPosTagger.postagging(ViTokenizer.tokenize(_sentence))
    compression_words = []
    previous_topic_word = ''
    max_likelihood_word = ''
    max_likelihood_word_prob = -1
    for _index, item in enumerate(t[0]):
        if item == '':
            continue
        item = item.lower()
        if t[1][_index][0] in 'NMP':
            if max_likelihood_word:
                compression_words.append(max_likelihood_word)
            compression_words.append(item)
            previous_topic_word = item
            max_likelihood_word = ''
            max_likelihood_word_prob = -1
        else:
            likelihood_word_prob = compute_2_N_grams_prob(previous_topic_word, item)
            # not existed in dictionary, so add anyway
            if likelihood_word_prob < 0:
                compression_words.append(item)
            else:
                if likelihood_word_prob > max_likelihood_word_prob:
                    max_likelihood_word = item
                    max_likelihood_word_prob = likelihood_word_prob
        if _index + 1 == len(t[0]):
            if item != compression_words[len(compression_words)-1] and item:
                compression_words.append(item)
    sentences = ''
    for word in compression_words:
        if '_' in word:
            sentences = u'%s %s' % (sentences, word.replace('_', ' '))
        else:
            sentences = u'%s %s' % (sentences, word)
    return sentences


@app.route('/summarizing', methods=['POST'])
def text_summarizing():
    payload = request.get_json()
    if 'text' not in payload:
        return jsonify({"message": "no content provided"})
    compressed_sentences = []
    text = payload['text']
    sentences = text.split('.')
    for sentence in sentences:
        clean_sentence = remove_special_character(sentence)
        compressed_sentence = compress_sentence(clean_sentence)
        compressed_sentences.append(compressed_sentence)
    print 'Result: '
    result = u'.'.join([item for item in compressed_sentences if item])
    return jsonify({"result": result})

def main():
    app.run(host='0.0.0.0', port=2907, debug=True)

if __name__ == "__main__":
    main()