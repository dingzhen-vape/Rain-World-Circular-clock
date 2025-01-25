from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QSlider, QLabel, QPushButton, QVBoxLayout, QLineEdit, QTabWidget, QGridLayout, \
    QScrollArea

import Config
import main


class SettingWindow(QWidget):
    # 设置窗口类，继承自QWidget
    def __init__(self, LabelList, MainWindow1):
        # 初始化设置窗口，传入标签列表和主窗口对象
        super().__init__()
        self.MainWindow : main.MainWindow = MainWindow1
        self.LabelList : dict = LabelList
        self.setWindowTitle("设置")
        self.resize(300, 200)

        self.tabWidget = QTabWidget()

        self.tab = QWidget()

        self.tabWidget.addTab(self.tab, "动画参数设置")

        # 为tab1和tab2设置布局
        self.layout = QVBoxLayout(self.tab)

        # 创建主布局并设置为当前窗口的布局
        self.MainLayout = QVBoxLayout()
        self.setLayout(self.MainLayout)

        # 将tabWidget添加到主布局中
        self.MainLayout.addWidget(self.tabWidget)

        # 初始化TextList字典并调用display和InitText方法
        self.TextList = {}
        self.display()
        self.InitText()


    def display(self):
        # 显示设置界面的各个控件
        # self.CreateSlider("每一业力等级所需的时间",default_value=Config.getValue("每一业力等级所需的时间"), max_value=120, min_value=30)
        self.CreateSlider("缩放大小",default_value=Config.getValue("缩放大小"))
        self.CreateInputBox("tick响应所需时间")
        self.CreateInputBox("主环入场时间")
        self.CreateInputBox("点动画入场时间")
        self.CreateInputBox("点动画出场时间")
        self.CreateInputBox("业力消失时间")
        self.CreateInputBox("业力进入时间")
        self.CreateInputBox("单个点所代表的时间")
        self.CreateButton("应用设置", self.RestartTtimer)

    def InitText(self):
        # 初始化文本显示
        for key, value in self.TextList.items():
            value.setText(f"{key}⬆:{Config.getValue(key)}\n"
                          f"---------------------------------------------")

    def CreateInputBox(self, name, func=lambda: None):
        # 创建一个输入框并添加到布局中
        InputBox = QLineEdit()
        InputBox.setText(str(Config.getValue(name)))
        InputBox.textChanged.connect(func)

        text = QLabel("", self)
        self.TextList[name] = text

        self.layout.addWidget(InputBox)
        self.layout.addWidget(text)

        InputBox.textChanged.connect(partial(self.updateText, name=name, text=text))

        InputBox.textChanged.connect(partial(Config.changeValue, key=name))

    def CreateSlider(self, name, max_value=10, min_value=0,default_value=10):
        # 创建一个滑块并添加到布局中
        slider = QSlider(Qt.Horizontal, self)
        slider.setMinimum(min_value)
        slider.setMaximum(max_value)
        slider.setValue(default_value)
        slider.setTickInterval(10)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.valueChanged.connect(partial(Config.changeValue, key=name))
        slider.valueChanged.connect(partial(self.RestartTtimer))

        text = QLabel("", self)
        self.TextList[name] = text

        self.layout.addWidget(slider)
        self.layout.addWidget(text)
        slider.valueChanged.connect(partial(self.updateText, name=name, text=text))

    def CreateButton(self, value, func=lambda: None):
        # 创建一个按钮并添加到布局中
        TempButton = QPushButton(value)
        TempButton.clicked.connect(func)  # 连接到槽函数
        self.layout.addWidget(TempButton)
        TempButton.show()
        print(f"Button '{value}' created and added to layout")  # 调试输出

    def RestartTtimer(self):
        for key,value in self.LabelList.items():
            value.change_size_start(1,self.MainWindow.ScaleCount)
        # 重启计时器
        try:
            self.MainWindow.calculagraph.Ptimer.stop()
            self.MainWindow.calculagraph.second = 0
        except:
            pass
        self.MainWindow.restart()
        self.MainWindow.timer.stop()
        self.MainWindow.readConfig()
        self.MainWindow.Ttimer()

    def updateText(self, value, name, text):
        # 更新滑块对应的文本显示
        text.setText(f"{name}⬆:{value}\n"
                     f"---------------------------------------------")

    def showEvent(self, event):
        super().showEvent(event)
        self.raise_()  # 确保窗口显示在最上层
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.show()  # 重新显示窗口以应用顶置标志

    def closeEvent(self, event):
        # 处理窗口关闭事件
        self.MainWindow.SettingIsOpen = False
        event.ignore()
        self.hide()
