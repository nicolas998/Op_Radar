#!/usr/bin/env python

import numpy as np 
import pickle 
import pandas as pnd
import os 
import datetime as dt



#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
print '###################################################### Actualiza caudales historicos observados ####################################'

#-------------------------------------------------------------------
#VARIABLES DEL CRON
#-------------------------------------------------------------------
rutaEst = '/home/nicolas/Operacional/Op_Radar/03_Simulaciones/03_Stream_Observed/Comparison_Stations.txt'
rutaFile = '/home/nicolas/Operacional/Op_Radar/03_Simulaciones/03_Stream_Observed/'
rutaTemp = '/home/nicolas/Operacional/Op_Radar/03_Simulaciones/03_Stream_Observed/Qobs_temp.qobs'
# replace: indica si se va a remplazar toda la serie historica consultada de caudales o no, por defecto se deja en que no 
replace = False
# DeltaAtras: Cantidad de pasos en minutos hacia atras para que se realice la consulta 
DeltaAtras = 60

#-------------------------------------------------------------------
#LEE PARAM DE LOS CAUDALES OBSERVADOS QUE DEBE CONSULTAR
#-------------------------------------------------------------------
#Lectura del archivo con la informacion de las estaciones con caudales.
f = open(rutaEst,'r')
L = f.readlines()
f.close()
#Obtiene en un diccionario las caracteristicas de las estaciones 
#Obtiene en un diccionario las caracteristicas de las estaciones 
DictCaudal = {}
for j in L[7:]:
    Data = j.split(',')
    if Data[0].startswith('#') == False:
        DictCaudal.update({Data[0]:{}})
        DictCaudal[Data[0]].update({'ID':int(Data[1])})
        DictCaudal[Data[0]].update({'Nodo':int(Data[2])})
        DictCaudal[Data[0]].update({'Coef':float(Data[3])})
        DictCaudal[Data[0]].update({'Expo':float(Data[4])})

#-------------------------------------------------------------------
#Fechas para la consulta 
#-------------------------------------------------------------------
# Obtiene el datetime 
fecha_1 =  dt.datetime.now() - dt.timedelta(minutes = DeltaAtras)
#Si no es cercano a 5 lo hace igual a un numero multiplo de cinco
if fecha_1.minute%5 <> 0:
    minute = int(np.floor(fecha_1.minute/10.0) * 10)
    fecha_1 = dt.datetime(fecha_1.year, fecha_1.month, fecha_1.day, fecha_1.hour, minute)
fecha_2 =  dt.datetime.now()# - dt.timedelta(minutes = 50)
if fecha_2.minute%5 <> 0:
    minute = int(np.floor(fecha_2.minute/10.0) * 10)
    fecha_2 = dt.datetime(fecha_2.year, fecha_2.month, fecha_2.day, fecha_2.hour, minute)
# Lo convierte en texto 
fecha1 = fecha_1.strftime('%Y-%m-%d')
fecha2 = fecha_2.strftime('%Y-%m-%d')
hora_1 = fecha_1.strftime('%H:%M')
hora_2 = fecha_2.strftime('%H:%M')

#-------------------------------------------------------------------
#Consulta y mira si debe actualizar
#-------------------------------------------------------------------
#Lista de caudales observados historicos acutales 
L = os.listdir(rutaFile)
L = [i for i in L if i.endswith('.qobs')]

#Itera sobre las estaciones que tienen caudales para consultarlas 
for k in DictCaudal.keys():
    #Para consultar una estacion
    idEst = str(DictCaudal[k]['ID'])
    c = str(DictCaudal[k]['Coef'])
    e = str(DictCaudal[k]['Expo'])
    #Nombre historico caudal 
    nombre = 'Qobs_'+k+'.qobs'
    # Mira si ya existen registros en la carpeta para esa estacion 
    Existe = False
    try:
        pos = L.index(nombre)
        Existe = True
        if replace:
            rutaFin = rutaFile + nombre
        else:
            rutaFin = rutaTemp
    except:
        rutaFin = rutaFile + nombre
    print rutaFin
    #Genera el comando de consulta y lo ejecuta
    comando = ('/home/nicolas/Operacional/Op_Radar/06_Codigos/Consulta_Caudal.py '+fecha1+' '+fecha2+' '
        +rutaFin+' '+idEst+' -t 5min -1 '+hora_1+' -2 '+hora_2
        +' -c '+c+' -e '+e)
    print comando
    os.system(comando)
    #Si ya existe le adjunta la nueva consulta 
    if Existe:
        Qhist = pnd.read_msgpack(rutaFile + L[pos])
        Qactual = pnd.read_msgpack(rutaTemp)
        #Junta ambos resgistros
        D = pnd.date_range(Qhist.index[0], Qactual.index[-1], freq='5min')
        Qjoin = pnd.Series(np.zeros(D.shape), D)
        Qjoin[Qhist.index] = Qhist
        Qjoin[Qactual.index] = Qactual
        #Guarda el archivo historico 
        Qjoin.to_msgpack(rutaFile + L[pos])
    print '################################################################################################'
    print 'consultado: '+k



#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
print '###################################################### Borra figuras de caudales simulados #########################################'

rutaQsim = '/media/nicolas/discoGrande/01_SIATA/ResultadosOperacion/Ope_Barbosa_Radar/Qsim/'
#Lista archivos y obtiene fechas de creacion
l = os.listdir(rutaQsim)
fechas = lambda x: dt.datetime.fromtimestamp(os.path.getmtime(x))
l = [ruta + i for i in l]
d = map(fechas, l)
#Organiza y prepara archivos para borrado
d2 = [[i,j] for i,j in zip(d,l)]
d2.sort()
d3 = d2[:-50] #cantidad de archivos que deja: 50.
#Borra archivos
comando = ['rm '+i[1] for i in d3]
map(os.system, comando)
