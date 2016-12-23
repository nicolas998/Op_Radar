#!/usr/bin/env python

import os
import datetime as dt
import pandas as pd
from multiprocessing import Pool
import numpy as np

#-------------------------------------------------------------------
#FUNBCIONES LOCALES
#-------------------------------------------------------------------


ruta_qsim = '/home/renea998/Simulaciones/extrapolated/'
ruta_ejec = '/home/renea998/scripts/Figuras_Qsim.py'
ruta_Figuras = '/home/renea998/FigExtrapolaciones/'
servidor = 'torresiata@siata.gov.co:/var/www/nicolas/FigExtrapolated/'

#-------------------------------------------------------------------
#GENERA LAS LISTAS DE LOS COMANDOS DE CREAR FIGURA Y ENVIAR FIGURA 
#-------------------------------------------------------------------

Lista = range(1,291)
ListaSelect = np.random.choice(Lista,50)
ListaSelect = ListaSelect.tolist()
ListaSelect.insert(0,1)
Lc1 = []
for i in ListaSelect:
	Lc1.append( ruta_ejec+' '+ruta_qsim+' '+str(i)+' '+ruta_Figuras+'Qsim_nodo_'+str(i)+'.png')


for i in Lc1:
	os.system(i)
#-------------------------------------------------------------------
#EJECUTA LOS COMANDO EN PARALELO
#-------------------------------------------------------------------
#try:
#	p = Pool(processes = 10)
#	p.map(os.system, Lc1)
#finally:
#	p.close()
#	p.join()


comando = 'scp '+ruta_Figuras+'Qsim_nodo_*.png '+servidor
os.system(comando)
