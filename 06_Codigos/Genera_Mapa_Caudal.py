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
parser.add_argument("cuenca",help="Archivo -nc de la cuenca con la cual se va a realizar el trabajo")
parser.add_argument("storage",help="Ruta al archivo binario con el almacenamiento")
parser.add_argument("ruta",help="Ruta donde se guarda la figura con la humedad")
parser.add_argument("-c", "--coord",help="Escribe archivo con coordenadas", default = False, type = bool)
parser.add_argument("-r", "--record",help="Record de lectura en el binario para graficar", 
	default = 1, type = int)

#lee todos los argumentos
args=parser.parse_args()

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#Lectura de cuenc ay variables
cu = wmf.SimuBasin(rute=args.cuenca)
v,r = wmf.models.read_float_basin_ncol(args.storage,args.record, cu.ncells, 5)
#lectura de constantes 
qmed = cu.Load_BasinVar('qmed')
horton = cu.Load_BasinVar('horton')
cauce = cu.Load_BasinVar('cauce')

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#Configura rutas
if args.ruta.endswith('.png'):
	ruta_texto = args.ruta[:-4] + '.txt'
	ruta_plot = args.ruta
else:
	ruta_texto = args.ruta + '.txt'
	ruta_plot = args.ruta + '.png'
#obtiene la razon entre Qsim y Qmed 
Razon = v[-1]*((60**2)/1000.0) / qmed
#Prepara mapas de grosor y de razon 
RazonC = np.ones(cu.ncells)
Grosor = np.ones(cu.ncells)
#Rangos = [[]]
for c,i in enumerate([20,50,80,200]):
    for h in range(1,6):        
        camb = 6 - h
        RazonC[(Razon >= i*camb) & (horton == h)] = c+2
        Grosor[(Razon >= i*camb*0.3) & (horton == h)] = np.log((c+1)*10)**1.4

#Plot 	
Coord = cu.Plot_Net(Grosor, RazonC,  
	tranparent = True, 
	ruta = ruta_plot,
	clean = True, 
	colorbar = False, 
	show_cbar = False,
	figsize = (10,12), 
	umbral = cauce, 
	escala = 1.5,
	cmap = wmf.pl.get_cmap('viridis',5),
	vmin = None,
	vmax = None,
	show = True)	

#Coord = cu.Plot_Net(v[-1]*((60**2)/1000.0), 
	#tranparent = True, 
	#ruta = ruta_plot,
	#clean = True, 
	#colorbar = False, 
	#figsize = (10,12), 
	#umbral = 0.05, 
	#escala = 1,
	#cmap = 'Blues',
	#vmin = 0.0,
	#vmax = 0.3,
	#show = False)	

#Guarda archuivo con coordenadas
if args.coord:
	f = open(ruta_texto, 'w')
	for t,i in zip(['Left', 'Right', 'Bottom', 'Top'], Coord):
		f.write('%s, \t %.4f \n' % (t,i))
	f.close()
