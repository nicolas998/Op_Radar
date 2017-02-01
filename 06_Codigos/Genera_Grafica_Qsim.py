#!/usr/bin/env python
import argparse
import textwrap
import pickle
from plotly.offline import download_plotlyjs, plot
from plotly.graph_objs import Scatter, Figure, Layout
import plotly.plotly as py
import plotly.graph_objs as go 
import numpy as np
import os 
import pandas as pnd
import commands

#Parametros de entrada del trazador
parser=argparse.ArgumentParser(
	prog='Genera_Grafica_Qsim',
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description=textwrap.dedent('''\
	Genera la figura de caudales simulados para un periodo asignado de tiempo, de forma 
	adicional presenta el hietograma de precipitacion.
        '''))
#Parametros obligatorios
parser.add_argument("nodo",help="Numero del nodo dentro de la red hidrica a plotear")
parser.add_argument("fechai",help="fecha de inicio de ploteo YYYY-MM-DD HH:MM:SS")
parser.add_argument("fechaf",help="fecha de finalizacion de ploteo YYYY-MM-DD HH:MM:SS")
parser.add_argument("observado",help="Numero de la estacion de caudales observada")
	
#lee todos los argumentos
args=parser.parse_args()

#Rutas por defecto
ruta_qsim = '/home/nicolas/Operacional/Op_Interpolated/03_Simulaciones/02_Stream_History/'
ruta_rain = '/home/nicolas/Operacional/Op_Interpolated/03_Simulaciones/01_Rain/Mean_Rain_History.rainh'
ruta_qobs = '/home/nicolas/Operacional/Op_Interpolated/03_Simulaciones/03_Stream_Observed/'
ruta_figura = '/media/nicolas/discoGrande/01_SIATA/ResultadosOperacion/Ope_AMVA_interpol/Qsim/'


#-----------------------------------------------------------------------------------------------------
#Lectura de infomraciion para el plot
#-----------------------------------------------------------------------------------------------------
#Nodo para buscar caudales
Nodo = int(args.nodo)
a = args.fechai
fechai = a[0:4]+'-'+a[4:6]+'-'+a[6:8]+' '+a[8:10]+':'+a[10:12]+':'+a[12:14]
a = args.fechaf
fechaf = a[0:4]+'-'+a[4:6]+'-'+a[6:8]+' '+a[8:10]+':'+a[10:12]+':'+a[12:14]

#Lista caudales simulados
LQsim = os.listdir(ruta_qsim)
LQsim = [i for i in LQsim if i.endswith('qsimh')]
#Carga la historia de los simulados
DictQsim = {}
DictQtext = {}
for l in LQsim:
    Qsim = pnd.read_msgpack(ruta_qsim+l)
    DictQsim.update({l[9:-6]:Qsim[Nodo][fechai:fechaf]})
    DictQtext.update({l[9:-6]: ['%.2fm3/s' % i for i in Qsim[Nodo][fechai:fechaf].values]})
#Carga el hietograma de la lluvia medio para la cuenca
Rain = pnd.read_msgpack(ruta_rain)
Rain = Rain[fechai:fechaf]
Rain[np.isnan(Rain)] = 0
RainText = ['%.2fmm' % i for i in Rain.values.T[0]]
#Carga observados y lluvia
if args.observado <> 'Nada':
	Qobs = pnd.read_msgpack(ruta_qobs + args.observado)
	Qobs = Qobs[fechai:fechaf]
	QobsText = ['%.2fm3/s' % i for i in Qobs.values]
#Encuentra min y max para establecer el rango de grafico 
Qmax = 0; Qmin = 9999
for i in DictQsim.keys():
    if DictQsim[i].max()> Qmax: Qmax = DictQsim[i].max()
    if DictQsim[i].min()< Qmin: Qmin = DictQsim[i].min()


#-----------------------------------------------------------------------------------------------------
# Prepara datos para ingresarlos en la figura
#-----------------------------------------------------------------------------------------------------
#colores de las simulaciones
Colors = []
for i,j in zip(np.linspace(0,230,100), np.linspace(120,200,100)):
    Colors.append('rgb('+str(i)+','+str(j)+',230)')

data =[]
for k,c in zip(DictQsim.keys(), Colors):
    trace = go.Scatter(
        y = DictQsim[k].values,
        x = DictQsim[k].index.to_pydatetime(),
        mode = 'lines',
        name = 'Sim '+k,
        line = dict(
            color = c
        ),
        hoverinfo = 'x+text',
        text = DictQtext[k],
    )
    data.append(trace)
