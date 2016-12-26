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
	prog='Consulta Lluvia',
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description=textwrap.dedent('''\
	Consulta los registros de lluvia de las estaciones de SIATA 
	entre una fecha y hora inicio y una fecha y hora fin, a la 
	resolucion temporal designada
        '''))
#Parametros obligatorios
parser.add_argument("fechaI",help="(YYYY-MM-DD) Fecha de inicio de imagenes")
parser.add_argument("fechaF",help="(YYYY-MM-DD) Fecha de fin de imagenes")
parser.add_argument("ruta_out",help="Ruta donde se guarda el archivo pickle con la informacion consultada")
parser.add_argument("-1","--hora_1",help="Hora inicial de lectura de los archivos",default= None )
parser.add_argument("-2","--hora_2",help="Hora final de lectura de los archivos",default= None )
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
elif horai <> None and horaj == None:
	DatesSort = pd.date_range(fechai+' '+horai, fechaj, freq = args.dt)
elif horai == None and horaj <> None:
	DatesSort = pd.date_range(fechai, fechaj+' '+horaj, freq = args.dt)


# datos del servidos para guardar datos
host   = "192.168.1.74"
user   = "torresiata"
passwd = "TlV729phz" 
dbname = "siata"
#conecta a la base de datos
conn_db   = MySQLdb.connect (host, user, passwd, dbname)
db_cursor = conn_db.cursor ()
#sentencia de consulta para saber el offset segun estacion
sentencia_consulta = ('SELECT Codigo, longitude, latitude FROM estaciones WHERE red="pluviografica";')
#consulta dentro de la base de datos con la sentencia enunciada
db_cursor.execute (sentencia_consulta)
estaciones= db_cursor.fetchall ()

#Variables de llenado con informacion final
DataFin = []
Columnas = []
Coord = []
#sentencia de consulta lluvia
for i in range(len(estaciones)):
	if args.verbose:
		print 'Consulta estacion: '+ estaciones[i][0] + '\n'
		print 'Progreso: '+str((float(i)/len(estaciones))*100.0)+'\n' 
    #Trata de consultar cada una de las estaciones
	try:
		#Sentencia de consulta
		sentencia_pr = ("SELECT fecha, hora, P1, P2, calidad FROM datos WHERE cliente= '"+estaciones[i][0]+
			"' AND fecha BETWEEN '"+fechai+"' AND '"+fechaj+"' ORDER BY fecha, hora;")
		#consulta
		db_cursor.execute (sentencia_pr)
		pr = db_cursor.fetchall()
		#Cuadra la informacion        
		Dates = []; pr_corr = []
		for j in pr:
		    try:
		        Dates.append(dt.datetime.combine(j[0], dt.time(0)))
		        pr_corr.append(j)
		    except:
		        pass
		DatesTime = [j + k[1] for j,k in zip(Dates, pr_corr)]
		Data = np.array([j[3] for j in pr_corr])
		Calidad = np.array([j[-1] for j in pr_corr])
		pos = np.where(Calidad <> 1)[0]
		Data[pos] = -999
		#Genera la serie para el rango de datos trabajado y en el delta de t requerido
		Rain = pd.Series(Data, pd.to_datetime(DatesTime))
		Rain = Rain.resample('5min').sum()        
		#Guarda en una mgran matriz
		DataFin.append(Rain[DatesSort].values)
		#Queda con la columna 
		Columnas.append(estaciones[i][0])
		Coord.append([float(estaciones[i][1]), float(estaciones[i][2])])
	except Exception, e:
		print repr(e)	
#cerrar la base de datos para evitar generar conexiones que duren cuatro horas abiertas
conn_db.close ()

#Proceso final a la informacion
DataFin = np.array(DataFin) 
DataFin[DataFin <0] = np.nan
DataFin = DataFin / 1000.0
DataFrame = pd.DataFrame(DataFin.T, index=DatesSort, columns=Columnas)
DataFrame[np.isnan(DataFrame)] = -999
#Proceso de las coordenadas
Coord = np.array(Coord).T

#Guardado de la consulta
f = open(args.ruta_out, 'w')
pickle.dump(DataFrame, f)
pickle.dump(Coord, f)
f.close()

print 'Consulta Finzalizada Satisfactoriamente'
