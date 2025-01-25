import json
import math
import os
import random
import time
from functools import partial

import numpy
from PyQt5.QtCore import QTimer, QPoint, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMenu, QMainWindow, QApplication

import BezierCurves
import Config
from AllResources import AllResources
import CalculagraphWindow
import DebugWindow
import DraggableLabelClass
import sys
import SettingWindow


class MainWindow(QMainWindow):
    # 主窗口类，继承自QMainWindow
    def __init__(self, parent=None):
        super().__init__(parent)

        self.timer = None
        self.calculagraph : CalculagraphWindow.CalculagraphWindow = None

        self.Setting:SettingWindow.SettingWindow = None
        self.readConfig()  #读取配置文件
        self.CalculagraphIsOpen = False
        self.SettingIsOpen = False
        self.TempLabel = None
        self.LabelList = {}
        self.pointAppearingBegging = False  #点动画是否开始
        self.ScaleCount = Config.getValue("缩放大小") #缩放大小
        self.Radius = (67 // 2)*self.ScaleCount #半径

        self.TickBegging = False
        self.changeBegging = False

        self.sec = 0
        self.PointNum = int(self.每一业力等级所需的时间 / self.单个点所代表的时间)  #点的个数
        self.Angle = 0  #当前角度

        self.Speed = 0.5  #旋转速度
        self.setwindow()  #设置窗口
        self.displayimg()  #显示图片
        self.Ttimer()  #旋转角度持续变化

        self.point_appearing_timer(1.5)  #刻度点动画
        self.showDebugWindow() #测试用



    # 显示窗口
    def showDebugWindow(self):
        self.Debug = DebugWindow.DebugWindow(self.LabelList,self)
        self.Debug.show()

    def showSettingWindow(self):
        try:
            if not self.Setting.isVisible():
                # self.Setting = SettingWindow.SettingWindow(self.LabelList, self)
                self.Setting.show()
        except:
            self.Setting = SettingWindow.SettingWindow(self.LabelList, self)
            self.Setting.show()

    def showCalculagraphWindow(self):
        try:
            if not self.calculagraph.isVisible():
                # self.calculagraph = CalculagraphWindow.CalculagraphWindow(self.LabelList, self)
                self.calculagraph.show()
        except:
            self.calculagraph = CalculagraphWindow.CalculagraphWindow(self.LabelList, self)
            self.calculagraph.show()

    def RestartTtimer(self):
        for key,value in self.LabelList.items():
            value.change_size_start(1,self.ScaleCount)
        # 重启计时器
        try:
            if self.calculagraph.Ptimer is not None:
                self.calculagraph.Ptimer.stop()
                self.calculagraph.second1 = 0
                self.calculagraph.second2 = 0
                self.calculagraph.second = 0
                self.calculagraph.PerSecond = 0
                self.calculagraph.Ptimer = None
                self.calculagraph.LabelList2["分:"].setValue(0)
                self.calculagraph.LabelList2["秒:"].setValue(0)
        except:
            pass
        self.restart()
        self.timer.stop()
        self.readConfig()
        self.Ttimer()

    def restart(self,TempPointNum = None):
        self.readConfig()
        if TempPointNum is not None: #计时不满一层时按计算得到的点来进行生成
            self.PointNum = TempPointNum
        else :
            self.PointNum = int(self.每一业力等级所需的时间 / self.单个点所代表的时间) #每层循环点的数量
        templist = []
        for i,_ in self.LabelList.items():
            #判断i是否为数字
            if isinstance(i,int):
                self.LabelList[i].deleteLater()
                templist.append(i)
        for i in templist:
            self.LabelList.pop(i)
        self.putPoint() #重新创建点
        # self.point_appearing_timer(self.点动画入场时间)


    #读取配置文件
    def readConfig(self):
        if not os.path.exists("Settings.json"):
            Config.create_config()

        with open("Settings.json", "r",encoding="utf-8") as f:
            config = json.load(f)
            self.tick响应所需时间 = config["tick响应所需时间"]
            self.主环入场时间 = config["主环入场时间"]
            self.点动画入场时间 = config["点动画入场时间"]
            self.点动画出场时间 = config["点动画出场时间"]
            self.业力消失时间 = config["业力消失时间"]
            self.业力进入时间 = config["业力进入时间"]
            self.单个点所代表的时间 = config["单个点所代表的时间"]
            self.每一业力等级所需的时间 = config["每一业力等级所需的时间"]
            self.ScaleCount = config["缩放大小"]

    #全屏窗口
    def setwindow(self):
        self.setWindowTitle("114514")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(1920, 1080)

    # 创建组件
    def CreateLabel(self, name, image: str, ScaleCount: int = 1, MainCircle=False, Touchable=False):

        # print(f"正在显示：{name}")

        temp = QPixmap(image)  # 读取图片
        TempLabel = DraggableLabelClass.DraggableLabel(self, MainCircle=MainCircle, Touchable=Touchable, image=image, index = name, resetPos = self.resetPos, MainWindow1 = self)  # 设置属性
        self.LabelList[name] = TempLabel# 加入字典方便索引
        TempLabel.setPixmap(temp.scaled(int(temp.width() * ScaleCount), int(temp.height() * ScaleCount)))  # 放置图片
        ScaledWidthTemp = temp.width() * ScaleCount
        ScaledheightTemp = temp.height() * ScaleCount
        TempLabel.resize(int(ScaledWidthTemp), int(ScaledheightTemp))# 设置大小以保持和图片一样大
        TempLabel.show()
        # 调试用
        # TempLabel.setStyleSheet("background-color: black")
        return TempLabel

    def putPoint(self,an = True):
        for i in range(self.PointNum):
            if i not in self.LabelList:
                if an:
                    self.CreateLabel(i, AllResources['point.png'], ScaleCount=self.ScaleCount).huan_ru_start(self.主环入场时间)
                else:
                    self.CreateLabel(i, AllResources['point.png'], ScaleCount=self.ScaleCount)
                self.LabelList[i].setFather(self.LabelList["Circle"])
        self.updatePointPos()


    # 显示图片
    def displayimg(self):
        #主环
        self.CreateLabel("Circle", AllResources["Circle.png"], self.ScaleCount, True, Touchable=True).huan_ru_start(self.主环入场时间,
                                                                                                                   "Pre")
        Circle = self.LabelList["Circle"]


        self.CreateLabel("Center", AllResources["Karma_1.png"], self.ScaleCount).huan_ru_start(self.主环入场时间)
        #创建点
        self.putPoint()


        self.LabelList["Center"].setFather(Circle)  #子绑父

        for _,i in self.LabelList.items(): #移动
            i.move(500,500)

    # 更新点坐标
    def updatePointPos(self, per=1.0):
        Circle = self.LabelList["Circle"]
        for i in range(self.PointNum):
            # 计算主圈中心坐标
            CircleCenter = QPoint(int(Circle.width() / 2), int(Circle.height() / 2)) + Circle.pos()
            self.Angle = (360 // self.PointNum) * per
            # 计算每个点所对应的角度
            rad = (math.pi / 180) *self.Angle + ((math.pi * 2 * per) / self.PointNum) * i

            # 计算计时点的相对坐标
            PointPos = QPoint(int(math.sin(rad) * self.Radius - self.LabelList[i].width() / 2),
                              -int(math.cos(rad) * self.Radius + self.LabelList[i].height() / 2))

            # 移动计时点到新位置
            self.LabelList[i].move(PointPos + CircleCenter)

    # 改变图标等级
    def changeLevel(self,level:str):
        def continue_changeLevel():
            print(f"改变等级->{level}")
            (self.CreateLabel("Center", AllResources[level], self.ScaleCount)
             .suo_xiao_ru_start(self.业力进入时间, self.setRadius, ScaleCount=self.ScaleCount, sound="Pre")
             .setFather(self.LabelList["Circle"])
             .move(self.LabelList["Circle"].pos()))
            # self.LabelList["Center"].huan_ru_start(2,sound="Pre")
            self.changeBegging = False
        if not self.changeBegging:
            self.changeBegging = True
            self.LabelList["Center"].suo_xiao_chu_start(self.业力消失时间, True, self.setRadius, ScaleCount=self.ScaleCount) #缓出并且删除
            QTimer.singleShot(self.业力消失时间 * 1000 + 1, lambda :continue_changeLevel())

    # 重置图标位置
    def resetPos(self):
        for index,i in self.LabelList.items():
            if not index in range(0,self.PointNum):
                ccpos = self.LabelList["Circle"].getCenterPos()
                try:
                    i.move(ccpos - QPoint(i.width()//2,i.height()//2))
                except:
                    pass
    # 出场时点的动画
    def pointAppearing(self, need_time):
        dt = time.time() - self.PStartTime
        #更新位置
        if dt <= need_time:
            per = (math.sin(dt * (math.pi / need_time) + math.pi * 3 / 2) + 1) / 2  #0 -> 100%
            value = DraggableLabelClass.bezier_curves(BezierCurves.BezierCurves["快入后缓"], per)[1]
            self.Radius = (67//2) *self.ScaleCount * value
            self.updatePointPos(per)
        else:
            self.pointAppearingBegging = False
            self.Ptimer.stop()

    # 设置半径，回调函数
    def setRadius(self, value):
        self.Radius = value

    def tick(self,Timer,St,R):
        dt = time.time() - St
        if dt <= 0.2:
            per = (math.sin(dt * (math.pi / 0.2) + math.pi * 3 / 2) + 1) / 2
            value = DraggableLabelClass.bezier_curves(BezierCurves.BezierCurves["弹一下"], per)[1]
            self.Radius = int(R+ 5*value)
            self.updatePointPos()
        else:
            self.TickBegging = False
            Timer.stop()
            if random.randint(0,1) == 0:
                self.playsound("tick")
            else:
                self.playsound("tock")

    def tick_timer(self):
        if not self.TickBegging and not self.pointAppearingBegging:
            self.TickBegging = True
            Ptimer = QTimer(self)
            PStartTime = time.time()
            R = self.Radius
            Ptimer.timeout.connect(partial(self.tick,Ptimer,PStartTime,R))
            Ptimer.start(10)

    # 点出现的计时器
    def point_appearing_timer(self, needtime=5):
        if not self.pointAppearingBegging:
            self.pointAppearingBegging = True
            self.Ptimer = QTimer(self)
            self.PStartTime = time.time()
            self.Ptimer.timeout.connect(partial(self.pointAppearing, needtime))
            self.Ptimer.start(10)

    # 增加计时器
    def Ttimer(self):
        self.timer = QTimer(self)
        self.StartTime = time.time()
        self.timer.timeout.connect(self.tick_timer)
        self.timer.start(self.tick响应所需时间*1000) #30秒激活

    # 播放声音
    def playsound(self,sound = "Pre"):
        self.sound_thread = DraggableLabelClass.SoundThread(AllResources[f"{sound}.wav"])
        self.sound_thread.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()

    sys.exit(app.exec())
