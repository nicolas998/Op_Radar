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
def Multiprocess_Warper(Lista):
	return cu.run_shia(Lista[0],Lista[1],Lista[2],Lista[3])
#Lectura calibraciones 
def Read_Calib(Proy):
    for k in Proy.keys():
        if 'calibFile' in Proy[k]:            
            #Lee las calibraciones dentro del archivo
            Calib = np.loadtxt(Proy[k]['calibFile'], skiprows=13, dtype=str)
            #Les los IDs de las calibraciones 
            CalibDict = {}
            for i in Calib:
                CalibDict.update({i[0]:[float(j) for j in i[1:]]})
            #Actualiza el diccionario le incluye las calibraciones
            Proy[k].update({'calibValues':CalibDict})
        else:
            Proy[k].update({'calibValues': None})

#-------------------------------------------------------------------
#PARSEADOR DE ARGUMENTOS  
#-------------------------------------------------------------------
#Parametros de entrada del trazador
parser=argparse.ArgumentParser(
        prog='Ejecuta_Modelo',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
	Script que se encarga de ejecutar el modelo hidrologico, para ello requiere:
	La cuenca a ejecutar, el binario con el campo de lluvia, el punto de inicio 
	la cantidad de pasos y el llugar de salida para guardar resultados
        '''))
#Parametros obligatorios
parser.add_argument("rutaABS",help="(Obligatorio) Ruta absoluta para buscar en el proyecto operacional donde buscar las cosas .nc")
parser.add_argument("rutaCampo",help="(Obligatorio) Ruta donde se cuentra el binario con el campo de lluvia (.bin)")
parser.add_argument("rutaStore",help="(Obligatorio) Ruta donde se guardan las condiciones de almacenamiento de la cuenca")
parser.add_argument("-v","--verbose",help="(Opcional) Hace que el modelo indique en que porcentaje de ejecucion va",
        action = 'store_true', default = False)

args=parser.parse_args()

#-------------------------------------------------------------------
#RUTAS Y CONFIGURACION DE LOS PROYECTOS 
#-------------------------------------------------------------------
Proyectos = {}
ruta = args.rutaABS+'01_Bin_Cuencas/'
#Proyectos de cuenca
L = os.listdir(ruta)
for i in L:
    try:
        a = int(i[-6:-3])
        Proyectos.update({i[-6:-3]: {'cuenca':ruta + i}})
        #Proyectos['ID'].update({i[-6:-3]:i})
    except:
        pass
#Archivos de calibracion
ruta = args.rutaABS+'02_Calibraciones/'
L = os.listdir(ruta)
for i in L:
    try:        
        a = int(i[-9:-6])
        pos = Proyectos.keys().index(i[-9:-6])
        Proyectos[i[-9:-6]].update({'calibFile': ruta + i})
    except:
        pass
Read_Calib(Proyectos)
#Almacenamientos Viejos
ruta = args.rutaABS+'04_Almacenamiento/'
L = os.listdir(ruta)
L2 = [i[-14:] for i in L]
for k in Proyectos.keys():
    #Crea la entrada en el diccionario
    Proyectos[k].update({'storeFile':{}})
    #Crea el elemento de comparacion
    if Proyectos[k]['calibValues']<>None:
        for k2 in Proyectos[k]['calibValues']:
            Elem = k+'_'+k2+'.StObin'
            try:
                pos = L2.index(Elem)
                Proyectos[k]['storeFile'].update({k2: ruta+L[pos]})
            except:
                pass
#-------------------------------------------------------------------
#Ejecucion proyectos
#-------------------------------------------------------------------
#Caudales 
wmf.models.show_storage = 1
wmf.models.separate_fluxes = 1
wmf.models.dt = 300
Caudales = {}
Rain = wmf.read_mean_rain(args.rutaCampo[:-4]+'.hdr', 13, 0)
#Ejecucion del modelo
for k in Proyectos:
    # Se fija que el proyecto tenga calibracion
    if Proyectos[k]['calibValues'] <> None:
        #Si si, comienza a cargar las cosas para la ejecuicion
        cu = wmf.SimuBasin(0,0,0,0, rute=Proyectos[k]['cuenca'])
        Caudales.update({k:{}})
        posControl = wmf.models.control[wmf.models.control<>0]
        #Itera para cada almacenamiento
        for k2 in Proyectos[k]['calibValues'].keys():
            #Obtiene la calibracion
            Calib = Proyectos[k]['calibValues'][k2]
            #Obtiene el almacenamiento 
            try:
                #Mira si hay almacenamiento para esa calibracion
                p = Proyectos[k]['storeFile'].keys().index(k2)
                # obtiene las rutas del binario y del encabezado de almacenamiento 
                ruta_sto_bin, ruta_sto_hdr = wmf.__Add_hdr_bin_2route__(Proyectos[k]['storeFile'][k2],
                    storage = True)
                # Carga las condiciones en la cuenca
                cu.set_Storage(ruta_sto_bin,0)
                #Corre la cuenca 
                Results = cu.run_shia(Calib, args.rutaCampo, 13, 1,
                    ruta_storage = Proyectos[k]['storeFile'][k2],
                    kinematicN = 7)
                print 'Aviso: El proyecto '+k+' corrio con la calibracion: '+k2 
            except:
                print 'Aviso: El proyecto '+k+' en la calibracion '+k2+' no cuenta con almacenamiento, se establece alm inicial en 0.0'
                #corre y guarda condiciones al 
                for i in range(5):
                    cu.set_Storage(0,i)
                Results = cu.run_shia(Calib, args.rutaCampo, 13, 1,
                    ruta_storage = args.rutaStore + 'Cuen999_'+k+'_'+k2,
                    kinematicN = 7)
            
            #Copia caudales             
            Qsim = pnd.DataFrame(Results['Qsim'][1:].T,
                index=Rain.index,
                columns=posControl)
            Caudales[k].update({k2:Qsim})
    else:
        print 'Error: El proyecto '+k+' no cuenta con ningun tipo de calibracion'

#-------------------------------------------------------------------
#Guarda los caudales 
#-------------------------------------------------------------------
	