#Datos de lluvia 
trace = go.Scatter(
    y = Rain.values.T[0],
    x = Rain.index.to_pydatetime(),
    fill = 'tozeroy',
    yaxis='y2',
    name = 'Precip',
    line=dict(width=0.5,
        color='rgb(0, 0, 255)'),
    hoverinfo = 'x+text',
    text = RainText
)
data.append(trace)
#Datos observados
if args.observado <> 'Nada':
	trace = go.Scatter(
	    y = Qobs.values,
	    x = Qobs.index.to_pydatetime(),
	    mode = 'lines+markers',
	    name = 'Observado',
	    line = dict(
	        color = 'rgb(192,21,61)'
	    ),
	    hoverinfo = 'x+text',
	    text = QobsText
	)
	data.append(trace)

#-----------------------------------------------------------------------------------------------------
# Prepara el estilo de la figura
#-----------------------------------------------------------------------------------------------------
#Estilo de la figura 
layout = go.Layout(
	width = '100%',
	height ='100%',
	legend=dict(
        x=0.,
        y=0.99
    ),
	autosize = True,
	margin=go.Margin(
		l=50,
		r=50,
		b=60,
		t=20,
		pad=7
	),
	xaxis = dict(
		title = 'Tiempo [5min]',
		zeroline = False,
		tickfont=dict(
			size=14,
			color='black'
		),
		exponentformat='e',
		showexponent='All',
		showline = True,
	),
	
	yaxis = dict(
        title = 'Caudal [m3/s]',
        zeroline = False,
        showline = True,
        range = [Qmin-Qmin*0.5, Qmax*1.5]
    ),
	
	yaxis2=dict(
        title=u'Precipitacion [mm]',
        titlefont=dict(
            color='rgb(0, 0, 255)'
        ),
        tickfont=dict(
            color='rgb(0, 0, 255)'
        ),
        overlaying='y',
        side='right',
        showgrid=False,
        zeroline = False,
        range = [Rain.values.T[0].max()*5, 0],
        showline = True
    )
)

Fig = go.Figure(data = data, layout = layout)

#-----------------------------------------------------------------------------------------------------
# Guarda el html lo abre y lo edita de nuevo 
#-----------------------------------------------------------------------------------------------------
#rute = ruta_figura +'Qsim_'+args.nodo+'_'+args.fechai+'_'+args.fechaf+'.html'

rute = ruta_figura +'Qsim_'+args.nodo+'.html'
plot(Fig, filename=rute, auto_open= False)
#modificacion
f = open(rute,'r')
L = f.readlines()
f.close()
#Modificaciones
var = '<html style="width: 100%, height: 100%;"><script type="text/javascript">Object.defineProperty(window.navigator, "userAgent", { get: function(){ return "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20120101 Firefox/33.0"; } });Object.defineProperty(window.navigator, "vendor", { get: function(){ return "Mozilla, Inc."; } });Object.defineProperty(window.navigator, "platform", { get: function(){ return "Windows"; } });</script><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"><style></style></head><body style="width: 100%, height: 100%;"><script type="text/javascript">/**'
L.insert(0, var)
#comenta el id
L[-1] = L[-1].replace('<div id=', '<!-- <div id=')
L[-1] = L[-1].replace('class="plotly-graph-div"></div>', 'class="plotly-graph-div"></div>-->')
#Mete el texto que no se bien que hace, define unas funciones para el 100% del size
var = 'var d3 = Plotly.d3;var gd3 = d3.select("body").append("div").style({width: "100%",height: "100%"});var gd = gd3.node();'
#str1 = '"https://plot.ly";'+L2[0].split('\n')[0]
str1 = '"https://plot.ly";'+var
L[-1] = L[-1].replace('"https://plot.ly";', str1)
#Quita el pedazo que indica el tamano del height y width
pos1 = L[-1].index('Plotly.newPlot')
pos2 = L[-1].index('[{"name": ')
l = L[-1][pos1:pos2]
ids = l.split('"')[1]
L[-1] = L[-1].replace('"'+ids+'"', 'gd')
L[-1] = L[-1].replace('"height": "100%", "width": "100%",', '')
#Para que se autosize y para quitar link 
L[-1] = L[-1].replace('window.removeEventListener("resize");window.addEventListener("resize", function(){Plotly.Plots.resize(document.getElementById(gd));});','')
L[-1] = L[-1].replace('"showLink": true', '"showLink": false')
#Pega para el resize
var = 'window.onresize = function() {Plotly.Plots.resize(gd);};'
L[-1] = L[-1].replace('</script></body></html>', var + '</script></body></html>')
#Escribe de nuevo el html
f = open(rute,'w')
f.writelines(L)
f.close()

#print commands.getoutput(rute)
print 'http://siata.gov.co/nicolasl/Ope_AMVA_interpol/Qsim/Qsim_'+args.nodo+'.html'

