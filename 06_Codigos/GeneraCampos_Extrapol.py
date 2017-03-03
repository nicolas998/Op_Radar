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
        prog='Genera Campos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
	Genera campos de precipitacion para las imagenes extrapoladas 
	de Olver Olfrei.
        '''))
#Parametros obligatorios
parser.add_argument("cuenca",help="(Obligatorio) Ruta de la cuenca en formato .nc")
parser.add_argument("binCampos",help="(Obligatorio) Ruta donde se guarda el binario de lluvia")
parser.add_argument("hdr", help = "Ruta del header del campo actual de lluvia, para tomar la fecha")
parser.add_argument("ruta", help = "Ruta donde se encuentran los binarios con extrapolacion")
parser.add_argument("-u","--umbral",help="(Opcional) Umbral de lluvia minima",default = 0.0,type=float)
parser.add_argument("-v","--verbose",help="Informa sobre la fecha que esta agregando", action = 'store_true')
parser.add_argument("-s","--super_verbose",help="Imprime para cada posicion las imagenes que encontro",
        action = 'store_true')
parser.add_argument("-o", "--old", help="Determina si va a escribir sobre un archivo viejo o no ", 
	default = True)
	

#lee todos los argumentos
args=parser.parse_args()

#------------------------------------------------------------------------------
#DETERMINA FECHA DE ULTIMO CAMPO 
#------------------------------------------------------------------------------
#lee el encabezado del campo actual 
f = open(args.hdr,'r')
L = f.readlines()
f.close()
# Obtiene el elemento en Datetime
fecha = L[6].split()[-1]
fecha = dt.datetime.strptime(fecha, '%Y-%m-%d-%H:%M')


#------------------------------------------------------------------------------
#LISTA DE CAMPOS DE EXTRAPOLACION DISPONIBLES
#------------------------------------------------------------------------------
#lista elementos disponibles de extrapolacion
Lista = os.listdir(args.ruta)
Lista.sort()
fin = Lista[-1]
#Discrimina desde puntos de partida de extrapolacion
ListaNames = [i for i in Lista if i.endswith('_005.bin')]
L2 = [i for i in Lista if i.startswith(fin[:12])]
#Mira en orden inverso quien de esos productos ya cuenta con mas de una hora de extrapolacion
Flag =True
for i in ListaNames[::-1]:
    #Mira cuantos archivos hay de esa fecha
    Ltemp = [j for j in Lista if j.startswith(i[:12])]
    #Si hay mas de doce toma esa fecha para la extrapolacion
    if len(Ltemp) >= 16 and Flag:
        FechaStart = i[:12]
        Flag = False
#Saca la lista de los elementos que va a evaluar y organiza sus fechas
ListaFin = [i for i in Lista if i.startswith(FechaStart)]
Fechas = [dt.datetime.strptime(i[:12], '%Y%m%d%H%M')+dt.timedelta(minutes = int(i[-7:-4])) for i in ListaFin]
Fechas = [i - dt.timedelta(hours = 5) for i in Fechas]
#Obtiene el punto de inicio para que las imagenes sean chevres 
Diferencias = [i - fecha for i in Fechas]
Segundos = np.array([i.seconds for i in Diferencias])
pos = np.argmin(Segundos)

#------------------------------------------------------------------------------
#LEE Y DETERMINA FECHAS DE ARCHIVOS CORRESPONDINTES
#------------------------------------------------------------------------------
#inicia la variable de radar y la variable cuenca 
cuAMVA = wmf.SimuBasin(rute = args.cuenca)
rad = radar.radar_process()
	
#Trabaja sobre la lista para adicionar campos
rvec = {'media':[], 
		'baja': [], 
		'alta': []}
for c,l in enumerate(ListaFin[pos:pos+12]):
	#convierte imagen de radar en lluvia	
	rad.read_bin(args.ruta+l)
	rad.detect_clouds(umbral=500)
	rad.ref = rad.ref * rad.binario
	rad.DBZ2Rain()
	for k in ['media','baja','alta']:
		rv = cuAMVA.Transform_Map2Basin(rad.ppt[k]/12.0,radar.RadProp)
		rvec[k].append(rv)
	#Dice info sobre lo que hace
	if args.verbose:
		print l, len(rvec[k])
		print '-----------------------------------------'

#Escribe los archivos binarios con la informacion de precpitaciojn extrapolada
for k in ['media','baja','alta']:
	#Ruta 
	ruta = args.binCampos + '_'+k
	#Toma las caracteristicas del archivo viejo
	if args.old:
		cuAMVA.rain_radar2basin_from_array(status='old',ruta_out=ruta)
	#Actualiza
	for c,v in enumerate(rvec[k]):
		dentro = cuAMVA.rain_radar2basin_from_array(vec = v,
			ruta_out = ruta,
			fecha = fecha + dt.timedelta(minutes = 5*(c+1)),
			dt = 300,
			umbral = args.umbral)
	# Cierra el binario y construye el hdr, luego reinicia el contador de radar
	cuAMVA.rain_radar2basin_from_array(status = 'close',ruta_out = ruta)
	cuAMVA.rain_radar2basin_from_array(status = 'reset')


