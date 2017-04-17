#!/usr/bin/env python 

import os 
from wmf import wmf 
import numpy as np 
import datetime as dt 
import pandas 
from radar import radar
import argparse
import textwrap

#Parametros de entrada del trazador
parser=argparse.ArgumentParser(
        prog='Genera Campos_Persistencia',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
	Genera campos iguales al ultimo, esto es para el caso en que  
	falla la extrapolacion de olver olfrei.
        '''))
#Parametros obligatorios
parser.add_argument("cuenca",help="(Obligatorio) Ruta de la cuenca en formato .nc")
parser.add_argument("binCampos",help="(Obligatorio) Ruta donde se guarda el binario de lluvia")
parser.add_argument("-v","--verbose",help="Informa sobre la fecha que esta agregando", action = 'store_true')
parser.add_argument("-s","--super_verbose",help="Imprime para cada posicion las imagenes que encontro",
        action = 'store_true')
parser.add_argument("-o", "--old", help="Determina si va a escribir sobre un archivo viejo o no ", 
	default = True)
parser.add_argument("-u","--umbral",help="(Opcional) Umbral de lluvia minima",
	default = 0.0, type=float)
args=parser.parse_args()

#Lee la cuenca	
cuAMVA = wmf.SimuBasin(rute = args.cuenca)
#Escribe los archivos binarios con la informacion de precpitaciojn extrapolada
for k in ['media','baja','alta']:
	#Ruta 
	ruta = args.binCampos + '_'+k
	#Toma las caracteristicas del archivo viejo
	if args.old:
		cuAMVA.rain_radar2basin_from_array(status='old',ruta_out=ruta)
	#Lee el campo:
	v,r = wmf.models.read_int_basin(ruta+'.bin',1, cuAMVA.ncells)
	if r <> 0: #Por si no hay registros en la imagen actual de radar
		v = np.zeros(cuAMVA.ncells)
	#Lee la fecha de la imagen actual 
	f = open(ruta+'.hdr','r')
	L = f.readlines()
	f.close()
	fecha = dt.datetime.strptime(L[-1].split()[-1], '%Y-%m-%d-%H:%M')
	#Actualiza
	for c in range(1,13):
		dentro = cuAMVA.rain_radar2basin_from_array(vec = v,
			ruta_out = ruta,
			fecha = fecha + dt.timedelta(minutes = 5*(c+1)),
			dt = 300,
			umbral = args.umbral)
	# Cierra el binario y construye el hdr, luego reinicia el contador de radar
	cuAMVA.rain_radar2basin_from_array(status = 'close',ruta_out = ruta)
	cuAMVA.rain_radar2basin_from_array(status = 'reset')
