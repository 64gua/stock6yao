#从markdown文件中批量提取信息
import os,re,shutil, csv
from  datetime import datetime, timedelta,date
import akshare_plotly as akPlot
import sqlite3
from aip import AipOcr
import sixyao
#Gan = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
#Zhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

def writeMdInfoToCSV(dir,csvname):
    #dir should be end with "/"
    full_csv=dir+csvname
    i=0
    for file in os.listdir(dir):
        #if file.endswith(".md") and  not file.startswith("total"):
        if file.endswith(".md") :
            i+=1
            #if i>5:
            #    return
            print(i,file)
            code,name=akPlot.extractStockName(file)
            guaName=akPlot.extractGuaName(file)
            day=akPlot.getDate(file)
            file_fullname=dir+file
            with open(file_fullname, 'r',encoding="utf-8") as f:
                cont=f.read()
            if guaName=="NULL":
                guaName=akPlot.extractGuaName(cont)
            if day=="NULL":
                day=akPlot.getDate(cont)
            if code=="NULL" and name=="NULL":
                code,name=akPlot.extractStockName(cont)   #here we can try search subject first
               # if code=="NULL" and name=="NULL":
                #    code="sh000001"
                 #   name="上证指数"            
            #CSV 格式
            infoList=[guaName,code,day,cont,file]
            with open(full_csv, 'a', newline='',encoding="utf-8" ) as cf:
                writer=csv.writer(cf)
                writer.writerow(infoList)
               # print(i, file, " is  now wriing")

def insertCsvToDatabase(csv_name):
    print("Let us start the new journey!...")
    #csv 格式由上一个函数生成 [guaName,code,day,subject,file, imgend]
    with open(csv_name, newline='',encoding="utf-8") as f:
        reader=csv.reader(f)
        i=0 
        for row in reader:
            i=i+1
            gua=row[0]
            code=row[1]
            day=row[2]
            cont=row[3]
            file=row[4]
            #img=row[5]
            #gua_code_day_cont_file_mini.csv
            dir=CURRENT_DIR
            query = (gua,code,day)
            conn=sqlite3.connect('Guas.db')
            cursor=conn.cursor()
            cursor.execute('SELECT * FROM stockGuas WHERE guaName=? and stockName=? and guaDate=?   ',query)
            db_result=cursor.fetchall()
            if len(db_result)==0:
                #filefull=CURRENT_DIR+file
                #with open(filefull, 'r',encoding="utf-8") as f:
                #    cont=f.read()
                #cont=cont.strip()
                tuple=(gua,code, day,cont,file)
                csv1="gua_code_day_cont_file.csv" 
                cursor.execute("INSERT INTO stockGuas (guaName,stockname, guaDate,guaContent,guaSubject)  VALUES (?,?,?,?,?)", tuple )
                print(i,'csv record inserted Successfully')
            else:
                print(i, "Record exists!......")
            conn.commit()
            conn.close()
    print("all the csv has been inserted to database! ")

def getInfofromNormalMdTitle(mdfile):
    infos=mdfile.split("_")
    gua=infos[0]
    code=infos[1]
    day=infos[2]
    subject=infos[3]
    return gua,code,day,subject

def prefindNullDateFile(dir):
    i=0
    for file in os.listdir(dir):
        if file.endswith(".md") :
            #day=akPlot.getDate(file)
            file_fullname=dir+file
            with open(file_fullname, 'r',encoding="utf-8") as f:
                cont=f.read()
            day=akPlot.getDate(cont)
            if day=="NULL":
                re1=r'images.+jpg|images.+.jpeg|images.+png'
                images=re.findall(re1,cont)
                if images:
                    #newname="K_"+file
                    #newname_full=dir+newname
                    #os.rename(file_fullname,newname_full)
                    print("markdown images Ok!...")
                else:
                    newname="KZ_"+file
                    newname_full=dir+newname
                    os.rename(file_fullname,newname_full)
                    i=i+1
                    print(i,newname_full)
    print(i,"files has been renamed with K_")

