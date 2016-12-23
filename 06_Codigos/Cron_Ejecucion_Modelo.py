#!/usr/bin/env python

import numpy as np
import os
import datetime as dt
import pandas as pd
import pickle 

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


ruta_ejec = '/home/renea998/scripts/Ejecuta_Modelo_v2.py'
ruta_cuenca = '/home/renea998/binCuencas/cuencaAMVA_v01.nc'
ruta_cuenca_temp = '/home/renea998/binCuencas/cuencaAMVA_temp'
ruta_campo_bin = '/mnt/RADAR/CamposNicolas/Campo_AMVA_operacional3.bin'
ruta_campo_hdr = '/mnt/RADAR/CamposNicolas/Campo_AMVA_operacional3.hdr'
ruta_campo_ext_bin = '/mnt/RADAR/CamposNicolas/Campo_AMVA_extrapolated.bin'
ruta_campo_ext_hdr = '/mnt/RADAR/CamposNicolas/Campo_AMVA_extrapolated.hdr'
ruta_calibracion = '/home/renea998/Calibraciones/AMVA_01.calib'
ruta_simulacion = '/home/renea998/Simulaciones/ultimaHora/'
ruta_historico = '/home/renea998/Simulaciones/'
ruta_qsim = '/home/renea998/Simulaciones/ultimaHora/Qsim_'
ruta_qsim_extra = '/home/renea998/Simulaciones/extrapolated/Qsim_ext_'

#-------------------------------------------------------------------
#OBTIENE LOS REGISTROS DE LAS ULTIMAS 24 HORAS
#-------------------------------------------------------------------
#Obtiene las posiciones de las ultimas 24 horas
os.system('tail /mnt/RADAR/CamposNicolas/Campo_AMVA_operacional3.hdr -n 1 > /home/renea998/temporal.txt')
f = open('/home/renea998/temporal.txt','r')
Lista = f.readlines()
f.close()
#obtiene posicion y cantidad de iteraciones
Inicio = int(Lista[0].split(',')[0]) - 1
print Inicio

#-------------------------------------------------------------------
#Ejecuta
#-------------------------------------------------------------------
#Ejecuta un solo intervlao para actualizar condiciones 
Comando = ruta_ejec+' '+ruta_cuenca+' '+ruta_campo_bin+' '+str(Inicio)+' 1 '+ruta_calibracion+' '+ruta_qsim+' -t 300 -u 0 -s'
os.system(Comando)
print Comando
print 'Ejecuta ultimos 5min'

#-------------------------------------------------------------------
# ACTUALIZA CAUDALES SIMULADOS E HISTORICOS 
#-------------------------------------------------------------------
#Lista caudales 
Lactual = os.listdir(ruta_simulacion)
Lactual = [i for i in Lactual if i.endswith('qsim')]
Lactual.sort()
Lhisto = os.listdir(ruta_historico)
Lhisto = [i for i in Lhisto if i.endswith('qsim')]
Lhisto.sort()
#Actualiza los caudales historicos 
for a,h in zip(Lactual, Lhisto):
	#Lectura de historicos
	Qhist,Shist = LeeQsim(ruta_historico+h)
	Qact,Sact = LeeQsim(ruta_simulacion+a)
	#Acopla actual con historico
	Q = np.vstack([Qhist.values,Qact.values]).T
	S = np.hstack([Shist.values.T,Sact.values.T])
	DatesAct = Qact.index
	DatesHist = Qhist.index
	DatesHist = DatesHist.append(DatesAct)
	QDataFrame = pd.DataFrame(Q[:,1:].T,index = DatesHist[1:],columns = Qhist.columns)
	SSeries = pd.Series(S[1:],index = DatesHist[1:])
	#Guarda el resultado
	writeQsim(ruta_historico+h,QDataFrame,SSeries)


#Ejecuta la prediccion
Comando = ruta_ejec+' '+ruta_cuenca+' '+ruta_campo_ext_bin+' 1 23  '+ruta_calibracion+' '+ruta_qsim_extra+' -t 300 -u 0'
#print Comando
os.system(Comando)
#print 'Ejecuto extrapolacion'
