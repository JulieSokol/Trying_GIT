import numpy as np
from osgeo import gdal, gdalconst
import os

work_folder = r'E:\IKI\Microwave_data\SSMIS\NSIDC-0032-v2\20130815'
os.chdir(work_folder)

fn_19V = r'EASE-F17-NL2013227.19V.bin'
fn_19H = r'EASE-F17-NL2013227.19H.bin'

fn_37V = r'EASE-F17-NL2013227.37V.bin'
fn_37H = r'EASE-F17-NL2013227.37H.bin'

fn_85V = r'EASE-F17-NL2013227.91V.bin'
fn_85H = r'EASE-F17-NL2013227.91H.bin'

def read_binary (file_name):
    dataset = gdal.Open(file_name)
    ds_array = dataset.GetRasterBand(1).ReadAsArray()
    return  ds_array

T19V = read_binary(fn_19V)
T19H = read_binary(fn_19H)
T37V = read_binary(fn_37V)
T37H = read_binary(fn_37H)
T85V = read_binary(fn_85V)
T85H = read_binary(fn_85H)


# Set pixel number:
row = 332
col = 373



print ('Расчет для пикселя: ', row, col)

# Calculate tg: tg(85-19 V), tg(85-37 H), tg(37-19 V)
tg85_19V = (T85V[row,col] - T19V[row,col]) / (85.5 - 19.35)
tg85_37H = (T85H[row,col] - T37H[row,col]) / (85.5 - 37)
tg37_19V = (T37V[row,col] - T19V[row,col]) / (37 - 19.35)
print('tg(85V-19V): ',tg85_19V, '\ntg85(H-37H): ', tg85_37H, '\ntg(37V-19V): ', tg37_19V)

# Set functions and find their minimums
d = {}
for I in np.arange(0, 10.1, 0.1):
    f_H85_H37 = -0.085*I + 0.908
    f_V85_V19 = -0.086*I + 0.55

    F1 = 0.5*(((f_H85_H37 - tg85_37H)**2) / (tg85_37H**2) + ((f_V85_V19 - tg85_19V)**2) / (tg85_19V**2))
    d.update({F1:I})
print ("Значения функции F1: ", d)

# Минимум целевой функции F1 определяет сплоченность ледяного покрова I1.
# I1 – сплоченность морского льда, без коррекции ошибок, связанных с возможным наличием снежно-водяной смеси на ледяном покрове.
F1_min = min(d.keys())
I1 = d[F1_min]
print('Минимум функции: ', F1_min)
print ('Сплоченность в пикселе (без учета снежниц): ', I1)

# Проверка на наличие снежниц
del_V37_V19 = -0.187*I1 + 1.1

if del_V37_V19 < tg37_19V:
    I2 = I1
    print('Снежниц нет, сплоченность осталась такой же:', I2)
elif del_V37_V19 >= tg37_19V:
    dd = {}
    for I in np.arange(0, 10.1, 0.1):
        fi_H85_H37 = -0.039 * I + 1.19
        fi_V85_V19 = -0.04 * I + 0.7

        F2 = 0.5 * (((fi_H85_H37 - tg85_37H) ** 2) / (tg85_37H ** 2) + ((fi_V85_V19 - tg85_19V) ** 2) / (tg85_19V ** 2))
        dd.update({F2: I})

    print("Значения новой функции (F2): ", dd)

    # Сплоченность ледяного покрова I2, соответствует реальной сплоченности льда в данном пикселе (с учетом снежно-водяной смеси на ледяном покрове).
    F_min = min(dd.keys())
    I2 = dd[F_min]
    print ('Сплоченность в пикселе (c учетом снежниц): ', I2)
# Разница I2 - I1 показывает удельную площадь поверхности, занятую снежницами на ледяном покрове
Puddles = I2 - I1
print('Площадь снежниц: ', Puddles)




