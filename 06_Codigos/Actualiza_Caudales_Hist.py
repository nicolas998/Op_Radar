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
	Actualiza los caudlaes simulados para las condiciones normales de lluvia 
	este script utiliza los caudales .qsim que se encuentra en la carpeta 
	03_Simulaciones y los .qsimh que se encuentran en la sub-carpeta 
	02_Stream_History. Las series tipo DataFrame de Pandas de esta ultima 
	carpeta se actulizan cada 5 min con las simulaciones obtenidas por cada
	parametrizacion del modelo.
        '''))
#Parametros obligatorios
parser.add_argument("rutaQhist",help="(Obligatorio) Carpeta con la serie historica de caudales .qsimh simulados por el modelo ")
parser.add_argument("rutaQsim",help="(Obligatorio) Carpeta con la series de caudales .qsim simulados en el ultimo intervalo")
parser.add_argument("-n", "--newhist", help="(Opcional) Con esta opcion el script genera un nuevo punto de generacion de historicos",
	action = 'store_true', default = False)
parser.add_argument("-i", "--fechai", help="(Opcional) Fecha de inicio de nuevo punto de historicos (YYYY-MM-DD HH:MM)")
parser.add_argument("-f", "--fechaf", help="(Opcional) Fecha de fin de nuevo punto de historicos (YYYY-MM-DD HH:MM)")
parser.add_argument("-v","--verbose",help="(Opcional) Hace que el modelo indique en que porcentaje de ejecucion va",
	action = 'store_true', default = False)

args=parser.parse_args()

#-------------------------------------------------------------------
# LISTA DE CAUDALES SIMULADOS 
#-------------------------------------------------------------------
#Lista caudales simulados sin repetir 
Lsim = os.listdir('/home/nicolas/Operacional/Op_Interpolated/03_Simulaciones/')
Lsim = [i for i in Lsim if i.endswith('qsim')]
Lsim = [i[:12] for i in Lsim]
Lsim = list(set(Lsim))

#Lee un caudal simulado para conocer las caracteristicas de este 
L = os.listdir('/home/nicolas/Operacional/Op_Interpolated/03_Simulaciones/')
L = [i for i in L if i.endswith('normal.qsim')]
Qsim = pnd.read_msgpack(args.rutaQsim + L[0])
Nodos = Qsim.shape[1]

#-------------------------------------------------------------------
# NUEVO PUNTO DE HISTORIA (solo si se habilita)
#-------------------------------------------------------------------
if args.newhist:	
	#Fechas de inicio y fin 
	FechaI = args.fechai
	FechaF = args.fechaf
	#Genera el Data Frame vacio desde el inicio hasta el punto de ejecucion
	DifIndex = pnd.date_range(FechaI, FechaF, freq='5min')
	Qh = pnd.DataFrame(np.zeros((DifIndex.size, Nodos))*np.nan, 
	    index=pnd.date_range(FechaI, FechaF, freq='5min'),
	    columns = Qsim.columns)
	#Guarda los caudales base para los historicos
	Lhist = os.listdir(args.rutaQhist)
	for i in Lsim:
	    #Pregunta si esta
	    try:
	        pos = Lhist.index(i+'.qsimh')
	        flag = raw_input('Aviso: El archivo historico : '+i+' ya existe, desea sobre-escribirlo, perdera la historia de este!! (S o N): ')
	        if flag == 'S':
	            flag = True
	        else:
	            flag = False
	    except:
	        flag = True
	    #Guardado
	    if flag:
	        Qh.to_msgpack(args.rutaQhist + i + '.qsimh')
	    
#-------------------------------------------------------------------
# ACTUALIZACION DE CAUDALES 
#-------------------------------------------------------------------
#Busca la simulacion del caso normal para cada calibracion
L = os.listdir('/home/nicolas/Operacional/Op_Interpolated/03_Simulaciones/')
L = [i for i in L if i.endswith('normal.qsim')]
# Actualiza caudales para cada parametrizacion 
for i in L:
    #busca que este el archivo base en la carpeta 
	try:
		Qhist = pnd.read_msgpack(args.rutaQhist + i[:-12] + '.qsimh')
		Qactual = pnd.read_msgpack(args.rutaQsim + i)
		# encuentra el pedazo que falta entre ambos 
		Gap = pnd.date_range(Qhist.index[-1], Qactual.index[0], freq='5min')
		#Genera el pedazo con faltantes
		GapData = pnd.DataFrame(np.zeros((Gap.size - 2, Nodos))*np.nan, 
			index= Gap[1:-1],
			columns = Qactual.columns)        
		#pega la informacion
		Qhist = Qhist.append(GapData)
		Qhist = Qhist.append(Qactual[Qactual.index == Qactual.index[0]])
		#Guarda el archivo historico 
		Qhist.to_msgpack(args.rutaQhist + i[:-12] + '.qsimh')
		#Aviso
		print 'Aviso: Se ha actualizado el archivo de caudales simulados historicos: '+i[:-12] + '.qsimh'
	except:
		print 'Aviso: No se encuentra el historico de caudales '+i+' Por lo tanto no se actualiza'
