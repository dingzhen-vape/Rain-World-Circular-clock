import math
import time
import numpy as np
import matplotlib.pyplot as plt

from BezierCurves import BezierCurves

# 模拟 BezierCurves 字典（示例）
st = time.time()

def bezier_curves(points, t):
    return ((1 - t) ** 3 * points[0] +
           3 * (1 - t) ** 2 * t * points[1] +
           3 * (1 - t) * t ** 2 * points[2] +
           t ** 3 * points[3])

# 初始化绘图
fig, ax = plt.subplots()
ax.plot(*BezierCurves["弹一下"].T, 'ro--', label="Control Points")
line, = ax.plot([], [], 'b-', label="Bezier Curve")
ax.legend()

# 计算并显示贝塞尔曲线点
st = time.time()
nt = 1  # 动画时间1秒

points = []

while True:
    dt = time.time() - st
    if dt <= nt:
        t = math.sin(math.pi/(2*nt)*dt)
        pos = bezier_curves(BezierCurves["弹一下"], t)
        points.append(pos)
        # print(pos)
        time.sleep(0.01)
    else:
        break

points = np.array(points)

# 更新贝塞尔曲线
line.set_data(points[:, 0], points[:, 1])

# 显示绘图
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.title('Simple Bezier Curve Display')
plt.show()
