import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QSlider, QLabel, QPushButton
from PyQt5.QtCore import Qt


class BezierCurveCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig, self.ax = plt.subplots()
        super().__init__(self.fig)
        self.setParent(parent)

        self.control_points = np.array([[0, 0], [1, 2], [2, 2], [3, 0]])

        self.plot_bezier_curve()

    def plot_bezier_curve(self):
        self.ax.clear()
        self.ax.plot(*self.control_points.T, 'ro-')

        t = np.linspace(0, 1, 100)
        B_t = ((1 - t) ** 3 * self.control_points[0][:, None] +
               3 * (1 - t) ** 2 * t * self.control_points[1][:, None] +
               3 * (1 - t) * t ** 2 * self.control_points[2][:, None] +
               t ** 3 * self.control_points[3][:, None])
        self.ax.plot(B_t[0, :], B_t[1, :], label="Bezier Curve")
        self.ax.legend()
        self.draw()

    def update_control_point(self, index, coord, value):
        self.control_points[index][coord] = value
        self.plot_bezier_curve()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Adjustable Cubic Bezier Curve Control Points")

        self.canvas = BezierCurveCanvas(self)

        # 创建滑块和标签
        self.sliders = []
        for i in range(4):
            slider_x = QSlider(Qt.Horizontal)
            slider_x.setMinimum(0)
            slider_x.setMaximum(10)
            slider_x.setValue(self.canvas.control_points[i][0])
            slider_x.valueChanged.connect(lambda value, idx=i: self.update_x_value(idx, value))
            label_x = QLabel(f"P{i} x:")

            slider_y = QSlider(Qt.Horizontal)
            slider_y.setMinimum(0)
            slider_y.setMaximum(10)
            slider_y.setValue(self.canvas.control_points[i][1])
            slider_y.valueChanged.connect(lambda value, idx=i: self.update_y_value(idx, value))
            label_y = QLabel(f"P{i} y:")

            self.sliders.append((slider_x, slider_y, label_x, label_y))

        # 创建打印按钮
        print_button = QPushButton("打印控制点坐标")
        print_button.clicked.connect(self.print_control_points)

        # 布局
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)

        for slider_x, slider_y, label_x, label_y in self.sliders:
            hlayout = QHBoxLayout()
            hlayout.addWidget(label_x)
            hlayout.addWidget(slider_x)
            hlayout.addWidget(label_y)
            hlayout.addWidget(slider_y)
            layout.addLayout(hlayout)

        layout.addWidget(print_button)  # 添加按钮到布局

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def update_x_value(self, index, value):
        self.canvas.update_control_point(index, 0, value)

    def update_y_value(self, index, value):
        self.canvas.update_control_point(index, 1, value)

    def print_control_points(self):
        points = self.canvas.control_points
        for i, point in enumerate(points):
            print(f"[{point[0]}, {point[1]}]",end=",")


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
