# coding=utf-8
from cart import *
from features_engineering import *
from ecs import *


def predict_vm(ecs_lines, input_lines):
    period = input_lines[4]  # --------------------------
    flavordic = input_lines[2]

    def getMoreData(dataset, window, label_period, sliding_distance):  # the extral featuresa are included
        result = []
        n = int((getTime_difference(dataset[-1][0], dataset[0][0]) - window[-1]) / sliding_distance)
        print len(dataset),window,label_period,sliding_distance,n,'++++++++++'
        for i in range(n):
            data, temp = SplitdatasetByday(dataset, sliding_distance * i)  # chuangkou huadong
            # print dataset[0],data[0]
            l, r = SplitdatasetByday(data, period - 1)
            # print('===',l[0][0],l[-1][0])
            # if getTime_difference(l[-1][0], l[0][0]) < window[-1]:
            print l[0][0],l[-1][0],'iiiiiiiii'
            if getTime_difference(l[-1][0], l[0][0]) < window[-1]:
                print 'breakkkkkkk'
                break
            if i == 0:
                proed_featuresdata = getMoreFeatures(l, window, r[0][0])
            else:
                proed_featuresdata = getMoreFeatures(l, window, r[0][0])
            distict_proed_featuresdata = []
            for j in proed_featuresdata:
                if j not in distict_proed_featuresdata:
                    distict_proed_featuresdata.append(j)
            # print (distict_proed_featuresdata[-1][0],r[0][0],r[-1][0])
            label = getLabel(r)
            print label,'lllllllllabel'
            for i in range(len(distict_proed_featuresdata)):
                if distict_proed_featuresdata[i][1] not in label:
                    distict_proed_featuresdata[i].append(0)
                else:
                    distict_proed_featuresdata[i].append(label[distict_proed_featuresdata[i][1]])
            result.extend(distict_proed_featuresdata)
        return result

    # Do your work from here#
    result = []
    if ecs_lines is None:
        print 'ecs information is none'
        return result
    if input_lines is None:
        print 'input file information is none'
        return result
    trainData=[]
    if period==7:
        print 111
        trainData = getMoreData(ecs_lines, [1, 2, 3, 5, 7], period, sliding_distance)
    else:
        print 222
        trainData = getMoreData(ecs_lines, [1, 2, 3, 5, 7], period, sliding_distance)
        print trainData, '---'
    distinct_trainData = []
    for i in trainData:
        if i not in distinct_trainData:
            distinct_trainData.append(i)
    for i in range(len(distinct_trainData)):
        temp = filter(lambda x: x not in flavordic, distinct_trainData[i])
        distinct_trainData[i] = temp

    treeModel = createTree(distinct_trainData, [0.001, 5])

    data1, yanzh = SplitdatasetByday(ecs_lines, period - 1)
    # if period == 7:
    #     yanzhf = getMoreFeatures(yanzh, [1, 2, 3, 5], input_lines[-2])
    #     f14 = getLabel(yanzh)
    # else:
    #     yanzhf = getMoreFeatures(yanzh, [1, 2, 3, 5], input_lines[-2])
    #     f14 = getLabel(yanzh)
    # for i in range(len(yanzhf)):
    #     if yanzhf[i][1] not in f14:
    #         yanzhf[i].append(0)
    #     else:
    #         yanzhf[i].append(f14[yanzhf[i][1]])
    yanzhf = getMoreFeatures(yanzh, [1, 2, 3, 5, 7], input_lines[-2])

    distinct_yanzhenf = []
    for i in yanzhf:
        if i not in distinct_yanzhenf:
            distinct_yanzhenf.append(i)
    for i in range(len(distinct_yanzhenf)):
        temp = filter(lambda x: x not in flavordic, distinct_yanzhenf[i])
        distinct_yanzhenf[i] = temp

    res = treeForeCast_dataSet(treeModel, distinct_yanzhenf)
    for i in range(len(res)):
        for j, k in input_lines[2].items():
            flag = 0
            if res[i][1] == int(k[0]) and res[i][2] == int(k[1]):
                res[i].append(j)
                flag = 1
            if flag == 1:
                break
    yucedic = {}
    for i in input_lines[2]:
        yucedic[i] = []
    for i in res:
        yucedic[i[-1]].append(i[-2])
    for i, j in yucedic.items():
        if len(j) != 0:
            yucedic[i] = round(math.fsum(j) / len(j))
        else:
            yucedic[i] = 0
    fenbu = BFD(yucedic, input_lines[2], input_lines[0], optsource=input_lines[3])
    for i in range(len(fenbu)):
        dic = {}
        for j in fenbu[i]:
            if fenbu[i][j] != 0 and j != 'CPU' and j != 'MEM':
                dic[j] = fenbu[i][j]
        result.append(dic)
    return [yucedic, result]
