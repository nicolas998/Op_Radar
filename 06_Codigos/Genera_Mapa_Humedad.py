#!/usr/bin/env python
import argparse
import textwrap
import numpy as np
import os 
from wmf import wmf 

#Parametros de entrada del trazador
parser=argparse.ArgumentParser(
	prog='Genera_Grafica_Qsim',
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description=textwrap.dedent('''\
	Genera la figura de caudales simulados para un periodo asignado de tiempo, de forma 
	adicional presenta el hietograma de precipitacion.
        '''))
#Parametros obligatorios
parser.add_argument("cuenca",help="Numero del nodo dentro de la red hidrica a plotear")
parser.add_argument("storage",help="Ruta al archivo binario con el almacenamiento")
parser.add_argument("ruta",help="Ruta donde se guarda la figura con la humedad")
parser.add_argument("-1", "--vmin",help="Minimo valor del imshow", default = 0, type = float)
parser.add_argument("-2", "--vmax",help="Maximo valor del imshow", default = 100, type = float)
parser.add_argument("-c", "--coord",help="Escribe archivo con coordenadas", default = False, type = bool)

#lee todos los argumentos
args=parser.parse_args()

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#Lectura de cuenc ay variables
cu = wmf.SimuBasin(rute=args.cuenca)
v,r = wmf.models.read_float_basin_ncol(args.storage,1, cu.ncells, 5)

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#Configura rutas
if args.ruta.endswith('.png'):
	ruta_texto = args.ruta[:-4] + '.txt'
	ruta_plot = args.ruta
else:
	ruta_texto = args.ruta + '.txt'
	ruta_plot = args.ruta + '.png'
#Plot 
#Humedad = 100.0*((v[0]+v[2])/(wmf.models.max_gravita + wmf.models.max_capilar))
Humedad = v[2]/wmf.models.max_gravita

Coord = cu.Plot_basinClean(Humedad, ruta_plot, figsize = (15,10), cmap = 'viridis', 
	vmax = args.vmax, vmin = args.vmin)
#Guarda archuivo con coordenadas
if args.coord:
	f = open(ruta_texto, 'w')
	for t,i in zip(['Left', 'Right', 'Bottom', 'Top'], Coord):
		f.write('%s, \t %.4f \n' % (t,i))
	f.close()
