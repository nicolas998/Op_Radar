#!/usr/bin/env python

from wmf import wmf 
import numpy as np 
import pickle 
import pandas as pnd
import pylab as pl
import argparse
import textwrap
import netCDF4
from multiprocessing import Pool
import os 

#-------------------------------------------------------------------
#FUNCIONES LOCALES
#-------------------------------------------------------------------

#-------------------------------------------------------------------
#PARSEADOR DE ARGUMENTOS  
#-------------------------------------------------------------------
#Parametros de entrada del trazador
parser=argparse.ArgumentParser(
        prog='Actualiza_Caudales_Hist',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
	Actualiza la lluvia media sobre la cuenca estimada por alguna 
	metodologia.
        '''))
#Parametros obligatorios
parser.add_argument("rutaRain",help="(Obligatorio) Ruta donde se encuentran los archivos de lluvia ")
parser.add_argument("-n", "--newhist", help="(Opcional) Con esta opcion el script genera un nuevo punto de generacion de historicos",
	action = 'store_true', default = False)
parser.add_argument("-i", "--fechai", help="(Opcional) Fecha de inicio de nuevo punto de historicos (YYYY-MM-DD HH:MM)")
parser.add_argument("-f", "--fechaf", help="(Opcional) Fecha de fin de nuevo punto de historicos (YYYY-MM-DD HH:MM)")
parser.add_argument("-v","--verbose",help="(Opcional) Hace que el modelo indique en que porcentaje de ejecucion va",
	action = 'store_true', default = False)

args=parser.parse_args()

nombre = 'Mean_Rain_History.rainh'

#-------------------------------------------------------------------
#CHECK DE SI YA HAY ARCHIVO DE HISTORIA O SI RE ESCRIBE
#-------------------------------------------------------------------

if args.newhist:	
    #Fechas de inicio y fin 
    FechaI = args.fechai
    FechaF = args.fechaf
    #Genera el Data Frame vacio desde el inicio hasta el punto de ejecucion
    DifIndex = pnd.date_range(FechaI, FechaF, freq='5min')
    Rh = pnd.DataFrame(np.zeros((DifIndex.size, 3))*np.nan, 
        index=pnd.date_range(FechaI, FechaF, freq='5min'),
        columns = ['media','baja','alta'])
    #Guarda los caudales base para los historicos
    Lhist = os.listdir(args.rutaRain)
    try:
        pos = Lhist.index(nombre)
        flag = raw_input('Aviso: El archivo historico : '+nombre+' ya existe, desea sobre-escribirlo, perdera la historia de este!! (S o N): ')
        if flag == 'S':
            flag = True
        else:
            flag = False
    except:
        flag = True
    #Guardado
    if flag:
        Rh.to_msgpack(args.rutaRain + nombre)
        
#-------------------------------------------------------------------
#ACTUALIZA HISTORIA DE LLUVIA
#-------------------------------------------------------------------

#Lista caudales simulados sin repetir 
Lsim = os.listdir('/home/nicolas/Operacional/Op_Radar/03_Simulaciones/01_Rain/')
Lsim = [i for i in Lsim if i.endswith('hdr')]
names = [i.split('_')[1][:-4] for i in Lsim]
#busca que este el archivo base en la carpeta 
try:	
	#lee la lluvia de los encabezados
	R = []    
	for n,l in zip(names, Lsim):
		r = pnd.read_csv(args.rutaRain + l, 
			header = 5, 
			index_col = 1, 
			parse_dates = True, 
			usecols=(2,3))
		R.append(r.values[0].tolist())
	R = np.array(R)
	#Genera un DataFrame con eso
	Rt = pnd.DataFrame(R.T, 
		index=[r.index[0],], 
		columns=names)
	#Lee el historico de lluvia
	Rhist = pnd.read_msgpack(args.rutaRain + nombre)
	#Rhist = pnd.read_msgpack('Mean_Rain_History.rainh')
	#encuentra el pedazo que falta entre ambos 
	Gap = pnd.date_range(Rhist.index[-1], Rt.index[0], freq='5min')
	#Genera el pedazo con faltantes
	GapData = pnd.DataFrame(np.zeros((Gap.size - 2, 3))*np.nan, 
		index= Gap[1:-1],
		columns = Rhist.columns)        
	#pega la informacion
	Rhist = Rhist.append(GapData)
	Rhist = Rhist.append(Rt)
	#Guarda el archivo historico 
	Rhist.to_msgpack(args.rutaRain + nombre)
	#Aviso
	print 'Aviso: Se ha actualizado el archivo de precipitacion media historica: '+nombre
except:
	print 'Aviso: No se encuentra el historico de precipitacion '+nombre+' Por lo tanto no se actualiza'
