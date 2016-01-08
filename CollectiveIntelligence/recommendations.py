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

#scores = top_matches(critics, 'Toby', n=3)
#rint scores

def get_recommendations(prefs, person, similarity=sim_pearson):
    """
    利用所有他人评价值的加权平均，为某人提供建议
    :param prefs:
    :param person:
    :param similarity:
    :return:
    """

    totals = {}
    simSums = {}
    for other in prefs:
        # 不要和自己做比较
        if other == person:
            continue

        sim = similarity(prefs, person, other)

        # 忽略评价值为零或者小于零的情况
        if sim <= 0:
            continue

        for item in prefs[other]:

            # 只对自己还未曾看过的影片进行评价
            if item not in prefs[person] or prefs[person][item] == 0:

                # 相似度 * 评价值
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item] * sim

                # 相似度之和
                simSums.setdefault(item, 0)
                simSums[item] += sim

    # 建立一个归一化的列表
    rankings = [(total/simSums[item], item) for item, total in totals.items()]

    # 返回经过排序的列表
    rankings.sort()
    rankings.reverse()
    return rankings

# rankings = get_recommendations(critics, 'Toby')
# print 'person\n', rankings
#
# rankings = get_recommendations(critics, 'Toby', similarity=sim_distance)
# print 'distance\n', rankings


def transform_prefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})

            #将物品和人员对调
            result[item][person] = prefs[person][item]

    return result

# movies = transform_prefs(critics)
# print top_matches(movies, 'Superman Returns')

def calculate_similar_items(prefs, n=10):
    """
    构建数据集
    :param prefs:
    :param n:
    :return:
    """

    # 建立字典，以给出与这些物品最为相近的所有其他物品
    result = {}

    # 以物品为中心，对偏好矩阵实施倒置处理
    itemPrefs = transform_prefs(prefs)
    c = 0
    for item in itemPrefs:
        # 针对大数据集更新状态变量
        c += 1
        if c%100 == 0:
            print "%d / %d" % (c, len(itemPrefs))
        #寻找最为相近的物品
        scores = top_matches(itemPrefs, item, n=n, similarity=sim_distance)
        result[item] = scores

    return result

itemsim = calculate_similar_items(critics)
print itemsim[itemsim.keys()[0]]

def get_recommend_items(prefs, itemMatch, user):
    userRatings = prefs[user]
    scores = {}
    totalSim = {}

    # 循环遍历由当前用户评分的物品
    for (item, rating) in userRatings.items():

        # 循环遍历与当前物品相近的物品
        for (similarity, item2) in itemMatch[item]:

            # 如果该用户已经对当前物品做过评价，则将其忽略
            if item2 in userRatings:
                continue

            # 评价值与相似度的加权之和
            scores.setdefault(item2, 0)
            scores[item2] += similarity * rating

            # 全部相似度之和
            totalSim.setdefault(item2, 0)
            totalSim[item2] += similarity

    # 将每个合计值除以加权和，求出平均值
    rankings = [(score / totalSim[item], item) for item, score in scores.items()]

    rankings.sort()
    rankings.reverse()
    return rankings

rankings = get_recommend_items(critics, itemsim, 'Toby')
print rankings