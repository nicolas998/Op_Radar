#!/usr/bin/env python
import argparse
import textwrap
import os 
import pandas as pd 
import json

#Parametros de entrada del trazador
parser=argparse.ArgumentParser(
	prog='Consulta_Caudal',
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description=textwrap.dedent('''\
	Genera un archivo json dedicado a alimentar el kml de despliegue del modelo en la 
	pagina del SIATA, este json contiene informacion de simulacion: Qsim, Qsim ultimas 24h
	, Qsim proxima hora en escenarios de baja, media y alta precipitacion.
        '''))
#Parametros obligatorios
parser.add_argument("parametrizacion",help="nombre sin la extension de los resultados de caudal de la parametrizacion a incluir")
parser.add_argument("param_hist",help="nombre sin la extension de los resultados de caudal historicos de la parametrizacion a incluir")
parser.add_argument("rutaJson",help="ruta donde se guarda el json con la informacion descrita")
	
#lee todos los argumentos
args=parser.parse_args()
ruta = args.parametrizacion
ruta_hist = args.param_hist

#-----------------------------------------------------------------------------------------------------
#Carga los caudales simulados 
#-----------------------------------------------------------------------------------------------------
Qsim = pd.read_msgpack(ruta_hist + '.qsimh')
QsimF = {}
QsimF.update({'Alto':pd.read_msgpack(ruta + '_alto.qsim')})
QsimF.update({'Bajo':pd.read_msgpack(ruta + '_bajo.qsim')})
QsimF.update({'Medio':pd.read_msgpack(ruta + '_normal.qsim')})
Nodos = Qsim.columns.values

#-----------------------------------------------------------------------------------------------------
#Genera el Diccionario con los caudales y escribe el json
#-----------------------------------------------------------------------------------------------------
Dict = {}
for n in Nodos:
    Dict.update({str(n):{}})
    Dict[str(n)].update({'ultimo': float('%.3f' % Qsim[n][-1])})
    Dict[str(n)].update({'max24h': float('%.3f' % Qsim[n][-288:].max())})
    for i in ['Bajo', 'Medio', 'Alto']:
        Dict[str(n)].update({i: float('%.3f' % QsimF[i][n].max())})
with open(args.rutaJson, 'w') as outfile:
    json.dump(Dict, outfile)
