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
parser.add_argument("Qsim",help="(Obligatorio) Caudal simulado, guardado en pickle")
parser.add_argument("-t","--dt",help="(Opcional) Delta de t en segundos",default = 300,type=float)
parser.add_argument("-u","--update",help="(Opcional) Actualiza o no el almacenamiento de la cuenca",
	action = 'store_true', default = False)
parser.add_argument("-n","--new",help="(Opcional) Si se da, se genera una nueva cuenca con el estado de almacenamiento ")
parser.add_argument("-v","--verbose",help="(Opcional) Hace que el modelo indique en que porcentaje de ejecucion va",
        action = 'store_true', default = False)
parser.add_argument("-p","--nprocess",help="(Opcional) Cantidad de procesadores a tomar para ejecutar", default = 10)
parser.add_argument("-s","--nstorage", metavar='N', type = int, nargs = '+', 
	help="(Opcional) Condiciones finales para guardar, si -u: toma el primero, si -n: Toma el orden de entrada para guardar condiciones")

args=parser.parse_args()

#-------------------------------------------------------------------
#CONFIGURA LA RUTA DEL BINARIO DE LLUVIA
#-------------------------------------------------------------------
if args.binCampos.endswith('.hdr') or args.binCampos.endswith('.bin'):
	ruta_bin = args.binCampos[:-3]+'.bin'
	ruta_hdr = args.binCampos[:-3]+'.hdr'
else:
	ruta_bin = args.binCampos+'.bin'
	ruta_hdr = args.binCampos+'.hdr'

#-------------------------------------------------------------------
#CARGA LA CUENCA y la ejecuta
#-------------------------------------------------------------------
#Cargado de la cuenca
cu = wmf.SimuBasin(0,0,0,0,rute=args.cuenca)
wmf.models.dt = args.dt
if args.verbose:
	wmf.models.verbose = 1
#Carga la calibracion 
Calibs = np.loadtxt(args.calibracion,skiprows=13)
Muchas = False
for i in Calibs:
	try:
		if i.shape[0] > 0:
			Muchas = True
	except:
		pass
#Ejecucion
Resultados = []
if Muchas:
	#Lista de argumentos para multi-proceso
	ListaParam = []
	for c in Calibs:
		ListaParam.append([c,ruta_bin,args.pasos,args.inicio])
	#Ejecucion en multiproceso
	try:
		p = Pool(processes = args.nprocess)
		Resultados = p.map(Multiprocess_Warper,ListaParam)
	finally:
		p.close()
		p.join()
else:
	Resultados.append(cu.run_shia(Calibs,ruta_bin,args.pasos,args.inicio))
#Lee la lluvia media 
S = wmf.read_mean_rain(ruta_hdr,args.pasos,args.inicio)

#-------------------------------------------------------------------
#GUARDA LOS CAUDALES EN BINARIO 
#-------------------------------------------------------------------
#Determina los puntos de control como su ubicacion al interior de la cuenca
#pos = np.where(wmf.models.control<>0)[1]
pos = wmf.models.control[wmf.models.control<>0]
#if len(pos)>0:
#	pos = np.insert(pos,0,1)
#Los convierte en un DataFrame de pandas
for c,Res in enumerate(Resultados):
	Qsim = pnd.DataFrame(Res['Qsim'][1:].T,index=S.index,columns=pos)
	f = open(args.Qsim+'_'+str(c+1)+'.qsim','wb')
	pickle.dump(Qsim,f)
	pickle.dump(S,f)
	f.close()

#-------------------------------------------------------------------
#ACTUALIZA CONDICIONES DE LA CUENCA  
#-------------------------------------------------------------------
#toma las rutas de la cuenca original
g = netCDF4.Dataset(args.cuenca)
ruta_dem = g.DEM
ruta_dir = g.DIR
g.close()
#toma el almacenamiento de actualizacion 
if args.nstorage:
	#Caso de una sola calibracion
	if not Muchas:
		R = Resultados[0]
		for c,s in enumerate(R['Storage']):
			cu.set_Storage(s,c)
	if Muchas:
		for pos in args.nstorage:
			R = Resultados[pos]
			for c,s in enumerate(R['Storage']):
				cu.set_Storage(s,c)
			if args.new <> None:
				cu.Save_SimuBasin(args.new+'_'+str(pos)+'.nc',
					ruta_dem = ruta_dem,
					ruta_dir = ruta_dir)
#Actualizacion de la cuenca ejecutada originalmente 
if args.update:
	#Actualiza la cuenca, en este caso solo cambia el almacenamiento 
	cu.Save_SimuBasin(args.cuenca,
		ruta_dem = ruta_dem,
		ruta_dir = ruta_dir)
