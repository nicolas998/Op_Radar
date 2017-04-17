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
	Genera el mapa de caudales estimados para cada elemento de la red hidrica
	de la cuenca.
        '''))
#Parametros obligatorios
parser.add_argument("cuenca",help="Numero del nodo dentro de la red hidrica a plotear")
parser.add_argument("storage",help="Ruta al archivo binario con el almacenamiento")
parser.add_argument("ruta",help="Ruta donde se guarda la figura con la humedad")
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
Coord = cu.Plot_Net(v[-1]*((60**2)/1000.0), 
	tranparent = True, 
	ruta = ruta_plot,
	clean = True, 
	colorbar = False, 
	figsize = (10,12), 
	umbral = 0.05, 
	escala = 1,
	cmap = 'Blues',
	vmin = 0.0,
	vmax = 0.3,
	show = False)	

#Guarda archuivo con coordenadas
#Guarda archuivo con coordenadas
if args.coord:
	f = open(ruta_texto, 'w')
	for t,i in zip(['Left', 'Right', 'Bottom', 'Top'], Coord):
		f.write('%s, \t %.4f \n' % (t,i))
	f.close()
