#!/usr/bin/env python
import argparse
import textwrap
import os 
from wmf import wmf

#Parametros de entrada del trazador
parser=argparse.ArgumentParser(
	prog='Consulta_Caudal',
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description=textwrap.dedent('''\
	Actualiza el kml obtenido por el modelo para que sea legible en la pagina del SIATA.
        '''))
#Parametros obligatorios
parser.add_argument("cuencaNC",help="Binario con la cuenca que se le va a obtener el kml")
parser.add_argument("umbral",help="Umbral para la generacion de red hidrica en la cuenca", type = float)
parser.add_argument("dx",help="Delta de x plano para la estimacion de longitud de cauces", type = float)
parser.add_argument("ruta",help="ruta donde se guarda el kml")
parser.add_argument("precip",help="ruta a mapa de precipitacion o contante de precipitacion")
parser.add_argument('-1','--coefMax', nargs='+', 
	help='Coeficientes de regionalizacion maxima defecto:[6.71, 3.29]', default = [6.71, 3.29], type = float)
parser.add_argument('-2','--expoMax', nargs='+', 
	help='Exponentes de regionalizacion maxima defecto:[0.82, 0.64]', default = [0.82, 0.64], type = float)
parser.add_argument('-3','--coefMin', nargs='+', 
	help='Exponentes de regionalizacion minima defecto:[0.4168, 0.2]', default = [0.4168, 0.2], type = float)
parser.add_argument('-4','--expoMin', nargs='+', 
	help='Exponentes de regionalizacion minima defecto:[1.058, 0.98]', default = [1.058, 0.98], type = float)
	
#lee todos los argumentos
args=parser.parse_args()
print args.expoMax
#-----------------------------------------------------------------------------------------------------
#Carga la cuenca y escribe un kml
#-----------------------------------------------------------------------------------------------------
#Carga la cuenca
cu = wmf.SimuBasin(0,0,0,0, rute=args.cuencaNC)
#Mira si la precipitacion es una ruta o un numero
try:
	Precip = float(args.precip)
except:
	Precip, p = wmf.read_map_raster(args.precip)
	Precip = cu.Transform_Map2Basin(Precip, p)
#Calcula caudales medios y regionalizacion de maximos 
cu.GetQ_Balance(Precip)
Qmax = cu.GetQ_Max(cu.CellQmed, args.coefMax, args.expoMax)
Qmin = cu.GetQ_Min(cu.CellQmed, args.coefMin, args.expoMin)
Qmin[Qmin<0] = 0
DictQ = {'Qmed': cu.CellQmed}
for c,k in enumerate(['2.33', '5', '10', '25', '50', '100']):
    DictQ.update({'Qmin'+k:Qmin[c]})
    DictQ.update({'Qmax'+k:Qmax[c]})
#Guarda el kml base
cu.Save_Net2Map(args.ruta, umbral=args.umbral, DriverFormat = 'kml', 
    NumTramo=True, 
    dx = args.dx,
    Dict = DictQ,
    formato = '%.3f')

#-----------------------------------------------------------------------------------------------------
#Corrige el encabezado y cambia colores 
#-----------------------------------------------------------------------------------------------------
#Leer kml 
f = open(args.ruta,'r')
LinKml = f.readlines()
f.close()
#Diccionario con colores para horton
DictColorHort = {'viejo':{'1': 'ffF1AE53', '2': 'ffC77E26', '3': 'ff9E4C22', '4': 'ff712010', '5': '03234D'},
	'nuevo':{'1': '#53AEF1', '2': '#267EC7', '3': '#224C9E', '4': '#102071', '5': '#03234D'}}

flag = True
while flag:
	try:
		#Coloca el estuilo de la corriente 
		pos = LinKml.index('\t<Style><LineStyle><color>ff0000ff</color></LineStyle><PolyStyle><fill>0</fill></PolyStyle></Style>\n')        
		horton = LinKml[pos+3].split('>')[1].split('<')[0]
		LinKml[pos] ='\t<Style><LineStyle><color>'+DictColorHort['viejo'][horton]+'</color><width>'+horton+'</width></LineStyle><PolyStyle><fill>0</fill></PolyStyle></Style>\n' 
		#Coloca el description 
		codigo = str(int(float(LinKml[pos+4].split('>')[1].split('<')[0])))
		Longitud = '.4f',float(LinKml[pos+2].split('>')[1].split('<')[0])
		Longitud = str(Longitud[1])
		LinKml[pos+2] = '\t\t<SimpleData name="Long[km]">'+Longitud+'</SimpleData>\n'
		LinKml[pos+4] = '\t\t<SimpleData name="Codigo">'+codigo+'</SimpleData>\n'
		LinKml.insert(pos+4,'\t\t<SimpleData name="color_linea">'+DictColorHort['nuevo'][horton]+'</SimpleData>\n')
		LinKml.insert(pos+4,'\t\t<SimpleData name="grosor_linea">'+horton+'</SimpleData>\n')
		nombre = '<name> Resultados Simulacion Hidrologica Tramo '+codigo+' </name>\n'
		LinKml.insert(pos,nombre)
		LinKml.insert(pos+4,'\t\t<SimpleData name="Q_sim">'+str(0.00)+'</SimpleData>\n')
		LinKml.insert(pos+4,'\t\t<SimpleData name="Q_sim_max_24h">'+str(0.00)+'</SimpleData>\n')        		
	except:
		flag = False

#Encabezado estatico
LinKml[4] = LinKml[4].replace('float', 'string')
LinKml[5] = LinKml[5].replace('int', 'string')
LinKml[6] = LinKml[6].replace('int', 'string')
LinKml[6] = LinKml[6].replace('Tramo', 'Codigo')
LinKml.insert(7,'\t<SimpleField name="color_linea" type="string"></SimpleField>\n', )
LinKml.insert(7,'\t<SimpleField name="grosor_linea" type="string"></SimpleField>\n', )
LinKml.insert(7,'\t<SimpleField name="Municipio" type="string"></SimpleField>\n', )
LinKml.insert(7,'\t<SimpleField name="Tipo_Canal" type="string"></SimpleField>\n', )
LinKml.insert(7,'\t<SimpleField name="Nombre_Cauce" type="string"></SimpleField>\n', )
LinKml.insert(7,'\t<SimpleField name="Barrio" type="string"></SimpleField>\n', )
LinKml.insert(7,'\t<SimpleField name="Vereda" type="string"></SimpleField>\n', )
LinKml.insert(7,'\t<SimpleField name="Resolucion" type="string"></SimpleField>\n', )
for i in range(7,20):
    LinKml[i] = LinKml[i].replace('float','string')
#Caudales simulados
LinKml.insert(7,'\t<SimpleField name="Q_sim" type="string"></SimpleField>\n', )
LinKml.insert(7,'\t<SimpleField name="Q_sim_max_24h" type="string"></SimpleField>\n', )

#-----------------------------------------------------------------------------------------------------
#Escribe el kml bueno
#-----------------------------------------------------------------------------------------------------
#Escribe nuevo kml
f = open(args.ruta,'w')
f.writelines(LinKml)
f.close()
