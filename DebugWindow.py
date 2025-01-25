import random
import sys
import time
from functools import partial

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QSlider, QLabel, QMessageBox

import main
from AllResources import *


class DebugWindow(QWidget):
    def __init__(self,LabelList,MainWindow1):
        """
        初始化DebugWindow类，设置窗口标题、大小、布局等。
        :param LabelList: 标签列表
        :param this_object: 当前对象
        """
        super().__init__()
        self.Ptimer = None
        self.MainWindow: main.MainWindow = MainWindow1
        self.LabelList = LabelList
        self.setWindowTitle("Debug Window")
        self.setGeometry(100, 100, 400, 300)
        self.second = 0

        self.TextList = {}
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.display()
        self.PointLevel = self.MainWindow.PointNum * 2 - 1
        self.当前到达的序号 = 0
        i = 0
        self.list = []
        for i in AllResources:
            if i.count(".png") == 1 and i not in ["Circle.png","point.png","half_point.png"]:
                self.list.append(i)

    def display(self):
        """
        在窗口中创建滑块和按钮，用于控制缩放、角度、随机切换等操作。
        """
        self.CreateSlider(self.change,"缩放倍数")
        self.CreateSlider(self.changeRad,"角度",max_value=360,min_value=0)
        self.CreateButton("随机切换",self.test)
        self.CreateButton("减少一次点",self.changePointLevel)
        self.CreateButton("同时",self.test2)
        self.CreateButton("开始计时",self.tick_timer)
        self.CreateButton("重开", self.MainWindow.restart)

    def changePointLevel(self):
        """
        减少点的层级，更新标签的显示状态。
        """
        for i in range(self.MainWindow.PointNum):
            if self.当前到达的序号 == i * 2:
                #如果当前到达的序号等于最前面点的序号
                self.LabelList[i].deleteLater()
                self.MainWindow.CreateLabel(i, AllResources["half_point.png"], self.MainWindow.ScaleCount).setFather(self.LabelList["Circle"]).update_label_opacity(1)
                self.MainWindow.updatePointPos()
            if self.当前到达的序号 == i * 2 + 1:
                #如果等于最前面点的序号的下一个则删除
                self.LabelList[i].deleteLater()
                self.MainWindow.CreateLabel(i, AllResources["point.png"], self.MainWindow.ScaleCount).setFather(self.LabelList["Circle"]).update_label_opacity(1)
                self.MainWindow.updatePointPos()
                self.LabelList[i].suo_xiao_chu_start(self.MainWindow.点动画出场时间, remove=False, setR = self.MainWindow.setRadius, ScaleCount=self.MainWindow.ScaleCount)
                i += 1
        print(f"当前到达的序号为{self.当前到达的序号}")
        self.当前到达的序号 += 1

        #test
        # 当当前到达的序号等于设置的点等级加一时，重置当前到达的序号并更新所有标签
        if self.当前到达的序号 == self.PointLevel+1:
            self.当前到达的序号 = 0
            # 遍历当前对象的点数量
            for i in range(self.MainWindow.PointNum):
                self.LabelList[i].huan_chu_start(1.5,remove=True) #测试用，删除所有标签
                self.MainWindow.CreateLabel(i, AllResources["point.png"], ScaleCount=self.MainWindow.ScaleCount).setFather(self.LabelList["Circle"])
                # self.LabelList[i].update_label_opacity(0).huan_ru_start(1.5)
                self.LabelList[i].update_label_opacity(0).suo_xiao_ru_start(self.MainWindow.点动画入场时间, self.MainWindow.setRadius, ScaleCount=self.MainWindow.ScaleCount)
                self.MainWindow.point_appearing_timer(self.MainWindow.点动画入场时间)
                self.MainWindow.updatePointPos()

            self.test()

    def test2(self):
        """
        测试函数，用于同时更新所有点的显示状态。
        """
        for i in range(self.MainWindow.PointNum):
            self.LabelList[i].deleteLater()
            self.MainWindow.CreateLabel(i, AllResources["point.png"],
                                        ScaleCount=self.MainWindow.ScaleCount).setFather(self.LabelList["Circle"])
            # self.LabelList[i].update_label_opacity(0).huan_ru_start(1.5)
            self.LabelList[i].update_label_opacity(0).suo_xiao_ru_start(self.MainWindow.点动画入场时间, self.MainWindow.setRadius,
                                                                        ScaleCount=self.MainWindow.ScaleCount)
            self.MainWindow.point_appearing_timer(self.MainWindow.点动画入场时间)
            self.MainWindow.updatePointPos()
        self.test()

    def changeRad(self,value):
        """
        修改角度并更新点的位置。
        :param value: 角度值
        """
        self.MainWindow.Angle = value
        self.MainWindow.updatePointPos()

    def change(self,value):
        """
        修改缩放比例并更新标签大小。
        :param value: 缩放比例值
        """
        self.MainWindow.ScaleCount = value

        for _,i in self.LabelList.items():
            self.MainWindow.Radius = (67 // 2) * self.MainWindow.ScaleCount
            i.changeSize(i.image, self.MainWindow.ScaleCount)
        self.MainWindow.updatePointPos()

    def updateText(self, value, name, text):
        """
        更新滑块对应的文本显示。
        :param value: 滑块值
        :param name: 滑块名称
        :param text: 文本标签
        """
        text.setText(f"{name}:{value}")

    def test(self):
        """
        随机切换显示状态。
        """
        self.MainWindow.changeLevel(self.list[random.randint(0, len(self.list)) - 1])

    def addSecond(self):
        """
        增加计时器秒数并检查是否需要更新点。
        """
        self.second += 0.001
        self.setWindowTitle(f"Debug Window ({self.second}s)")
        self.checkSecond()

    def checkSecond (self):
        """
        检查计时器秒数
        """
        if self.second >= self.MainWindow.单个点所代表的时间 / 2:
            self.second = 0
            self.changePointLevel()

    def tick_timer(self):
        """
        启动计时器，每0.001触发一次addSecond函数。
        """
        self.Ptimer = QTimer(self)
        self.Ptimer.timeout.connect(self.addSecond)
        self.Ptimer.start(1)

    def CreateSlider(self,func,name,max_value=10,min_value=0):
        """
        创建一个滑块并添加到布局中。
        :param func: 滑块值改变时调用的函数
        :param name: 滑块名称
        :param max_value: 滑块最大值
        :param min_value: 滑块最小值
        """
        slider =  QSlider(Qt.Horizontal,self)
        slider.setMinimum(min_value)
        slider.setMaximum(max_value)
        slider.setValue(0)
        slider.setTickInterval(10)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.valueChanged.connect(func)
        self.layout.addWidget(slider)
        text = QLabel("",self)
        self.TextList[(slider,name,text)] = text
        self.layout.addWidget(text)
        slider.valueChanged.connect(partial(self.updateText,name=name,text=text))

    def CreateButton(self, value,func):
        """
        创建一个按钮并添加到布局中。
        :param value: 按钮显示的文本
        :param func: 按钮点击时调用的函数
        """
        TempButton = QPushButton(value)
        TempButton.clicked.connect(func)  # 连接到槽函数
        self.layout.addWidget(TempButton)
        TempButton.show()
        print(f"Button '{value}' created and added to layout")  # 调试输出

    def showEvent(self, event):
        super().showEvent(event)
        self.raise_()  # 确保窗口显示在最上层
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.show()  # 重新显示窗口以应用顶置标志