import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QDate
from decimal import Decimal
import sqlite3
#import plotlyjk
import sixyao

# 六爻排盘小程序

qtcreator_file  = "E:/stock6yao/bugua.ui" # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtcreator_file)

class MyWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.txtDate.setText("2023-02-20")
        self.txtTotalName.setText("卦名")
        #self.txtUser.setText("风生水起")
        self.btnByYao.clicked.connect(self.displayByYao)
        self.btnByTotal.clicked.connect(self.displayByName)
        self.btnRefresh.clicked.connect(self.refresh)
        self.mycalendar.clicked[QtCore.QDate].connect(self.showDate)
        self.btnInsert.clicked.connect(self.insertRecord)
        self.yao6.setCurrentIndex(1)
        self.yao5.setCurrentIndex(1)
        self.yao4.setCurrentIndex(1)
        self.yao3.setCurrentIndex(1)
        self.yao2.setCurrentIndex(1)
        self.yao1.setCurrentIndex(1)
        
    def showDate(self, date):
        self.txtDate.setText(date.toString("yyyy-MM-dd"))
        
    def displayByYao(self):
        str6=str(self.yao6.currentIndex())
        str5=str(self.yao5.currentIndex())
        str4=str(self.yao4.currentIndex())
        str3=str(self.yao3.currentIndex())
        str2=str(self.yao2.currentIndex())
        str1=str(self.yao1.currentIndex())
        string=str6+str5+str4+str3+str2+str1
        gua1=sixyao.Zhugua()
        day1=self.txtDate.text()
        gzstring=gua1.setDate(day1)
        gua1.makeGuaByYaostring(string)
        outGuaName,guaCont=gua1.displayDoubleGuaText()
        self.txtTotalName.setText(outGuaName)
        self.txtContent.append("占问: "+self.txtObject.text())   
        self.txtContent.append(guaCont)

    def displayByName(self):
        gua=sixyao.Zhugua()
        day1=self.txtDate.text()
        name=self.txtTotalName.text()
        index1=name.find("之")
        if index1!=-1:
            name1=name[0:index1]
            name2=name[index1+1:]
        else:
            name1=name.replace("静卦","")
            name2=name1
        gzstring=gua.setDate(day1)
        gua.makeGuaByName(name1,name2)
        outGuaName, guaCont=gua.displayDoubleGuaText()
        self.txtTotalName.setText(outGuaName)     
        self.txtContent.append(self.txtObject.text())
        self.txtContent.append(guaCont)
        #f.close()
        
    def refresh(self):
        self.txtDate.setText("")
        self.txtTotalName.setText("")
        self.txtObject.setText("")
        self.txtContent.setText("")

    def insertRecord(self):
        conn = sqlite3.connect('Guas.db')
        c = conn.cursor()
        print("cursor is OK....")
        tump1=(self.txtObject.text(), self.txtDate.text(), self.txtTotalName.text(), self.txtContent.toPlainText() )
        print("tump is OK")
        c.execute("INSERT INTO stockGuas ( guaSubject, guaDate,guaName,guaContent) VALUES (?,?,?,?)",tump1 )
        print("insert is OK")
        conn.commit()
        conn.close()
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.setWindowTitle("六爻排盘小程序")
    window.show()    
    sys.exit(app.exec_())
