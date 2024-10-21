# -*- coding:utf-8 -*-
"""
------------------------------------------------
File Name: 文本框.py
Description:
Author: lzq
date:2024-07-27 11:28
------------------------------------------------
"""
import sys

import PyQt5 
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QWidget, QTextEdit, QPushButton, QVBoxLayout, QApplication

html_content='''
   <font color='red' size='6'>python 程序设计<p>pyQt5界面设计</p></font>
   <p>C语言中文网，一个在线学习编程的网站，网址：<a href="http://www.biancheng.net/" target="_blank">http://www.biancheng.net/</a></p>
    <p>C语言中文网目前已经发布了将近 <b>50</b> 套教程，包括 HTML、CSS、JavaScript 等，您可以<a href="http://c.biancheng.net/sitemap/" target="_blank">猛击这里</a>查看所有教程。</p>
    <p>我们的 Slogan：千锤百炼，只为大作；精益求精，句句斟酌；这种教程，看一眼就倾心。</p>
    <img src="images/000810_2016-02-03_D.jpg" alt="C语言中文网Logo"> 
'''
class MyWidget(QWidget):
    def __init__(self, parent=None):
        super(MyWidget, self).__init__(parent)
        self.setWindowTitle("文本框QTextEdit测试")
        self.resize(600,540)
        self.te = QTextEdit()
        self.btn1 = QPushButton("显示HTML")
        self.btn2 = QPushButton("恢复显示")
        vlayout=QVBoxLayout()
        vlayout.addWidget(self.te)
        vlayout.addWidget(self.btn1)
        vlayout.addWidget(self.btn2)
        self.setLayout(vlayout)
        # 设置文本框初始显示内容和颜色
        self.te.setPlainText("Python 编辑\nPyQt5 界面编程")
        self.te.setTextColor(PyQt5.QtGui.QColor(0,0,255))

        self.btn1.clicked.connect(self.btn1Clicked)
        self.btn2.clicked.connect(self.btn2Clicked)

    def btn1Clicked(self):
        global tmp
        tmp=self.te.toPlainText()
       # self.te.setHtml("<font color='red' size='6'>python 程序设计<p>pyQt5界面设计</p></font>")
        self.te.setHtml(html_content)

    def btn2Clicked(self):
        global tmp
        self.te.setPlainText(tmp)

    def paintEvent(self, event):  # set background_img
        painter = QPainter(self)
        painter.drawRect(self.rect())
        pixmap = QPixmap("./images/bg.jpg")  # 换成自己的图片的相对路径
        painter.drawPixmap(self.rect(), pixmap)

if __name__=='__main__':
    app = QApplication(sys.argv)
    w = MyWidget()
    w.paintEngine()
    w.show()
    sys.exit(app.exec())