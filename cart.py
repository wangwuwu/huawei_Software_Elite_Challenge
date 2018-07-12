#encoding=utf-8
import math
import random
import copy
def loadDatSet(filename):
    dataMat=[]
    fr=open(filename)
    for line in fr.readlines():
        curline=line.strip().split('\s+')
        fltline=map(float,curline)
        dataMat.append(fltline)
    return fltline

def reggressLeaf(dataSet):#对于回归计算叶子节点值，一般为标签列的均值
    l=[x[-1] for x in dataSet]
    return math.fsum(l)/len(l)

def regressErr(dataSet):
    if len(dataSet)==0:
        return 0
    else:

         l=[x[-1] for x in dataSet]
         mean=math.fsum(l)/len(l)
         var=0
         for  x in l:
            var+= math.pow(x-mean,2)
         return var

def binarySplitDataSet(dataSet,feaatures,value):#根据特征features的值values将数据划分为两个集和,features was number type
    dataset=dataSet#copy.deepcopy(dataSet)
    left=[]
    right=[]
    for data in dataset:
        if data[feaatures]>value:
            left.append(data)
        else:
            right.append(data)
    # for i in range(len(left)):
    #     del left[i][feaatures]
    # for i in range(len(right)):
    #     del right[i][feaatures]
    return left,right#左大右小

def select_Best_Split(dataSet,op=[1,4]):
    if len(set([x[-1] for x in dataSet]))==1:
        # print 'len(set([x[-1] for x in dataSet]))==1'
        return None,reggressLeaf(dataSet)
    # print len(dataSet)
    f=len(dataSet[0])
    bestS=float('inf')
    bestFeature=-1
    bestValue=-1
    S=regressErr(dataSet)
    for features in range(f-1):
        for splitVal in set([x[features] for x in dataSet]):
            mat0,mat1=binarySplitDataSet(dataSet,features,splitVal)
            newS=regressErr(mat0)+regressErr(mat1)
            if bestS>newS:
                bestFeature=features
                bestValue=splitVal
                bestS=newS
            # print(features, splitVal, newS)
    # print 'xunzhaozuiyoudian'
    if (S-bestS)<op[0]:#说明分前后误差不大
        # print '(S-bestS)<op[0]',':',S-bestS
        return None,reggressLeaf(dataSet)
    dataL,dataR=binarySplitDataSet(dataSet,bestFeature,bestValue)
    # print 'popo',len(dataL)
    # print 'opppppppp',len(dataR)
    if len(dataL) <op[1] or len(dataR)<op[1]:
        # print 'len(dataL) <op[1] or len(dataR)<op[1]'
        return None,reggressLeaf(dataSet)
    # print(bestFeature,bestValue,bestS)
    return bestFeature,bestValue

def createTree(dataSet,op=[1,4]):#m为特征数，max_level为树深度
    bestFeatures,bestValue=select_Best_Split(dataSet,op)
    # print bestFeatures,bestValue,'++++++++++'
    # print '====',bestFeatures,'====',bestValue
    if bestFeatures==None:
        return bestValue#叶子节点
    retTree={}
    retTree['bestFeatures']=bestFeatures
    retTree['bestVal']=bestValue
    lSet,rSet=binarySplitDataSet(dataSet,bestFeatures,bestValue)
    retTree['right']=createTree(rSet,op)
    retTree['left']=createTree(lSet,op)
    # print retTree
    return  retTree

def treeForecast_oneData(tree,data):#预测单个数据样本
    if not isTree(tree):
        print 'kkkkkkkkkkkkkkkkkkk'
        return float(tree)#此时为叶子节点
    # print '++++++++++',data[tree['bestFeatures']],'++++++',tree['bestVal']
    # print tree['bestFeatures'], tree['bestVal'],'--------'
    print '++',tree['bestFeatures']
    print tree['bestVal']
    print len(data)
    print  data[tree['bestFeatures']],'+++'
    if data[tree['bestFeatures']]>tree['bestVal']:
        if isTree(tree['left']):
            return treeForecast_oneData(tree['left'], data)
        else:
            return float(tree['left'])
    else:
        if isTree(tree['right']):
            return treeForecast_oneData(tree['right'], data)
        else:
            return float(tree['right'])

def treeForeCast_dataSet(tree,dataset):#单棵树预测整个数据测试集
    dataSet=dataset#copy.deepcopy(dataset)
    for i in range(len(dataSet)):
        a=treeForecast_oneData(tree,dataSet[i])
        dataSet[i].append(a)
    return dataSet

# def RF_predict(trees,dataSet):
#     l=[0]*len(dataSet)
#     for tree in trees:
#         l=map(lambda (a,b):a+b,zip(l,treeForeCast_dataSet(tree,dataSet)))
#     a=len(trees)
#     return [x/a for x in l]

def isTree(obj):#判断是否是叶子节点
    return isinstance(obj,dict)#(type(obj).__name__=='dict')

def getMean(tree):
    if isTree(tree['left']):
        tree['left']=getMean(tree['left'])
    if isTree(tree['right']):
        tree['right'] = getMean(tree['right'])
    return (tree['left']+tree['left'])/2.0

def prune(tree,testData):
    if len(testData)==0:return getMean(tree)# 存在测试集中没有训练集中数据的情况
    if isTree(tree['left']) or isTree(tree['right']):
        leftTestData, rightTestData = binarySplitDataSet(testData, tree['bestFeatures'], tree['bestVal'])
    # 递归调用prune函数对左右子树,注意与左右子树对应的左右子测试数据集
    if isTree(tree['left']): tree['left'] = prune(tree['left'], leftTestData)
    if isTree(tree['right']): tree['right'] = prune(tree['right'], rightTestData)
    # 当递归搜索到左右子树均为叶节点时，计算测试数据集的误差平方和
    if not isTree(tree['left']) and not isTree(tree['right']):
        leftTestData, rightTestData = binarySplitDataSet(testData,tree['bestFeatures'], tree['bestVal'])
        lsum=0
        rsum=0
        for data in leftTestData:
            lsum+=math.pow(data[-1]-tree['left'],2)
        for data in rightTestData:
            rsum+=math.pow(data[-1]-tree['right'],2)
        errorNOmerge=lsum+rsum
        # errorNOmerge = sum(math.power(leftTestData[:, -1] - tree['left'], 2)) + sum(
        #     math.power(rightTestData[:, -1] - tree['right'], 2))
        errorMerge=0
        mean=getMean(tree)
        for data  in testData:
            errorMerge+=math.pow(data[-1]-mean,2)
        # errorMerge = sum(math.power(testData[:, 1] - getMean(tree), 2))
        if errorMerge < errorNOmerge:
            # print('Merging')
            return mean
        else:
            return tree
    else:
        return tree

def creteTrees(dataSet,n,m,op):# the number of forest,the number of features
    m=int(m)
    def getMfeatures(dataset,f):
        data=[]
        w=len(dataset[0])
        l=[]
        while len(l)<f:
            index=random.randint(0,w-1)
            if index not in l:
                l.append(index)
        for array in dataset:
            temp=[]
            for i in l:
                temp.append(array[i])
            temp.append(array[-1])
            data.append(temp)
        return data
    Trees=[]
    for i in range(n):
        data=getMfeatures(dataSet,m)
        Trees.append(createTree(data,op))
    return Trees
