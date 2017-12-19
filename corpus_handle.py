import os
import logging
import re
import jieba.analyse
import jieba
import sys
import codecs
from collections import defaultdict
import json
def filte(input_file, output_file):
    p1 = re.compile('（')
    p2 = re.compile('）')
    p3 = re.compile('「')
    p4 = re.compile('」')
    p5 = re.compile('<doc (.*)>')
    p6 = re.compile('</doc>')
    p7 = re.compile('\n')
    p8 = re.compile('\t')
    outfile = codecs.open(output_file, 'w', 'utf-8')
    #index = 0
    flag = 1
    #index = 256625
    index = 874927
    with codecs.open(input_file, 'r', 'utf-8') as myfile:
        for line in myfile:
            if re.match(p5, line.strip()):
                outfile.write(str(index) + '\t')
            elif re.match(p6, line.strip()):
                outfile.write('\n')
                index += 1
                flag = 1
            else:
                line = p1.sub('', line)
                line = p2.sub('', line)
                line = p3.sub('', line)
                line = p4.sub('', line)
                # line = p5.sub('', line)
                # line = p6.sub('', line)
                line = p7.sub('', line)
                line = p8.sub('', line)
                if flag:
                    outfile.write(line + '\t')
                    flag = 0
                else:
                    outfile.write(line)
    outfile.close()
def separate_words(inp, outp):
    program = os.path.basename(sys.argv[0])
    logger = logging.getLogger(program)
    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
    logging.root.setLevel(level=logging.INFO)
    output = open(outp, 'w', encoding='utf-8')
    inp = open(inp, 'r', encoding='utf-8')

    for line in inp.readlines():
        seg_list = jieba.cut(line.strip())
        output.write(' '.join(seg_list) + '\n')
    logger.info("finished separate words!")

def main():
    filte('resources/AA/zh_wiki_02', 'resources/AA/std_zh_wiki_02')
    #separate_words('resources/AA/std_zh_wiki_00',
    #                'resources/AA/std_zh_wiki_00_sep')
    # separate_words('resources/AA/std_zh_wiki_01',
    #                 'resources/AA/std_zh_wiki_01_sep')
    # separate_words('resources/AA/std_zh_wiki_02',
    #                'resources/AA/std_zh_wiki_02_sep')
    
if __name__=='__main__':
   main()

