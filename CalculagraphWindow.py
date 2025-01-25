from functools import partial

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QWidget, QSlider, QLabel, QPushButton, QVBoxLayout, QLineEdit, QTabWidget, QGridLayout, \
    QScrollArea, QMessageBox

import Config
import main
from AllResources import AllResources

def Complete():
    # QMessageBox().information(None, "提示", "计算完成！", QMessageBox.Ok)
    print("Done")
class CalculagraphWindow(QWidget):
    # 设置窗口类，继承自QWidget
    def __init__(self, LabelList, MainWindow1):
        # 初始化设置窗口，传入标签列表和主窗口对象
        super().__init__()

        self.Ptimer = None
        self.MainWindow:main.MainWindow = MainWindow1
        self.LabelList = LabelList
        self.LabelList2 = {}
        self.setWindowTitle("设置")
        self.resize(300, 200)

        self.PerSecond = 0
        self.second1 = 0
        self.second2 = 0
        self.当前到达的序号 = 0
        self.hour = 0
        self.minute = 0
        self.second = 0
        self.IterationsNum = 0
        self.CurrentIterations = 0


        self.tabWidget = QTabWidget()
        self.tab = QWidget()

        self.tabWidget.addTab(self.tab, "倒计时")

        self.layout = QGridLayout(self.tab)
        self.layout.setSpacing(0)
        # 创建主布局并设置为当前窗口的布局
        self.MainLayout = QVBoxLayout()
        self.setLayout(self.MainLayout)

        # 将tabWidget添加到主布局中
        self.MainLayout.addWidget(self.tabWidget)

        # 初始化TextList字典并调用display和InitText方法
        self.TextList = {}
        self.display()


    def display(self):
        # 显示设置界面的各个控件
        self.CreateInputBox("时:",self.changeHour,0,1)
        self.CreateSlider("分:",self.changeMinute,0,60,0,0,3)
        self.CreateSlider("秒:",self.changeSecond,0,60,0,0,5)
        self.CreateButton("开始计时",self.tick_timer, 2, 1)
        self.CreateButton("重启计时器",self.MainWindow.RestartTtimer, 2, 3)

    def CreateText(self, value="" ,y=0,x=0):
        # 创建文本显示标签
        text = QLabel()
        text.setText(value)
        self.LabelList2[value] = text

        self.layout.addWidget(text, y, x)

    def CreateInputBox(self, name, func=lambda: None, y=0, x=0,NeedText = True):
        # 创建一个输入框并添加到布局中
        InputBox = QLineEdit()
        validator = QIntValidator()
        InputBox.setValidator(validator)
        InputBox.textChanged.connect(func)
        self.LabelList2[name] = InputBox
        text = QLabel(name, self)
        self.TextList[name] = [text,y, x]

        self.layout.addWidget(InputBox,y, x)
        if NeedText:
            self.layout.addWidget(text,y+1, x)
            InputBox.textChanged.connect(partial(self.updateText, name=name, text=text))

    def CreateSlider(self, name,func = lambda: None,default_value=0, max_value=10, min_value=0, y=0, x=0,NeedText=True):
        # 创建一个滑块并添加到布局中
        slider = QSlider(Qt.Horizontal, self)
        slider.setMinimum(min_value)
        slider.setMaximum(max_value)
        slider.setValue(default_value)
        slider.setTickInterval(10)
        slider.setTickPosition(QSlider.TicksBelow)

        text = QLabel(name, self)
        self.TextList[name] = [text, y, x]
        self.LabelList2[name] = slider

        self.layout.addWidget(slider,y, x)
        if NeedText:
            self.layout.addWidget(text,y+1, x)
        slider.valueChanged.connect(func)
        slider.valueChanged.connect(partial(self.updateText, name=name, text=text))

    def CreateButton(self, value, func=lambda: None, y=0, x=0):
        # 创建一个按钮并添加到布局中
        TempButton = QPushButton(value)
        self.LabelList2[value] = TempButton

        TempButton.clicked.connect(func)  # 连接到槽函数
        self.layout.addWidget(TempButton,y, x)
        TempButton.show()
        print(f"Button '{value}' created and added to layout")  # 调试输出

    def updateText(self, value, name, text):
        # 更新滑块对应的文本显示
        text.setText(f"{name}{value}\n")

    def changeHour(self, value):
        self.hour = value
    def changeMinute(self, value):
        self.minute = value
    def changeSecond(self, value):
        self.second = value

    def addSecond(self):
        """
        增加计时器秒数并检查是否需要更新点。
        """
        self.second1 += 0.001
        self.second2 += 0.001
        self.MainWindow.Debug.setWindowTitle(f"当前秒数：{self.second2}")



        self.checkSecond()

    def checkSecond (self):
        """
        检查计时器秒数
        """
        def an():
            self.MainWindow.PointNum = int(self.MainWindow.每一业力等级所需的时间 / self.MainWindow.单个点所代表的时间)
            self.MainWindow.putPoint(False)
            for i in range(self.MainWindow.PointNum):
                self.LabelList[i].deleteLater()  # 测试用，删除所有标签
                self.LabelList.pop(i)
                Temp = self.MainWindow.CreateLabel(i, AllResources["point.png"],
                                            ScaleCount=self.MainWindow.ScaleCount).setFather(
                    self.LabelList["Circle"])
                self.LabelList[i] = Temp
                # self.LabelList[i].update_label_opacity(0).huan_ru_start(1.5)
                self.LabelList[i].update_label_opacity(0).suo_xiao_ru_start(self.MainWindow.点动画入场时间,
                                                                            self.MainWindow.setRadius,
                                                                            ScaleCount=self.MainWindow.ScaleCount)
                self.MainWindow.point_appearing_timer(self.MainWindow.点动画入场时间)
            self.MainWindow.updatePointPos()

        if self.second1 >= self.MainWindow.单个点所代表的时间 / 2:
            self.second1 = 0
            self.changePointLevel()
        if self.second2 >= self.MainWindow.每一业力等级所需的时间: #如果到达了每循环的时间
            self.CurrentIterations += 1
            self.second1 = 0
            self.second2 = 0
            self.当前到达的序号 = 0
            self.MainWindow.Debug.test()
            an()
            if self.CurrentIterations >= self.IterationsNum: #结束
                self.setWindowTitle(f"当前循环次数：{self.CurrentIterations}/{self.IterationsNum}")
                self.Ptimer.stop()
                self.Ptimer = None
                self.LabelList2["分:"].setValue(0)
                self.LabelList2["秒:"].setValue(0)
                Complete()
            else:

                self.setWindowTitle(f"当前循环次数：{self.CurrentIterations}/{self.IterationsNum}")


    def changePointLevel(self):
        """
        减少点的层级，更新标签的显示状态。
        """
        def change(i):
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
        for i in range(self.MainWindow.PointNum): #遍历所有点，更新点的显示状态
            change(i)
        print(f"当前序号:{self.当前到达的序号}")
        self.当前到达的序号 += 1

    def tick_timer(self):
        """
        启动计时器，每0.001触发一次addSecond函数。
        """
        #计算

        if self.Ptimer is None:
            self.CurrentIterations = 0
            self.Ptimer = QTimer(self)
            self.MainWindow.restart(self.countIterations())
            if self.CurrentIterations == 0 and self.PerSecond != 0: #第一次循环
                self.second2 = self.MainWindow.每一业力等级所需的时间 - self.PerSecond
            if self.Ptimer is not None:
                self.Ptimer.timeout.connect(self.addSecond)
                self.Ptimer.start(1)



    def countIterations(self):
        """
        计算循环次数。
        """
        if self.hour == 0 and self.minute == 0 and self.second == 0: #啥几把也没有填
            self.Ptimer = None
        else:
            self.PerSecond = self.second
            # print(self.PerSecond)
            self.second = int(self.hour) * 3600 + self.minute * 60 + self.second
            self.IterationsNum = self.second // self.MainWindow.每一业力等级所需的时间

            if self.IterationsNum < 1: #若循环次数少于一次，则进行单循环计时
                TempPointNum = self.second // self.MainWindow.单个点所代表的时间
                return TempPointNum
            else:
                if self.PerSecond != 0:
                    return self.PerSecond // self.MainWindow.单个点所代表的时间
                else:
                    return None


    def showEvent(self, event):
        super().showEvent(event)
        # self.raise_()  # 确保窗口显示在最上层
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.show()  # 重新显示窗口以应用顶置标志

    def closeEvent(self, event):
        # 处理窗口关闭事件
        self.MainWindow.CalculagraphIsOpen = False
        event.ignore()
        self.hide()
