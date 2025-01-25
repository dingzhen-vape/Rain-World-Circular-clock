import math
import sys
import time
from functools import partial

import pygame
from PyQt5.QtCore import Qt, QPoint, QTimer, QThread
from PyQt5.QtGui import QPixmap

from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QGraphicsOpacityEffect, QMenu

import BezierCurves
import Config
from AllResources import AllResources
import main


# OopCompanion:suppressRename
#声音线程,放置播放声音堵塞主程序动画
class SoundThread(QThread):
    def __init__(self, sound_file=None):
        super().__init__()
        self.sound_file = sound_file

    def run(self):
        if self.sound_file:
            pygame.mixer.init()
            pygame.mixer.music.load(self.sound_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                self.msleep(100)  # 等待声音播放完成

#贝塞尔曲线
def bezier_curves(points, t):
    return ((1 - t) ** 3 * points[0] +
            3 * (1 - t) ** 2 * t * points[1] +
            3 * (1 - t) * t ** 2 * points[2] +
            t ** 3 * points[3])

class DraggableLabel(QLabel):
    def __init__(self, parent=None,MainCircle = False,Touchable = False,image = None,index = None,resetPos= None,MainWindow1 = None):

        super().__init__(parent)

        self.ChangeSizeTimer = None
        self.MainWindow : main.MainWindow = MainWindow1 #接受一个主窗口的地址
        self.resetPos = resetPos #接受一个方法的地址
        self.index= index #自身的序号
        self.Touchable = Touchable #是否可以触摸
        self.image = image #自己的图片

        self.SuoXiaoChuBegging = False
        self.SuoXiaoRuBegging = False#缩小入场
        self.HuanChuBegging = False#缓出
        self.HuanRuBegging = False #缓入是否开始

        self.last_position = None #记录上一次移动的坐标
        self.delta = None #坐标偏移量
        self.ChildLabelList = [] #子组件列表
        self.MainCircle = MainCircle #是否是主组件
        self.dragging = False #是否正在拖拽
        self.childLabel = None #是否是子组件
        self.opacity_value = 0#透明度
        self.setAttribute(Qt.WA_TransparentForMouseEvents,not Touchable) #是否可以拖拽，默认不可以
        self.drag_start_position = QPoint()#获取坐标
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        #缓入
        self.update_label_opacity(0)





    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_start_position = event.globalPos() - self.pos()
            self.last_position = self.pos()
        if event.button() == Qt.RightButton:
            menu = QMenu(self)
            calculagraph = menu.addAction("打开计时器")
            setting = menu.addAction("打开参数设置")
            exit = menu.addAction("退出")
            calculagraph.triggered.connect(lambda :self.MainWindow.showCalculagraphWindow())
            setting.triggered.connect(lambda : self.MainWindow.showSettingWindow())
            exit.triggered.connect(lambda : sys.exit())
            menu.exec_(event.globalPos())

    def mouseMoveEvent(self, event):
        self.MainWindow.resetPos()
        if self.dragging and self.Touchable:
            current_position = event.globalPos() - self.drag_start_position
            self.move(current_position)
            if not self.delta:#如果偏移量不存在
                self.delta = self.pos()
            if self.last_position:#如果上个坐标存在
                self.delta = current_position - self.last_position
            if self.ChildLabelList:#如果子组件存在
                for i in self.ChildLabelList:
                    #i 为子组件
                    try:
                        i.move(self.delta +i.pos())
                    except:
                        self.ChildLabelList.remove(i)
            self.last_position = current_position

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            # self.resetPos()

    #设置子组件（子组件跟着父组件移动）
    def setChild(self,child):
        self.childLabel = child
        self.ChildLabelList.append(child)
        child.setAttribute(Qt.WA_TransparentForMouseEvents,True)
        return self
    #调用父组建的设置子组件方法设置子组件为自己
    def setFather(self,father):
        father.setChild(self)
        return self
    #更新透明度
    def update_label_opacity(self, opacity):
        # 通过 QGraphicsOpacityEffect 设置透明度
        self.opacity_effect.setOpacity(opacity)
        return self
    #获取中心坐标
    def getCenterPos(self):
        return self.pos() + QPoint(self.width()//2,self.height()//2)
    #改变大小
    def changeSize(self, image, ScaleCount=1.0,Change = False):
        temp = QPixmap(image)#读取图片
        cPos = self.getCenterPos()
        t = temp.width()
        if Change:
            self.MainWindow.ScaleCount = ScaleCount
        self.setPixmap(temp.scaled(int(temp.width() * ScaleCount), int(temp.height() * ScaleCount))) #放置图片
        self.ScaledWidthTemp,self.ScaledheightTemp = int(temp.width() * ScaleCount),int(temp.height() * ScaleCount)
        self.resize(self.ScaledWidthTemp, self.ScaledheightTemp) #设置大小以保持和图片一样大
        dp = cPos - self.getCenterPos()

        self.move(self.pos() + (1 * dp))


        return self.ScaledWidthTemp
    #缓入动效
    def huan_ru(self,need_time,HuanRuStartTime,HuanRuTimer, sound:str = None):
        dt = time.time() - HuanRuStartTime
        if dt <= need_time:
            t = math.sin(math.pi/(2*need_time)*dt)
            value = bezier_curves(BezierCurves.BezierCurves["sin"],t)
            self.opacity_value = value[1]
            self.update_label_opacity(self.opacity_value)
        else:
            self.HuanRuBegging = False
            HuanRuTimer.stop()  # 当透明度达到 1.0 时停止计时器
            if self.MainCircle or sound != None:
                self.playsound(sound)
    #缓出
    def huan_chu(self,need_time,HuanChuStartTime,HuanChuTimer,remove, sound:str = None):
        dt = time.time() - HuanChuStartTime
        if dt <= need_time:
            t = math.sin(math.pi/(2*need_time)*dt)
            value = bezier_curves(BezierCurves.BezierCurves["sin"],t)
            self.opacity_value = 1-value[1]
            self.update_label_opacity(self.opacity_value)
        else:
            if remove:
                self.deleteLater()
            self.HuanRuBegging = False
            HuanChuTimer.stop()  # 当透明度达到 1.0 时停止计时器
            if self.MainCircle or sound != None:
                self.playsound(sound)
    #缩小入场
    def suo_xiao_ru(self,need_time,SuoXiaoRuStartTime,setR,ScaleCount,Timer, sound:str = None):
        dt = time.time() - SuoXiaoRuStartTime
        self.dragging = False #关闭拖拽
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)#不可触碰
        if dt <= need_time:
            Pre = math.sin(math.pi/(2*need_time)*dt)
            value = bezier_curves(BezierCurves.BezierCurves["快入后缓"],Pre)
            self.update_label_opacity(value[1])
            w = self.changeSize(self.image,5*ScaleCount*(1-value[1]) + ScaleCount)
            if self.index == "Circle":
                setR(w//2) #设置半径 回调函数
        else:

            if self.index == "Center":
                self.resetPos()
            Timer.stop()
            self.setAttribute(Qt.WA_TransparentForMouseEvents, not self.Touchable)
            self.SuoXiaoRuBegging = False
            if sound is not None:
                self.playsound(sound)

    def suo_xiao_chu(self,need_time,SuoXiaoChuStartTime,setR,ScaleCount,Timer,remove, sound:str = None):
        dt = time.time() - SuoXiaoChuStartTime
        self.dragging = False #关闭拖拽
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)#不可触碰
        if dt <= need_time:
            Pre = math.sin(math.pi/(2*need_time)*dt)
            value = bezier_curves(BezierCurves.BezierCurves["慢入后快"],Pre)
            self.update_label_opacity(1-value[1])
            w = self.changeSize(self.image,ScaleCount*(1-value[1]))
            if self.image == AllResources["Circle.png"]:
                setR(w//2) #设置半径 回调函数
        else:
            if remove:
                self.deleteLater()
                self.SuoXiaoChuBegging = False
            self.setAttribute(Qt.WA_TransparentForMouseEvents, not self.Touchable)
            self.SuoXiaoRuBegging = False
            if self.index == "Center":
                self.resetPos()
            Timer.stop()
            self.setAttribute(Qt.WA_TransparentForMouseEvents, not self.Touchable)
            self.SuoXiaoRuBegging = False
            if sound is not None:
                self.playsound(sound)

    def change_size(self,need_time,ChangeSizeStartTime,ScaleCount,Timer,ds, sound:str = None):
        dt = time.time() - ChangeSizeStartTime
        if dt <= need_time:
            Pre = math.sin(math.pi/(2*need_time)*dt)
            value = bezier_curves(BezierCurves.BezierCurves["快入后缓"],Pre)
            w = self.changeSize(self.image,ScaleCount + ds*value[1],True)
            if self.image == AllResources["Circle.png"]:
                self.MainWindow.setRadius(w//2)
                self.MainWindow.updatePointPos()
        else:
            Timer.stop()
            if sound is not None:
                self.playsound(sound)

    #播放音效
    def playsound(self,sound = "Pre"):
        self.sound_thread = SoundThread(AllResources[f"{sound}.wav"])
        self.sound_thread.start()
    #缓出的计时器
    def huan_chu_start(self,needtime,remove = False, sound = None):
        if not self.HuanChuBegging:
            self.HuanChuBegging =True
            HuanChuTimer = QTimer(self)
            HuanChuStartTime = time.time()
            HuanChuTimer.timeout.connect(lambda : self.huan_chu(needtime,HuanChuStartTime,HuanChuTimer,remove,sound))
            HuanChuTimer.start(1)
        return self
    #缓入的计时器
    def huan_ru_start(self, needtime, sound = None):
        #动画不会重复触发
        if not self.HuanRuBegging:
            self.HuanRuBegging =True
            HuanRuTimer = QTimer(self)
            HuanRuStartTime = time.time()
            HuanRuTimer.timeout.connect(lambda : self.huan_ru(needtime,HuanRuStartTime,HuanRuTimer,sound))
            HuanRuTimer.start(1)
        return self
    #缩小入场的计时器
    def suo_xiao_ru_start(self,needtime = 1,setR = None, sound = None,ScaleCount = 1):
        # 动画不会重复触发
        if not self.SuoXiaoRuBegging:
            self.SuoXiaoRuBegging =True
            SuoXiaoRuTimer = QTimer(self)
            SuoXiaoRuStartTime = time.time()
            SuoXiaoRuTimer.timeout.connect(lambda :self.suo_xiao_ru(needtime,SuoXiaoRuStartTime,setR,ScaleCount,SuoXiaoRuTimer,sound))
            SuoXiaoRuTimer.start(1)

        return self

    def suo_xiao_chu_start(self,needtime = 1,remove = False,setR = None, sound = None,ScaleCount = 1):
        # 动画不会重复触发
        if not self.SuoXiaoChuBegging:
            self.SuoXiaoChuBegging =True
            SuoXiaoChuTimer = QTimer(self)
            SuoXiaoChuStartTime = time.time()
            SuoXiaoChuTimer.timeout.connect(lambda :self.suo_xiao_chu(needtime,SuoXiaoChuStartTime,setR,ScaleCount,SuoXiaoChuTimer,remove,sound))
            SuoXiaoChuTimer.start(1)

        return self

    def change_size_start(self,needtime = 1,ScaleCount = 1):
        """
        改变大小的计时器
        :param needtime:
        :param ScaleCount: 设定大小
        :return:
        """
        try:
            self.ChangeSizeTimer.stop()
        except:
            pass
        ds = Config.getValue("缩放大小") - ScaleCount

        self.ChangeSizeTimer = QTimer(self)
        ChangeSizeStartTime = time.time()
        self.ChangeSizeTimer.timeout.connect(lambda :self.change_size(needtime,ChangeSizeStartTime,ScaleCount,self.ChangeSizeTimer,ds))
        self.ChangeSizeTimer.start(1)

