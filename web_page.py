# -*- coding: UTF-8 -*-
import urllib
import re
from bs4 import BeautifulSoup
import requests
from urllib.parse import quote
import ques
import jieba.analyse
import jieba.posseg as pseg

'''
获取百度搜索的结果
'''
def get_html_baidu(query):
    url = 'https://www.baidu.com/s?wd=' + quote(query)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
    try:
        soup_baidu = BeautifulSoup(requests.get(url=url, headers=headers).content.decode('utf-8'), "html5lib")
    except:
        soup_baidu = BeautifulSoup("", "html5lib")
    return soup_baidu


def get_page(query):
    soup_baidu = get_html_baidu(query)
    first_answer = []
    second_answer = []
    for index in range(1, 11):
        result = soup_baidu.find(id=index)
        if result == None:
            break
        # 百度知道
        # print(str(result.get_text()))
        if u'百度知道' in str(result.get_text()) or u'最佳答案' in str(result.get_text()):
            regex = r"href=\"([\s\S]*?url=[\s\S]*?)\""
            url = re.findall(regex, str(result.find('a')))
            if len(url) > 0:
                Ans = get_bd_answer(url[0])
                if Ans == None:
                    second_answer.append(result.get_text())
                else:
                    first_answer.append(Ans)
                    break
            else:
                second_answer.append(result.get_text())
        elif u'百度作业帮' in str(result.get_text()):
            regex = r"href=\"([\s\S]*?url=[\s\S]*?)\""
            url = re.findall(regex, str(result.find('a')))
            if len(url) > 0:
                Ans = get_gd_answer(url[0])
                if Ans == None:
                    second_answer.append(result.get_text())
                else:
                    first_answer.append(Ans)
                    break
            else:
                second_answer.append(result.get_text())
        else:
            second_answer.append(result.get_text())
    if len(first_answer) > 0:
        return first_answer
    elif len(second_answer) > 0:
        return second_answer
    else:
        return ["no answer"]