def infoBaiduOCR(picfile):  # picfile:图片文件名
    # 百度提供
    APP_ID='30244035'
    API_KEY='hZU6fDI7MP6iG5bFaXtIGcsk'
    SECRET_KEY = 'QGChDbrUKMwxMONN1tWnm24a6ZKz91We'
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    print("Baidu clinet connection is OK!")
    i = open(picfile, 'rb')
    img = i.read()
    message = client.basicGeneral(img)
    print(message)
    #data = str(client.basicGeneral(image))
    i.close() 
    string=""    
    for text in message.get('words_result'):  # 识别的内容
        str_row=text.get('words')
        string+=str_row
    guaDate=akPlot.getDateOcr(string)
    subject=akPlot.getSubject(string)
    return guaDate,subject

def allInfoBaiduOCR(picfile):  # picfile:图片文件名
    # 百度提供易经卦象APP
    #APP_ID='30244035'
    #API_KEY='hZU6fDI7MP6iG5bFaXtIGcsk'
    #SECRET_KEY = 'QGChDbrUKMwxMONN1tWnm24a6ZKz91We'
    #basicGeneral
    #BBS图片APP
    APP_ID='33729717'
    API_KEY='AmTpsvEE94bj7nBqj31mAEqh'
    SECRET_KEY='GyM1D4puHpfaoWsgd5jGHj1jbqeRFXZq'
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    print("Baidu clinet connection is OK!")
    i = open(picfile, 'rb')
    img = i.read()
    #message = client.basicGeneral(img)
    message = client.basicAccurate(img)
    #print(message)
    #data = str(client.basicGeneral(image))
    i.close() 
    string=""    
    for text in message.get('words_result'):  # 识别的内容
        str_row=text.get('words')
        string+=str_row+"\n"
    #print(string)
    guaName=akPlot.getGuaName(string)
    code,name=akPlot.extractStockName(string)
    guaDate=akPlot.getDateOcr(string)
    #guaDate2=akPlot.getDate(string)
    subject=akPlot.getSubject(string)
    #print("old way date:",guaDate2)
    return guaName, code, guaDate,subject


def processNullDateFiles(dir):  #预先处理NULL日期信息的文件，也就是主要是图片，文字极少的md文件
    #os.chdir(dir)
    i=0
    for file in os.listdir(dir):
        if file.startswith("KZ_"):
            print(file,"is processing!")
            file_full=CURRENT_DIR+file
            with open(file_full,"r",encoding="utf-8") as f:
                cont=f.read()
            date=akPlot.getDate(cont)
            #subject=akPlot.getSubject(cont)
            if date=="NULL":
                re1=r'images.+jpg|images.+.jpeg|images.+png'
                images=re.findall(re1,cont)
                if images:
                    image=images[0]
                    image_full=CURRENT_DIR+image
                    #print(image)
                    #date,subject=infoBaiduOCR(image)
                    guaName, code, date,subject=allInfoBaiduOCR(image_full)
                    print(guaName,code,date,subject)
                    if date=="NULL" or guaName=="NULL":
                        newfile=CURRENT_DIR+ file.replace("K","KZ")
                        os.rename(file_full,newfile)
                        print("tough file to DZ label")
                        continue
                    else:
                        if guaName!="NULL" and date!="NULL":
                            outgua,guacont=sixyao.paipan2(guaName,date)
                            if outgua!="NULL":
                                file0="源文件名:"+file.replace("K_","").replace(".md","")
                                info=f'{outgua}_{code}\n占事: {subject}\n{guacont}\n'
                                newcont=info+cont+"\n"+file0
                                with open(file_full,"w",encoding="utf-8") as f:
                                    f.write(newcont)
                                print(i, "file insert: ", file_full)
                                newfile=CURRENT_DIR+ file.replace("K","KO")
                                os.rename(file_full,newfile)
                                i=i+1
                            else:
                                newfile=CURRENT_DIR+ file.replace("K","KZ")
                                os.rename(file_full,newfile)
                                print("tough file to DZ label")
    print("every is OK!")
CURRENT_DIR="D:/Markdown/A年卦月卦周卦/"

if __name__ == "__main__":
    markdown_dir=CURRENT_DIR
    csv1="gua_code_day_cont_file.csv" 
    #prefindNullDateFile(markdown_dir)
    #processNullDateFiles(markdown_dir)
    #writeMdInfoToCSV(markdown_dir,csv1)
    insertCsvToDatabase(CURRENT_DIR+csv1)

