# Op_Interpolated

Estructura de carpetas, archivos y codigos para la ejecucion operacional del modelo hidrologico distribuido.
En este caso el modelo opera mediante la interpolacion de campos de precipitacion a partir de estaciones 
pluviometricas en tierra.  El modulo acepta multiples proyectos para la misma cuenca y multiples esctructuras 
de calibracion.  La estructura de compone de la siguiente forma:

Esta es simplemente una propuesta de estrcutura operacional para la modelacion hidrologica,
se ha planteado para funcionar acoplada al paquete de python **WMF** 
(**https://github.com/nicolas998/WMF.git**).

## 01 Cuenca(s) base:

Son los proyectos montados para la modelacion de la cuenca en cuestion.
Estos deben ser obtenidos mediante el **WMF**, localizado en **https://github.com/nicolas998/WMF.git**.
La carpeta que contiene los proyectos de modelacion se llama: **01_Bin_Cuencas**. Al menos 
se debe contar con un proyecto de simulacion.

Los archivos de las cuencas se identifican por ser archivos del tipo **netCDF4**, por lo 
que su extensión termina en ".nc", estos archivos deben tener un numero de hasta tres 
cifras al final de su identificador, ej:

- cuenca_V1_001.nc
- cuencaLoca_002.nc
- cuencaLoca_010.nc
- etc...

## 02 Calibraciones:

Carpeta donde se contienen las calibraciones del modelo, debe existir un archivo 
de calibracion por proyecto y se encuentran terminados en **.calib**, y este 
archivo se conecta con la cuenca mediante el numero identificador de la cuenca, 
con lo cual de acuerdo al ejemplo anterior se tendrían los siguientes 
archivos de calibracion:

- cu_V1_Calib_001.calib
- Loca002.calib
- CalibLoca_010.calib

Cada proyecto puede tener una o más calibraciones, de las cuales se ejecutan 
las que no se encuentren comentadas (Mas detalle en el README.txt de 02_Calibraciones).
Cada calibracion al interior de un archivo de calibracion cuenta con un ID.

## 03 Simulaciones 

Contiene los archivos de caudales simulados por cada combinacion de proyecto 
y por cada calibración, estos arvhicos son binarios de python que contienen 
series de tiempo en formato **DataFRame** de **pandas**.  La combinación 
de los archivos se da de acuerdo al ID de la cuenca (cuID) y al ID de la calibracion
(caID) de la siguiente forma: **QSim_cuID_caID.qsim**.  De acuerdo 
a los ejemplos anteriores se tendrían las siguientes simulaciones para 
la cuenca 001 contando que la calibracion 001 contenga IDs 01, 02, 03:

- Qsim_001_01.qsim
- Qsim_001_02.qsim
- Qsim_001_03.qsim

Estos archivos se generan de forma automatica durante la ejecucion del
modelo operacional.

## 04 Almacenamiento

Carpeta para el guardado de las condiciones de almacenamiento de flujo de los 
diferentes tanques para los diferentes elementos de simulacion de la cuenca
(ya sean estos celdas o laderas).  Las condiciones de almacenamiento se 
guardan en formato binario de **Fortran 90**, los archivos son leidos y 
escritos por funciones propias de **WMF**.

El nombre de los archivos esta dado por el nombre del proyecto cuenca 
y por el numero de la calibracion de la siguiente manera: 
**Storage_cuID_caID.StoHdr**.  Estos archivos se componen de dos elementos:

- Hdr: Encabezado de almacenamiento, contiene informacion promedio de los 
almacenamientos de los diferentes tanque del modelo, su extención 
termina en **.StoHdr**.
- Bin: Binario con los almacenamientos del modelo en cada elemento
 de simulación. termina con **StoBin**.

Se plantea realizar el almacenamiento de las ultimas 24 horas.

## 05 Figuras

Carpeta donde se guardan las figuras de simulacion, se plantea el 
guardado de las siguientes figuras:

- Caudales simulados en cada nodo de la red hidrográfica.
- Campo de lluvia obtenido en las últimas 24 horas y 
extrapolado una hora adelante.
- Campo de humedad de las ultimas 24 horas y extrapolado 
una hora adelante.

## 06 Codigos

Contiene los codigos para la ejecucion operacional del modelo, 
la generación de campos, la actualización de los mismos y la 
generación de figuras.  En su interior los códigos se dividen en 
dos grandes grupos. 1. Códigos de ejecución directa, se ejecutan 
de forma directa sobre la terminal. 2. Códigos operacionales: 
Estos llaman a los del grupo 1 para realizar tareas periódicas.

## 07 Logs Crons

Dentro de esta carpeta se escriben los logs de las ejecuciones
periódicas de la modelación.

## 00 Notas de avance:

**Cosas que estan hechas:**

- Montaje de la estructura operacional ordenada.

**Cosas que faltan**

- Operacion generacion de campos de lluvia actuales.
- Generación campos de lluvia futuros.
- Ejecución del modelo con los campos.
- Guardado de Figuras.
