#!/usr/bin/env python
import pandas as pd 
import datetime as dt 
import os 

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


