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
    
def OpenProject():
    tk.messagebox.showinfo('Ой', 'А вот это я не сделал...')
    
def LoadBMPFile():
    # Запрос на открытие картинки
    filename = filedialog.askopenfilename()
    # Если юзер выбрал файл, то обрабатываем его
    if (filename != ''):
        w, h, image = LoadBMP(filename)
        
        if w > 0 and h > 0: # Файл открылся успешно        
            ObstacleLoaded(w, h, image, 555, 200, 2, 60, 10)

def ObstacleLoaded(w, h, image, WV, Size, L, Scale, PixelL):
    #==РИСУЕМ ПРЕПЯТСТВИЕ==
    fig = Figure(figsize = (4, 3), dpi = 100)            
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
    
    # Масштаб диф картинки
    Scale_enter = tk.Entry(width = 6)
    Scale_enter.grid(row = 4, column = 1, sticky='W')
    Scale_enter.insert(0, str(Scale))
    
    Scale_label = tk.Label(text = 'Масштаб картинки')
    Scale_label.grid(row = 4, column = 0, sticky='W')
    
    # Размер пикселя
    PixelL_enter = tk.Entry(width = 6)
    PixelL_enter.grid(row = 5, column = 1, sticky='W')
    PixelL_enter.insert(0, str(PixelL))
    
    PixelL_label = tk.Label(text = 'Размер пикселя, мкм(?)')
    PixelL_label.grid(row = 5, column = 0, sticky='W')
    
    tk.Button(text = 'Вычислить дифракционную картину',
              command = lambda: ComputeDifraction(image, h, w, WV_enter, Size_enter, L_enter, Scale_enter, PixelL_enter)).grid(row = 6, column = 0)
    


def ComputeDifraction(points, h, w, WV_enter, Size_enter, L_enter, Scale_enter, PixelL_enter):   
    Wavelength = float(WV_enter.get()) / 1000 # Перевели в мкм
    Size = int(Size_enter.get())
    L = float(L_enter.get()) * 10**6 # Перевели в мкм
    Scale = int(Scale_enter.get())
    PixelLen = int(PixelL_enter.get())
    
    progress_label = tk.Label(text = 'Прогресс выполнения:')   
    progress_label.grid(row = 1, column = 2) 
    progress_bar = ttk.Progressbar(window, orient = "horizontal", mode = "determinate",
                                   maximum = 100, value = 0, length = 200)
    progress_bar.grid(row = 2, column = 2)
    
    
    DiffractionPicture = Diffraction(points, h, w, Size, Scale, Wavelength, L, PixelLen, progress_bar, window)
    DiffractionPicture.calc_intensity()
    
    # Рисуем картинку
    fig = Figure(figsize = (4, 3), dpi = 100)            
    plot = fig.add_subplot(111)
    
    plot.imshow(DiffractionPicture.color_matrix, cmap = 'hot')
    plot.grid(False)
    plot.set_xticks([])
    plot.set_yticks([])
    fig.suptitle('Дифракционная картина')
  
    # Это будет нарисовано в окне
    canvas = FigureCanvasTkAgg(fig, master = window)  
    canvas.draw()
  
    # Рисуем
    canvas.get_tk_widget().grid(row = 0, column = 2)
    
    progress_bar.grid_forget()
    tk.Label(text='Завершено').grid(row = 2, column = 2)
    

#Создаём окно
window = tk.Tk()
window.title("Моделирование дифракции v0.1")
window.geometry('800x600')

#== МЕНЮ ==
menu = tk.Menu(window)

#Файл
Menu_File = tk.Menu(menu, tearoff = 0)

Menu_File.add_command(label = 'Новый проект', command = NewProject)
Menu_File.add_command(label = 'Создать проект из файла BMP', command = LoadBMPFile)
Menu_File.add_separator()
Menu_File.add_command(label = 'Загрузить проект', command = OpenProject)


menu.add_cascade(label = 'Файл', menu = Menu_File)  
window.config(menu = menu)

w, h, img = Example1()
ObstacleLoaded(w, h, img, 555, 200, 2, 60, 15)

#== МЕНЮ закончилось ==

window.mainloop()
