import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from BMP import*


class Diffraction:
    def __init__(self, matrix, h, w, diff_grid_size, Lambda, dist, pixel_len, pixel_len_diff):
        # Размер исходной картинки в пикселях
        self.h = h  # Высота
        self.w = w  # Ширина
        # Размер дифракционной картины в пикселях
        self.color_grid_size = diff_grid_size
        # Матрица точек отверстия (исходная картинка)
        self.matrix = matrix
        # Матрица дифракционной картины
        self.color_matrix = np.zeros(
            (self.color_grid_size, self.color_grid_size))
        # Расстояние от отверстия до экрана (в микрометрах)
        self.L = dist
        # Физическая длина одного пикселя исходной картинки (в микрометрах)
        self.pixel_len = pixel_len
        # Физическая длина одного пикселя дифракционной картинки (в микрометрах)
        self.pixel_len_diff = pixel_len_diff
        # Длина волны в микрометрах
        self.Lambda = Lambda

    def center_of_mass(self):
        '''
        Находит расположение центра масс отверстия

        Returns
        -------
        x_c : float
            x-координата центра отверстия.
        y_c : float
            y-координата центра отверстия.

        '''
        x_c = 0
        y_c = 0
        num_of_cells = 0
        for i in range(self.w):
            for j in range(self.h):
                if self.matrix[i][j] == 0:
                    x_c += i
                    y_c += j
                    num_of_cells += 1
        x_c /= num_of_cells
        y_c /= num_of_cells
        return (x_c, y_c)

    def summing_tension(self, s_x, s_y, E_0, x_c, y_c):
        '''
        Находит интенсивность поля в рассматриваемой точке

        Parameters
        ----------
        s_x : float
            Проекция единичного вектора направления дифрагированного пучка
            на ось 0X.
        s_y : float
            Проекция единичного вектора направления дифрагированного пучка
            на ось 0Y..
        E_0 : float
            Амплитуда напряженности поля
        x_c : float
            x - координата геометрического центра отверстия
            (определяется как точка с нулевой начальной фазой).
        y_c : float
            y - координата геометрического центра отверстия
            (определяется как точка с нулевой начальной фазой).

        Returns
        -------
        E : float
            Интенсивность в точке наблюдения P (на самом деле функция
        возвращает модуль напряженности поля в точке, но это не влияет на
        результат, а сделано в целях оптимизации и получения хорошей
        дифракционной картинки (интенсивность к краям при возведении в
        квадрат быстро убывает)).

        '''
        E = 0
        for i in range(self.w):
            for j in range(self.h):
                if self.matrix[i][j] == 0:
                    x = (i - x_c) * self.pixel_len
                    y = (j - y_c) * self.pixel_len
                    E += E_0 * \
                        np.cos((x * s_x + y * s_y)
                               * 2 * np.pi/self.Lambda)
        return abs(E)

    def calc_intensity(self):
        '''
        Подсчет интенсивности результирующего излучения в наблюдаемой точке.
        Заполняет матрицу color_matrix значениями, соответствующими
        значениям интенсивности в соответствующей точке экрана.

        Returns
        -------
        None.

        '''
        # Подсчет положения центра масс отверстия
        x_c, y_c = self.center_of_mass()
        for i in tqdm(range(self.color_grid_size)):
            for j in range(self.color_grid_size):
                # Нахождение проекций вектора направления распространения
                # дифрагированного пучка
                s_x = (i - self.color_grid_size / 2) *\
                    self.pixel_len_diff
                s_y = (j - self.color_grid_size / 2) *\
                    self.pixel_len_diff

                # Модуль вектора направления распространения
                ro = np.sqrt(s_x**2 + s_y**2 + self.L**2)

                # Конечные значения проекций единичного вектора (нормировка вектора)
                s_x /= ro
                s_y /= ro

                # alpha и beta в формуле
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

                E_0 = a_s * b_s  # Напряженность волны от пикселя поверхности

                # Суммарная интенсивность в каждой точке экрана
                self.color_matrix[i][j] = \
                    self.summing_tension(s_x, s_y, E_0, x_c, y_c)


# Обработка файла
h, w, points = LoadBMP('circlehole3.bmp')

# DiffractionPicture = Diffraction(points, h, w, 150, 60, 0.555, 2 * 10**6, 10)
DiffractionPicture = Diffraction(
    points, h, w, 50, 0.555, 2 * 10**6, 100, 100)

# Подсчет интенсивности
DiffractionPicture.calc_intensity()

# График matplotlib
fig, axs = plt.subplots(1, 2, figsize=(35, 15), constrained_layout=True)
p1 = axs[0].imshow(DiffractionPicture.color_matrix,
                   cmap='hot')
fig.colorbar(p1, ax=axs[0])

p2 = axs[1].contourf(DiffractionPicture.color_matrix,
                     levels=500,
                     cmap='hot')
fig.colorbar(p2, ax=axs[1])

axs[0].set_xticks(np.linspace(0,
                              DiffractionPicture.color_grid_size, 11))
axs[0].set_xticklabels(np.linspace((-DiffractionPicture.color_grid_size/2) *
                                   DiffractionPicture.pixel_len_diff,
                                   DiffractionPicture.color_grid_size/2 *
                                   DiffractionPicture.pixel_len_diff,
                                   11), fontsize=15)
axs[0].set_yticks(np.linspace(0,
                              DiffractionPicture.color_grid_size,
                              11))

axs[0].set_yticklabels(np.linspace((-DiffractionPicture.color_grid_size/2) *
                                   DiffractionPicture.pixel_len_diff,
                                   DiffractionPicture.color_grid_size/2 *
                                   DiffractionPicture.pixel_len_diff,
                                   11), fontsize=15)
axs[1].set_xticks(np.linspace(0,
                              DiffractionPicture.color_grid_size, 11))
axs[1].set_xticklabels(np.linspace((-DiffractionPicture.color_grid_size/2) *
                                   DiffractionPicture.pixel_len_diff,
                                   DiffractionPicture.color_grid_size/2 *
                                   DiffractionPicture.pixel_len_diff,
                                   11), fontsize=15)

axs[1].set_yticks(np.linspace(0,
                              DiffractionPicture.color_grid_size,
                              11))
axs[1].set_yticklabels(np.linspace((-DiffractionPicture.color_grid_size/2) *
                                   DiffractionPicture.pixel_len_diff,
                                   DiffractionPicture.color_grid_size/2 *
                                   DiffractionPicture.pixel_len_diff,
                                   11), fontsize=15)
axs[0].set_title(
    'Дифракционная картинка, построенная с помощью функции imshow', fontsize=20)
axs[1].set_title(
    'Дифракционная картинка, построенная с помощью функции contourf', fontsize=20)

axs[0].set_xlabel('x, мкм', fontsize=17)
axs[0].set_ylabel('y, мкм', fontsize=17)
axs[1].set_xlabel('x, мкм', fontsize=17)
axs[1].set_ylabel('y, мкм', fontsize=17)

