import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox as mb
import tkinter.ttk as ttk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
                                               NavigationToolbar2Tk)

from BMP import *
from Diffraction import *
from Samples import *


global FLAG_CALCULATED
FLAG_CALCULATED = 0

global IMAGE2SAVE
global OBSTACLE2SAVE


def ProgramVersion():
    mb.showinfo("Версия", "Версия программы 2.1 - 06.12.2022.\nРазработчики: Амир Исмагилов, Михаил Мельников,\nСавва Куцубин.")
    

def ProgramQuestion():
    mb.showinfo("Справка", "Программа позволяет численно рассчитать дифракционную картину на произвольном отверстии." +
                " В качестве отверстия используется массив numpy, каждый элемент которого равен 0 (отверстие) или 1 (препятствие). " +
                "Он может быть задан двумя способами: 1) Предустановленный (Файл > Загрузить пример;\n" +
                "2) Загрузить BMP файл. BMP файл должен быть несжатым, RGB 8 бит/цвет и также он должен содержать "+
                "только цвета #000000 (полностью чёрный) и #FFFFFF (полностью белый). Белый переводится в 1 - препятствие," +
                "чёрный - в 0 (отсутствие препятствия).\n\n"+
                "Программа позволяет сохранять и открывать проекты, при этом проекту необходимо выделить отдельную директорию." +
                "Также можно сохранять полученные картинки в формате png.")


def SaveProject():
    global OBSTACLE2SAVE
    global IMAGE2SAVE
    global FLAG_CALCULATED
    
    if FLAG_CALCULATED == 0:
        mb.showerror("Ой", "Пока что вам нечего сохранять...")
        return 0
    
    directory = filedialog.askdirectory()    
    if directory == '':
        return 0
    
    
    np.save(directory + '/obstacle', OBSTACLE2SAVE)
    np.save(directory + '/image', IMAGE2SAVE.color_matrix)
    
    file = open(directory + '/parameters.pdp', "w")
    file.write(str(IMAGE2SAVE.h) + '\n')
    file.write(str(IMAGE2SAVE.w) + '\n')
    file.write(str(IMAGE2SAVE.color_grid_size) + '\n')
    file.write(str(IMAGE2SAVE.Lambda) + '\n')
    file.write(str(IMAGE2SAVE.L) + '\n')
    file.write(str(IMAGE2SAVE.pixel_len) + '\n')
    file.write(str(IMAGE2SAVE.pixel_len_diff) + '\n')   
    file.close()
    
def LoadProject():
    directory = filedialog.askdirectory()
    if directory == '':
        return 0
    
    
    obstacle = np.load(directory + '/obstacle.npy')
    image = np.load(directory + '/image.npy')
    
    file = open(directory + '/parameters.pdp', "r")
    h = int(file.readline())
    w = int(file.readline())
    Size = int(file.readline())
    Wavelength = float(file.readline()) * 1000
    L = float(file.readline()) / 10**6
    PixelLen = float(file.readline())
    PixLDiff = float(file.readline())
    file.close()
    
    progress_label = tk.Label(text = 'Прогресс выполнения:')   
    progress_label.grid(row = 1, column = 2) 
    progress_bar = ttk.Progressbar(window, orient = "horizontal", mode = "determinate",
                                   maximum = 100, value = 0, length = 200)
    progress_bar.grid(row = 2, column = 2)
    
    
    ObstacleLoaded(h, w, obstacle, Wavelength, Size, L, PixelLen, PixLDiff)
    Image = Diffraction(obstacle, h, w, Size, Wavelength, L, PixelLen, PixLDiff, progress_bar, window)
    Image.color_matrix = image
    
    
    fig = PlotDiffImg(Image)
    canvas = FigureCanvasTkAgg(fig, master = window)  
    canvas.draw()
    canvas.get_tk_widget().grid(row = 0, column = 2)
    
    progress_bar.grid_forget()
    tk.Label(text = 'Завершено').grid(row = 2, column = 2)
    
    global FLAG_CALCULATED
    FLAG_CALCULATED = 1
    global IMAGE2SAVE
    IMAGE2SAVE = Image

