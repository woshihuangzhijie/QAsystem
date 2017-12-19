import re
from classify import *
from collections import ChainMap
import jieba.posseg
import thulac
import classify

punct = '[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）《》“”：〈-]+'
countryList = ["中华民国", "中国", "苏联", "巴拿马", "所罗门群岛", "斯洛伐克", "贝宁", "圣多美和普林西比", "埃及", "中非", "冈比亚", "以色列", "科特迪瓦", "佛得角", "亚美尼亚", "波斯尼亚", "阿尔巴尼亚", "比利时", "马来西亚", "伊拉克", "苏里南", "津巴布韦", "伊朗", "布隆迪", "巴勒斯坦", "秘鲁", "立陶宛", "几内亚比绍", "智利", "新加坡", "卡塔尔", "利比亚", "萨摩亚", "墨西哥", "朝鲜", "缅甸", "柬埔寨", "英国", "巴西", "阿富汗", "日本", "格鲁吉亚", "巴基斯坦", "爱沙尼亚", "孟加拉", "毛里塔尼亚", "马尔代夫", "匈牙利", "沙特", "尼日尔", "拉脱维亚", "文莱", "哈萨克斯坦", "波兰", "安道尔", "卢森堡", "塞拉利昂", "阿曼", "台湾", "印度", "毛里求斯", "斯洛文尼亚", "韩国", "古巴", "希腊", "蒙古", "纳米比亚", "乍得", "摩纳哥", "埃塞俄比亚", "丹麦", "挪威", "哥伦比亚", "格林纳达", "摩洛哥", "德国", "斯里兰卡", "苏丹", "汤加", "澳大利亚", "新西兰", "叙利亚", "突尼斯", "刚果金", "阿根廷", "阿尔及利亚", "南非", "奥地利", "乌干达", "特立尼达和多巴哥", "喀麦隆", "塞舌尔", "葡萄牙", "保加利亚", "不丹", "东帝汶", "乌拉圭", "委内瑞拉", "瑞士", "玻利维亚",
               "西班牙", "摩尔多瓦", "加纳", "土库曼斯坦", "圭亚那", "吉尔吉斯", "坦桑尼亚", "尼日利亚", "塔吉克斯坦", "乌兹别克斯坦", "阿联酋", "马里", "瑞典", "白俄罗斯", "多哥", "法国", "罗马尼亚", "圣卢西亚", "俄罗斯", "赞比亚", "加蓬", "科威特", "卢旺达", "几内亚", "塞内加尔", "赤道几内亚", "泰国", "瑙鲁", "厄瓜多尔", "老挝", "荷兰", "马耳他", "越南", "尼泊尔", "博茨瓦纳", "利比里亚", "约旦", "多米尼克", "爱尔兰", "也门", "安哥拉", "吉布提", "巴林", "瓦努阿图", "土耳其", "美国", "刚果布", "塞浦路斯", "冰岛", "莱索托", "巴哈马", "意大利", "菲律宾", "索马里", "印尼", "阿塞拜疆", "肯尼亚", "巴巴多斯", "牙买加", "塞尔维亚", "列支敦士登", "密克罗尼西亚", "马其顿", "新几内亚", "黎巴嫩", "斐济", "莫桑比克", "厄立特里亚", "圣马力诺", "布基纳法索", "捷克", "芬兰", "科摩罗", "克罗地亚", "加拿大", "安提瓜和巴布达", "马达加斯加", "乌克兰", "图瓦卢", "圣文森特和格林纳丁斯", "多米尼加", "哥斯达黎加", "基里巴斯", "斯威士兰", "巴拉圭", "帕劳", "马拉维", "萨尔瓦多", "尼加拉瓜", "海地", "南苏丹", "伯利兹", "危地马拉", "洪都拉斯", "黑山共和国", "圣基茨和尼维斯", "梵蒂冈", "马绍尔群岛"]


def calcuScore(text, ans, keywords):
    score = 0
    if ans not in text:
        return 0
    for key in keywords:
        if key in text:
            score += 1
    return score



def getansCountry(line, hitlist, keywords):
    ansDict = dict()
    for hit in hitlist:
        for country in countryList:
            if(country in line):
                continue
            if(country in hit[1]):
                score = calcuScore(hit[1], country, keywords)
                if country in ansDict:
                    ansDict[country] += score
                else:
                    ansDict[country] = score
    if ansDict:
        items = sorted(ansDict.items(), key=lambda x: x[1], reverse=True)
        return items[0][0]
    return ''


def getansPlace(line, hitlist, keywords, type):
    ansDict = dict()
    for hit in hitlist:
        ans = jieba.posseg.cut(hit[1])
        # print('hit:', hit[1])
        for each in ans:
            if(each.flag in type):
                if each.word in line:
                    continue
                if each.word in countryList:
                    continue
                score = calcuScore(hit[1], each.word, keywords)
                if each.word in ansDict:
                    ansDict[each.word] += score
                else:
                    ansDict[each.word] = score
    if ansDict:
        items = sorted(ansDict.items(), key=lambda x: x[1], reverse=True)
        return items[0][0]
    return ''


def getansNext(line, hitlist, keywords):
    pre = re.findall(r'“(.+)”.*下一句', line)
    if len(pre) <= 0:
        return ''
    pattern = pre[0] + r'，' + r'([\u4E00-\u9FA5]+)' + r'\b'
    for hit in hitlist:
        res = re.findall(pattern, hit[1])
        if len(res) > 0:
            return res[0]
    return ''
def getansColor(line, hitlist, keywords):
    for hit in hitlist:
        s = re.compile(r'[\u4E00 -\u9FA5]{,3}色')
        res = re.findall(s, hit[1])
        if len(res) > 0:
            for x in res:
                if x[x.find('色')-1] == '颜':
                    continue
                else:
                    return x
    return ''

