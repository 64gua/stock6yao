#2024-6-24 v1.2
import sys, shutil,os,re
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog
from PyQt5.QtGui import QPixmap, QIcon
from decimal import Decimal
import sqlite3
import sixyao
import akshare_plotly as akPlot
import html

qtcreator_file  = "db_search_2_H.ui" # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtcreator_file)

class MyWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        self.switch=1
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.tableGua.setSelectionBehavior(QTableWidget.SelectRows)
        self.tableGua.setSelectionMode(QTableWidget.SingleSelection  )
        for i in range(0,8):
            self.tableGua.setColumnWidth(i, 80) 
        self.btn_search.clicked.connect(lambda: self.loadInfo(1))
        self.btn_search_bytime.clicked.connect(lambda: self.loadInfo(0))
        self.btn_title.clicked.connect(lambda: self.loadInfo(2))
        self.btn_draw30.clicked.connect(lambda:self.drawpicDaily(30))
        self.btn_draw15.clicked.connect(lambda:self.drawpicDaily(15))
        self.btn_draw_month.clicked.connect(self.drawpicMonth)
        self.tableGua.cellDoubleClicked.connect(self.displayGua)
        self.btn_save.clicked.connect(self.saveContentChange)
        self.txtStockCode.editingFinished.connect(self.renewStockName)
        self.txtStockName.editingFinished.connect(self.renewStockCode)
        self.btn_paipan.clicked.connect(self.paipan)
        self.btn_save_img.clicked.connect(self.saveJPG)
        self.actMd.triggered.connect(self.saveMdFiles)
        self.actDelete.triggered.connect(self.deleteWaste)
        self.actRemove.triggered.connect(self.removeRecord)
        self.act_all_in.triggered.connect(self.allInOneMarkdownHtml)
        self.act_single.triggered.connect(self.singleMarkdown)
        self.act_new.triggered.connect(self.refreshText)
        #self.act_del_same_pics.triggered.connect(self.deleteSamePics)
        self.act_generate_pics.triggered.connect(self.generatePics)
        self.act_save_new.triggered.connect(self.saveNewRecord)
        self.comboImg.currentIndexChanged.connect(self.refreshImg)
        self.btn_wash.clicked.connect(self.washContent)

    def loadInfo (self,searchmode) :
        self.mode=searchmode
        connection=sqlite3.connect('Guas.db')
        cursor=connection.cursor()
        mainsql='select postTitle,guaDate, stockName,guaName,user,guaContent,CAST(rowid as text),imgPath, cast(markdown as text),dir from StockGuas '
        orderby= '  order by cast( substr(guaDate,6,2) as integer), guaDate  '
        if searchmode==1:  #按照卦名搜索
            self.txtTitle.setText("")
            self.txtEndDay.setText("")
            self.txtStartDay.setText("")
            str=self.txtSearchGuaName.text().strip()
            self.modestr=f'where guaName like "{str}"  '
        elif searchmode==0:  #按照时间段搜索
            self.txtSearchGuaName.setText("")
            self.txtTitle.setText("")
            startday=self.txtStartDay.text().strip()
            endday=self.txtEndDay.text().strip()
            self.modestr=f'where guaDate between"{startday}" and "{endday}"   ' 
        elif searchmode==2:  #按照帖子标题搜索
            self.txtStartDay.setText("")
            self.txtEndDay.setText("")
            self.txtSearchGuaName.setText("")
            str=self.txtTitle.text().strip()
            self.modestr=f'where postTitle like "{str}"    ' 
        query=mainsql+self.modestr+orderby
        print("query: ",query)
        result=cursor.execute(query)
      #  self.tableGua.setRowCount(0)
        print("result is is OK!")
        rows=cursor.fetchall()
        #self.tableGua.clearContents()
        self.tableGua.setRowCount(0)
        for x,row in enumerate(rows):
            #print(x)
            self.tableGua.insertRow (x)
            for y, info in enumerate(row):
                item= QtWidgets.QTableWidgetItem(info)
                self.tableGua.setItem(x,y,item)            
        cursor.close()
        connection.close()

    def displayGua(self):
        self.comboImg.clear()
        self.label_pic.clear()
        items=self.tableGua.selectedItems()
        postTitle=items[0].text()
        guaContent=items[5].text()
        guaName=items[3].text()
        imgPath=items[7].text()
        dir=items[9].text()
        if not postTitle in guaContent:
            guaContent="主帖标题: "+postTitle+"\n"+guaContent
        rawStock=items[2].text()
        gDate=items[1].text()
        self.txtContent.setPlainText(guaContent)
        stockCode,stockName=akPlot.extractStockName(rawStock)
        if stockCode=="NULL" or stockName=="NULL":
            stockCode,stockName=akPlot.extractStockName(postTitle)
        subject=akPlot.getSubject(guaContent)
        re1=r'images.+jpg|images.+.jpeg|images.+png'
        images=re.findall(re1,guaContent)
        self.dir=dir
        if images:
            img=images[0]
            self.comboImg.addItems(images)
            dir_default="c:/youdaoMD/BBS/"
            imgfull=dir_default+img
            if not os.path.exists(imgfull):
                imgfull=dir+img
            pixmap=QPixmap(imgfull)
            self.label_pic.setPixmap(pixmap)
        self.txtStockCode.setText(stockCode)
        self.txtStockName.setText(stockName)
        self.txtGuaDate.setText(gDate)
        self.txtGuaName.setText(guaName)
        self.txtSubject.setText(subject)
        #self.refreshImg()

    def drawpicDaily(self,days):
        self.drawType="D"
        guaDate=self.txtGuaDate.text()
        stockCode=self.txtStockCode.text()
        dateOrigin=guaDate
        imgfile=akPlot.drawDailyLine(stockCode,dateOrigin,time_period=days)
        print(imgfile)
        #self.comboImg.addItem(imgfile)
        pixmap=QPixmap(imgfile)
        self.label_pic.setPixmap(pixmap)
        if imgfile=="alert.jpg":
            QMessageBox.information(None, "警告", "股票名字或代号出错，是否退市？") 

    def drawpicMonth(self):
        self.drawType="M"
        guaDate=self.txtGuaDate.text()
        stockCode=self.txtStockCode.text()
        dateOrigin=guaDate
        imgfile=akPlot.drawMonthLine(stockCode,dateOrigin)
        print(imgfile)
        pixmap=QPixmap(imgfile)
        self.label_pic.setPixmap(pixmap) 
        if imgfile=="alert.jpg":
            QMessageBox.information(None, "警告", "股票名字或代号出错，是否退市？")  

    def saveContentChange(self):
        QMessageBox.information(None, "注意", "当前界面的:卦内容-卦名-股票名-K线图片文件名，均被更新存入数据库")
        row = self.tableGua.currentRow()
        rowid = self.tableGua.item(row, 6).text()
        new_stockCode=self.txtStockCode.text()
        new_guaName=self.txtGuaName.text()
        new_content = self.txtContent.toPlainText()
        new_guaDate=self.txtGuaDate.text()
        #mdlink=self.txtImg.text()
        mdlink=self.comboImg.currentText()
        connection = sqlite3.connect('Guas.db')
        cursor = connection.cursor()
        query='UPDATE StockGuas  SET guaDate="{}", stockName = "{}", guaName="{}", guaContent ="{}",  imgPath="{}" WHERE rowid = {}  '.format( new_guaDate, new_stockCode, new_guaName, new_content, mdlink, rowid)
        cursor.execute(query)
        connection.commit()
        cursor.close()
        connection.close()
        print("saving Change is OK")
        self.loadInfo(self.mode)
        self.tableGua.setCurrentCell(row, 1) 

    def washContent(self):
        cont=self.txtContent.toPlainText()
        cont=re.sub(r'农历.*\s.*\s.*\s干支','\n干支',cont)
        cont=re.sub(r'农历.*','',cont)
        cont=re.sub(r'.*元亨利贞网.*','',cont)
        cont=re.sub(r'出生.*性别[；：]','',cont)
        cont=re.sub(r'\n{2}',"\n",cont)
        self.txtContent.setPlainText(cont)

    def deleteWaste(self):
        QMessageBox.information(None, "危险！", "当前帖子重复或数据无效，请确认将被删除！")
        row = self.tableGua.currentRow()
        rowid = self.tableGua.item(row, 6).text()
        connection = sqlite3.connect('Guas.db')
        cursor = connection.cursor()
        query='delete from  StockGuas  WHERE rowid = {}  '.format(rowid)
        cursor.execute(query)
        connection.commit()
        cursor.close()
        connection.close()
        print("deleting is finished")
        self.loadInfo(self.mode)
        self.tableGua.setCurrentCell(row, 1) 

    def removeRecord(self):
        QMessageBox.information(None, "警告！", "当前帖子将被移除到futures表格！")
        row = self.tableGua.currentRow()
        rowid = self.tableGua.item(row, 6).text()
        connection = sqlite3.connect('Guas.db')
        cursor = connection.cursor()
        query1='insert into futures  select * from  StockGuas  WHERE rowid = {}  '.format(rowid)
        query2='delete from stockGuas where rowid={}  '.format(rowid)
        cursor.execute(query1)
        cursor.execute(query2)
        connection.commit()
        cursor.close()
        connection.close()
        print("deleting is finished")
        self.loadInfo(self.mode)
        self.tableGua.setCurrentCell(row, 1) 

    def singleMarkdown(self):
        QMessageBox.information(None, "通知！", "当前帖子将写入markdwon！")
        diag=QFileDialog()
        options = diag.Options()
        row = self.tableGua.currentRow()
        rowid = self.tableGua.item(row, 6).text()
        postid=self.tableGua.item(row,6).text()
        new_stockCode=self.txtStockCode.text()
        new_guaName=self.txtGuaName.text()
        new_content = self.txtContent.toPlainText()
        new_date=self.txtGuaDate.text()
        mddir = "/youdaoMD/BBS/"
        file_name = f"{new_guaName}_{new_stockCode}_{new_date}_{postid}.md"
        file_name=mddir+file_name
        file_name, _ = diag.getSaveFileName(self, "保存当前记录到markdown文件！", file_name, "markdown Files (*.md);;txt  file(*.txt)", options=options)
        if file_name:
            with open(file_name, 'w',encoding="utf-8") as file:
                file.write(new_content)
            connection = sqlite3.connect('Guas.db')
            cursor = connection.cursor()
            query='update StockGuas set markdown=1 where rowid={}  '.format(rowid)
            cursor.execute(query)
            connection.commit()
            cursor.close()
            connection.close()
            self.loadInfo(self.mode)
            self.tableGua.setCurrentCell(row, 1) 
            QMessageBox.information(None, "OK!", "当前帖子已经写入markdwon！")
        
    def saveMdFiles(self):
        QMessageBox.information(None, "注意", "搜索结果即将批量写入markdown文件，文件默认目录为c://youdaoMD/BBS/")
        mddir = "c:/youdaoMD/BBS/"
        xsize=self.tableGua.rowCount() 
        ysize=self.tableGua.columnCount()
        #print(xsize,ysize)
        for x in range(0,xsize):
            date = self.tableGua.item(x,1).text()
            stock = self.tableGua.item(x,2).text()
            gua=self.tableGua.item(x,3).text()
            cont=self.tableGua.item(x,5).text()
            postid=self.tableGua.item(x,6).text()
            # Generate the file name based on code and name
            file_name = f"{gua}_{stock}_{date}_{postid}.md"
            file_name=mddir+file_name
            print(file_name)
            print(cont)
            # Write the introduction content to the markdown file
            with open(file_name, 'w',encoding="utf-8") as file:
                file.write(cont)
        self.refreshMark()

    def refreshMark(self):            
        connection = sqlite3.connect('Guas.db')
        cursor = connection.cursor()
        query='update StockGuas set markdown=1 '+self.modestr
        cursor.execute(query)
        connection.commit()
        cursor.close()
        connection.close()

    def allInOneMarkdownHtml(self):
        diag=QFileDialog()
        options = diag.Options()
        QMessageBox.information(None, "注意", "搜索结果即将全部汇总写入一个markdown文件，文件默认目录为c://youdaoMD/BBS/")
        mddir = "/youdaoMD/BBS/"
        xsize=self.tableGua.rowCount() 
        ysize=self.tableGua.columnCount()
        guaNameStr=self.txtSearchGuaName.text().strip()
        list=[]
        totalContent=""
        for x in range(0,xsize):
            cont=self.tableGua.item(x,5).text()
            totalContent=totalContent+cont+"\n*****\n"
            #cont=cont.replace("![](","*******").replace(".jpg)",".jpg")  #"这是从数据库中获取的\n包含换行的文本"
            # 将文本字段内容转义为 HTML 格式
            escaped_text = html.escape(cont)
            html_cont = escaped_text.replace("\n", "<br>")
            img=self.tableGua.item(x,7).text()
            imgPath="c:/youdaoMD/BBS/"+img
            if img=="":
                imgPath="c:/youdaoMD/roob.jpg"
            #注意：obsedian文件最大宽为800px
            imgLink=' <img src="{}" width="350" height="350" > '.format(imgPath)
            list1=[html_cont, imgLink]
            list.append(list1)
        htmlout=create_html_table(list)
        file_name =mddir+f"{guaNameStr}_汇总_双栏.md"
        file_name2=mddir+f"{guaNameStr}_汇总_单列.md"
        file_back = "c:/Users/Robert/Desktop/"+f"{guaNameStr}_汇总.html"
        file_name, _ = diag.getSaveFileName(self, "保存文件", file_name, "HTML Files (*.html);; markdown file(*.md)", options=options)
        if file_name:
            with open(file_name, 'w',encoding="utf-8") as file:
                file.write(htmlout)
            with open(file_name2,'w',encoding="utf-8") as f:
                f.write(totalContent)
            shutil.copy(file_name, file_back)
        print("Total HTML and Markdown is finished!")
        self.refreshMark()
        

    def paipan(self):
        gua=sixyao.Zhugua()
        day1=self.txtGuaDate.text()
        namestr=self.txtGuaName.text()
        if '之' in namestr:
            split_string=self.txtGuaName.text().split('之')
            name1 = split_string[0].strip() 
            name2 = split_string[1].strip() 
        else:
            name1=namestr.strip("静卦")
            name2=namestr.strip("静卦")
        gzstring=gua.setDate(day1)
        gua.makeGuaByName(name1,name2)
        #outname,guacont=gua.displayDoubleGuaText()
        outGuaName,guacont=gua.displayDoubleGuaText()
        self.txtContent.append(guacont)

    def refreshImg(self):  #用现成的图片地址框刷新图片，以备比较网络数据画出的图片
        img=self.comboImg.currentText()
        #dir=self.dir
        dir_default="c:/youdaoMD/BBS/"
        imgfull=dir_default+img
        if not os.path.exists(imgfull):
            imgfull=self.dir+img
        pixmap=QPixmap(imgfull)
        self.label_pic.setPixmap(pixmap)

    def refreshText(self):
        self.txtGuaName.clear()
        self.txtStockCode.clear()
        self.txtStockName.clear()
        self.txtGuaDate.clear()
        self.txtContent.clear()
        self.txtSubject.clear()
        self.label_pic.clear()
        self.btn_save.setDisabled(True)
        self.insert_mode=True

    def saveNewRecord(self):
        #row = self.tableGua.currentRow()
        #rowid = self.tableGua.item(row, 6).text()
        new_stockCode=self.txtStockCode.text()
        new_guaName=self.txtGuaName.text()
        new_content = self.txtContent.toPlainText()
        new_guaDate=self.txtGuaDate.text()
        #mdlink=self.txtImg.text()
        mdlink=self.comboImg.currentText()
        conn = sqlite3.connect('Guas.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO stockGuas (guaDate,stockName,guaName,guaContent,imgPath ) VALUES (?, ?, ?, ?,?) ", 
                         (new_guaDate, new_stockCode, new_guaName, new_content, mdlink))
        conn.commit()
        #cursor.close()
        conn.close()
        self.btn_save.setDisabled(False)

    def saveJPG(self):
        diag=QFileDialog()
        options = diag.Options()
        mddir = "/youdaoMD/BBS/images/"
        secNum=self.txtStockCode.text()  
        originDay=self.txtGuaDate.text()
        filename=secNum+"_"+originDay+"_"+self.drawType+".jpg"
        defaultFile=mddir+filename
        print("defaultfile is : ", defaultFile)
        newfile, _ = diag.getSaveFileName(self, "保存文件", defaultFile, "jpg Files (*.jpg);; png file(*.png)", options=options)
        #print(newfile)
        if newfile:
            src="temp.jpg"
            shutil.copy(src, newfile)
            print("image file is saved! ")
        mdlink="images/"+os.path.basename(newfile)
        self.txtContent.append( f'![]({mdlink})')
        #self.txtImg.setText(mdlink)
        self.comboImg.addItem(mdlink)
        self.comboImg.setCurrentText(mdlink)
        #if self.insert_mode==False:
        #    self.saveContentChange()
        
    '''
    def deleteSamePics(self):
        newfile=self.txtImg.text().replace("images/","")
        mddir = "/youdaoMD/BBS/images/"
        oldfiles=os.listdir(mddir)
        posnew=newfile.rindex("_")
        for file in oldfiles:
            posold=file.rindex("_")
            if file[0:posold] == newfile[0:posnew] and file != newfile:
                QMessageBox.information(None, "警告", file+"发现与目前保存文件类似，需要删除？") 
                print(mddir+file)
                os.remove(mddir+file)
                print(f"Deleted {file}")
    '''

    def renewStockName(self):   #可以同时搜索股票和ETF
        code=self.txtStockCode.text()
        name=akPlot.findname_stock(code)
        self.txtStockName.setText(name)

    def renewStockCode(self):  #可以同时搜索股票和ETF
        name=self.txtStockName.text()
        code=akPlot.findcode_stock(name)
        code=code.replace("sh","").replace("sz","")
        self.txtStockCode.setText(code)

    def generatePics(self):
        xsize=self.tableGua.rowCount() 
        mddir = "/youdaoMD/BBS/images/"
        #ysize=self.tableGua.columnCount()
        #self.drawType="D"
        for x in range(0,xsize):
            rowid = self.tableGua.item(x, 6).text()
            postTitle=self.tableGua.item(x,0).text()
            rawStock=self.tableGua.item(x,2).text()
            stockCode,stockName=akPlot.extractStockName(rawStock)
            if stockCode=="NULL" or stockName=="NULL":
                stockCode,stockName=akPlot.extractStockName(postTitle)
            stockDate=self.tableGua.item(x,1).text()
            scr=akPlot.drawDailyLine(stockCode,stockDate)
            #pixmap=QPixmap(imgfile)
            filename=secNum+"_"+originDay+"_D.jpg"
            newfile=mddir+filename
            shutil.copy(src, newfile)
            mdlink="images/"+os.path.basename(newfile)
            connection = sqlite3.connect('Guas.db')
            cursor = connection.cursor()
            query='UPDATE StockGuas  SET imgPath="{}" WHERE rowid = {}  '.format(mdlink, rowid)
            cursor.execute(query)
            connection.commit()
            cursor.close()
            connection.close()
        print("batch saving images is OK")

def create_html_table(rows):   
    htmlpage =' <table  width="100%"  border="1" cellpadding="50" > '
    for row in rows:
        htmlpage += "<tr>"
        #length=len(row)
        #setWidth=90/length
        for cell in row:
            # default 两列表格 
            htmlpage += ' <td  width="50%"  > {}   </td> '.format(cell)
        htmlpage += "</tr>"
    htmlpage += "</table>"
    return htmlpage

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.setWindowTitle("金融易经案例库")
    window.show()
    sys.exit(app.exec_())