def SaveImage():
    global IMAGE2SAVE 
    global FLAG_CALCULATED
    
    if FLAG_CALCULATED == 0:
        mb.showerror('Ой', 'Пока что вам нечего сохранять...')
        return 0  
    
    fig = PlotDiffImg(IMAGE2SAVE)   
    # Запрос на открытие картинки
    filename = filedialog.asksaveasfilename()
    if (filename != ''):
        fig.savefig(filename)
        mb.showinfo("Ура!", "Файл успешно сохранён")

def NewProject():
    AskSampleWindow = tk.Toplevel(window)
    AskSampleWindow.geometry('250x250')
    AskSampleWindow.title('Выберите пример')
    
    tk.Label(AskSampleWindow, 
             text = 'Выберите пример для вычисления\n дифракционной картины').pack()
    
    var = tk.IntVar()
    var.set(0)
    ex1 = tk.Radiobutton(AskSampleWindow, text = "Круговое отверстие", variable = var, value = 0)
    ex2 = tk.Radiobutton(AskSampleWindow, text = "Шестиугольное отверстие", variable = var, value = 1)
    ex3 = tk.Radiobutton(AskSampleWindow, text = "Отверстие в виде звёздочки", variable = var, value = 2)    
    ex4 = tk.Radiobutton(AskSampleWindow, text = "Дифракционная решётка", variable = var, value = 3)    
    ex1.pack()
    ex2.pack()
    ex3.pack()
    ex4.pack()
    button = tk.Button(AskSampleWindow, text = "Открыть", command = lambda: Sample(var, AskSampleWindow))
    button.pack()
    
    '''w, h, image = Example3()
    ObstacleLoaded(w, h, image, 555, 200, 2, 60)'''
    
def Sample( number, askwindow ):
    askwindow.destroy()
    if (number.get() == 0):
        w, h, image = Example1()
    elif (number.get() == 1):
        w, h, image = Example2()
    elif (number.get() == 2):
        w, h, image = Example3()
    else:
        w, h, image = Example4()
    ObstacleLoaded(w, h, image, 555, 200, 2, 60, 15)
    
def LoadBMPFile():
    # Запрос на открытие картинки
    filename = filedialog.askopenfilename()
    # Если юзер выбрал файл, то обрабатываем его
    if (filename != ''):
        w, h, image = LoadBMP(filename)
        
        if w > 0 and h > 0: # Файл открылся успешно        
            ObstacleLoaded(w, h, image, 555, 200, 2, 60, 10)

def ObstacleLoaded(w, h, image, WV, Size, L, PixelDif, PixelL):
    #==РИСУЕМ ПРЕПЯТСТВИЕ==
    fig = Figure(figsize = (4, 4), dpi = 100)            
    plot = fig.add_subplot(111)
    
    # Рисуем картинку
    plot.imshow(image, cmap = 'gray')
    plot.grid(False)
    plot.set_xticks([])
    plot.set_yticks([])
    fig.suptitle('Препятствие')
  
    # Это будет нарисовано в окне
    canvas = FigureCanvasTkAgg(fig, master = window)  
    canvas.draw()
  
    # Рисуем
    canvas.get_tk_widget().grid(row = 0, column = 0, columnspan = 2)
    
    
    #== ПАРАМЕТРЫ ВЫЧИСЛЕНИЯ ==
    # Длина волны
    WV_enter = tk.Entry(width = 6)
    WV_enter.grid(row = 1, column = 1, sticky='W')
    WV_enter.insert(0, str(WV))
    
    WV_label = tk.Label(text = 'Длина волны, нм')
    WV_label.grid(row = 1, column = 0, sticky='W')
    
    # Разрешение диф картинки
    Size_enter = tk.Entry(width = 6)
    Size_enter.grid(row = 2, column = 1, sticky='W')
    Size_enter.insert(0, str(Size))
    
    Size_label = tk.Label(text = 'Разрешение дифракционной картинки, px')
    Size_label.grid(row = 2, column = 0, sticky='W')
    
    # Расстояние от препятствия до экрана
    L_enter = tk.Entry(width = 6)
    L_enter.grid(row = 3, column = 1, sticky='W')
    L_enter.insert(0, str(L))
    
    L_label = tk.Label(text = 'Расстояние от препятствия до экрана, м')
    L_label.grid(row = 3, column = 0, sticky='W')
    
    # Размер пикселя диф картинки
    PixL_Diff_enter = tk.Entry(width = 6)
    PixL_Diff_enter.grid(row = 4, column = 1, sticky='W')
    PixL_Diff_enter.insert(0, str(PixelDif))
    
    PixL_Diff_label = tk.Label(text = 'Размер пикселя дифракционной картинки, мкм')
    PixL_Diff_label.grid(row = 4, column = 0, sticky='W')
    
    # Размер пикселя препятствия
    PixelL_enter = tk.Entry(width = 6)
    PixelL_enter.grid(row = 5, column = 1, sticky='W')
    PixelL_enter.insert(0, str(PixelL))
    
    PixelL_label = tk.Label(text = 'Размер пикселя препятствия, мкм')
    PixelL_label.grid(row = 5, column = 0, sticky='W')
    
    tk.Button(text = 'Вычислить дифракционную картину',
              command = lambda: ComputeDifraction(image, h, w, WV_enter, Size_enter, L_enter, PixL_Diff_enter, PixelL_enter)).grid(row = 6, column = 0)
    


