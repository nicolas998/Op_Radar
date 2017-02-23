#!/usr/bin/env python
import argparse
import textwrap
import numpy as np
import os 
from wmf import wmf 

#Parametros de entrada del trazador
parser=argparse.ArgumentParser(
	prog='Copia_StorageBackup',
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description=textwrap.dedent('''\
	Genera una copia del almacenamiento de backup y las coloca en 
	donde se encuentra el modelo operacional de forma que pueda seguir 
	trabajando.
        '''))
#Parametros obligatorios
parser.add_argument("rutaBack",help="Ruta donde se encuentra el backup")
parser.add_argument("rutaRes",help="Ruta donde va a dejar las copias")
parser.add_argument("Ncopias",help="Cantidad de copias que va a hacer de esta", type=int)

#lee todos los argumentos
args=parser.parse_args()

#------------------------------------------------------------------------------
#Lo hace
#------------------------------------------------------------------------------
#Lista los archivos que sean de backup
L = os.listdir(args.rutaBack)
L = [i for i in L if i.endswith('StOhdr') or i.endswith('StObin')]
#Itera haciendo copias
for i in range(1, args.Ncopias+1):
	if i<10:
		ti = '00'+str(i)
	elif i<100:
		ti = '0'+str(i)
	else:
		ti = str(i)
	#Explota el elemento 
	for j in L:
		l1 = j.split('_')
		l1 = l1[:-1] + l1[-1].split('.')
		l1[2] = ti
		a = '_'.join(l1[:-1]) + '.'+l1[-1]
		comando = 'cp '+args.rutaBack+j+' '+args.rutaRes+a
		os.system(comando)
	
