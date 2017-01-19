#!/usr/bin/env python
import argparse
import textwrap
from wmf import wmf
import pickle
from plotly.offline import download_plotlyjs, plot, iplot
from plotly.graph_objs import Scatter, Figure, Layout
import plotly.plotly as py
import plotly.graph_objs as go 
from wmf import wmf 
import numpy as np

#Parametros de entrada del trazador
parser=argparse.ArgumentParser(
	prog='Consulta_Caudal',
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description=textwrap.dedent('''\
	Actualiza el kml obtenido por el modelo para que sea legible en la pagina del SIATA.
        '''))
#Parametros obligatorios
parser.add_argument("cuencaNC",help="Binario con la cuenca que se le va a obtener el kml")
parser.add_argument("rutaPlots",help="Ruta donde se guardan las figuras de tiempos de concentracion")
parser.add_argument("rutaGeomorfo",help="Ruta donde se guarda el pickle con el diccionario con las propiedades geomorfologicas de los tramos")
parser.add_argument("-u","--umbral",help="Umbral para la generacion de red hidrica en la cuenca", type = float, default = 30)
	
#lee todos los argumentos
args=parser.parse_args()

#-----------------------------------------------------------------------------------------------------
#Carga la cuenca	 
#-----------------------------------------------------------------------------------------------------
cu = wmf.SimuBasin(0,0,0,0, rute=args.cuencaNC)
#Carga los nodos 
nodos = wmf.models.control[wmf.models.control<>0]
#Obtiene parametros en los demas lugares (nodos)
x,y = wmf.cu.basin_coordxy(cu.structure, cu.ncells)
DictParam = {}
for pos,nodo in zip(cu.hills[0][:10],nodos[:10]):
    #Calcula la cuenca y param
    cu2 = wmf.Basin(x[pos-1], y[pos-1], cu.DEM, cu.DIR, umbral=args.umbral)
    cu2.GetGeo_Parameters(GetPerim = False)
    #Guarda los parametros
    DictParam.update({str(nodo):{'Geo':cu2.GeoParameters,
        'Tc':cu2.Tc}})
print 'Tiempos de concentracion calculados'
#-----------------------------------------------------------------------------------------------------
#Define la funcion de plot de plotly
#-----------------------------------------------------------------------------------------------------
def Plot_Tc_Plotly(TcDict, show = True, rute = None):
    #Set de textos
    x = TcDict.keys()
    x.insert(0,'Mediana')
    y = [TcDict[k] for k in TcDict.keys()]
    y.insert(0,np.median(np.array(TcDict.values())))
    ytext = ['%.3f[hrs]' % i for i in y]
    #Para preparar grafico 
    desv = np.array(TcDict.values()).std()
    Colores = ['rgb(0,102,204)' for i in range(len(y))]
    Colores[0] = 'rgb(0,25,51)'
    for c,i in enumerate(y[1:]):
        if i>y[0]+desv or i<y[0]-desv:
            Colores[c+1] = 'rgb(153,0,0)'
    #informacion a desplegar en la barra
    data = [go.Bar(
            x = x,
            y = y,
            dx = 0.1,
            hoverinfo = 'x+text',
            text = ytext,
            marker = dict(
                color = Colores
            )
        )]
    #Estilo de layout
    layout = go.Layout(
        width = 600,
        height = 400,
        xaxis = dict(
            tickfont = dict(
                size = 14,
                color = 'black'
            ),

        ),
        yaxis = dict(
            title = 'Tiempo [horas]',
            zeroline = False,
            showline = True,
        )
    )
    #figura
    Fig = go.Figure(data = data, layout = layout)
    if show:
        iplot(Fig)
    if rute<>None:
        plot(Fig, filename=rute, auto_open= False)
#guyarda las figuras
ruta = args.rutaPlots
for k in DictParam:
    Plot_Tc_Plotly(DictParam[k]['Tc'], rute = ruta + 'Tc_'+k+'.html', show=False)
    print k
print 'Figuras de tiempo de concentracion guardadas'
#Guarda el diccionario con las propiedades de los tramos
f = open(args.rutaGeomorfo, 'w')
pickle.dump(DictParam,f)
f.close()
