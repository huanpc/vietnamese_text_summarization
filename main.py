# -*- coding: utf-8 -*-
from pyvi.pyvi import ViTokenizer, ViPosTagger
from HTMLParser import HTMLParser
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
import json
import csv
import time

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
def store_word_to_db(word, two_grams):
    conn = _engine.connect()
    try:
        result = conn.execute("""INSERT INTO dictionary VALUES(null,:word,:grams);""", {'word': word, 'grams': json.dumps(two_grams)})
        return True
    except Exception as e:
        print e
        print '%s' % word
    finally:
        conn.close()

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
    myre = re.compile(u'[0-9-!@#$></.,:()\"\'\n]+', re.I)
    return myre.sub(u'', text)


def compress_sentence(_sentence):
    t = ViPosTagger.postagging(ViTokenizer.tokenize(_sentence))
    compression_words = []
    previous_topic_word = ''
    max_likelihood_word = ''
    max_likelihood_word_prob = -1
    for _index, item in enumerate(t[0]):
        if t[1][_index][0] in 'NMP':
            item = item.lower()
            compression_words.append(max_likelihood_word)
            compression_words.append(item)
            previous_topic_word = item
            max_likelihood_word = ''
            max_likelihood_word_prob = -1
        else:
            likelihood_word_prob = compute_2_N_grams_prob(previous_topic_word, item)
            if likelihood_word_prob > max_likelihood_word_prob:
                max_likelihood_word = item
                max_likelihood_word_prob = likelihood_word_prob
        if _index + 1 == len(t[0]):
            if item not in compression_words:
                compression_words.append(item)
    return u' '.join(compression_words)

def compute_2_N_grams_prob(word_1, word_2):
    word_1_dict = get_word_from_db(word_1)
    if word_1_dict:
        if word_2 in word_1_dict:
            return word_1_dict[word_2]
    return 0

def update_2_grams(word_1, word_2, _dictionary=dict()):
    word_1 = word_1.lower()
    word_2 = word_2.lower()
    if word_1 in _dictionary:
        if word_2 in dict(_dictionary[word_1]):
            _dictionary[word_1][word_2] += 1
        else:
            _dictionary[word_1][word_2] = 1
    else:
        _dictionary[word_1] = dict()

# dictionary = {}
# dataset_len = 10000
# start_time = time.time()
# print '####### Build dictionary #######'
# with open('a1.csv') as csvfile:
#     csvreader = csv.DictReader(csvfile, delimiter=',')
#     for index, row in enumerate(csvreader):
#         content = u''
#         try:
#             json_body = json.loads(row['body'])
#             for item in json_body:
#                 try:
#                     if item and item['type'] == 'text':
#                         parsed_text = parse_html_string(item['content'])
#                         clean_text = remove_special_character(parsed_text)
#                         content = u'{0} {1}'.format(content, clean_text)
#                 except:
#                     pass
#         except:
#             continue
#         tokens, post_tags = ViPosTagger.postagging(ViTokenizer.tokenize(content))
#         for _index, item in enumerate(tokens):
#             if _index == 0:
#                 continue
#             update_2_grams(tokens[_index-1], item, dictionary)
#         print '----> %s ' % (index*100/dataset_len)
#
# with open('a2.csv') as csvfile:
#     csvreader = csv.DictReader(csvfile, delimiter=',')
#     for index, row in enumerate(csvreader):
#         content = u''
#         try:
#             json_body = json.loads(row['body'])
#             for item in json_body:
#                 try:
#                     if item and item['type'] == 'text':
#                         parsed_text = parse_html_string(item['content'])
#                         clean_text = remove_special_character(parsed_text)
#                         content = u'{0} {1}'.format(content, clean_text)
#                 except:
#                     pass
#         except:
#             continue
#         tokens, post_tags = ViPosTagger.postagging(ViTokenizer.tokenize(content))
#         for _index, item in enumerate(tokens):
#             if _index == 0:
#                 continue
#             update_2_grams(tokens[_index-1], item, dictionary)
#         print '----> %s ' % (index*100/dataset_len)
#
# print 'Total key %s' % len(dictionary.keys())
# print 'Total time %s minutes' % ((time.time()-start_time)/60)
# print '####### Store dictionary to database #######'
# start_time = time.time()
# # with open('dict.csv', 'a') as csvfile:
#     # writer = csv.DictWriter(csvfile, fieldnames=['word', '2_grams'], delimiter=',', quoting=csv.QUOTE_ALL)
#     # writer.writeheader()
# for _word, _two_grams in dictionary.items():
#     # for row in dictionary:
#         # _word = _word.decode('utf-8')
#     store_word_to_db(_word, _two_grams)
#         # writer.writerow(row)
# print 'Total time %s minutes' % ((time.time()-start_time)/60)

start_time = time.time()
print '####### Text summarize #######'
text = u"""
Tôi lớn lên ở xóm chợ, một xóm nhỏ nằm ven tuyến quốc lộ 10 nối từ Hải Phòng sang Thái Bình.

Như ngàn vạn xóm nghèo khác, người dân trong xóm nghiễm nhiên coi mọi không gian trên lòng, lề đường là nơi buôn bán, mưu sinh.

Nhất cận thị, nhị cận giang, ai cũng nghĩ như vậy nên người đến mua đất, xây nhà, làm quán quanh chợ dần đông hơn. Nhưng đường sá thì ngày càng hẹp đi, nhếch nhác và nguy hiểm. Chúng tôi may mắn lớn lên bình an. Nhưng có nhiều gia đình không có được niềm hạnh phúc ấy.

Tôi vẫn nhớ như in một buổi sáng cuối năm, đó là phiên chợ Tết. Người dân bày đủ thứ, từ bóng bay, hoa thược dược, gà, ngan, gạo nếp... ra ven đường để bán. Chợ mới họp được chừng hai tiếng thì một chiếc xe tải, trong khi cố tránh những gánh hàng rong, đã đâm vào quán cắt may của ông Quỳnh thương binh. Ông Quỳnh chỉ còn một chân nên không kịp chạy. Trong thoáng chốc, tử thần như đã điểm danh. Nhưng ông Quỳnh không chết, nạn nhân thiệt mạng hôm ấy là chị Luyến người ở xã khác. Chị Luyến đi ra khu chợ may đồ để chuẩn bị lấy chồng.
"""
compressed_sentences = []
sentences = text.split('.')
for sentence in sentences:
    clean_sentence = remove_special_character(sentence)
    compressed_sentence = compress_sentence(clean_sentence)
    compressed_sentences.append(compressed_sentence)
print 'Result: '
print u' '.join(compressed_sentences)
print 'Total time %s minutes' % ((time.time()-start_time)/60)

# t = ViPosTagger.postagging(text)
# for index, item in enumerate(t[0]):
#     print '%s - %s' % (item, t[1][index])