#coding=utf8

critics={'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
 'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,
 'The Night Listener': 3.0},
'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
 'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0,
 'You, Me and Dupree': 3.5},
'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
 'Superman Returns': 3.5, 'The Night Listener': 4.0},
'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
 'The Night Listener': 4.5, 'Superman Returns': 4.0,
 'You, Me and Dupree': 2.5},
'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
 'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
 'You, Me and Dupree': 2.0},
'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
 'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
'Toby': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0}}


from math import sqrt

def sim_distance(prefs, person1, person2):
    """
    返回一个有关person1与person2的基于距离的相似度评价
    :param prefs:
    :param person1:
    :param person2:
    :return:
    """

    # 得到shared_items的列表
    shared_items = {}
    for item in prefs[person1]:
        if item in prefs[person2]:
            shared_items[item] = 1

    # 如果两者没有共同之处，则返回0
    if len(shared_items) == 0:
        return 0

    # 计算所有差值的平方和
    sum_of_squares = sum([pow(prefs[person1][item]-prefs[person2][item], 2)
                          for item in prefs[person1] if item in prefs[person2]])
    return 1/(1+sqrt(sum_of_squares))


#dis = sim_distance(critics, 'Lisa Rose', 'Jack Matthews')
#print dis

def sim_pearson(prefs, person1, person2):
    """
    返回p1和p2的皮尔逊相关系数
    :param prefs:
    :param person1:
    :param person2:
    :return: 介于[-1, 1]，值为1表明两个人对每一样物品均有着完全一致的评价
    """

    # 得到双方都曾评价过的物品列表
    shared_items = {}
    for item in prefs[person1]:
        if item in prefs[person2]:
            shared_items[item] = 1

    # 得到列表元素的个数
    n = len(shared_items)

    # 如果没有共同之处，则返回1
    if n == 0:
        return 1

    # 对所有偏好求和
    sum1 = sum([prefs[person1][item] for item in shared_items])
    sum2 = sum([prefs[person2][item] for item in shared_items])

    # 求平方和
    sum1_sq = sum([pow(prefs[person1][item], 2) for item in shared_items])
    sum2_sq = sum([pow(prefs[person2][item], 2) for item in shared_items])

    # 求乘积之和
    pSum = sum([prefs[person1][item] * prefs[person2][item] for item in shared_items])

    # 计算皮尔逊评价值
    num = pSum - (sum1*sum2/n)
    den = sqrt((sum1_sq - pow(sum1, 2)/n) * (sum2_sq - pow(sum2, 2)/n))
    if den == 0:
        return 0

    r = num/den

    return r

#dis = sim_pearson(critics, 'Lisa Rose', 'Jack Matthews')
#print dis

def top_matches(prefs, person, n=5, similarity=sim_pearson):
    """
    从反映偏好的字典中返回最为匹配者
    返回结果的个数和相似度函数均为可选参数
    :param prefs:
    :param person:
    :param n:
    :param similarity:
    :return:
    """
    scores = [(similarity(prefs, person, other), other)
              for other in prefs if other != person]

    # 对列表进行排序，评价值最高者排载最前面
    scores.sort()
    scores.reverse()
    return scores[:n]

scores = top_matches(critics, 'Toby', n=3)
print scores