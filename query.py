# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import sys
import os
sys.path.append("../")
from whoosh.index import create_in, open_dir
from whoosh import qparser
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh.fields import Schema, TEXT
from jieba.analyse import ChineseAnalyzer
from ques import get_ques_keyword
from whoosh import analysis,scoring
from collections import OrderedDict
analyzer = ChineseAnalyzer()
stopword_list = []
with open("resources/stopwords.txt", 'r') as f:
    for word in f:
        stopword_list.append(word.strip())
def creat_index():
    schema = Schema(title=TEXT(stored=True), id=TEXT(stored=True),
                    content=TEXT(stored=True, analyzer=analyzer))
    if not os.path.exists("index"):
        os.mkdir("index")

    ix = create_in("index", schema)  # for create new index
    #ix = open_dir("tmp") # for read only
    writer = ix.writer()
    with open('resources/AA/std_zh_wiki_00', 'r') as fd0:
        for line in fd0:
            text = line.strip().split('\t')
            if len(text) > 2:
                writer.add_document(
                    title=text[1],
                    id=text[0],
                    content=text[2])
            else:
                pass
    print(1)
    with open('resources/AA/std_zh_wiki_01', 'r') as fd1:
        for line in fd1:
            text = line.strip().split('\t')
            if len(text) > 2:
                writer.add_document(
                    title=text[1],
                    id=text[0],
                    content=text[2])
            else:
                pass
    print(2)
    with open('resources/AA/std_zh_wiki_02', 'r') as fd2:
        for line in fd2:
            text = line.strip().split('\t')
            if len(text) > 2:
                writer.add_document(
                    title=text[1],
                    id=text[0],
                    content=text[2])
            else:
                pass
    print(3)
    writer.commit()
def Search(ques):
    ix = open_dir('index')
    searcher = ix.searcher()
    keyword = get_ques_keyword(ques)
    print(keyword)
    key_word = []
    for word in keyword:
        if word not in stopword_list:
            key_word.append(word)
    need_find = ' '.join(key_word)
    og = qparser.OrGroup.factory(0.9)
    parser2 = qparser.QueryParser("content", schema=ix.schema, group=og)
    q2 = parser2.parse(need_find)
    result_content = searcher.search(q2, limit = 10)
    vd = []
    for hit in result_content:
        vd.append((hit["id"],hit["title"],hit["content"]))
    return vd

def Search_index(ind):
    ix = open_dir('index')
    searcher = ix.searcher()
    parser = QueryParser("id", schema=ix.schema)
    q = parser.parse(ind)
    result = searcher.search(q)
    print(len(result))
    return result[0]["content"]

def Search_sentence(ques):
    stopword = ['谁', '什', '么', '几', '多', '少', '是', '的', '哪', '个', '啊', '']
    #ques_list = [u'公元1653年，清顺治帝派谁出任湖广云贵等五省经略']
    #ques = ques_list[0]
    ix = open_dir('index')
    searcher = ix.searcher()
    ans = Search(ques)
    #ans = vd
    print("over")
    # ix = open_dir('index')
    # searcher = ix.searcher()
    parser = QueryParser("id", schema=ix.schema)
    all_con = []
    for hit in ans:
        q = parser.parse(hit[0])
        result = searcher.search(q)
        if len(result) == 1:
            content = result[0]["title"] + result[0]["content"]
            # print("1")
            con_sep = re.split(r'。|！|？', content)
            # print("w")
            # print(con_sep)
            for sen in con_sep:
                if len(sen) > 0:
                    all_con.append((result[0]["id"], result[0]["title"] + sen))
        else:
            print("something wrong")
    pattern = re.compile(r'(?![\\p{P}\\p{S}])[\u4e00-\u9fa50-9A-Za-z]')
    q = pattern.findall(ques)
    q_w = []
    i = 0
    while i < (len(q)):
        num = ''
        en_word = ''
        if q[i].isdigit():
            while q[i].isdigit():
                num += q[i]
                i += 1
        if len(num) > 0:
            q_w.append(num)

        if q[i].isalpha():
            while q[i].isdigit():
                en_word += q[i]
                i += 1
        if len(num) > 0:
            q_w.append(en_word)
        if q[i] not in stopword:
            q_w.append(q[i])
        i += 1
    print(q_w)
    index = 0
    score = dict()
    for Id, sentence in all_con:
        for i in range(len(q_w)):
            if q_w[i] in sentence:
                if q_w[i].isdigit() and len(q_w[i]) >= 3:
                    if index in score:
                        score[index] += 5
                    else:
                        score[index] = 5
                elif q_w[i].isalpha():
                    if index in score:
                        score[index] += 3
                    else:
                        score[index] = 3
                else:
                    if index in score:
                        score[index] += 1
                    else:
                        score[index] = 1
        index += 1
    #print(score)
    can_ans = sorted(score.items(), key=lambda x: x[1], reverse=True)[:20]
    result = []
    for Ans in can_ans:
        #print(all_con[Ans[0]][0], all_con[Ans[0]][1])
        result.append((all_con[Ans[0]][0], all_con[Ans[0]][1]))
        #print('\n')
    return result
def main():
    ques_list = ['黄梅戏中经典选段《天仙配》“树上的鸟儿成双对”的下一句是',"《孔子家语》中”良药苦口利于病“，的下一句.", '少壮不努力“的下一句是', '1976唐山大地震的损失估计有多少美元',
                 '2012年获得诺贝尔文学奖的中国作家是谁']
    print(Search(ques_list[0]))
    ans = Search_sentence(ques_list[0])
    print(ans)

if __name__ == '__main__':
    main()
