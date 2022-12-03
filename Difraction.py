import numpy as np
import matplotlib.pyplot as plt
import tqdm

pixel_size = 600  # Разрешение входной картинки
grid_step = 15  # Размер пикселя преобразованной входной картинки
grid_size = int(pixel_size /
                grid_step)  # Разрешение преобразованной входной картинки
color_grid_size = 600  # Разрешение выходной картинки
color_grid_step = int(pixel_size /
                      color_grid_size)  # Размер пикселя выходной картинки


class Difraction:
    def _init_(self):
        # Матрица точек отверстия
        self.matrix = np.zeros((grid_size, grid_size))
        # Матрица дифракционной картинки
        self.color_matrix = np.zeros((color_grid_size, color_grid_size))
        # Расстояние от отверстия до экрана (в микрометрах)
        self.L = 2 * 10 ** 5
        # Физическая длина одного пикселя дифракционной картины
        self.pixel_len = 10
        # Длина волны
        self.Lambda = 500 * 10 ** (-2)

    def center_of_mass(self):
        '''
        Находит центр масс отверстия

        Returns
        -------
        x_rel : float
            x-координата центра масс отверстия.
        y_rel : float
            y-координата центра масс отверстия.

        '''
        x_rel = 0
        y_rel = 0
        num_of_cells = 0
        for i in range(Difraction.grid_size):
            for j in range(Difraction.grid_size):
                if self.matrix[i][j] > 0:
                    x_rel += i * Difraction.grid_step
                    y_rel += j * Difraction.grid_step
                    num_of_cells += 1
        x_rel /= num_of_cells
        y_rel /= num_of_cells
        return (x_rel, y_rel)

    def field_strength(self, s_x, s_y, x_rel, y_rel):
        '''
        Считает суммарную напряженность поля в точке наблюдения

        Parameters
        ----------
        s_x : float
            Проекция единичного вектора направления дифрагированного луча на
            ось 0X.
        s_y : float
            Проекция единичного вектора направления дифрагированного луча на
            ось 0Y.
        x_rel : float
            x-координата центра отверстия
            (берем в этой точке фазу равной нулю).
        y_rel : float
            y-координата центра отверстия
            (берем в этой точке фазу равной нулю)..

        Returns
        -------
        None.

        '''
        sum_strength = 0
        for i in range(grid_size):
            for j in range(grid_size):
                if self.matrix[i][j] != 0:
                    sum_strength += (grid_size * self.pixel_len) ** 2 *\
                        np.cos(2*np.pi*self.pixel_len/self.Lambda *
                               (s_x*(i * grid_size - x_rel) +
                                s_y*(j * grid_size - y_rel)))

    def intensivity(self):
        '''
        Считает интенсивность волны во всех точках экрана

        Returns
        -------
        None.

        '''
        x_rel, y_rel = self.center_of_mass()
        for i in tqdm(range(color_grid_size)):
            for j in range(color_grid_size):
                s_x = i/(np.sqrt((i) ** 2 + j ** 2 +
                                 (self.L/self.pixel_len) ** 2))
                s_y = j/(np.sqrt((i-pixel_size/2) ** 2 + (j-pixel_size) ** 2 +
                                 (self.L/self.pixel_len) ** 2))
                self.color_matrix[color_grid_size - j - 1][i] =\
                    self.field_strength(s_x, s_y, x_rel, y_rel) ** 2

    def norm(self):
        '''
        Нормирует матрицу с дифракционной картинкой

        Returns
        -------
        None.

        '''
        maximum = -99999
        for i in range(color_grid_size):
            for j in range(color_grid_size):
                if self.color_matrix[i][j] > maximum:
                    maximum = self.color_matrix[i][j]
        self.color_matrix = self.color_matrix/maximum


# *обработка файла*
'''Your code might be here'''

# Подсчет интенсивности
DifractionPicture = Difraction()
DifractionPicture.intensivity()
DifractionPicture.norm()

# График matplotlib
fig, ax = plt.subplots(figsize=(10, 10))
ax.imshow(DifractionPicture.color_matrix, 'hot')
