#encoding=utf-8
import time
import os
from datetime import datetime
import copy
import math


def getTime_difference(a,b):#fan fanhui tian shu
    # if a>b:
    #    result=(a-b).total_seconds()/3600/24
    # else:
    #     result = (b - a).total_seconds() / 3600 / 24
    # return int((a-b).days)
    if a>b:
        return int((a-b).days)
    else:
        return int((b-a).days)
def getSourceInfo(path):
     l=[]
     file=open(path,'rU')
     for line in file.readlines():
         line=line.strip()
         if not len(line):
            continue
         l.append(line)
     Physource=[int(x) for x in l[0].split()]
     flavornums=int(l[1])
     Optsource=l[-3]
     time2=datetime.strptime(l[-1].split()[0],'%Y-%m-%d')
     time1=datetime.strptime(l[-2].split()[0],'%Y-%m-%d')
     period=getTime_difference(time1,time2)
     flavordic={}
     for i in l[2:2+flavornums]:
         x=i.split()
         if x[0] not in flavordic:
             flavordic[x[0]]=x[1:3]
     return Physource,flavornums,flavordic,Optsource,period,time1,time2


def getAndprocess_originaldata(filepath,flavordic):
    file=open(filepath,'rU')
    l=[]
    for line in file.readlines():
        record=line.strip().split()
        if record[1] in flavordic:
            cpu,mem=[int(x) for x in flavordic[record[1]]]
            # print cpu,mem,'-------------cpu'
            timee=record[2].replace(" ","").replace("\t","").replace("\n","").replace("\r\n","").strip()#+'-'+record[3]
            # timee=datetime.strptime(timee[0:10],'%Y-%m-%d')
            timee = datetime.strptime(timee, '%Y-%m-%d')
            l.append([timee,record[1],cpu,mem])
    return l

def SplitdatasetByday(dataSet,day):#split by day
    dataset=dataSet#copy.copy(dataSet)
    point=0
    if day==0:
        return dataset,None
    else:
        for i  in range(len(dataset)-1,1,-1):
            if getTime_difference(dataset[-1][0],dataset[i-1][0])>day and getTime_difference(dataset[-1][0],dataset[i][0])<=day:
               point=i
               break
        return dataset[0:point],dataset[point:]

def getLabel(dataSet):
    dic={}
    for array in dataSet:
        if array[1] not in dic:
            dic[array[1]]=1
        else:
            dic[array[1]]+=1
    return dic

def getMoreFeatures(dataSet,daysarray,timepoint):#1,2,3,5,7,14
    dataset=copy.deepcopy(dataSet)
    length=len(dataset)
    def getXdaysFeatures(x):
        index=-1
        for i in range(length - 1, 1, -1):
            if getTime_difference(timepoint, dataset[i - 1][0]) > x and getTime_difference(timepoint, dataset[i][0]) <= x:
                index=i
                break
        if index==-1:#最近x天没有数据
            for i in range(length):
                    dataset[i].append(0)
        else:
        #Count the  number of each type of flavor in X days
           dic=getLabel(dataset[index:])
           for i in range(length):
               if dataset[i][1] not in dic:
                   dataset[i].append(0)
               else:
                   dataset[i].append(dic[dataset[i][1]])

    for i in daysarray:
        getXdaysFeatures(i)
    return dataset


def initPhyMachine(flavorsdic,resource):
    # l=[0]*len
    # ll=[resource[0],resource[1]]
    dic={}
    for i in flavorsdic:
        dic[i]=0
    dic['CPU']=resource[0]
    dic['MEM']=resource[1]
    return dic

def BFD(resultdic,flavordic,source,optsource):#resultdic为{flavor:nums}
    # resultArra[]
    source=[source[0],source[1]*1024]
    # print(source,'ggggggg')
    resultArray=[]#穷举出所有的虚拟机
    Physical_machines = []# 存放每种虚拟机个数，剩余CPU、MEM数量
    if optsource=='CPU':
        for i in resultdic:
            if resultdic[i] != 0:
                temp = [(i, flavordic[i][0], flavordic[i][1])] * int(round(resultdic[i]))
                resultArray.extend(temp)
        resultArraytemp = sorted(resultArray, key=lambda x: x[1], reverse=True)
        resultArray = [x[0] for x in resultArraytemp]
        # print('result',resultArray)
          # 存放每种虚拟机个数，剩余CPU、MEM数量
        Physical_machines.append(initPhyMachine(flavordic, source))
        # for flavor in resultArray:
            ##对 phy_machines排序
        # Physical_machines = sorted(Physical_machines, key=lambda x: x['CPU'])
        for i in resultArray:
            flag = 0
            for j in range(len(Physical_machines)):
                 if int(flavordic[i][0]) <= Physical_machines[j]['CPU'] and int(flavordic[i][1]) <= Physical_machines[j][
                        'MEM']:
                        Physical_machines[j][i] += 1
                        Physical_machines[j]['CPU'] -= int(flavordic[i][0])
                        Physical_machines[j]['MEM'] -= int(flavordic[i][1])
                        flag = 1
                        break
                # 现有没有符合的
            if flag == 0:
                temp_machine = initPhyMachine(flavordic, source)
                #从新申请的物理机中选择一个虚拟机
                temp_machine[i]+=1
                temp_machine['CPU'] -= int(flavordic[i][0])
                temp_machine['MEM'] -= int(flavordic[i][1])
                Physical_machines.append(temp_machine)
            Physical_machines = sorted(Physical_machines, key=lambda x: x['CPU'])
    if optsource=='MEM':
        for i in resultdic:
            if resultdic[i] != 0:
                temp = [(i, flavordic[i][0], flavordic[i][1])] * round(resultdic[i])
                resultArray.extend(temp)
        resultArraytemp = sorted(resultArray, key=lambda x: x[2], reverse=True)
        resultArray = [x[0] for x in resultArraytemp]
        Physical_machines.append(initPhyMachine(flavordic, source))
        for i in resultArray:
            flag = 0
            for j in range(len(Physical_machines)):
                 if int(flavordic[i][0]) <= Physical_machines[j]['CPU'] and int(flavordic[i][1]) <= Physical_machines[j][
                        'MEM']:
                        Physical_machines[j][i] += 1
                        Physical_machines[j]['CPU'] -= int(flavordic[i][0])
                        Physical_machines[j]['MEM'] -= int(flavordic[i][1])
                        flag = 1
                        break
                # 现有没有符合的
            if flag == 0:
                temp_machine = initPhyMachine(flavordic, source)
                temp_machine[i]+=1
                temp_machine['CPU'] -= int(flavordic[i][0])
                temp_machine['MEM'] -= int(flavordic[i][1])
                Physical_machines.append(temp_machine)
            ##对 phy_machines排序
            Physical_machines = sorted(Physical_machines, key=lambda x: x['MEM'])

    return Physical_machines





