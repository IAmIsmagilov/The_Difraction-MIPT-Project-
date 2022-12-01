'''
Небольшие пояснения для господинов разработчиков сей программы :
        tkinter --- графический модуль Python
            tkinter.Canvas() --- создание пустого холста (или окна, на котором
            все происходит, как я понял)
            tkinter.grid() --- задает сетку на холсте (по сути некоторая
            координатная система, мы можем расставлять обЪекты, обращаясь
            к координатам сетки)
            tkinter.bind() --- назначение команд для кнопок на клавиатуре(мыши)
            'B1-Motion' --- движение мышки с зажатой ЛКМ
            'Button-Release' --- опускание кнопки мыши
        tqdm --- отображение окна загрузки в консоли справа(то есть, насколько
        процентов выполнена программа построения дифракционной картинки)---
        можно будет убрать потом
'''

import tkinter
import numpy as np
import sys
from tqdm import tqdm
import matplotlib.pyplot as plt


class Application(tkinter.Frame):

    pixel_size = 600
    grid_step = 15
    grid_size = int(pixel_size / grid_step)
    color_grid_size = 600
    color_grid_step = int(pixel_size / color_grid_size)

    def __init__(self, master, color):
        tkinter.Frame.__init__(self, master)
        self.color = color
        self.prev_x = -1
        self.prev_y = -1
        self.grid()
        self.flag = 0
        self.create_widgets()
        self.draw_finished = 0

        # Точки из отверстия
        self.points = []

        # Список, состоящий из точек отверстия
        self.matrix = [[0 for x in range(Application.grid_size)]
                       for y in range(Application.grid_size)]

        # Цвета точек отверстия
        self.color_matrix = np.zeros((Application.color_grid_size,
                                      Application.color_grid_size))

        # Физические параметры системы, указаны в МИКРОМЕТРАХ

        # Дистанция между отверстием и линзой
        self.L = 2 * 10 ** 5

        # Длина пикселя
        self.pixel_len = 10

        # Длина волны
        self.Lambda = 500 * 10 ** (-2)

    def create_widgets(self):
        '''
        Отрисовка отверстия от руки

        Returns
        -------
        None.

        '''
        # Создание холста
        self.canvas = tkinter.Canvas(self, width=Application.pixel_size,
                                     height=Application.pixel_size)
        # Сетка на холсте
        self.canvas.grid()
        # Рисование отверстия от руки
        self.canvas.bind('<B1-Motion>', self.draw)  # Рисование
        self.canvas.bind('<ButtonRelease-1>',
                         self.change_flag)  # Опускание кнопки мыши

    def summing_tension(self, s_x, s_y, default_e, x_rel, y_rel):
        '''
        Находит суммарную напряженность поля в рассматриваемой точке

        Parameters
        ----------
        s_x : float
            Проекция единичного вектора направления дифрагированного пучка
            на ось 0X.
        s_y : float
            Проекция единичного вектора направления дифрагированного пучка
            на ось 0Y..
        default_e : float
            Коэффициент в интеграле???????????????????????????????????????
        x_rel : float
            x - координата геометрического центра отверстия
            (определяется как точка с нулевой начальной фазой).
        y_rel : float
            y - координата геометрического центра отверстия
            (определяется как точка с нулевой начальной фазой).

        Returns
        -------
        e : float
            Модуль вектора напряженности в точке наблюдения P.

        '''
        e = 0
        for i in range(Application.grid_size):
            for j in range(Application.grid_size):
                if self.matrix[i][j] != 0:
                    x_c = (i * Application.grid_step - x_rel) * self.pixel_len
                    y_c = (j * Application.grid_step - y_rel) * self.pixel_len
                    e += default_e * \
                        np.cos((x_c * s_x + y_c * s_y)
                               * 2 * np.pi/self.Lambda)
        return abs(e)

    # Calculating whole diffraction pattern

    def calc_intensity(self):
        '''
        Подсчет интенсивности результирующего излучения в наблюдаемой точке

        Returns
        -------
        None.

        '''
        x_rel, y_rel = self.center_of_mass()
        for i in tqdm(range(Application.color_grid_size)):  # tqdm ведетподсчет
            for j in range(Application.color_grid_size):

                # Нахождение проекций единичного вектора(не совсем
                # разобрался как)
                s_x = (Application.color_grid_step * i -
                       Application.pixel_size / 2) * self.pixel_len
                s_y = (Application.color_grid_step * j -
                       Application.pixel_size / 2) * self.pixel_len

                # Поправка на наличие линзы????
                ro = np.sqrt(s_x**2 + s_y**2 + self.L**2)

                # Конечные значения проекций единичного вектора
                s_x /= ro
                s_y /= ro

                # alpha и beta в формулах
                alpha = np.pi * self.pixel_len * s_x / self.Lambda
                beta = np.pi * self.pixel_len * s_y / self.Lambda
                if alpha == 0:
                    a_s = 1
                else:
                    a_s = np.sin(alpha) / alpha

                if beta == 0:
                    b_s = 1
                else:
                    b_s = np.sin(beta) / beta

                d = self.pixel_len*Application.grid_step
                default_e = d**2 * a_s * b_s

                # Summing fields in direction (s_x, s_y, s_z)
                self.color_matrix[Application.color_grid_size - j - 1][i] = \
                    self.summing_tension(s_x, s_y, default_e, x_rel, y_rel)

    def change_flag(self, event):
        self.flag = (self.flag + 1) % 2

    def stop_drawing(self):
        self.canvas.bind("<B1-Motion>", lambda e: None)
        self.color_int()
        self.calc_intensity()

    # Filling with 1 all points between (x_p, y_p) and (x, y)

    def color_cells(self, x_p, y_p, x, y):
        if x - x_p != 0:
            k = (y - y_p) / (x - x_p)
            if abs(k) <= 1:
                x_start = min(x_p, x)
                x_end = max(x_p, x)
                it_x = np.sqrt(1 / (np.sqrt(1 + k**2))) * self.grid_step
                while x_start < x_end:
                    self.matrix[int(((x_start - x) * k + y) / self.grid_step)
                                ][int(x_start / self.grid_step)] = 1
                    x_start += it_x

        if y - y_p != 0:
            k = (x - x_p) / (y - y_p)
            y_start = min(y_p, y)
            y_end = max(y_p, y)
            it_y = np.sqrt(1 / (np.sqrt(1 + k**2))) * self.grid_step
            while y_start < y_end:
                self.matrix[int(y_start / self.grid_step)
                            ][int(((y_start - y) * k + x) / self.grid_step)] = 1
                y_start += it_y

    # Mouse capturing

    def draw(self, event):
        if self.prev_x != -1 and self.flag == 0:
            self.points.append([event.x, event.y])
            self.canvas.create_line(
                self.prev_x, self.prev_y, event.x, event.y, fill="#000", width=2)
            self.color_cells(self.prev_x, self.prev_y, event.x, event.y)
        self.prev_x = event.x
        self.prev_y = event.y

        if self.flag != 0:
            self.flag = 0

    # Filling interior with 1(yea its crazy, i know)

    def color_int(self):
        for i in range(Application.grid_size):
            state = 0
            first_zero = -1
            first_one = -1
            j = 0
            first_one_locked = 0
            while j < Application.grid_size:
                if self.matrix[i][j] == 1:
                    if self.matrix[i][j + 1] == 1:
                        if first_one_locked == 0:
                            first_one = j
                            first_one_locked = 1
                        if self.matrix[i][j + 2] == 0:
                            if (((self.matrix[i+1][first_one] == 1) or (self.matrix[i + 1][first_one - 1] == 1)) and
                                ((self.matrix[i - 1][j + 1] == 1) or (self.matrix[i - 1][j + 2] == 1))) or (((self.matrix[i - 1][first_one] == 1) or (self.matrix[i - 1][first_one - 1] == 1)) and
                                                                                                            ((self.matrix[i + 1][j + 1] == 1) or (self.matrix[i + 1][j + 2] == 1))):
                                if state == 0:
                                    state = 1
                                    first_zero = j + 2
                                    j = j + 2
                                    first_one = -1
                                    first_one_locked = 0
                                    continue
                                for k in range(first_zero, first_one):
                                    self.matrix[i][k] = 2
                                first_zero = -1
                                state = 0
                                j = j + 2
                                first_one = -1
                                first_one_locked = 0
                                continue
                            if state == 0:
                                j = j + 2
                                first_one = -1
                                first_one_locked = 0
                                continue
                            for k in range(first_zero, first_one):
                                self.matrix[i][k] = 2
                            first_zero = j + 2
                            j = j + 2
                            first_one = -1
                            first_one_locked = 0
                            continue
                        j += 1
                        continue
                    if (self.matrix[i][j + 1] == 0) and (state == 0):
                        first_zero = j + 1
                        state = 1

                    elif (first_zero >= 0) and (state == 1):
                        for k in range(first_zero, j):
                            self.matrix[i][k] = 2
                        first_zero = -1
                        state = 0
                j += 1

    # Calculating geometric center of hole(it will be the point with 0 initial phase of field)

    def center_of_mass(self):
        x_rel = 0
        y_rel = 0
        num_of_cells = 0
        for i in range(Application.grid_size):
            for j in range(Application.grid_size):
                if self.matrix[i][j] > 0:
                    x_rel += i * Application.grid_step
                    y_rel += j * Application.grid_step
                    num_of_cells += 1
        x_rel /= num_of_cells
        y_rel /= num_of_cells
        return (x_rel, y_rel)


if __name__ == "__main__":
    ROOT = tkinter.Tk()
    ROOT.title("Дифракционная картина от различных щелей")

    colors = ["red", "green", "blue", "yellow", "magneta", "cyan", "fancy"]
    if (len(sys.argv) > 1):
        if (sys.argv[1] in colors):
            color = sys.argv[1]
        else:
            raise NameError(
                "Invalid color! Only 'red', 'green', 'blue', 'yellow', 'magneta', 'cyan' and 'fancy' are available.")
    else:
        color = "yellow"

    APP = Application(ROOT, color)

    BUTTON1 = tkinter.Button(
        ROOT, text="Начать отрисовку дифракции", command=APP.stop_drawing)
    BUTTON1.configure(width=30, activebackground="#33B5E5")
    BUTTON1_WINDOW = APP.canvas.create_window(300, 20, window=BUTTON1)

    ROOT.mainloop()

    fig, ax = plt.subplots(figsize=(7, 4), layout='constrained')
    ax.imshow(APP.color_matrix)
