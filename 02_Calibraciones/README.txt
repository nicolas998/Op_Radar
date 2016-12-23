En La carpeta calibraciones se guardan los archivos que contienen las 
calibraciones para las diferentes configuraciones del modelo, de acuerdo 
a la version del modelo se tiene un archivo diferente, de esta manera 
para la configuracion 01 (lo que eso signifique), se tendria 
la configuracion:

Cuenca_01.calib

Normalmente en donde dice "Cuenca" se puede colocar el nombre de 
la cuenca que se esta simulando. 

Dentro de cada archivo se tiene la siguiente estructura:
----------------------------------------------------------------------
Inicio Archivo:

1.  La calibración se compone de 10 parámetros escalares, los cuales son:
2.  - R[1] : Evaporación.
3.  - R[2] : Infiltración.
4.  - R[3] : Percolación.
5.  - R[4] : Pérdidas.
6.  - R[5] : Vel Superficial.
7.  - R[6] : Vel Sub-superficial.
8.  - R[7] : Vel Subterranea.
9.  - R[8] : Vel Cauces.
10. - R[9] : Alm capilar maximo.
11. - R[10] : Alm gravitacional maximo.
12. 
13.  StorageName     evp     ks_v    kp_v    Kpp_v   v_sup   v_sub   v_supt  v_cau   Hu      Hg
14.  cuenca_Calib_01   1.0     0.01    1.0     0.0     0.8     0.8     0.01    1.0     0.4      0.8
15.  cu01_Calib_02   1.0     1.0     5.0     0.0     0.6     0.8     0.01    0.93    1.0     1.0
16.  cu01_Calib_03   1.0     1.0     5.0     0.0     0.2     0.7     0.01    0.97    1.0     1.0
.
.
.
N.   cu01_Calib_N   1.0     1.0     5.0     0.0     0.2     0.7     0.01    0.97    1.0     1.0
-------------------------------------------------------------------------------


Para un mismo proyecto se pueden establecer tantas calibraciones como 
se desee, el modelo guardara las condiciones para cada una de ellas en el tiempo