def getansTime(line, hitlist, keywords, type):
    ansDict = dict()
    if '哪天' in line:
        for hit in hitlist:
            ans = re.findall('\d+月\d+日', hit[1])
            for each in ans:
                if each in line:
                    continue
                score = calcuScore(hit[1], each, keywords)
                if each in ansDict:
                    ansDict[each] += score
                else:
                    ansDict[each] = score
    else:
        thu1 = thulac.thulac()
        for hit in hitlist:
            ans = thu1.cut(hit[1])
            # print('hit:', hit[1])
            for each in ans:
                if(each[1] in type):
                    if each[0] in line:
                        continue
                    score = calcuScore(hit[1], each[1], keywords)
                    if each[0] in ansDict:
                        ansDict[each[0]] += score
                    else:
                        ansDict[each[0]] = score
    if ansDict:
        items = sorted(ansDict.items(), key=lambda x: x[1], reverse=True)
        return items[0][0]
    return ''

# n-grams


def getNgrams(input, n, line):
    input = re.sub(punct, "", input)
    output = {}
    for i in range(len(input) - n + 1):
        ngramTemp = input[i:i + n]
        if ngramTemp in line:
            continue
        if ngramTemp not in output:
            output[ngramTemp] = 0
        output[ngramTemp] += n
    return output
# def getNgrams(text, n, line, keywords, type):
#     text = re.sub(punct, "", text)
#     output = {}
#     for i in range(len(text) - n + 1):
#         ngramTemp = text[i:i + n]
#         if type == '国家' and ngramTemp not in countryList:
#             continue
#         if ngramTemp in line:
#             continue
#         index = text.find(ngramTemp)
#         score = 1
#         for key in keywords:
#             keyindex = text.find(key, index - 20, index + 20)
#             if keyindex != -1:
#                 score += (20 - abs(index - keyindex))
#         if ngramTemp not in output:
#             output[ngramTemp] = 0
#         output[ngramTemp] += n * score
#     return output


def getans0(line, text, keywords):
#     out = getNgrams(text, 2, line, keywords)
#     out2 = getNgrams(text, 3, line, keywords)
#     merged = ChainMap(out, out2)
#     items = sorted(merged.items(), key=lambda x: x[1], reverse=True)
#     if(len(items) == 0):
#         return ''
#     return items[0][0]
    out = []
    for i in range(2, 11):
        out.append(getNgrams(text, i, line))
    merged = ChainMap(out[0], out[1], out[2], out[3], out[4], out[5],out[6], out[7], out[8])
    items = sorted(merged.items(), key=lambda x: x[1], reverse=True)
    print(items)
    if(len(items) == 0):
        return ''
    for item in items:
        if len(set(item[0]) & set(line)) >= 3:
            continue
        else:
            return item[0]
    return ''

def getans1(line, hitlist, keywords, type):
    ansDict = dict()
    for hit in hitlist:
        #print(hit)
        ans = jieba.posseg.cut(hit[1])
        #print('hit:', hit[1])
        for each in ans:
            if each.flag in type:
                if each.word in line:
                    continue
                score = calcuScore(hit[1], each.flag, keywords)
                if each.word in ansDict:
                    ansDict[each.word] += score
                else:
                    ansDict[each.word] = score
    if ansDict:
        items = sorted(ansDict.items(), key=lambda x: x[1], reverse=True)
        #print(items)
        if classify.gettype(line) == '谁':
            for item in items:
                #print(item[0])
                if len(item[0]) >= 2:
                    return item[0]
                else:
                    continue
        else:
            s = re.compile(r'^(-{0,1}\d+)(\.\d+){0,1}$')
            for item in items:
                if re.match(s, item[0]):
                    return item[0]
                else:
                    continue
    return ''


if __name__ == '__main__':
    ques = u'阿根廷国家足球队赢得过多少次美洲杯冠军'
    text = u'阿根廷是全世界最成功的国家足球队之一，曾夺得2届世界杯冠军，奥运金牌等，阿根廷队史上的马拉多纳、梅西为世纪球王。 阿根廷是巴西之外南美洲另一个足球天王强国，曾经进入过5次世界杯决赛：包括1930年首届世界杯，以2-4败于乌拉圭：至1978年阿根廷以东道主身份，先在第二轮小组赛压倒巴西晋级决赛，决赛再以3-1击败连续两届都打进决赛的荷兰首次夺得世界杯；1986年，阿根廷在名将马拉多纳领导下，先在八强赛富争议地以2-1淘汰英格兰，最后在决赛以3-2击败西德再登颁奖台，4年后再次晋级决赛，但这届阿根廷被指运气多于实力，结果决赛再遇西德以0-1败阵卫冕失败。自1990年之后20余年，阿根廷一直与世界杯决赛无缘，2002年世界杯更在首轮小组赛出局，而2006年及2010年世界杯，阿根廷连续两届在八强赛被德国淘汰。2014年世界杯，阿根廷在梅西的带领之下再次打进决赛，但以0比1败给德国，无缘大力神杯，成为世界杯史上第一支连续三届都遭到同一个对手淘汰的球队。 另外阿根廷是迄今第二支夺得最多美洲杯冠军的球队，共14次夺冠（仅次于乌拉圭），在2004年和2008年二届奥运足球赛中，分别击败巴拉圭和尼日利亚赢得奥运金牌，而1928年及1996年得到银牌。 其他锦标包括6次夺得世青杯冠军（1977年、1979年、1995年、1997年、2001年及2005年、2007年），1992年夺得联合会杯。'

    quesType = gettype(ques)
    # print('type list len:', len(typeDict))
    ans = getans0(ques, text, [])
    print(ans)
