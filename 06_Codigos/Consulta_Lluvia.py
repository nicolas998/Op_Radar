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

#Funbcion de prediccion de lluvia
def Genera_Prediccion(Percent, umbral = 0.05, bandas = False):
    #Define la variable con la prediccion de lluvia y el contador
    Precip = np.zeros(Percent.shape[1])
    cont = 0
    #Itera para todos los intervalos futuros hasta llegar a una hora.
    for Pe in Percent.T:
        #Histograma
        d = np.random.uniform(Pe.min(),Pe.max(),100)
        h,b = np.histogram(d, bins=np.unique(Pe))
        #Vector con datos ponderados     
        LongVect = np.zeros(100)
        c = 0
        for i,b1,b2 in zip(h,b[:-1],b[1:]):
            for z in range(i):
                LongVect[c] = (b1 + b2)/2.0
                c += 1
        #Eleccion de la precipitacion en el intervalo (Luego se le debe hacer una correccion de magnitud)
        Precip[cont] = np.random.choice(LongVect)
        cont += 1
        if Precip[cont-1] < umbral:
            Precip[cont:] = 0.0
            break
    if bandas:
        PrecipBandas = np.zeros((3,Precip.shape[0]))
        PrecipBandas[0] = Precip-Precip*np.random.uniform(0,1.0,1)
        PrecipBandas[-1] = Precip+Precip*np.random.uniform(0,1.5,1)
        PrecipBandas[1] = Precip
        return PrecipBandas
    return Precip

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
parser.add_argument("-b","--umbral_b",help="Umbral para hacer que la lluvia se haga cero para los casos de bajo acumulado",
	default= 0.3, type = float )
parser.add_argument("-a","--umbral_a",help="Umbral para hacer que la lluvia se haga cero para los casos de alto acumulado",
	default= 0.1, type = float)

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
#f = open(args.ruta_out, 'w')
#pickle.dump(DataFrame, f)
#pickle.dump(Coord, f)
#f.close()

print 'Consulta Finzalizada Satisfactoriamente'

#-------------------------------------------------------------------
#Genera la lluvia futura 
#-------------------------------------------------------------------
#Lectura de reglas 
f = open('/home/nicolas/Operacional/Op_Interpolated/03_Simulaciones/01_Rain/ReglasGeneracion.bin','r')
ReglasDict = pickle.load(f)
IntervalosDict = pickle.load(f)
f.close()
#generacion de la lluvia
umbralAlto = args.umbral_a
umbralBajo = args.umbral_b
DataFrame[DataFrame<0] = 0
Rain24h = DataFrame	
Predicciones = {'normal':{}, 'bajo':{}, 'alto':{}}
for k in Rain24h.keys():
    R = np.copy(Rain24h[k])[::-1]
    #mira si tiene registro diferente de cero 
    if R[0]>0:
        #Si no es cero, pregunta por el acumulado
        cont = 1
        acum = R[0]
        while R[cont]<>0 and cont<=10:
            acum+=R[cont]
            cont+=1
        if cont>10: cont = 10
        #Sale de acumular y genera la prediccion de acuerdo al acumulado
        if acum <= IntervalosDict[cont][1]:
            Pred = Genera_Prediccion(ReglasDict['bajo'][cont], umbral = umbralBajo, bandas = False)
            for k2 in Predicciones.keys():
                Predicciones[k2].update({k:Pred})
        elif acum > IntervalosDict[cont][1]:
            Pred = Genera_Prediccion(ReglasDict['alto'][cont], umbral = umbralAlto, bandas = True)
            Predicciones['bajo'].update({k:Pred[0]})
            Predicciones['normal'].update({k:Pred[1]})
            Predicciones['alto'].update({k:Pred[2]})
    else:
        #si no lo tiene coloca cero en los proximos 12 intervalos de 5 min
        Pred = np.zeros(12)
        for k2 in Predicciones.keys():
            Predicciones[k2].update({k:Pred})

print 'Genera prediccions sin problema \n'

#-------------------------------------------------------------------
#Escribe los registros de lluvia con las predicciones
#-------------------------------------------------------------------
#Obtiene las fechas
Dates = Rain24h.index.to_pydatetime().tolist()
#Genera la serie de pandas
DatesNew = [Dates[-1]+dt.timedelta(minutes = 5*i) for i in range(1,13)]
#itera para escribir los archivos con la rpeduiccion de lluvia 
for k in Predicciones.keys():
	DictPred = {}
	for k2 in Rain24h.keys():
		DictPred.update({k2:np.hstack([Rain24h[k2][-1], Predicciones[k][k2]])})
	DatesNew = [Dates[-1]+dt.timedelta(minutes = 5*i) for i in range(0,13)]
	RainPred = pd.DataFrame(DictPred, index=pd.to_datetime(DatesNew))
	#Guardado de la consulta
	f = open(args.ruta_out + '_cast_'+k+'.rain', 'w')
	pickle.dump(RainPred, f)
	pickle.dump(Coord, f)
	f.close()
	#imprime para el log 
	print 'Registro de lluvia en prediccion para condiciones '+k+'\n'
	print RainPred.mean(axis = 1)
	print '\n'
