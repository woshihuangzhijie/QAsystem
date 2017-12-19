from __future__ import unicode_literals
import classify
import getans
import query
import re
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
from whoosh import analysis, scoring
from collections import OrderedDict
import random
stopword_list = []
x = 1
with open("resources/stopwords.txt", 'r') as f:
    for word in f:
        stopword_list.append(word.strip())
fd = open("close1.txt", 'w')
ix = open_dir('index')
searcher = ix.searcher()
#with open('/Users/huangzhijie/AnacondaProjects/webQA/resources/wdm_assignment_3_samples.txt','r') as infile:
with open('test.txt', 'r') as infile:
    for l in infile:
        text = ''
        ques = l.strip()
        #ques = l.strip().split('\t')[0]
        ques = "芙蓉鲫鱼是湘菜还是粤菜?"
        if ques == '':
            continue
        if "下一句" in ques or "下句" in ques or "上一句" in ques or "上句" in ques:
            Q1 = ques.replace(u'“', '"')
            Q2 = Q1.replace(u'”', '"')
            print(Q2)
            e1 = -1
            for i in range(len(Q2)):
                if Q2[i] == '"':
                    e1 = i
            if e1 == -1:
                need_find = Q2
            else:
                need_find = Q2[(Q2.index('"') + 1):e1]
        else:
            #ques = "被称为“地球之肺”的是哪片位于南美洲的热带雨林"
            keyword = get_ques_keyword(ques)
            #print(keyword)
            key_word = []
            for word in keyword:
                if word not in stopword_list:
                    key_word.append(word)
            need_find = ' '.join(key_word)
        og = qparser.OrGroup.factory(0.9)
        parser2 = qparser.QueryParser("content", schema=ix.schema, group=og)
        q2 = parser2.parse(need_find)
        result_content = searcher.search(q2, limit=10)
        res = []
        for hit in result_content:
            res.append((hit["id"], hit["title"], hit["content"]))
        stopword = ['谁', '什', '么', '几', '多', '少', '是', '的', '哪', '个', '啊', '']
        #print("over")
        #print(res)
        all_con = []
        for result in res:
            content = result[2]
            con_sep = re.split(r'。|！|？', content)
            for sen in con_sep:
                if len(sen) > 0:
                    all_con.append((result[0], result[1] + sen))
        pattern = re.compile(r'(?![\\p{P}\\p{S}])[\u4e00-\u9fa50-9A-Za-z]')
        q = pattern.findall(ques)
        q_w = []
        i = 0
        while i < (len(q)):
            num = ''
            en_word = ''
            if i < len(q) and q[i].isdigit():
                while i < len(q) and (q[i].isdigit() or q[i] == '.'):
                    num += q[i]
                    i += 1
            if len(num) > 0:
                q_w.append(num)
            if i < len(q) and q[i].isalpha():
                while i < len(q) and q[i].isdigit():
                    en_word += q[i]
                    i += 1
            if len(num) > 0:
                q_w.append(en_word)
            if i < len(q) and q[i] not in stopword:
                q_w.append(q[i])
            i += 1
        #print(q_w)
        index = 0
        score = dict()
        for Id, sentence in all_con:
            for i in range(len(q_w)):
                if q_w[i] in sentence:
                    s = re.compile(r'^ (-?\d+)(\.\d+)?$')
                    if  re.match(s, q_w[i]) and len(q_w[i]) >= 3:
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
        for hit in result:
            text += hit[1]
        quesType = classify.gettype(ques)
        print(result)
        print(quesType)
        ans = ''
        if quesType == '国家':
            ans = getans.getansCountry(ques, result, keyword)
        elif quesType == '地点':
            ans = getans.getansPlace(ques, result, keyword, ['ns','nz', 'nt', 'nsf'])
        elif quesType == '下一句':
            ans = getans.getansNext(ques, result, keyword)
        elif quesType == '谁':
            ans = getans.getans1(ques, result, keyword, ['nr'])
        elif quesType == '时间':
            ans = getans.getansTime(ques, result, keyword, ['t'])
        elif quesType == '数字':
            ans = getans.getans1(ques, result, keyword, ['m', 'mq'])
        elif quesType == '颜色':
            ans = getans.getansColor(ques, result, keyword)
        elif quesType == '是否':
            ans = random.randint(0, 1)
            if ans == 1:
                ans = '是'
            else:
                ans = '否'
        else:
            
            ans = getans.getans0(ques, text, keyword)
        fd.write(ans + '\n')
        print(x,quesType,ans)
        x += 1
        break
    
