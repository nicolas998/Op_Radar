#!/usr/bin/env python
import pandas as pd 
import datetime as dt 
import os 
from multiprocessing import Pool
import numpy as np
import pickle 

# Texto Fecha: el texto de fecha que se usa para guardar algunos archivos de figuras.
dateText = dt.datetime.now().strftime('%Y%m%d%H%M')


#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
print '###################################################### CONSULTA DE LA LLUVIA Y EXTRAPOLACION #######################################'

#-------------------------------------------------------------------
#GENERA LA FECHA ACTUAL 
#-------------------------------------------------------------------
# Obtiene el datetime 
fecha_1 =  dt.datetime.now() + dt.timedelta(hours = 5) - dt.timedelta(minutes = 5)
fecha_2 =  dt.datetime.now() + dt.timedelta(hours = 5) 
# Lo convierte en texto 
fecha1 = fecha_1.strftime('%Y-%m-%d')
fecha2 = fecha_2.strftime('%Y-%m-%d')
hora_1 = fecha_1.strftime('%H:%M')
hora_2 = fecha_2.strftime('%H:%M')

#-------------------------------------------------------------------
#RUTAS DE TRABAJO
#-------------------------------------------------------------------
rutaCodigo = '/home/nicolas/Operacional/Op_Radar/06_Codigos/GeneraCampos_Radar.py'
#rutaCuenca = '/home/nicolas/Operacional/Op_Radar/01_Bin_Cuencas/Cuenca_AMVA_Barbosa_001.nc'
rutaCuenca = '/home/nicolas/Operacional/Op_Radar/01_Bin_Cuencas/Barbosa_Slides_001.nc'
rutaBinario = '/home/nicolas/Operacional/Op_Radar/03_Simulaciones/01_Rain/CampoRain'
rutaRadar = '/media/nicolas/Radar/'

#-------------------------------------------------------------------
#Campo de lluvia en los ultimos 5min
#-------------------------------------------------------------------
comando = rutaCodigo+' '+fecha1+' '+fecha2+' '+rutaCuenca+' '+rutaBinario+' '+rutaRadar+' -1 '+hora_1+' -2 '+hora_2

#print comando
os.system(comando)
print '01. Campo de lluvia actual actualizado '

#-------------------------------------------------------------------
#Campo de lluvia extrapolado
#-------------------------------------------------------------------
rutaCodigo = '/home/nicolas/Operacional/Op_Radar/06_Codigos/GeneraCampos_Extrapol.py'
rutaHeader = '/home/nicolas/Operacional/Op_Radar/03_Simulaciones/01_Rain/CampoRain_media.hdr'
rutaExtrapol = '/media/nicolas/Extrapol/'

comando = rutaCodigo+' '+rutaCuenca+' '+rutaBinario+' '+rutaHeader+' '+rutaExtrapol
os.system(comando)
print '02. Campo extrapolado agregado al campo actual de lluvia de la cuenca.'

##||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
##||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
##||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
##||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
print '\n'
print '###################################################### EJECUCION DEL MODELO ########################################################'

rutaEjec = '/home/nicolas/Operacional/Op_Radar/06_Codigos/Ejecuta_Modelo_Radar.py'
rutaOper = '/home/nicolas/Operacional/Op_Radar/'
rutaCampos = '/home/nicolas/Operacional/Op_Radar/03_Simulaciones/01_Rain/CampoRain_'
rutaStorage = '/home/nicolas/Operacional/Op_Radar/04_Almacenamiento/'
rutaQsim = '/home/nicolas/Operacional/Op_Radar/03_Simulaciones/'
rutaSlides = '/home/nicolas/Operacional/Op_Radar/03_Simulaciones/04_SlidesSim/'

#-------------------------------------------------------------------
#Ejecuta para todos los escenarios
#-------------------------------------------------------------------
Lista = []
for escena in ['baja', 'alta']:
	Lista.append(rutaEjec+' '+rutaOper+' '+rutaCampos+escena+'.bin '+rutaStorage+' '+rutaQsim+' '+rutaSlides)
Lista.append(rutaEjec+' '+rutaOper+' '+rutaCampos+'media.bin '+rutaStorage+' '+rutaQsim+' '+rutaSlides+' -s')
#Ejecucion
P = Pool(processes = 3)
r = P.map(os.system, Lista)
print '------------------------------------------'
print '03. Modelo Ejecutado'
print '\n'


#-------------------------------------------------------------------
#Actualiza caudales historicos simulados 
#-------------------------------------------------------------------
#Rutas de ejecucion
rutaEjec = '/home/nicolas/Operacional/Op_Radar/06_Codigos/Actualiza_Caudales_Hist.py'
rutaQhist = '/home/nicolas/Operacional/Op_Radar/03_Simulaciones/02_Stream_History/'
rutaQsim = '/home/nicolas/Operacional/Op_Radar/03_Simulaciones/'
#Ejecucion 
comando = rutaEjec+' '+rutaQhist+' '+rutaQsim
os.system(comando) 
print '04. Caudales historicos guardados'
print '\n'


#-------------------------------------------------------------------
#Actualiza lluvia
#-------------------------------------------------------------------
#Ruta ejecucion 
rutaEjec = '/home/nicolas/Operacional/Op_Radar/06_Codigos/Actualiza_MeanRain_Hist.py'
rutaRain = '/home/nicolas/Operacional/Op_Radar/03_Simulaciones/01_Rain/'
#Ejecucion
comando = rutaEjec+' '+rutaRain 
os.system(comando)

