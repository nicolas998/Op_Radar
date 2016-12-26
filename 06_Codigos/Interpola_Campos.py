#!/usr/bin/env python

from wmf import wmf 
#import func_SIATA as fs
import pylab as pl
import numpy as np
import pickle
import datetime as dt
import argparse
import textwrap
import os 
import pandas as pd


#Parametros de entrada del trazador
parser=argparse.ArgumentParser(
	prog='Genera Campos',
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description=textwrap.dedent('''\
	Interpola campos de lluvia para que estos sean utilizados por 
	el modelo hidrologico, la metodologia para la interpolacion es IDW.
        '''))
#Parametros obligatorios
parser.add_argument("RutaBinRain",help="ruta donde se encuentra el binario de lluvia con el cual se generan los campos")
parser.add_argument("RutaCuenca",help="Ruta con el archivo .nc de la cuenca")
parser.add_argument("RutaCampos",help="Ruta donde quedan almacenados los campos de lluvia interpolados")
parser.add_argument("-p","--exponente",help="(Opcional) Exponente con el cual se ponderan los pesos para la interpolacion",default = 4,type=float)

#lee todos los argumentos
args=parser.parse_args()

#-------------------------------------------------------------------
#CARGADO DE CUENCA Y CONFIGURACION MODELO
#-------------------------------------------------------------------
cu = wmf.SimuBasin(0,0,0,0, rute=args.RutaCuenca)
wmf.models.nodata = -999
print 'Cargado de la cuenca existoso... \n'
#-------------------------------------------------------------------
#CARGADO DE LOS REGISTROS DE PRECIPITACION
#-------------------------------------------------------------------
#Carga registros
f = open(args.RutaBinRain,'r')
RainData = pickle.load(f)
Coord = pickle.load(f)
f.close()
print 'Cargado de registros existoso... \n'
#Interpola con los registros
a = cu.rain_interpolate_idw(Coord, RainData,
    args.RutaCampos, p = 6)
print 'Interpolacion exitosa \n'
print a[0]
print '\n'
