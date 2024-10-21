import csv,os
import sqlite3
import plotlyjk
import jqdatasdk as jq
from datetime import datetime, timedelta,date
import sixyao

def date_to_jk(dateString):  #2022年11月20日  to  2022-11-20
    print(dateString)
    if "年" in dateString:
        day10=datetime.strptime(dateString,"%Y年%m月%d日").date().strftime("%Y-%m-%d")
    elif "/" in dateString:
            day10=datetime.strptime(dateString,"%Y/%m/%d").date().strftime("%Y-%m-%d")
    elif "-" in dateString:
            day10=datetime.strptime(dateString,"%Y-%m-%d").date().strftime("%Y-%m-%d")
    else:
        day10="3000年1月1日"     
    #date_jk=day10.strftime("%Y-%m-%d")
    return day10

def writeCSV(csvfilename,inputlist):
    #csvfilename='e:/WeiXinGuaImage/Finished/guas1000.csv'
    with open(csvfilename, 'a', newline='') as csvfile:
        writer=csv.writer(csvfile)
        writer.writerow(inputlist)
        
def insertRecord(c1, tuple):
    #c.execute("INSERT INTO Ichingcases800 (user, guaSubject, guaDate, stockName,guaName,guaContent) VALUES (?, ?, ?,?,?,?)", ("abc","xxyyzz","2023-04-28", "300133","随之无妄", "demo" ) )
    query = (tuple[0],tuple[1],tuple[2])
    #print(query)
    c1.execute('SELECT * FROM Ichingcases800 WHERE guaName=? and guaSubject=? and guaDate=? ',query)
    db_result=c1.fetchall()
    if len(db_result)==0:
        c1.execute("INSERT INTO Ichingcases800 (guaName,guaSubject, guaDate,guaContent, user,stockName)  VALUES (?, ?, ?,?,?,?)", tuple )
        print('Studnet Data inserted Successfully')
    else:
        print("Record exists")

def extractGua(string):
    index1=string.find("之")
    index2=string.find("静")
    if index1>=0:
        name1=string[0:index1]
        name2=string[index1+1:]
    else:
        name1=string[0:index2]
        name2=name1
    return name1, name2

def getContent(namestring,day):
    name1,name2=extractGua(namestring)
    gua1=sixyao.Zhugua()
    gz=gua1.setDate(day)
    print(gz)
    gua1.makeGuaByName(name1,name2)
    print("make gua by name.. OK")
    gua1.displayDoubleGua()
    guacont=gua1.guaContent()
    return guacont
                       
def insertCSV():      
    print("工作目录", os.getcwd())
    #jq.auth('13162806189', 'Sunshine1972')  
    #conn = sqlite3.connect('E:/JupyterCode/myspider/Guas.db')
    conn = sqlite3.connect('E:/pythoncode/iching/Guas.db')
    c = conn.cursor()
    #print("cursor is OK....")
    #csv表格顺序: 卦名，预测主题，日期，日期时间,用户或备注,股票名字
    oldcsv='e:/jupytercode/guas1000+200v4.csv'
    newcsv='e:/jupytercode/guas1000+200v5.csv'    
    with open(oldcsv, newline='') as f:
        reader = csv.reader(f)
        i=1
        for row in reader:
            print(row)
            olddate=row[2]
            newdate=date_to_jk(olddate)
            cont=getContent(row[0],newdate)
            contnew="起卦hour:" +row[3]+'\n'+cont
            print(i)
            print(contnew)
            
            list1=[ row[0],row[1],newdate,contnew,row[4],row[5] ]
            tup1=( row[0],row[1],newdate,contnew,row[4],row[5] )
            #writeCSV(newcsv, list1)
            print(tup1)
            #insertRecord(c, tup1)
            print("Insert Record is OK")
            i+=1
            input('请暂停：')  
            if i>=3:
                break
               # input('请暂停：')         
    conn.commit()
    conn.close()

if __name__ == "__main__":
    day="2023-05-10"
    #cont=getContent("同人之大有",day)
    print("starting a new process......")
    insertCSV()
    



    
            
