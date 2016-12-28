#!/usr/bin/env python

import numpy as np
import os
import datetime as dt
import pandas as pd
import pickle 
from multiprocessing import Pool


#Lectura de cuadales simulados 
def LeeQsim(ruta):
	f = open(ruta,'rb')
	Q = pickle.load(f)
	S = pickle.load(f)
	f.close()
	return Q,S

def writeQsim(ruta,Q,S):
	f = open(ruta,'wb')
        pickle.dump(Q,f)
        pickle.dump(S,f)
        f.close()

rutaEjec = '/home/nicolas/Operacional/Op_Interpolated/06_Codigos/Ejecuta_Modelo_v3.py'
rutaOper = '/home/nicolas/Operacional/Op_Interpolated/'
rutaCampos = '/home/nicolas/Operacional/Op_Interpolated/03_Simulaciones/01_Rain/CampoIDW_'
rutaStorage = '/home/nicolas/Operacional/Op_Interpolated/04_Almacenamiento/'
rutaQsim = '/home/nicolas/Operacional/Op_Interpolated/03_Simulaciones/'

#-------------------------------------------------------------------
#Ejecuta para todos los escenarios
#-------------------------------------------------------------------
Lista = []
for escena in ['bajo', 'alto']:
	Lista.append(rutaEjec+' '+rutaOper+' '+rutaCampos+escena+'.bin '+rutaStorage+' '+rutaQsim)
Lista.append(rutaEjec+' '+rutaOper+' '+rutaCampos+'normal.bin '+rutaStorage+' '+rutaQsim+' -s')

#Ejecucion
P = Pool(processes = 3)
r = P.map(os.system, Lista)
