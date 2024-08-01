import sys, os,re, shutil
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QWidget, QTreeView, QFileSystemModel, QPlainTextEdit, QMessageBox,QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QDate
from decimal import Decimal
import sixyao
import akshare_plotly as akPlot
from aip import AipOcr

qtcreator_file  = "md2candle.ui" # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtcreator_file)


class MyWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.model = QFileSystemModel()
        self.rootPath = CURRENT_DIR
        self.model.setRootPath(self.rootPath) # 设置显示根目录
        self.model.setNameFilters(['*.md','*.html']) # 
        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(CURRENT_DIR)) 
        self.tree_view.clicked.connect(self.file_selected)
        self.tree_view.rootIsDecorated()
        self.btn_draw.clicked.connect(self.drawCandle)
        self.btn_draw2.clicked.connect(self.drawCandleMonth)
        self.btn_save.clicked.connect(self.saveContent)
        self.btn_save_img.clicked.connect(self.saveJPG)
        #self.txtImg.editingFinished.connect(self.refreshImg)
        self.btn_paipan.clicked.connect(self.paipan)
        self.txtStockCode.editingFinished.connect(self.renewStockName)
        self.txtStockName.editingFinished.connect(self.renewStockCode)
        self.btn_subject.clicked.connect(self.refreshSubject)
        self.btn_insert_filename.clicked.connect(self.insertFileName)
        #self.btn_insert_info.clicked.connect(self.insertInfo)
        self.actRename.triggered.connect(self.renameFile)
        self.actSaveAs.triggered.connect(self.saveAsNewFile)
        self.actDelete.triggered.connect(self.deleteFile)
        self.actMove.triggered.connect(self.moveFile)
        self.comboBox.currentIndexChanged.connect(self.refreshImg)
        self.btn_ocr.clicked.connect(self.baiduOCR)

    def renewStockName(self):   #可以同时搜索股票和ETF
        code=self.txtStockCode.text()
        name=akPlot.findname_stock(code)
        self.txtStockName.setText(name)

    def renewStockCode(self):  #可以同时搜索股票和ETF
        name=self.txtStockName.text()
        code=akPlot.findcode_stock(name)
        code=code.replace("sh","").replace("sz","")
        self.txtStockCode.setText(code)

    def file_selected(self, index):
        self.comboBox.clear()
        self.txtSubject.clear()
        file_path = self.model.filePath(index)
        print("file_path:", file_path)
        self.filesel=file_path
        if os.path.isfile(file_path) and file_path.endswith('.md'):
            with open(file_path, 'r',encoding="utf-8") as file:
                content = file.read()
            content=re.sub(r'\n{2,}','\n',content)
            filename=os.path.basename(file_path)
            print("filename:",filename)
            self.txtContent.setPlainText(content)
            guaName=akPlot.getGuaFromTitle(filename)
            if guaName=="NULL":
                guaName=akPlot.getGuaName(content)
            day=akPlot.getDate(filename)
            if day=="NULL":
                day=akPlot.getDate(content)
            code,name=akPlot.extractStockName(filename)
            if code=="NULL" and name=="NULL":
                code,name=akPlot.extractStockName(content)
            #if code=="NULL" and name=="NULL":
            #    code="sh000001"
            #    name="上证指数"
            self.txtStockCode.setText(code)
            self.txtStockName.setText(name)
            self.txtGuaDate.setText(day)
            self.txtGuaName.setText(guaName)
            subject=akPlot.getSubject(content)
            if subject=="NULL":
                name=os.path.basename(self.filesel)
                name=name.replace(".md","")
                subject=name
            self.txtSubject.setText(subject)
            re1=r'images.+jpg|images.+.jpeg|images.+png'
            images=re.findall(re1,content)
            self.imagelist=images
            if images:
                img=images[0]
                #self.txtImg.setText(img)
                self.comboBox.addItems(images)
                mddir = os.path.dirname(self.filesel)
                img=mddir+"/"+img
                pixmap=QPixmap(img)
                self.label_pic.setPixmap(pixmap)

    def drawCandle(self):
        self.drawType="W"
        mddir = os.path.dirname(self.filesel)
        print("dir is : ", mddir)
        imgdir=mddir+"/images"
        code=self.txtStockCode.text()
        date=self.txtGuaDate.text()
        if code=="NULL" or date=="NULL":
            QMessageBox.information(None, "警告", "代码与时间不能为空")
        else:
            imgfile=akPlot.drawDailyLine(code,date)
            self.filename=imgfile.split("/")[-1]
            print(imgfile, self.filename)
            pixmap=QPixmap('temp.jpg')
            self.label_pic.setPixmap(pixmap)
            #mdlink="images/"+self.filename
            #self.txtImg.setText(mdlink)

    def drawCandleMonth(self):
        self.drawType="M"
        mddir = os.path.dirname(self.filesel)
        print("dir is :", mddir)
        imgdir=mddir+"/images"
        code=self.txtStockCode.text()
        date=self.txtGuaDate.text()
        if code=="NULL" or date=="NULL":
            QMessageBox.information(None, "警告", "代码与时间不能为空")
        else:
            imgfile=akPlot.drawMonthLine(code,date)
            self.filename=imgfile.split("/")[-1]
            print(imgfile, self.filename)
            pixmap=QPixmap('temp.jpg')
            self.label_pic.setPixmap(pixmap)
            #mdlink="images/"+self.filename
            #self.txtImg.setText(mdlink)

    def saveContent(self):
        with open(self.filesel, 'w',encoding="utf-8") as file:
            newcontent=self.txtContent.toPlainText()
            file.write(newcontent)
        print("save pic link to file is OK!")
    
    def saveAsNewFile(self):
        diag=QFileDialog()
        options = diag.Options()
        new_stockCode=self.txtStockCode.text()
        new_stockName=self.txtStockName.text()
        new_guaName=self.txtGuaName.text()
        new_content = self.txtContent.toPlainText()
        new_date=self.txtGuaDate.text()
        new_subject=self.txtSubject.text()
        file_name =  f"{new_guaName}_{new_stockCode}_{new_stockName}_{new_date}_{new_subject}.md"
        file_name=CURRENT_DIR +file_name
        file_name, _ = diag.getSaveFileName(self, "保存当前记录到全新markdown文件！", file_name, "markdown Files (*.md);;txt  file(*.txt)", options=options)
        if file_name:
            with open(file_name, 'w',encoding="utf-8") as file:
                file.write(new_content)

    def saveJPG(self):
        diag=QFileDialog()
        options = diag.Options()
        secNum=self.txtStockCode.text()  
        originDay=self.txtGuaDate.text()
        filename=secNum+"_"+originDay+"_"+self.drawType+".jpg"
        defaultFile=CURRENT_DIR+"/images/"+filename
        print("default is : ", defaultFile)
        newfile, _ = diag.getSaveFileName(self, "保存文件", defaultFile, "jpg Files (*.jpg);; png file(*.png)", options=options)
        #print(newfile)
        if newfile:
            src="temp.jpg"
            shutil.copy(src, newfile)
            print("image file is saved! ")
        mdlink="images/"+os.path.basename(newfile)
        self.txtContent.append( f'![]({mdlink})')
        #self.txtImg.setText(mdlink)
        self.comboBox.addItem(mdlink)
        self.saveContent()
    
    def refreshImg(self):
        img=self.comboBox.currentText()
        #img=self.txtImg.text()
        mddir = os.path.dirname(self.filesel)
        img=mddir+"/"+img
        pixmap=QPixmap(img)
        self.label_pic.setPixmap(pixmap)
    
    def paipan(self):
        if self.txtGuaName.text()=="NULL" or self.txtGuaDate.text()=="NULL":
            QMessageBox.information(None, "警告", "卦名与时间不能为空")
            self.txtGuaName.setFocus()
        else:
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
            outGuaName,guacont=gua.displayDoubleGuaText()
            self.txtContent.insertPlainText(guacont)

    def renameFile(self):
        old_name=self.filesel
        new_guaName=self.txtGuaName.text()
        new_stockCode=self.txtStockCode.text()
        new_stockName=self.txtStockName.text()
        new_date=self.txtGuaDate.text()
        new_subject=self.txtSubject.text()
        self.saveContent()
        new_name = f"{new_guaName}_{new_stockCode}_{new_stockName}_{new_date}_{new_subject}.md"
        new_name=CURRENT_DIR+new_name
        diag=QFileDialog()
        options = diag.Options()
        new_name, _ = diag.getSaveFileName(self, "文件将改名为：", new_name, "markdown Files (*.md);;txt  file(*.txt)", options=options)
        if new_name:
            print(old_name, new_name)
            if not os.path.exists(new_name):
                os.rename(old_name,new_name)
                print("old file has been renamed!")
            else:
                os.remove(old_name)
                print("new file exists, old file has been deleted!")
            self.clear()

    def refreshSubject(self):
        content=self.txtContent.toPlainText()
        subject=akPlot.getSubject(content)
        #if not akPlot.isSubjectValid(subject):
        #    subject=os.path.basename(self.filesel).replace(".md","")
        self.txtSubject.setText(subject)

    def baiduOCR(self):  # picfile:图片文件名
        imgCurrent=self.comboBox.currentText()
        #img=self.txtImg.text()
        mddir = os.path.dirname(self.filesel)
        picfile=mddir+"/"+imgCurrent
        print(picfile)
        # 百度提供
        APP_ID='30244035'
        API_KEY='hZU6fDI7MP6iG5bFaXtIGcsk'
        SECRET_KEY = 'QGChDbrUKMwxMONN1tWnm24a6ZKz91We'
        client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
        print("Baidu clinet connection is OK!")
        i = open(picfile, 'rb')
        img = i.read()
        message = client.basicGeneral(img)
        #data = str(client.basicGeneral(image))
        i.close() 
        string=""    
        for text in message.get('words_result'):  # 识别的内容
           # print(text.get('words'))
            str_row=text.get('words')
            string+=str_row
        print("BAIDU OCR RESULT: ")
        print(string)
        guaName=self.txtGuaName.text()
        stockCode=self.txtStockCode.text()
        stockName=self.txtStockName.text()
        if guaName=="NULL":
            guaName=akPlot.getGuaName(string)
        if stockCode=="NULL":
            stockCode,stockName=akPlot.extractStockName(string)
        guaDate=akPlot.getDate(string)
        if guaDate=="NULL":
            guaDate=day=akPlot.getDateFromGanzi(string) 
        subject=akPlot.getSubject(string)
        if subject=="NULL":
            name=os.path.basename(self.filesel)
            name=name.replace(".md","")
            subject=name
        info=f'{guaName}_{stockCode}_{guaDate}\n占事:{subject}\n'
        self.txtGuaName.setText(guaName)
        self.txtStockName.setText(stockName)
        self.txtStockCode.setText(stockCode)
        self.txtGuaDate.setText(guaDate)
        self.txtSubject.setText(subject)
        text_cursor = self.txtContent.textCursor()
        text_cursor.setPosition(0)
        text_cursor.insertText(info)
        if guaName=="NULL" or guaDate=="NULL" :
            QMessageBox.information(None, "警告", "卦名与时间不能为空")
        else:
            self.paipan()
    
    def insertFileName(self):
        #name=self.filesel
        name=os.path.basename(self.filesel)
        name=name.replace(".md","")
        name=name+"\n"
        text_cursor = self.txtContent.textCursor()
        text_cursor.setPosition(0)
        text_cursor.insertText(name)

    def clear(self):
        self.txtSubject.clear()
        self.txtContent.clear()
        self.txtStockName.clear()
        self.txtStockCode.clear()
        self.txtGuaName.clear()
        self.label_pic.clear()
        self.txtGuaDate.clear()
        self.comboBox.clear()

    def deleteFile(self):
        old_name=self.filesel
        #mddir = os.path.dirname(self.filesel)
        print(old_name)
        QMessageBox.information(None, "警告", old_name+"将被删除，请确认！")
        os.remove(old_name)

    def moveFile(self):
        old_name=self.filesel
        diag=QFileDialog()
        options = diag.Options()
        new_name, _ = diag.getSaveFileName(self, "文件将移动到新目录下：", old_name, "markdown Files (*.md);;txt  file(*.txt)", options=options)
        if new_name:
            if not os.path.exists(new_name):
                os.rename(old_name,new_name)
                if len(self.imagelist)>0:
                    for img in self.imagelist:
                        mddir = os.path.dirname(self.filesel)
                        oldimg=mddir+"/"+img
                        target_dir=os.path.dirname(new_name)
                        newimg=target_dir+"/"+img
                        os.rename(oldimg,newimg)
                        print("img is moving:", oldimg,newimg)
        print("the file has move to:", new_name)

#CURRENT_DIR="C:/youdaoMD/测股卦例v3/"
#CURRENT_DIR="C:/youdaoMD/A年卦月卦周卦/2014甲午年/"
#CURRENT_DIR="C:/youdaoMD/A年卦月卦周卦/2015乙未年/"
#CURRENT_DIR="C:/youdaoMD/A年卦月卦周卦/2017丁酉年/"
#CURRENT_DIR="C:/youdaoMD/A年卦月卦周卦/2018戊戌年/"
#CURRENT_DIR="C:/youdaoMD/A年卦月卦周卦/2019己亥年/"
#CURRENT_DIR="C:/youdaoMD/A年卦月卦周卦/2020庚子年/"
#CURRENT_DIR="C:/youdaoMD/易经测市/"
CURRENT_DIR="C:/youdaoMD/A年卦月卦周卦/"

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.setWindowTitle("md文件增加K线图")
    window.show()    
    sys.exit(app.exec_())