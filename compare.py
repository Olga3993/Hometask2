import sys
from xml.dom.minidom import parse
import time
import matrixops


dom = parse(sys.argv[1])
kol = 0
flag = 0
dom = dom.childNodes[0]
for child in dom.childNodes:
    if child.nodeType == dom.ELEMENT_NODE:
        if child.nodeName == "net":
            kol += 1
        else:
            if flag == 0:
                matr = []   # исходная таблица сопротивлений между узлами
                for j in range(kol):
                    matr1 = []
                    for i in range(kol):
                        if i != j:
                            # инициализация таблицы значениями inf
                            matr1.append(float("+inf"))   
                        else:
                            matr1.append(0)   # 0 на главной диагонале
                            matr.append(matr1)
                            flag=1
                            
            atts = child.attributes
            if child.nodeName == "diode":
                res1 = float("+inf")
                res2 = float("+inf")
                for k, v in atts.items():
                    if k == "net_from":
                        i = int(v) - 1
                    elif k == "net_to":
                        j = int(v) - 1
                    elif k == "resistance":
                        res1 = float(v)
                    else:
                        res2 = float(v)
                # обработка деления на 0        
                if  1 / res1 + 1 / matr[i][j] == 0 or 1 / res2 + 1 / matr[i][j] == 0:
                    matr[i][j] = float("+inf")
                    matr[j][i] = float("+inf")
                else:
                    matr[i][j] = 1 / (1 / res1 + 1 / matr[i][j])
                    matr[j][i] = 1 / (1 / res2 + 1 / matr[j][i])
            else:   # "resistor" и "capactor"
                res = float("+inf")
                for k, v in atts.items():
                    if k == "net_from":
                        i = int(v) - 1
                    elif k == "net_to":
                        j = int(v) - 1
                    else:
                        res = float(v)
                if  1 / res + 1 / matr[i][j] == 0:
                    matr[i][j] = float("+inf")
                    matr[j][i] = float("+inf")
                else:
                    matr[i][j] = 1 / (1 / res + 1 / matr[i][j])
                    matr[j][i] = matr[i][j]
matr_cxx = []
start_cxx = time.time()
matr_cxx = matrixops.f_w_algorithm(matr)
finish_cxx= time.time()
print(start_cxx)
print(finish_cxx)
start_py = time.time()                    
# рассчет сопртивлений по алгоритму Флойда-Уоршела
for k in range(len(matr)):
    for i in range(len(matr)):
        for j in range(len(matr)):
            if matr[i][j] == 0:
                a = float("+inf")
            else:
                a = 1 / matr[i][j]
            if   matr[i][k] == 0 and matr[k][j] == 0:
                b = float("+inf")
            else:
                b = 1 / (matr[i][k] + matr[k][j])
            if a + b == 0:
                matr[i][j] = float("+inf")
            else:
                matr[i][j] = 1 / (a + b)
finish_py = time.time()
                    
# запись таблицы в файл
with open(sys.argv[2],"w") as fd:
    for i in range(len(matr)):
        for j in range(len(matr)):
            if j != len(matr) - 1:
                fd.write(str(round(matr[i][j]- matr_cxx[i][j],6)) + ', ')
            else:
                fd.write(str(round(matr[i][j] - matr_cxx[i][j],6)) + "\n")
                
# запись таблицы в файл
with open(sys.argv[3],"w") as fd:
    for i in range(len(matr_cxx)):
        for j in range(len(matr_cxx)):
            if j != len(matr_cxx) - 1:
                fd.write(str(round(matr_cxx[i][j],6)) + ', ')
            else:
                fd.write(str(round(matr_cxx[i][j],6)) + "\n")
                
print((finish_py - start_py)/(finish_cxx - start_cxx)) # время работы программы



    
