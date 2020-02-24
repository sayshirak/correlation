#-*- coding:utf-8 -*-
import os
import xlrd
import xlwt
import re
import sqlite3
import numpy
import csv
from numpy.distutils import numpy_distribution


tableName = "changeRate"
strPath = "E:\\program\\PYTHON\\correlation\\dat\\"
newFile = "E:\\program\\PYTHON\\correlation\\newDat.txt"
host = "127.0.0.1"  
dbname = "metrosavingexpert"  
user = "root"
password = "thtf600100"
filterFileList = list()
fundList = list()
rowLength = 0   #用于记录所有基金中交易日期最长的天数

def sort():
    csv_reader = csv.reader(open("E:\\program\\PYTHON\\correlation\\场内基金相关性4.csv", encoding='utf-8'))
    fileSort = open("E:\\PROGRAM\\PYTHON\\correlation\\sort.txt","w")
    
    nRow = 0
    nCol = 0
    nCount = 0
    p = set()
    for row in csv_reader:
        if nRow == 0:
            nRow += 1
            continue
        for col in row:
            if nCol == 0:
                nCol += 1
                continue
            if (( col != 1 ) and ( col != 0 ) ):
                p.add(col)
                #nCount += 1
        nRow += 1
    #pList = list()
    for val in p:
    #pList.append(val)
    #pList.sort()
        fileSort.write(val+"\n")
    fileSort.close()
    #print(nCount)    
    
def genTable():
    db = pymysql.connect(host,user,password,dbname )
    cursor = db.cursor()
    sql = "DROP TABLE IF EXISTS `" + tableName + "`"
    cursor.execute(sql)
    sql = "CREATE TABLE `" + tableName + "` (`TRADEDATE` datetime NOT NULL,";
    for file in filterFileList:
        col = file[3:9]
        sql += "`" + col + "` double DEFAULT 0,";
    sql += "  PRIMARY KEY (`TRADEDATE`) )  ENGINE=MyISAM DEFAULT CHARSET=utf8";
    cursor.execute(sql)
    
def filterFund():
    global rowLength
    #获取目录内文件名
    colRaw = os.listdir(strPath)
    filterFileList.clear()
    #遍历每一个文件，先挑出交易天数在1300天以上，日平均交易量在1000000以上的
    for file in colRaw:
        i  = 0
        j = 0   #统计有成交量的天数
        lTurnover = 0   #每天成交量
        strDate = "";
        for line in open(strPath + file):
            if i > 2:
                tempStr = line.split('\t')
                if len(tempStr) > 2:                    
                    if float(tempStr[5]) > 0: 
                        lTurnover += float(tempStr[5])
                        j += 1
            i += 1
        if i - 3 > rowLength:
            rowLength = i - 3
        if j > 600:
            lTurnover = lTurnover/j;    #平均日成交量，以股为单位
            if  lTurnover > 1000000:
                filterFileList.append(file)                
                
def read_xlsx():
    workbook = xlrd.open_workbook("E:\\PROGRAM\\PYTHON\\correlation\\changerate_delCol_noHeader4.xlsx")
    booksheet = workbook.sheet_by_name('changerate')
    p = list()
    i = 0
    j = 0
    for col in range(booksheet.ncols):
        col_data = []
        i = 0
        for row in range(booksheet.nrows):
            cel = booksheet.cell(row, col)
            val = cel.value            
            print(type(val))
            col_data.append(val)
            i += 1
        #print(col_data)
        p.append(col_data)
        j += 1
    print(i)
    print(j) 
    return  p

def GenCorreDatFile():
    changeRate = list()
    j = 0
    for file in filterFileList:
        row = []
        col = file[3:9]
        fundList.append(col)
        i  = 0
        Date = "";
        for line in open(strPath + file):
            if i > 1:
                tempStr = line.split('\t')
                if len(tempStr) > 2:                    
                    if float(tempStr[5]) > 0:
                        Date = tempStr[0]; 
                        Change = (float(tempStr[4]) - float(tempStr[1]) )/float(tempStr[1])
                        row.append(float(round(Change,6)))               
            i += 1
        tmp = len(row)
        if  tmp < rowLength:
            for k in range( rowLength - tmp):
                row.append(0)
        changeRate.append(row)
        j += 1
    return changeRate

def SearchSqlFile(path):
    if ( False == os.path.exists(path) ):
        error = "目录：" + path +  " 不存在！"
        return error
    else:
        fileList = os.listdir(path)
        return fileList

def TestList():
    changeRate = list()
    for i in range(5000):
        row = []
        for j in range(5000):
            num = j*0.24 + i/3
            row.append(float(num))
        changeRate.append(row)
    print(changeRate)
    return changeRate
    
def CompareCorrelation(fund1,fund2):
    i = 0
    row1 = list()
    for line in open(strPath + fund1):
        if i > 1:
            tempStr = line.split('\t')
            if len(tempStr) > 2:                    
                if float(tempStr[5]) > 0:
                    Date = tempStr[0]; 
                    Change = (float(tempStr[4]) - float(tempStr[1]) )/float(tempStr[1])
                    row1.append(float(round(Change,6)))               
        i += 1
        
    i = 0
    row2 = list()    
    for line in open(strPath + fund2):
        if i > 1:
            tempStr = line.split('\t')
            if len(tempStr) > 2:                    
                if float(tempStr[5]) > 0:
                    Date = tempStr[0]; 
                    Change = (float(tempStr[4]) - float(tempStr[1]) )/float(tempStr[1])
                    row2.append(float(round(Change,8)))               
        i += 1
    i = 0
    if len(row1) > len(row2):
        for i in range ( len(row1) - len(row2) ):
            row2.append(0)
    elif len(row2) > len(row1):
        for i in range ( len(row2) - len(row1) ):
            row1.append(0)
    print(numpy.corrcoef(row1,row2) )

if __name__ == '__main__':
    filterFund()
    #CompareCorrelation("SH#510050.txt","SZ#159901.txt")
    temp = GenCorreDatFile()
    data_list = numpy.array(temp,dtype = float) #必须要保证每行的元素相同，否则会自动将每一行转换为一个list
    corr_list = numpy.corrcoef(data_list)    
    corr_list = numpy.row_stack((fundList,corr_list))
    fundList.insert(0, "")
    corr_list = numpy.column_stack((fundList,corr_list))
    numpy.savetxt("E:\\PROGRAM\\PYTHON\\correlation\\场内基金相关性4.csv", corr_list, fmt = "%s", delimiter=",")
    sort()

