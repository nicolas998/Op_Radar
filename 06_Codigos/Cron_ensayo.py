#!/usr/bin/env python
import pandas as pd 
import datetime as dt 
import os 
from multiprocessing import Pool
import numpy as np
import pickle 

#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
print '###################################################### CONSULTA DE LA LLUVIA Y EXTRAPOLACION #######################################'

#-------------------------------------------------------------------
#GENERA LA FECHA ACTUAL 
#-------------------------------------------------------------------
# Obtiene el datetime 
fecha_1 =  dt.datetime.now() - dt.timedelta(hours = 12)
fecha_2 =  dt.datetime.now()
# Lo convierte en texto 
fecha1 = fecha_1.strftime('%Y-%m-%d')
fecha2 = fecha_2.strftime('%Y-%m-%d')
hora_1 = fecha_1.strftime('%H:%M')
hora_2 = fecha_2.strftime('%H:%M')

#-------------------------------------------------------------------
#RUTAS DE TRABAJO
#-------------------------------------------------------------------
rutaCodigo = '/home/nicolas/Operacional/Op_Interpolated/06_Codigos/'
rutaBinario = '/home/nicolas/Operacional/Op_Interpolated/03_Simulaciones/01_Rain/ConsultaRain'

#-------------------------------------------------------------------
#Consulta la lluvia en las ultimas 12 horas de lluvia 
#-------------------------------------------------------------------
comando = rutaCodigo+'Consulta_Lluvia.py '+fecha1+' '+fecha2+' '+rutaBinario+' -t 5min -1 '+hora_1+' -2 '+hora_2
os.system(comando)



#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
print '###################################################### INTERPOLACION DE LA LLUVIA ########################################################'

#-------------------------------------------------------------------
#RUTAS DE TRABAJO
#-------------------------------------------------------------------
rutaCodigo = '/home/nicolas/Operacional/Op_Interpolated/06_Codigos/Interpola_Campos.py'
rutaCuenca = '/home/nicolas/Operacional/Op_Interpolated/01_Bin_Cuencas/Cuenca_AMVA_Barbosa_001.nc'
rutaRain = '/home/nicolas/Operacional/Op_Interpolated/03_Simulaciones/01_Rain/ConsultaRain_cast'
rutaCampo = '/home/nicolas/Operacional/Op_Interpolated/03_Simulaciones/01_Rain/CampoIDW_'

#-------------------------------------------------------------------
#Consulta la lluvia en las ultimas 12 horas de lluvia 
#-------------------------------------------------------------------
Lista = []
for k in ['normal', 'bajo', 'alto']:
	comando = rutaCodigo+' '+rutaRain+'_'+k+'.rain '+rutaCuenca+' '+rutaCampo+k+'.bin'
	Lista.append(comando)
print Lista
P = Pool(processes = 3)
r = P.map(os.system, Lista)

#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
print '###################################################### EJECUCION DEL MODELO ########################################################'

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

#-------------------------------------------------------------------
#Actualiza caudales historicos simulados 
#-------------------------------------------------------------------
#Rutas de ejecucion
rutaEjec = '/home/nicolas/Operacional/Op_Interpolated/06_Codigos/Actualiza_Caudales_Hist.py'
rutaQhist = '/home/nicolas/Operacional/Op_Interpolated/03_Simulaciones/02_Stream_History/'
rutaQsim = '/home/nicolas/Operacional/Op_Interpolated/03_Simulaciones/'
#Ejecucion 
comando = rutaEjec+' '+rutaQhist+' '+rutaQsim
os.system(comando) 

#-------------------------------------------------------------------
#Actualiza lluvia
#-------------------------------------------------------------------



#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
print '###################################################### GRAFICAS DEL MODELO ########################################################'


#-------------------------------------------------------------------
#Serie de tiempod e caudales simulados 
#-------------------------------------------------------------------


#-------------------------------------------------------------------
#Mapa de caudales simulados 
#-------------------------------------------------------------------


#-------------------------------------------------------------------
#Mapa de humedad en la cuenca
#-------------------------------------------------------------------
