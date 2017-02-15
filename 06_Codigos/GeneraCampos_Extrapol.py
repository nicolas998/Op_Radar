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
parser.add_argument("-u","--umbral",help="(Opcional) Umbral de lluvia minima",default = 0.0,type=float)
parser.add_argument("-v","--verbose",help="Informa sobre la fecha que esta agregando", action = 'store_true')
parser.add_argument("-s","--super_verbose",help="Imprime para cada posicion las imagenes que encontro",
        action = 'store_true')

#lee todos los argumentos
args=parser.parse_args()

#------------------------------------------------------------------------------
#lECTURA Y ESCRITURA DE LA LISTA 
#------------------------------------------------------------------------------
#Lista los archivos en la carpeta
Lista = os.listdir('/mnt/RADAR/extrapolation/')
Lista.sort()
#Obtiene los nombres de los que son unicos 
Nombres = np.array([int(i[:12]) for i in Lista])
Nombres = np.unique(Nombres)
Nombres = [str(n) for n in Nombres]
#Calcula la cantidad de imagenes de cada nombre 
CantidadImagenes = []
for n in Nombres:
	c = 0
	for l in Lista:
		try:
			l.index(n)
			c+=1
		except:
			pass
	CantidadImagenes.append(c)
#Obtiene la fecha que va a usar como punto de partida para tomar las imagenes 
Flag = True
N = len(CantidadImagenes)-1
while Flag:
	if CantidadImagenes[N] == 24:
		Flag = False
		Pos = N
	else:
		N-=1
	if N == 0:
		Pos = 0
		Flag = False
if args.verbose:
	print 'Archivo Base: ' + Nombres[Pos]
	print '-----------------------------------'
#------------------------------------------------------------------------------
#LEE Y DETERMINA FECHAS DE ARCHIVOS CORRESPONDINTES
#------------------------------------------------------------------------------
#inicia la variable de radar y la variable cuenca 
cuAMVA = wmf.SimuBasin(0,0,0,0,rute = args.cuenca)
rad = radar.radar_process()
#toma solo los nombres que interesan
Lista = [i for i in Lista if i.startswith(Nombres[Pos])]
Lista.sort()


for c,l in enumerate(Lista):
	#convierte imagen de radar en lluvia	
	rad.read_bin('/mnt/RADAR/extrapolation/'+l)
        rad.detect_clouds(umbral=500)
        rad.ref = rad.ref * rad.binario
	rad.DBZ2Rain()
        rvec = cuAMVA.Transform_Map2Basin(rad.ppt/12.0,radar.RadProp)
	#Obtiene la fecha
	date = dt.datetime.strptime(l[:12],'%Y%m%d%H%M') - dt.timedelta(hours = 5)
	#Pone la lluvia de radar en el binario de la cuenca 
        dentro = cuAMVA.rain_radar2basin_from_array(vec = rvec,
        	ruta_out = args.binCampos,
                fecha = date + dt.timedelta(minutes = 5*(c+1)),
                dt = 300,
                umbral = args.umbral)
	if args.verbose:
                print date+dt.timedelta(minutes = 5*(c+1)),rvec.mean(), dentro
                print '-----------------------------------------'

# Cierra el binario y construye el hdr
cuAMVA.rain_radar2basin_from_array(status = 'close',
        ruta_out = args.binCampos)


