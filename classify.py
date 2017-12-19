# -*- coding: UTF-8 -*-
import re
from collections import defaultdict

typeDict = defaultdict(list)
index = 0
name = ''
with open('typelist.txt', 'r') as typefile :
    for line in typefile:
        line = line.strip()
        if line == '':
            continue
        if index % 2 == 0:
            name = line
        else:
            # tmp.pre = typefile.readline().strip('\n')
            # tmp.rank = int(typefile.readline().strip('\n'))
            typeDict[name].append(line.split(' '))
            # tmp.apattern = typefile.readline().strip('\n').split(' ')
            name = ''
        index += 1

def gettype(ques):
    for key in typeDict:
        for pattern in typeDict[key][0]:
            if pattern in ques:
                return key
    return ''


if __name__ == '__main__':
    ques = u'阿根廷国家足球队赢得过多少次美洲杯冠军'
    text = u'阿根廷是全世界最成功的国家足球队之一，曾夺得2届世界杯冠军，奥运金牌等，阿根廷队史上的马拉多纳、梅西为世纪球王。 阿根廷是巴西之外南美洲另一个足球天王强国，曾经进入过5次世界杯决赛：包括1930年首届世界杯，以2-4败于乌拉圭：至1978年阿根廷以东道主身份，先在第二轮小组赛压倒巴西晋级决赛，决赛再以3-1击败连续两届都打进决赛的荷兰首次夺得世界杯；1986年，阿根廷在名将马拉多纳领导下，先在八强赛富争议地以2-1淘汰英格兰，最后在决赛以3-2击败西德再登颁奖台，4年后再次晋级决赛，但这届阿根廷被指运气多于实力，结果决赛再遇西德以0-1败阵卫冕失败。自1990年之后20余年，阿根廷一直与世界杯决赛无缘，2002年世界杯更在首轮小组赛出局，而2006年及2010年世界杯，阿根廷连续两届在八强赛被德国淘汰。2014年世界杯，阿根廷在梅西的带领之下再次打进决赛，但以0比1败给德国，无缘大力神杯，成为世界杯史上第一支连续三届都遭到同一个对手淘汰的球队。 另外阿根廷是迄今第二支夺得最多美洲杯冠军的球队，共14次夺冠（仅次于乌拉圭），在2004年和2008年二届奥运足球赛中，分别击败巴拉圭和尼日利亚赢得奥运金牌，而1928年及1996年得到银牌。 其他锦标包括6次夺得世青杯冠军（1977年、1979年、1995年、1997年、2001年及2005年、2007年），1992年夺得联合会杯。'

    quesType = gettype(ques)
    # print('type list len:', len(typeDict))
    ans = getans(ques, text, quesType)
    print(ans)
