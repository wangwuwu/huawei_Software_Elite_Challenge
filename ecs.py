# coding=utf-8
import sys
import os
import  predictor
from features_engineering import  *
from cart import *
sliding_distance = 2
def main():
    # print 'main function begin.'
    if len(sys.argv) != 4:
        print 'parameter is incorrect!'
        print 'Usage: python esc.py ecsDataPath inputFilePath resultFilePath'
        exit(1)
    # Read the input files
    ecsDataPath = sys.argv[1]
    inputFilePath = sys.argv[2]
    resultFilePath = sys.argv[3]
    Physource, flavornums, flavordic, Optsource, period, time1, time2 = getSourceInfo(inputFilePath)
    dataset = getAndprocess_originaldata(ecsDataPath,flavordic)  # 得到的数据都是符合要求的
    # dataset, yanzh = SplitdatasetByday(dataSet, 2 * period - 1)
    ecs_infor_array=dataset
    input_file_array=[Physource, flavornums, flavordic, Optsource, period, time1, time2]
    predic_result = predictor.predict_vm(ecs_infor_array, input_file_array)#
    if len(predic_result) != 0:
        write_result(predic_result, resultFilePath)
    else:
        predic_result.append("NA")
        write_result(predic_result, resultFilePath)
    print 'main function end.'


def write_result(array, outpuFilePath):
    flavorNums=0
    yucedic=array[0]
    fenbu=array[1]
    machinesNum=len(fenbu)
    for i in yucedic:
        flavorNums+=yucedic[i]
    yucedicArray=[]
    yucedicArray=sorted(yucedic.items(),key=lambda x:int(x[0][6:]))

    with open(outpuFilePath, 'w') as output_file:
        output_file.write('%s\n'%int(flavorNums))
        for item in yucedicArray:
            output_file.write('%s %s\n'%(item[0],int(item[1])))
        output_file.write('\n')
        output_file.write('%s\n'%int(machinesNum))
        k = 0
        for dic in fenbu:
            k += 1
            output_file.write('%s '%k)
            i=1
            for j in dic:
                if i==len(dic):
                    output_file.write('%s %s' % (j, int(dic[j])))
                else:
                    output_file.write('%s %s '%(j,int(dic[j])))
                i+=1
            if k!=len(fenbu):
               output_file.write('\n')


if __name__ == "__main__":
    main()
