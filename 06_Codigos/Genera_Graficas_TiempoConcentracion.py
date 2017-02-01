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
	Genera las ofiguras dinamicas en plotly del tiempo de concentracion en cada elemento de la cuenca 
	(parte de la red), de forma adicional genera un pickle con un diccionario en el cual se 
	encuentra el informe geomorfologico de las cuencas asociadas a cada uno de los nodos 
	hidrologicos.
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
posicion = np.where(wmf.models.control<>0)[1]
#Obtiene parametros en los demas lugares (nodos)
x,y = wmf.cu.basin_coordxy(cu.structure, cu.ncells)
DictParam = {}
for pos,nodo in zip(posicion,nodos):
	#Calcula la cuenca y param
	cu2 = wmf.Basin(x[pos], y[pos], cu.DEM, cu.DIR, umbral=args.umbral)
	cu2.GetGeo_Parameters(GetPerim = False)
	#Guarda los parametros
	DictParam.update({str(nodo):{'Geo':cu2.GeoParameters,
		'Tc':cu2.Tc}})
    
print 'Tiempos de concentracion calculados'
#-----------------------------------------------------------------------------------------------------
#Define la funcion de plot de plotly
#-----------------------------------------------------------------------------------------------------
def Plot_Tc_Plotly(TcDict, rute = None):
    #Set de textos
    x = [i[:10] for i in TcDict.keys()]
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
        width = '100%',
        height ='100%',
        autosize = True,
        margin=go.Margin(
            l=50,
            r=20,
            b=40,
            t=20,
            pad=4
        ),
        
        xaxis = dict(
            tickfont = dict(
                size = 10,
                color = 'black'
            ),

        ),
        yaxis = dict(
            title = 'Tiempo [horas]',
            zeroline = False,
            showline = True,
        ),
        
    )
    #figura
    Fig = go.Figure(data = data, layout = layout)
    if rute<>None:
        plot(Fig, filename=rute, auto_open= False)
        #modificacion
        f = open(rute)
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
        pos2 = L[-1].index('[{"text": ')
        l = L[-1][pos1:pos2]
        ids = l.split('"')[1]
        L[-1] = L[-1].replace('"'+ids+'"', 'gd')
        L[-1] = L[-1].replace('"height": "100%", "width": "100%",', '')
        #Pega para el resize
        var = 'window.onresize = function() {Plotly.Plots.resize(gd);};'
        L[-1] = L[-1].replace('</script></body></html>', var + '</script></body></html>')
        L[-1] = L[-1].replace('window.removeEventListener("resize");window.addEventListener("resize", function(){Plotly.Plots.resize(document.getElementById(gd));});','')
        L[-1] = L[-1].replace('"showLink": true', '"showLink": false')
        #Escribe de nuevo el html
        f = open(rute,'w')
        f.writelines(L)
        f.close()
#guyarda las figuras
ruta = args.rutaPlots
for k in DictParam.keys():
    Plot_Tc_Plotly(DictParam[k]['Tc'], rute = ruta + 'Tc_'+k+'.html')
    print k
print 'Figuras de tiempo de concentracion guardadas'
#Guarda el diccionario con las propiedades de los tramos
f = open(args.rutaGeomorfo, 'w')
pickle.dump(DictParam,f)
f.close()
