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
import os 

#-------------------------------------------------------------------
#FUNCIONES LOCALES
#-------------------------------------------------------------------

#-------------------------------------------------------------------
#PARSEADOR DE ARGUMENTOS  
#-------------------------------------------------------------------
#Parametros de entrada del trazador
parser=argparse.ArgumentParser(
        prog='Actualiza_Caudales_Hist',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
	Actualiza las series de almacenamiento medio estimadas por el modelo 
	para la cuenca en la cual se este simulando, existen tantos archivos de 
	almacenamiento medio como calibraciones para el proyecto de la cuenca 
	existan.
        '''))
#Parametros obligatorios
parser.add_argument("rutaShist",help="(Obligatorio) Carpeta con la serie historica de almacenamientos .StoHist simulados por el modelo ")
parser.add_argument("rutaSsim",help="(Obligatorio) Carpeta con las series de almacenamientos .StOhdr simulados en el ultimo intervalo")
parser.add_argument("-n", "--newhist", help="(Opcional) Con esta opcion el script genera un nuevo punto de generacion de historicos",
	action = 'store_true', default = False)
parser.add_argument("-i", "--fechai", help="(Opcional) Fecha de inicio de nuevo punto de historicos (YYYY-MM-DD HH:MM)")
parser.add_argument("-f", "--fechaf", help="(Opcional) Fecha de fin de nuevo punto de historicos (YYYY-MM-DD HH:MM)")
parser.add_argument("-v","--verbose",help="(Opcional) Hace que el modelo indique en que porcentaje de ejecucion va",
	action = 'store_true', default = False)

args=parser.parse_args()

#-------------------------------------------------------------------
# LISTA DE CAUDALES SIMULADOS 
#-------------------------------------------------------------------
#Lista caudales simulados sin repetir 
L = os.listdir(args.rutaSsim)
L = [i for i in L if i.endswith('StOhdr')]
Lhist = [i[:-7] + '.StoHist' for i in L]

#-------------------------------------------------------------------
# NUEVO PUNTO DE HISTORIA (solo si se habilita)
#-------------------------------------------------------------------
if args.newhist:	
    #Fechas de inicio y fin 
    FechaI = args.fechai
    FechaF = args.fechaf
    #Genera el Data Frame vacio desde el inicio hasta el punto de ejecucion
    DifIndex = pnd.date_range(FechaI, FechaF, freq='5min')
    Sh = pnd.DataFrame(np.zeros((DifIndex.size, 5))*np.nan, 
        index=pnd.date_range(FechaI, FechaF, freq='5min'),
        columns = ['Tanque_'+str(i) for i in range(1,6)])
    Lold = os.listdir(args.rutaShist)
    for i in Lhist:
        #Pregunta si esta
        try:
            pos = Lold.index(i)
            flag = raw_input('Aviso: El archivo historico : '+i+' ya existe, desea sobre-escribirlo, perdera la historia de este!! (S o N): ')
            if flag == 'S':
                flag = True
            else:
                flag = False
        except:
            flag = True
        #Guardado
        if flag:
            Sh.to_msgpack(args.rutaShist + i)
            	    
#-------------------------------------------------------------------
# ACTUALIZACION DE CAUDALES 
#-------------------------------------------------------------------
#busca que este el archivo base en la carpeta 
for act, hist in zip(L, Lhist):
    try:
        #Lee el almacenamiento actual
        Sactual = pnd.read_csv(args.rutaSsim+act, header = 4, index_col = 5, parse_dates = True, usecols=(1,2,3,4,5,6))
        St = pnd.DataFrame(Sactual[Sactual.index == Sactual.index[0]].values, index=[Sactual.index[0],], 
            columns = ['Tanque_'+str(i) for i in range(1,6)])
        #Lee el historico
        Shist = pnd.read_msgpack(args.rutaShist + hist)
        # encuentra el pedazo que falta entre ambos 
        Gap = pnd.date_range(Shist.index[-1], Sactual.index[0], freq='5min')
        #Genera el pedazo con faltantes
        GapData = pnd.DataFrame(np.zeros((Gap.size - 2, 5))*np.nan, 
            index= Gap[1:-1],
            columns = ['Tanque_'+str(i) for i in range(1,6)])        
        #pega la informacion
        Shist = Shist.append(GapData)
        Shist = Shist.append(St)
        #Guarda el archivo historico 
        Shist.to_msgpack(args.rutaShist + hist)
        #Aviso
        print 'Aviso: Se ha actualizado el archivo de estados historicos: '+hist
    except:
        print 'Aviso: No se encuentra el historico de estados: '+hist+' Por lo tanto no se actualiza'
