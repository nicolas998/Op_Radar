# Op_Interpolated

Estructura de carpetas, archivos y codigos para la ejecucion operacional del modelo hidrologico distribuido.
En este caso el modelo opera mediante la interpolacion de campos de precipitacion a partir de estaciones 
pluviometricas en tierra.  El modulo acepta multiples proyectos para la misma cuenca y multiples esctructuras 
de calibracion.  La estructura de compone de la siguiente forma:

## Cuenca(s) base:

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

## Calibraciones:

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

## Simulaciones 


