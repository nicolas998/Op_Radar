#!/usr/bin/env python
from wmf import wmf 
import numpy as np 
import pickle 
import pandas as pnd
import pylab as pl
import argparse
import textwrap
import os
from multiprocessing import Pool

#-------------------------------------------------------------------
#FUNBCIONES LOCALES
#-------------------------------------------------------------------
def Multiprocess_Warper(Lista):
	return cu.run_shia(Lista[0],Lista[1],Lista[2],Lista[3])
def ReadQsimPickle(ruta,nodo):
	f = open(ruta,'rb')
	Q = pickle.load(f)
	S = pickle.load(f)
	f.close()
	return Q[nodo].values,S

#-------------------------------------------------------------------
#PARSEADOR DE ARGUMENTOS  
#-------------------------------------------------------------------
#Parametros de entrada del trazador
parser=argparse.ArgumentParser(
        prog='Figuras_Qsim',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
        Script hecho para generar figuras de las simulaciones realizadas por 
	el modelo, el escript toma la lista de caudales simulados y para 
	cada nodo saca el caudal obtenido 
	'''))
#Parametros obligatorios
parser.add_argument("dir_qsim", help="(Obligatorio) Directorio con caudales simulados")
parser.add_argument("nodo",help="(Obligatorio) Nodo sobre el cual se realizara la figura",type = int)
parser.add_argument("ruta",help="(Obligatorio) Ruta donde se escribe la figura")
parser.add_argument("-c","--observada",help="(Opcional) ID de la estacion observada",type=int)

args=parser.parse_args()

#-------------------------------------------------------------------
#Lista los caudales simulados en la zona  
#-------------------------------------------------------------------
#Lista los archivos de simulacion presentes 
L = os.listdir(args.dir_qsim)
L = [l for l in L if l.endswith('qsim')]
#Trata de leer los caudales 
nombres = []
CaudalesSim = []
for l in L:
	#try:
	Q,s = ReadQsimPickle(args.dir_qsim+l,args.nodo)
	CaudalesSim.append(Q.tolist())
	nombres.append(l[:-4])
	#except:
	#	pass
CaudalesSim = np.array(CaudalesSim)

#-------------------------------------------------------------------
#Si hay una serie de caudales observada la lee 
#-------------------------------------------------------------------
if args.observada:
	print 'hola'

#-------------------------------------------------------------------
#Genera la figura para ese periodo
#-------------------------------------------------------------------
if args.observada:
	wmf.plot_sim_single(CaudalesSim, mrain = s.values,
		Dates = s.index.to_pydatetime(),
		ruta = args.ruta,
		Qo = CaudalObservado)
else:
        wmf.plot_sim_single(CaudalesSim, mrain = s.values,
                Dates = s.index.to_pydatetime(),
                ruta = args.ruta,
		legend = False)

