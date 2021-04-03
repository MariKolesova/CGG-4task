import math
import numpy

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys


class ForthTask(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 600, 600)

        self.x1 = -3
        self.x2 = 3
        self.y1 = -3
        self.y2 = 3
        self.top = []
        self.bottom = []
        self.rotation_angle = 0
        self.n = 50

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Forth Task')
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)
        self.show()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        qp.setPen(QPen(Qt.blue, 3, Qt.SolidLine))

        self.draw_function(qp)

        qp.end()

    def draw_function(self, qp: QPainter):
        # Инициализируем состояние горизонтов.
        self.top = [self.geometry().height()] * (self.geometry().width() + 1)
        self.bottom = [0] * (self.geometry().width() + 1)


        # Число точек на одной линии обязано быть большим. Его обычно
        # берут равным удвоенному разрешению экрана по оси x.
        m = self.geometry().width() * 2
        mx = self.geometry().width()
        my = self.geometry().height()

        # Непосредственно перед рисованием проводим инициализацию
        # верхнего и нижнего горизонтов.
        minx, maxx, miny, maxy = self.find_max_and_min(m)

        # Перед рисованием необходимо просчитать по сетке диапазон
        # изменения координат в плоскости экрана.
        # Это необходимо для последующего масштабирования.
        for i in range(self.n + 1):
            x = self.x2 + i * (self.x1 - self.x2) / self.n
            for j in range(m):
                y = self.y2 + j * (self.y1 - self.y2) / m
                z = self.function(x, y)
                xp, yp = self.projection(x, y, z)
                xx = round((xp - minx) * mx / (maxx - minx))
                yy = round((yp - miny) * my / (maxy - miny))
                # Точки выше верхнего горизонта находятся на лицевой части поверхности,
                # а ниже - на обратной стороне
                if yy > self.bottom[xx]:
                    qp.setPen(QPen(Qt.red, 1, Qt.SolidLine))
                    qp.drawPoint(xx, yy)
                    self.bottom[xx] = yy
                if yy < self.top[xx]:
                    qp.setPen(QPen(Qt.blue, 1, Qt.SolidLine))
                    qp.drawPoint(xx, yy)
                    self.top[xx] = yy

        # Перед рисованием линий в перпендикулярном направлении необходимо заново
        # инициализировать состояние горизонтов.
        self.top = [self.geometry().height()] * (self.geometry().width() + 1)
        self.bottom = [0] * (self.geometry().width() + 1)

        minx, maxx, miny, maxy = self.find_max_and_min_across(m)

        for i in range(self.n + 1):
            y = self.y2 + i * (self.y1 - self.y2) / self.n
            for j in range(m):
                x = self.x2 + j * (self.x1 - self.x2) / m
                z = self.function(x, y)
                xp, yp = self.projection(x, y, z)
                xx = round((xp - minx) * mx / (maxx - minx))
                yy = round((yp - miny) * my / (maxy - miny))
                if yy > self.bottom[xx]:
                    qp.setPen(QPen(Qt.red, 1, Qt.SolidLine))
                    qp.drawPoint(xx, yy)
                    self.bottom[xx] = yy
                if yy < self.top[xx]:
                    qp.setPen(QPen(Qt.blue, 1, Qt.SolidLine))
                    qp.drawPoint(xx, yy)
                    self.top[xx] = yy

    def find_max_and_min(self, m):
        minx = 10000
        maxx = -minx
        miny = minx
        maxy = maxx
        for i in range(self.n + 1):
            x = self.x2 + i * (self.x1 - self.x2) / self.n
            for j in range(m):
                y = self.y2 + j * (self.y1 - self.y2) / m
                z = self.function(x, y)
                xp, yp = self.projection(x, y, z)
                if xp > maxx: maxx = xp
                if yp > maxy: maxy = yp
                if xp < minx: minx = xp
                if yp < miny: miny = yp
        return minx, maxx, miny, maxy

    def find_max_and_min_across(self, m):
        minx = 100000
        maxx = -minx
        miny = minx
        maxy = maxx
        for i in range(self.n + 1):
            y = self.y2 + i * (self.y1 - self.y2) / self.n
            for j in range(m):
                x = self.x2 + j * (self.x1 - self.x2) / m
                z = self.function(x, y)
                xp, yp = self.projection(x, y, z)
                if xp > maxx: maxx = xp
                if yp > maxy: maxy = yp
                if xp < minx: minx = xp
                if yp < miny: miny = yp
        return minx, maxx, miny, maxy

    def function(self, x, y):
        return x*y**3-y*x**3
        # return math.cos(x + y) + x**2/1 - y**2/1
        # return math.sin(x**2 + y**2)
        # return math.cos(x * y)

    def rotatate_vector(self, x, y, z):
        # Поворот вокруг оси z в плоскости (x, y) на угол γ
        # соответствует умножению на матрицы
        alpha = numpy.radians(self.rotation_angle)
        c, s = numpy.cos(alpha), numpy.sin(alpha)
        rotation_matrix = numpy.array(((c, s, 0),
                                       (-s, c, 0),
                                       (0, 0, 1),))
        return rotation_matrix.dot(numpy.array((x, y, z))).tolist()

    def projection(self, x, y, z):
        return self.isometric_projection(x, y, z)
        # return self.dimetric_projection(*self.rotatate_vector(x, y, z))

    def isometric_projection(self, x, y, z):
        # В изометрии все углы между осями равны 120 градусов.
        # Расстояния по каждой из осей откладываются одинаковые.
        # xx = (y - x) * sqrt(3)/2
        # yy = (x + y) / 2 - z
        return (y - x) * math.sqrt(3.0) / 2, (x + y) / 2 - z

    def dimetric_projection(self, x, y, z):
        # В диметрии ось х расположена относительно двух других
        # осей под углом 135 градусов.
        # При этом вдоль нее расстояния откладываются вдвое меньше.
        # xx = -x/(2*sqrt(2)) + y
        # yy = x/(2*sqrt(2)) - z
        return -x / (2 * math.sqrt(2)) + y, x / (2 * math.sqrt(2)) - z


def my_exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


if __name__ == '__main__':
    sys.excepthook = my_exception_hook
    app = QApplication(sys.argv)
    ex = ForthTask()
    sys.exit(app.exec_())