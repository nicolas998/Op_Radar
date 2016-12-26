#!/usr/bin/env python
import pandas as pd 
import datetime as dt 
import os 
from multiprocessing import Pool


#-------------------------------------------------------------------
#RUTAS DE TRABAJO
#-------------------------------------------------------------------
rutaCodigo = '/home/nicolas/Operacional/Op_Interpolated/06_Codigos/Interpola_Campos.py'
rutaCuenca = '/home/nicolas/Operacional/Op_Interpolated/01_Bin_Cuencas/Cuenca_AMVA_Barbosa_C.nc'
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