#-------------------------------------------------------------------
#Actualiza Estados de almacenamiento del modelo historicos
#-------------------------------------------------------------------
#Ruta ejecucion 
rutaEjec = '/home/nicolas/Operacional/Op_Interpolated/06_Codigos/Actualiza_MeanStorage_Hist.py'
rutaStorage = '/home/nicolas/Operacional/Op_Radar/04_Almacenamiento/'
rutaStorageH = '/home/nicolas/Operacional/Op_Radar/04_Almacenamiento/02_Storage_History/'
print '------------------------------------------'
#Ejecucion
comando = rutaEjec+' '+rutaStorageH+' '+rutaStorage
os.system(comando)


#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
print '###################################################### Actualizacion Caudales ########################################################'

#-------------------------------------------------------------------
#Actualiza json
#-------------------------------------------------------------------
#Rutas
rutaEjec = '/home/nicolas/Operacional/Op_Radar/06_Codigos/Genera_json.py'
rutaParam = '/home/nicolas/Operacional/Op_Radar/03_Simulaciones/Qsim_001_002'
rutaHist = '/home/nicolas/Operacional/Op_Radar/03_Simulaciones/02_Stream_History/Qsim_001_002'
rutaJson = '/media/nicolas/discoGrande/01_SIATA/ResultadosOperacion/Ope_Barbosa_Radar/json/Caudales_Simulados.json'

#Ejecucion
comando = rutaEjec+' '+rutaParam+' '+rutaHist+' '+rutaJson
os.system(comando)
print 'Json Actualizado con caudales simulados de ultimo intervalo'


#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
print '###################################################### Figuras de mapas que siempre salen ########################################################'

#Descripcion:
#-------------------------------------------------------------------
# Grafica cada 5 min la humedad en toda la cuenca. Se utiliza llamando a Genera_Mapa_Humedad.py
# este apartado necesita de la cuenca.nc y de un archivo de almacenamiento.StObin, ese debe ser 
# seleccionado por el usuario de acuerdo a lo que este considere (la calibracion mas adecuada)
# Finalmente se debe elegir donde se aloja la figura y el archivo de texto con las coordenadas.

#Rutas
rutaCuenca = '/home/nicolas/Operacional/Op_Radar/01_Bin_Cuencas/Barbosa_Slides_001.nc'
rutaEjec = '/home/nicolas/Operacional/Op_Radar/06_Codigos/Genera_Mapa_Humedad.py'
rutaFolder = '/media/nicolas/discoGrande/01_SIATA/ResultadosOperacion/Ope_Barbosa_Radar/humedad/'
rutaRes = rutaFolder + dateText + '_hu.png'
rutaStorage = '/home/nicolas/Operacional/Op_Radar/04_Almacenamiento/CuBarbosa_001_002.StObin'

#comando de ejecucion
comando = rutaEjec+' '+rutaCuenca+' '+rutaStorage+' '+rutaRes+' -1 0 -2 0.8'
os.system(comando)
print 'Se ha escrito el mapa de humeda en:' + rutaRes
#Copia el ultimo archivo de humedad para que sea el que se muestra por defecto en la pagina 
comando = 'cp '+rutaRes+' /media/nicolas/discoGrande/01_SIATA/ResultadosOperacion/Ope_Barbosa_Radar/humedad/MapaHumedad.png'
os.system(comando)
print 'Mapa humedad '+dateText+'_hu.png se ha copiado a MapaHumedad.png' 
##Borra los archivos que tengan mas de 24 horas de viejos.
Lista = os.listdir(rutaFolder)
Lista = [i for i in Lista if i.endswith('_hu.png')]
Lista.sort()
Lista2 = Lista[:-288]
if len(Lista2)>0:
	comando  = ['rm '+rutaFolder+i for i in Lista2]
	map(os.system, comando)
	print 'Se han borrado mapas con antiguedad mayor a 24 horas'

#Descripcion:
#-------------------------------------------------------------------
# Grafica cada 5 min un estimado de la cantidad de agua que fluye por cada una de las vertientes 
# de la cuenca

#Rutas
rutaCuenca = '/home/nicolas/Operacional/Op_Radar/01_Bin_Cuencas/Barbosa_Slides_001.nc'
rutaEjec = '/home/nicolas/Operacional/Op_Radar/06_Codigos/Genera_Mapa_Caudal.py'
rutaFolder = '/media/nicolas/discoGrande/01_SIATA/ResultadosOperacion/Ope_Barbosa_Radar/mapQsim/'
rutaRes = rutaFolder + dateText + '_Qsim.png'
rutaStorage = '/home/nicolas/Operacional/Op_Radar/04_Almacenamiento/CuBarbosa_001_002.StObin'

##comando de ejecucion
comando = rutaEjec+' '+rutaCuenca+' '+rutaStorage+' '+rutaRes
os.system(comando)
print 'Se ha escrito el mapa de caudales en:' + rutaRes
##Copia el ultimo archivo de humedad para que sea el que se muestra por defecto en la pagina 
comando = 'cp '+rutaRes+' /media/nicolas/discoGrande/01_SIATA/ResultadosOperacion/Ope_Barbosa_Radar/mapQsim/RedQsim.png'
os.system(comando)
print 'Mapa Red hidrica simulada '+dateText+'_Qsim.png se ha copiado a RedQsim.png' 
#Borra los archivos que tengan mas de 24 horas de viejos.
Lista = os.listdir(rutaFolder)
Lista = [i for i in Lista if i.endswith('_Qsim.png')]
Lista.sort()
Lista2 = Lista[:-288]
if len(Lista2)>0:
	comando  = ['rm '+rutaFolder+i for i in Lista2]
	map(os.system, comando)
	print 'Se han borrado mapas con antiguedad mayor a 24 horas'
