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

#-------------------------------------------------------------------
#FUNBCIONES LOCALES
#-------------------------------------------------------------------
def Multiprocess_Warper(Lista):
	return cu.run_shia(Lista[0],Lista[1],Lista[2],Lista[3])


#-------------------------------------------------------------------
#PARSEADOR DE ARGUMENTOS  
#-------------------------------------------------------------------
#Parametros de entrada del trazador
parser=argparse.ArgumentParser(
        prog='Ejecuta_Modelo',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
	Script que se encarga de ejecutar el modelo hidrologico, para ello requiere:
	La cuenca a ejecutar, el binario con el campo de lluvia, el punto de inicio 
	la cantidad de pasos y el llugar de salida para guardar resultados
        '''))
#Parametros obligatorios
parser.add_argument("cuenca",help="(Obligatorio) Ruta de la cuenca en formato .nc")
parser.add_argument("binCampos",help="(Obligatorio) Ruta donde se encuentra el binario de lluvia")
parser.add_argument("inicio",help="(Obligatorio) Punto de inicio de simulacion dentro del binario",type=int)
parser.add_argument("pasos",help="(Obligatorio) Cantidad de pasos hacia adelante en simulacion",type = int)
parser.add_argument("calibracion",help="(Obligatorio) Ruta al archivo con las calibraciones")
parser.add_argument("qsim",help="(Obligarotio) Rurta donde se guardan las simulaciones de caudal")
parser.add_argument("-t","--dt",help="(Opcional) Delta de t en segundos",default = 300,type=float)
parser.add_argument("-u","--update",help="(Opcional) Usa estados guardados de la cuenca para cargar en las condiciones",
	default = 0, type = int)
parser.add_argument("-v","--verbose",help="(Opcional) Hace que el modelo indique en que porcentaje de ejecucion va",
        action = 'store_true', default = False)
parser.add_argument("-s","--storage", help="(Opcional) Condiciones finales para guardar",
	action = 'store_true', default = False)

args=parser.parse_args()

#-------------------------------------------------------------------
#CONFIGURA LA RUTA DEL BINARIO DE LLUVIA
#-------------------------------------------------------------------
ruta_bin, ruta_hdr = wmf.__Add_hdr_bin_2route__(args.binCampos)

#-------------------------------------------------------------------
#CARGA LA CUENCA y CALIBRACION
#-------------------------------------------------------------------

#Cargado de la cuenca
cu = wmf.SimuBasin(0,0,0,0,rute=args.cuenca)
wmf.models.show_storage = 1
wmf.models.dt = args.dt
if args.verbose:
	wmf.models.verbose = 1

#Carga la calibracion 
C = np.loadtxt(args.calibracion, skiprows=13, dtype = str)
#Para una sola calibracion 
if C.size == 11:
	CalibNames = [C[0]]
	Calibs = np.array([[float(i) for i in C[1:]]])
	Muchas = False
#Para multiples calibraciones
elif C.size > 11:
	CalibNames =  [i[0] for i in C]
	Calibs = []
	for j in C:
		C2 = [float(i) for i in j[1:]]
		Calibs.append(C2)
	C2 = []
	Calibs = np.array(Calibs)
	Muchas = True

#-------------------------------------------------------------------
#EJECUTA LA CUENCA
#-------------------------------------------------------------------
S = wmf.read_mean_rain(ruta_hdr,args.pasos,args.inicio)
for Nombre,Calib in zip(CalibNames, Calibs):
	# Si el nombre no es NaN y la opcion update esta habilitada carga condiciones 
	if args.update>-1 and Nombre <> 'NaN':
		# obtiene las rutas del binario y del encabezado de almacenamiento 
		ruta_sto_bin, ruta_sto_hdr = wmf.__Add_hdr_bin_2route__('/home/renea998/Storage/'+Nombre,
			storage = True)
		# Carga las condiciones en la cuenca
		cu.set_Storage(ruta_sto_bin,args.update)
		print 'AVISO: actualizo almacenamiento'
	#Si se habilita la opcion de guardado, se guardan las condiciones de almacenamiento en la cuenca 
	if args.storage:
		ruta_storage = '/home/renea998/Storage/'+Nombre
		wmf.models.save_storage = 1
		#Ejecucion de la cuenca
		Res = cu.run_shia(Calib,ruta_bin,args.pasos,args.inicio,
			ruta_storage = ruta_storage)
	else:
		wmf.models.save_storage = 0
		#Ejecucion de la cuenca
		Res = cu.run_shia(Calib,ruta_bin,args.pasos,args.inicio)
	#Guarda el caudal simulado en un binario tipo pickle
	ruta_Qsim = args.qsim+Nombre+'.qsim'
	pos = wmf.models.control[wmf.models.control<>0]
	Qsim = pnd.DataFrame(Res['Qsim'][1:].T,index=S.index,columns=pos)
        f = open(ruta_Qsim,'wb')
        pickle.dump(Qsim,f)
        pickle.dump(S,f)
        f.close()
	#Si es versobre muestra en que simulacion va 
	if args.verbose:
		print 'AVISO: Ejecutando Simulacion: '+ Nombre
