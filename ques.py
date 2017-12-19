import jieba.posseg as pseg
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import svm
from sklearn.externals import joblib
import re
import numpy as np
from sklearn.preprocessing import scale
import jieba
import jieba.analyse
# 输入一个问题集，对问题进行分类
#问题集分为几类：人物，时间，事件（其他），数字，地点，国家，诗词接龙
#               0   1   2           3   4       5   6
ques_tag = {
0:'ques_person' ,
1:'ques_time' ,
2:'ques_other',
3:'ques_number' ,
4:'ques_place',
5:'ques_country',
6:'ques_poem'
}
# 问题的一些停用词
stopwords = ["中","的","了","与","和",",","，",".","？","?","\"","“","”"]



# 问题列表, 每个元素都是二元祖（id,problem)
def clasify(ques_list):
    tags = []
    word_list = []
    with open('resources/word.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            word_list.append(line.strip())
    for question in ques_list:
        if "下一句" in question[1] or "下句" in question[1] or "上一句" in question[1] or "上句" in question[1]:
            tags.append(ques_tag[6])
            continue
        if "哪个国家"in question[1] or "哪国" in question[1] or "国家" in question[1]:
            tags.append(ques_tag[5])
            continue
        if "谁" in question[1] or "哪位" in question[1] or "哪个人" in question[1] or "叫" in question[1]:
            tags.append(ques_tag[0])
            continue
        if ("哪里" in question[1] or "哪座城市" in question[1] or "哪所" in question[1] or "何处" in question[1]
        or "在哪" in question[1] or "位于" in question[1] or "地点是" in question[1]):
            tags.append(ques_tag[4])
            continue
        if "哪一年" in question[1] or "何时" in question[1] or "哪年" in question[1] or "什么时候" in question[1] or "生于" in question[1]:
            tags.append(ques_tag[1])
            continue
        if ("多少" in question[1] or "几" in question[1] or "多大" in question[1] or "多远" in question[1]
            or "多快" in question[1] or "多长" in question[1] or "多宽" in question[1] or "多高" in question[1]):
            tags.append(ques_tag[3])
            continue
        if ("哪一事件" in question[1] or "什么意思" in question[1] or "是什么" in question[1]):
            tags.append(ques_tag[2])
            continue
        x = np.zeros(len(word_list))
        for i in range(len(word_list)):
            if word_list[i] in question[1]:
                x[i] = 1.0
        scale(x)
        #print(x)
        clf = joblib.load('resources/clf.pkl')
        y = clf.predict([x])
        tags.append(ques_tag[y[0]])
    return tags

def N_SVM():
    ques = []
    fd = open("resources/wdm_assignment_3_samples.txt", "r")
    lines = fd.readlines()
    i = 0
    for line in lines:
        line = re.split('\t| ', line.strip())
        ques.append((i, line[0]))
    # 获取关键词
    corpus = []
    for Ques in ques:
        tags = pseg.cut(Ques[1])
        tmp = []
        for word in tags:
            if word.word not in stopwords and word.flag not in ['n', 'nr', 'm']:
                tmp.append(word.word)
        corpus.append(' '.join(tmp))
    vectorizer = CountVectorizer()  # 该类会将文本中的词语转换为词频矩阵，矩阵元素a[i][j] 表示j词在i类文本下的词频
    transformer = TfidfTransformer()  # 该类会统计每个词语的tf-idf权值
    tfidf = transformer.fit_transform(
        vectorizer.fit_transform(corpus))  # 第一个fit_transform是计算tf-idf，第二个fit_transform是将文本转为词频矩阵
    word = vectorizer.get_feature_names()  # 获取词袋模型中的所有词语
    weight = tfidf.toarray()  # 将tf-idf矩阵抽取出来，元素a[i][j]表示j词在i类文本中的tf-idf权重
    # for i in range(len(weight)):  # 打印每类文本的tf-idf词语权重，第一个for遍历所有文本，第二个for便利某一类文本下的词语权重
    #     print(u"-------这里输出第", i, u"类文本的词语tf-idf权重------")
    #     for j in range(len(word)):
    #         print(word[j], weight[i][j])
    # print(word)
    # print(len(word))
    with open('resources/word.txt', 'w') as f:
        for w in word:
            f.write(w)
            f.write('\n')

    tag = []
    with open('resources/tag.txt', 'r') as fd:
        lines = fd.readlines()
        for line in  lines:
            tag.append(int(line.strip()))

    clf = svm.SVC(decision_function_shape='ovr')
    clf.fit(weight, tag)
    joblib.dump(clf,'resources/clf.pkl')

def ques_cut(ques):
    return list(jieba.cut(ques))
def get_ques_keyword(ques):
    #cutlist = ques_cut(ques)
    return jieba.analyse.extract_tags(ques, topK=8, withWeight=False, allowPOS=())
if __name__ == '__main__':

    # N_SVM()
    clf = joblib.load('resources/clf.pkl')
    x = np.array([[1]*282])
    scale(x)
    print(clf.predict(x))