def ComputeDifraction(points, h, w, WV_enter, Size_enter, L_enter, PixL_Diff_enter, PixelL_enter):   
    Wavelength = float(WV_enter.get()) / 1000 # Перевели в мкм
    Size = int(Size_enter.get())
    L = float(L_enter.get()) * 10**6 # Перевели в мкм
    PixLDiff = float(PixL_Diff_enter.get())
    PixelLen = float(PixelL_enter.get())
    
    progress_label = tk.Label(text = 'Прогресс выполнения:')   
    progress_label.grid(row = 1, column = 2) 
    progress_bar = ttk.Progressbar(window, orient = "horizontal", mode = "determinate",
                                   maximum = 100, value = 0, length = 200)
    progress_bar.grid(row = 2, column = 2)
    
    DiffractionPicture = Diffraction(points, h, w, Size, Wavelength, L, PixelLen, PixLDiff, progress_bar, window)
    DiffractionPicture.calc_intensity()
    
    # Рисуем картинку
    '''fig = Figure(figsize = (4, 3), dpi = 100)            
    plot = fig.add_subplot(111)
    
    plot.imshow(DiffractionPicture.color_matrix, cmap = 'hot')
    plot.grid(False)
    plot.set_xticks([])
    plot.set_yticks([])
    fig.suptitle('Дифракционная картина')'''
    
    fig = PlotDiffImg(DiffractionPicture)
  
    # Это будет нарисовано в окне
    canvas = FigureCanvasTkAgg(fig, master = window)  
    canvas.draw()
  
    # Рисуем
    canvas.get_tk_widget().grid(row = 0, column = 2)
    
    progress_bar.grid_forget()
    tk.Label(text = 'Завершено').grid(row = 2, column = 2)
    
    #Глобальные переменные, чтобы их можно было сохранить
    global IMAGE2SAVE
    IMAGE2SAVE = DiffractionPicture
    global OBSTACLE2SAVE
    OBSTACLE2SAVE = points
    global FLAG_CALCULATED
    FLAG_CALCULATED = 1
    

#Создаём окно
window = tk.Tk()
window.title("Фраунхгофера дифракция на произвольном отверстии")
window.geometry('800x600')

#== МЕНЮ ==
menu = tk.Menu(window)

#Файл
Menu_File = tk.Menu(menu, tearoff = 0)

Menu_File.add_command(label = 'Открыть пример', command = NewProject)
Menu_File.add_command(label = 'Создать проект из файла BMP', command = LoadBMPFile)
Menu_File.add_separator()
Menu_File.add_command(label = 'Сохранить проект', command = SaveProject)
Menu_File.add_command(label = 'Открыть проект', command = LoadProject)
Menu_File.add_separator()
Menu_File.add_command(label = 'Сохранить картинку', command = SaveImage)

menu.add_cascade(label = 'Файл', menu = Menu_File)

#Справка
Menu_Question = tk.Menu(menu, tearoff = 0)

Menu_Question.add_command(label = 'Справка', command = ProgramQuestion)
Menu_Question.add_command(label = 'Версия программы', command = ProgramVersion)
menu.add_cascade(label = 'Справка', menu = Menu_Question)  

  
window.config(menu = menu)


w, h, img = Example1()
ObstacleLoaded(w, h, img, 555, 200, 2, 100, 100)

#== МЕНЮ закончилось ==

window.mainloop()
