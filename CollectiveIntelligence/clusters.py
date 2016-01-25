#coding=utf8

def readfile(filename):
    lines = [line for line in file(filename)]

    # 第一行是列标题
    colnames = lines[0].strip().split('\t')[1:]

    rownames = []
    data = []
    for line in lines[1:]:
        p = line.strip().split('\t')
        # 每行的第一列是行名
        rownames.append(line[0])

        data.append([float(x) for x in p[1:]])
    return rownames, colnames, data

rownames, colnames, data = readfile('blogdata.txt')
print colnames[0]

from math import sqrt
def pearson(v1, v2):
    pass