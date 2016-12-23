#!/usr/bin/env python
import pandas as pd 
import datetime as dt 
import os 

#-------------------------------------------------------------------
#GENERA LA FECHA ACTUAL 
#-------------------------------------------------------------------
# Obtiene el datetime 
fecha =  dt.datetime.now() + dt.timedelta(hours = 5)
hora_1 = dt.datetime.now() + dt.timedelta(hours = 5) - dt.timedelta(minutes = 5)
hora_2 = dt.datetime.now() + dt.timedelta(hours = 5)
# Lo convierte en texto 
fecha = fecha.strftime('%Y-%m-%d')
hora_1 = hora_1.strftime('%H:%M')
hora_2 = hora_2.strftime('%H:%M')

#-------------------------------------------------------------------
#TIENE LAS RUTAS DE LO QUE NECESITA  
#-------------------------------------------------------------------
#Genera las rutas 
ruta_ejec = '/home/renea998/scripts/GeneraCampos_v2.py'
ruta_cuenca = '/home/renea998/binCuencas/AMVA_base.nc'
ruta_campo = '/mnt/RADAR/CamposNicolas/Campo_AMVA_operacional3'
#Comando para ejecucion
comando = 'sudo '+ruta_ejec+' '+fecha+' '+fecha+' '+ruta_cuenca+' '+ruta_campo+' -o si -t 300 -u 0.0001 -v -s -1 '+hora_1+' -2 '+hora_2 
#Ejecuta el comando 
os.system(comando)
#print comando

