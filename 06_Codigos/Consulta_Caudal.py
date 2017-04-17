#!/usr/bin/env python
import MySQLdb
import pandas as pd
import datetime as dt
import numpy as np
import pylab as pl
import pickle
import argparse
import textwrap
import os 


#Parametros de entrada del trazador
parser=argparse.ArgumentParser(
	prog='Consulta_Caudal',
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description=textwrap.dedent('''\
	consulta la serie de caudales en una estacion especifica
        '''))
#Parametros obligatorios
parser.add_argument("fechaI",help="(YYYY-MM-DD) Fecha de inicio de imagenes")
parser.add_argument("fechaF",help="(YYYY-MM-DD) Fecha de fin de imagenes")
parser.add_argument("ruta_out",help="Ruta donde se guarda el archivo pickle con la informacion consultada")
parser.add_argument("id_est",help="Id de la estacion a consultar")
parser.add_argument("-c","--coef",help="Coeficiente para convertir nivel a caudal", type = float, default = 46.1144)
parser.add_argument("-e","--expo",help="Exponente para convertir nivel a caudal", type = float, default = 1.31)
parser.add_argument("-s","--ventana",help="toma una ventana para suavizar los datos consultados", type = float, default = 0.0)
parser.add_argument("-1","--hora_1",help="(HH:MM) Hora inicial de lectura de los archivos",default= None )
parser.add_argument("-2","--hora_2",help="(HH:MM) Hora final de lectura de los archivos",default= None )
parser.add_argument("-t","--dt",help="(Opcional) Delta de t en segundos",default = '5min')
parser.add_argument("-v","--verbose",help="Informa sobre la fecha que esta agregando", 
	action = 'store_true')


#lee todos los argumentos
args=parser.parse_args()

fechai = args.fechaI
fechaj = args.fechaF
horai = args.hora_1
horaj = args.hora_2

#Genera las fechas que son para el objeto
if horai <> None and horaj <> None:
	DatesSort = pd.date_range(fechai+' '+horai, fechaj+' '+horaj, freq = args.dt)
elif horai == None and horaj == None:
	DatesSort = pd.date_range(fechai, fechaj, freq = args.dt)
	horai = ' 00:00'
	horaj = ' 00:00'
elif horai <> None and horaj == None:
	DatesSort = pd.date_range(fechai+' '+horai, fechaj, freq = args.dt)
	horaj = ' 00:00'
elif horai == None and horaj <> None:
	DatesSort = pd.date_range(fechai, fechaj+' '+horaj, freq = args.dt)
	horai = ' 00:00'


# datos del servidos para guardar datos
host   = "192.168.1.74"
user   = "torresiata"
passwd = "TlV729phz" 
dbname = "siata"
#conecta a la base de datos
conn_db   = MySQLdb.connect (host, user, passwd, dbname)
db_cursor = conn_db.cursor ()
#sentencia de consulta para saber el offset segun estacion
sentencia_consulta = ('SELECT Codigo, longitude, latitude FROM estaciones WHERE red="nivel";')
#consulta dentro de la base de datos con la sentencia enunciada
db_cursor.execute (sentencia_consulta)
estaciones= db_cursor.fetchall ()

Estaciones="SELECT Codigo,Nombreestacion, offsetN,N red  FROM estaciones WHERE codigo=("+args.id_est+")"
db = MySQLdb.connect(host, user,passwd,dbname)
db_cursor = db.cursor()
db_cursor.execute(Estaciones)
Cod = db_cursor.fetchall()
tipo=Cod[0][3]

if tipo == 1:#ultrasonido
    niv='ni'
if tipo == 0:
    niv='pr'

sql_datos = ("SELECT fecha, hora,DATE_FORMAT(hora, '%H:%i:%s'), DATE_FORMAT(CONCAT(fecha, ' ', hora), '%Y-%m-%d %H:%i:%s'), ("+
    str(Cod[0][2]) +"-"+niv+"), calidad FROM datos WHERE cliente = ("+args.id_est+") and DATE_FORMAT(CONCAT(fecha, ' ', hora), '%Y-%m-%d %H:%i') BETWEEN '"+
    fechai+' '+horai + " " +"' and '"+fechaj +' '+horaj+"'")

db_cursor.execute (sql_datos)
pr = db_cursor.fetchall()

conn_db.close()

Data = []
DatesTime = []
Calidad = []
for i in pr:
    try:
        DatesTime.append(dt.datetime.strptime(i[3], '%Y-%m-%d %H:%M:%S'))
        Data.append(i[4])
        Calidad.append(j[-1])
        pos = np.where(Calidad <> 1)[0]
        Data[pos] = -999
    except:
        pass
Calidad = np.array(Calidad)
Data = np.array(Data)
Data[Calidad<>1] = np.nan

#Genera la serie para el rango de datos trabajado y en el delta de t requerido
Data[Data<0] = np.nan
Data[Calidad<>1] = np.nan
nivel = pd.Series(Data, pd.to_datetime(DatesTime))
Caudal = args.coef*((nivel/100)**args.expo)
Caudal = Caudal.resample(args.dt).mean()        
#Guarda en una mgran matriz
Caudal = Caudal[DatesSort]

#convierte a caudal y guarda 

if args.ventana <> 0:
	Caudal = Caudal.rolling(args.ventana).median()
Caudal.to_msgpack(args.ruta_out)
	
