import numpy as np


def error_incorrect_file():
    print('Файл BMP некорректный')
    return 0


def error_bigsize():
    print('Файл слишком большой')
    return 0


def LoadBMP(filename):
    '''
    == ОПИСАНИЕ ФУНКЦИИ ==
    Функция получает имя файла формата BMP: filename.
    Возвращает (w, h, pixels), где w - ширина, h - высота массива,
        pixels - целочисленный массив numpy, содержащий только 0 или 1.


    Файл BMP должен быть несжатым.
    Каждый пиксель должен принимать значение (0, 0, 0) или (255, 255, 255).
    (0, 0, 0) переводится в 0 в массив numpy, (255, 255, 255) - в 1.

    В случае, если размеры файла превышают HMAX и WMAX, вызывается функция
    error_bigsize(). Если она возвращает 0, то LoadBMP() завершает работу и
    возвращает (0, 0, 0), в противном случае инчего не происходит.

    В случае, если файл не соответствует указанным выше требованиям
    или он повреждён, вызывается функция error_incorrect_file()
    и функция LoadBMP возвращает (0, 0, 0).
    '''

    HMAX = 1000
    WMAX = 1000

    header = np.zeros(27, 'int')

    file = open(filename, "rb")

    # Читаем заголовок файла (из полезной информации там w и h)
    for i in range(27):
        a = int.from_bytes(file.read(1), 'little')
        b = int.from_bytes(file.read(1), 'little')
        header[i] = b * 256 + a

    # Проверка корректности файла(несжатый, RGB, 8 бит на цвет и мб что-то ещё)
    if (header[0] != 19778
            or header[5] != 54
            or header[7] != 40
            or header[13] != 1
            or header[14] != 24):
        file.close()
        error_incorrect_file()
        return (0, 0, 0)

    w = header[9]  # ширина
    h = header[11]  # высота
    d = w % 4  # количество пустых байт, дополняющих каждую строку в конце

    # Проверка размера файла
    if (w >= WMAX or h >= HMAX):
        if (error_bigsize() == 0):
            file.close()
            return (0, 0, 0)

    # Массив, где будет храниться картинка
    pixels = np.zeros((h, w), 'int')

    # Массив под 3 байта R, G, B
    pixel = [30] * 3

    for i in range(h):
        for j in range(w):
            for c in range(3):
                # Считываем один пиксель
                pixel[c] = int.from_bytes(file.read(1), 'little')

    # Записысаем подходящее значение в файл, проверяя соответствие формату
            if (pixel[0] == pixel[1] and pixel[1] == pixel[2]):
                if (pixel[0] == 0):
                    pixels[h - i - 1][j] = 0
                elif (pixel[0] == 255):
                    pixels[h - i - 1][j] = 1
                else:
                    file.close()
                    error_incorrect_file()
                    return (0, 0, 0)
            else:
                file.close()
                error_incorrect_file()
                return (0, 0, 0)

        # Пропускаем пустые байты
        if d != 0:
            for i in range(d):
                file.read(1)

    file.close()
    return(w, h, pixels)
    # Конец функции LoadBMP()