def get_bd_answer(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
    soup_answer = BeautifulSoup(requests.get(url=url, headers=headers).content,"html5lib")
    #print(soup_answer)

    result = soup_answer.find(class_="bd answer")
    if result == None:
        return None
    if result.find('pre') is not None:
        #print(result.get_text())
        return result.find('pre').get_text()

    else:
        return None


def get_gd_answer(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
    soup_answer = BeautifulSoup(requests.get(url=url, headers=headers).content, "html5lib")
    result = soup_answer.find(id="good-answer")
    if result == None:
        return None
    if result.find('pre') is not None:
        return result.get_text()[9:]
    else:
        return None

def get_answer(Q_list):
    fd = open("open.txt", "w")
    ques_class = ques.clasify(Q_list)
    index = 0
    for Q in Q_list:
        print(index)
        if ques_class[index] == 'ques_poem':
            Q1 = Q[1].replace(u'“', '"')
            Q2 = Q1.replace(u'”', '"')
            print(Q2)
            e1 = -1
            for i in range(len(Q2)):
                if Q2[i] == '"':
                    e1 = i
            if e1 == -1:
                Ques = Q2
            else:
                Ques = Q2[(Q2.index('"') + 1):e1] + "下一句"
            ans_list = get_page(Ques)
            if len(ans_list) == 1:
                if Ques[:-3] in ans_list[0]:
                    start = ans_list[0].index(Ques[:-3]) + len(Ques[:-3])
                    fd.write(ans_list[0][start:(start + 15)] + '\n')
                    continue
        else:
            ans_list = get_page(Q[1])

        if ans_list[0] == "no answer":
            fd.write('no answer' + '\n')
        else:
            if len(ans_list) == 1:
                a = ''.join(ans_list[0].split('\n'))
                #print(a)
                if len(a) <= 30:
                    p2 = re.compile(r'[\.0-9a-zA-Z\u4e00-\u9fa5]')
                    p = p2.findall(a)
                    fd.write((''.join(p))[:20] + '\n')
                else:
                    lans = jieba.analyse.extract_tags(a, topK=50, withWeight=False, allowPOS=(
                        'i', 'I', 'm', 'Ng', 'n', 'nr', 'ns', 'nt', 'nz', 's', 'tg', 't', 'z', 'vn'))
                    l = pseg.cut(''.join(lans))
                    if ques_class[index] == 'ques_person':
                        an = ''
                        i = 0
                        for word in l:
                            if word.flag in ['nr']:
                                if i > 3 or len(an) + len(word.word) + 1 >= 20:
                                    break
                                an += word.word + ' '
                                i += 1
                        fd.write(an + '\n')
                    elif ques_class[index] == 'ques_time' or ques_class[index] == 'ques_number':
                        an = ''
                        for word in l:
                            if word.flag in ['tg', 't', 'm']:
                                if len(an) + len(word.word) + 1 >= 20:
                                    break
                                an += word.word + ' '

                        fd.write(an + '\n')
                    else:
                        p2 = re.compile(r'[0-9a-zA-Z\u4e00-\u9fa5]')
                        p = p2.findall(a)
                        fd.write((''.join(p))[:20] + '\n')

            else:
                ans_str = ''
                for ans in ans_list:
                    ans_str += ans
                lans = jieba.analyse.extract_tags(ans_str, topK=50, withWeight=False, allowPOS=(
                'i', 'I', 'm', 'Ng', 'n', 'nr', 'ns', 'nt', 'nz', 's', 'tg', 't', 'z', 'vn'))
                # 0: 'ques_person',
                # 1: 'ques_time',
                # 2: 'ques_other',
                # 3: 'ques_number',
                # 4: 'ques_place',
                # 5: 'ques_country',
                # 6: 'ques_poem'
                clans = []
                for word in lans:
                    if word in ['百度', '快照', '\n', '...', '答案', '文库', '题库'] or '.' in word or word in Q[1]:
                        pass
                    else:
                        clans.append(word)
                #print(clans)
                l = pseg.cut(''.join(clans))
                if ques_class[index] == 'ques_person':
                    an = ''
                    i = 0
                    for word in l:
                        if word.flag in ['nr']:
                            if i > 3 or len(an) + len(word.word) + 1 >= 20:
                                break
                            an += word.word + ' '
                            i += 1
                    fd.write(an + '\n')
                elif ques_class[index] == 'ques_time':
                    an = ''
                    for word in l:
                        if word.flag in ['tg', 't']:
                            if len(an) + len(word.word) + 1 >= 20:
                                break
                            an +=  word.word + ' '

                    fd.write(an + '\n')
                elif ques_class[index] == 'ques_other':
                    an = ''
                    for word in l:
                        if len(an) + len(word.word) + 1 >= 20:
                            break
                        an += word.word + ' '
                    fd.write(an + '\n')
                elif ques_class[index] == 'ques_number':
                    an = ''
                    for word in l:
                        if word.flag in ['m']:
                            if len(an) + len(word.word) + 1 >= 20:
                                break
                            an +=  word.word + ' '
                    fd.write(an + '\n')
                elif ques_class[index] == 'ques_place' or ques_class[index] == 'ques_country':
                    an = ''
                    for word in l:
                        if word.flag in ['ns', 'nt', 's']:
                            if len(an) + len(word.word) + 1 >= 20:
                                break
                            an +=  word.word + ' '

                    fd.write(an + '\n')
                else:
                    an = ''
                    for word in l:
                        if word.flag in ['i', 'I']:
                            if len(an) + len(word.word) + 1 >= 20:
                                break
                            an +=  word.word + ' '

                    fd.write(an + '\n')
        index += 1
    fd.close()


if __name__ == '__main__':
    ques_list = []
    i = 0
    with open("test.txt", "r") as fd:
        for q in fd:
            ques_list.append((i, q.strip()))
            i += 1
    #print(ques_list[0])
    get_answer(ques_list)
